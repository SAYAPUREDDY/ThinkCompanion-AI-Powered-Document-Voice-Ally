import mimetypes
from pathlib import Path

def get_mime_types(session_folder):
    """
    Get MIME types of files in the specified session folder.

    Args:
        session_folder (Path): Path to the session folder.

    Returns:
        dict: A dictionary with file paths as keys and their MIME types as values.
    """
    mime_types = ""

    try:
        # Ensure the session folder exists and is a directory
        if not session_folder.exists():
            raise FileNotFoundError(f"The folder '{session_folder}' does not exist.")
        if not session_folder.is_dir():
            raise NotADirectoryError(f"The path '{session_folder}' is not a directory.")
        
        # Process files in the session folder
        for file in session_folder.iterdir():
            try:
                if file.is_file():  # Ensure it's a file
                    mime_type, _ = mimetypes.guess_type(file)  # Guess MIME type
                    mime_types[file] = mime_type
            except Exception as file_error:
                print(f"Error processing file '{file}': {file_error}")
    except FileNotFoundError as fnf_error:
        print(fnf_error)
    except NotADirectoryError as nad_error:
        print(nad_error)
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")
    
    return mime_type







