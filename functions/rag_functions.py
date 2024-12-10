import os
import json
from pathlib import Path
import warnings
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from functions.loader_mapping import loader_mapping
from functions.model_loader import ModelInitializer

# Suppress warnings
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = "RAG_CHATBOT"

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT

model_initializer = ModelInitializer()

# Initialize embeddings and LLM
try:
    embeddings = model_initializer.initialize_google_embeddings()
    # print("Embeddings initialized successfully.")
    model = model_initializer.initialize_gemini_flash()
    # print("LLM initialized successfully.")
except Exception as e:
    raise RuntimeError(f"Error initializing embeddings or LLM: {e}")

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
    "Given a chat history and the latest user question which might reference context in the chat history, "
    "formulate a standalone question which can be understood without the chat history. "
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", retriever_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# In-memory storage for chat sessions
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Retrieves or creates session history for a given session ID.
    """
    try:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]
    except Exception as e:
        raise ValueError(f"Error retrieving session history for session_id '{session_id}': {e}")

def save_chat_to_file(session_id: str, file_name: str) -> None:
    """
    Saves chat history for a session to a JSON file in the 'chats' folder.
    """
    try:
        # Use pathlib to manage paths more effectively
        directory = Path("chats")
        directory.mkdir(parents=True, exist_ok=True)  # Ensure the 'chats' directory exists

        # Construct the full file path correctly
        full_file_path = directory / file_name  # This will join 'chats' and file_name correctly

        # Fetch the current session's chat history from the store (if it exists)
        if session_id in store:
            # Format the chat history for saving
            history = [
                {"role": "User" if isinstance(msg, HumanMessage) else "AI", "content": msg.content}
                for msg in store[session_id].messages
            ]

            # Save to the JSON file
            with open(full_file_path, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4)

            print(f"Chat saved successfully to {full_file_path}.")
        else:
            raise ValueError(f"No chat history found for session '{session_id}' to save.")
    except Exception as e:
        raise RuntimeError(f"Error saving chat to file: {e}")


def process_uploaded_file(file_content):
    """
    Processes the uploaded document by determining the file type, extracting text,
    splitting it into chunks, and creating a vector store.

    Args:
        uploaded_file: The uploaded file object.

    Returns:
        retriever: A retriever object created from the vector store.
    """
    try:
        content_documents=file_content
        # Split content into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(content_documents)
        print("splits okayy")
        # Create a vector store from the chunks
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        print("vectorestores okay")
        retriever=vectorstore.as_retriever()
        # Return the retriever for further processing
        return retriever

    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the document: {e}")


# Core RAG functionality setup
def rag_pipeline(retriever, session_id: str, user_input: str) -> str:

    """
    Sets up the RAG pipeline using the provided file, handles user input, 
    and returns the response from the pipeline.
    
    Args:
        file_path (str): Path to the file to be processed.
        session_id (str): Unique identifier for the user session.
        user_input (str): The input query from the user.
    
    Returns:
        str: The response generated by the RAG pipeline.
    """
    try:
        print("Rag pipeline")
        # Step 2: Create the history-aware retriever
        history_aware_retriever = create_history_aware_retriever(model, retriever, contextualize_q_prompt)

        # Step 3: Create the question-answer chain and the retrieval chain
        question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # Step 4: Combine RAG pipeline with session history
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        print("RAG pipeline initialized successfully.")

        # Step 5: Invoke the RAG pipeline with user input
        response = conversational_rag_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}},
        )
        return response["answer"]

    except Exception as e:
        raise RuntimeError(f"Error in RAG pipeline: {e}")




