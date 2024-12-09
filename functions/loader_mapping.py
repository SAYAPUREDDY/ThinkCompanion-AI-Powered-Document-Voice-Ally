from functions.loaders import Loaders

def loader_mapping(content_type: str, uploaded_file):
    """
    Processes an uploaded file by determining its type (from content_type)
    and invoking the appropriate loader method.

    Args:
        content_type: The MIME type of the uploaded file (e.g., "application/pdf", "text/plain").
        uploaded_file: The uploaded file object (e.g., from FastAPI or Flask).

    Returns:
        list: A list of Document objects containing the extracted content.

    Raises:
        ValueError: If the file type is unsupported or an error occurs during processing.
    """
    try:
        # Create an instance of the Loaders class
        loader_instance = Loaders()

        # Mapping of MIME types to loader methods
        loaders = {
            "text/plain": loader_instance.load_text,
            "application/pdf": loader_instance.load_pdf,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": loader_instance.load_docx,
            "image/png": loader_instance.load_image,
            "image/jpeg": loader_instance.load_image,
        }

        # Validate content type
        if content_type not in loaders:
            raise ValueError(f"Unsupported file type: {content_type}")

        # Log the processing file type
        print(f"Processing file of type: {content_type}")

        # Get the corresponding loader method and execute it
        loader_method = loaders[content_type]
        print(loader_method)
        print("loader is successfully loaded")
        content = loader_method(uploaded_file)
        # print(content)
        # Return the extracted content (e.g., list of Documents)
        return content

    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")






