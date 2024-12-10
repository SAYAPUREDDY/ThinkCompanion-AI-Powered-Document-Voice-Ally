from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


class ModelInitializer:
    def __init__(self):
        """
        Initializes an instance of the ModelInitializer.
        """
        print("ModelInitializer instance created.")

    def initialize_gemini_flash(self, model_name: str = "gemini-1.5-flash", convert_system_message_to_human: bool = True):
        """
        Initialize and return the ChatGoogleGenerativeAI model(Gemini 1.5 flash)

        Args:
            model_name (str): Name of the Google Generative AI model (default: "gemini-1.5-flash").
            convert_system_message_to_human (bool): Whether to convert system messages to human-readable format.

        Returns:
            ChatGoogleGenerativeAI: The initialized model instance.
        """
        try:
            # Assuming ChatGoogleGenerativeAI is already imported and available
            model = ChatGoogleGenerativeAI(
                model=model_name,
                convert_system_message_to_human=convert_system_message_to_human
            )
            print("Google Generative AI LLM initialized successfully.")
            return model
        except Exception as e:
            print(f"Failed to initialize Google Generative AI LLM: {e}")
            raise

    def initialize_google_embeddings(self, model_name: str = "models/embedding-001"):
        """
        Initialize and return the GoogleGenerativeAIEmbeddings model.

        Args:
            model_name (str): Name of the Google Generative AI embeddings model (default: "models/embedding-001").

        Returns:
            GoogleGenerativeAIEmbeddings: The initialized embeddings instance.
        """
        try:
            # Assuming GoogleGenerativeAIEmbeddings is already imported and available
            embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
            print("Google Generative AI Embeddings initialized successfully.")
            return embeddings
        except Exception as e:
            print(f"Failed to initialize Google Generative AI Embeddings: {e}")
            raise
    

