import json
from pathlib import Path

def update_chat_history(session_id: str, user_input: str, ai_response: str) -> None:
    """
    Updates the chat history for a session by appending the new user input and AI response.
    This version is a function, not part of a class.
    """
    try:
        # Define the path for the chat history file
        chat_history_file = Path("chats") / f"chat_history_{session_id}.json"
        
        # Load the previous chat history if it exists
        if chat_history_file.exists():
            with open(chat_history_file, "r") as file:
                chat_history = json.load(file)
        else:
            chat_history = []

        # Append the new user input and AI response
        chat_history.append({"role": "User", "content": user_input})
        chat_history.append({"role": "AI", "content": ai_response})

        # Save the updated chat history back to the file
        with open(chat_history_file, "w", encoding="utf-8") as file:
            json.dump(chat_history, file, indent=4)

    except Exception as e:
        raise RuntimeError(f"Error updating chat history: {e}")


