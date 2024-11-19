import uuid
from functions import rag_functions

def main():
    session_id = str(uuid.uuid4())  # Generate a unique session ID
    print(f"Session ID: {session_id}")

    print("\nChatbot initialized! Type your messages below (type 'exit' to end):\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            file_path = f"chat_history_{session_id}.json"
            rag_functions.save_chat_to_file(session_id, file_path)
            print(f"\nChat saved to {file_path}. Goodbye!")
            break
        response = rag_functions.invoke_rag(session_id, user_input)
        print(f"Igris: {response}")


if __name__ == "__main__":
    main()
