import os
import json
import warnings
import bs4
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders import WebBaseLoader

warnings.filterwarnings("ignore")
load_dotenv()

# Initialize environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = "RAG_CHATBOT"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

# Initialize embeddings and LLM
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

# Load and process documents
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("post-content", "post-title", "post-header"))),
)
doc = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(doc)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
retriever = vectorstore.as_retriever()

# Define prompts
system_prompt = (
    "You are a friendly assistant named Igris. "
    "For general conversations, greetings, or casual chat, respond in a friendly and engaging manner. "
    "For specific questions that require context, use the following pieces of retrieved context to answer. "
    "If you don't know the answer, say 'I don't know'. "
    "Keep your answers concise and to the point, with a maximum of three sentences. "
    "Use the retrieved context only if the question is related to the document you have processed. "
    "For general chats like 'hi', 'hello', or any casual conversation, feel free to respond naturally without referring to the document. "
    "\n\n{context}"
)

retriever_prompt = (
    "Given a chat history and the latest user question which might reference context in the chat history,"
    "formulate a standalone question which can be understood without the chat history."
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", retriever_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(model, retriever, contextualize_q_prompt)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# In-memory storage
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


def invoke_rag(session_id: str, user_input: str) -> str:
    response = conversational_rag_chain.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    return response["answer"]


def save_chat_to_file(session_id: str, file_path: str) -> None:
    if session_id in store:
        with open(file_path, "w") as file:
            history = [
                {"role": "User" if isinstance(msg, HumanMessage) else "AI", "content": msg.content}
                for msg in store[session_id].messages
            ]
            file.write(json.dumps(history, indent=4))
