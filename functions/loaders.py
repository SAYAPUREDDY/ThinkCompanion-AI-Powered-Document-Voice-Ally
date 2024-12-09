import os
import csv
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import requests
from io import BytesIO
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader



class Loaders:
    """A utility class for loading and extracting text from various file types."""

    def load_text(self, uploaded_file) -> list:
        """Extracts text from a TXT file."""
        try:
            documents=[]
            with open(uploaded_file) as inp:
                for line in inp:
                    documents.append(Document(page_content=line, metadata={"title": "document"}))
            return documents
        except Exception as e:
            raise ValueError(f"Error reading TXT file: {e}")

    def load_pdf(self, uploaded_file) -> list:
        """Extracts text from a PDF file and returns it as a list of Documents."""
        try:
            text = ''
            documents=[]
            pdf_reader = PdfReader(uploaded_file)
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
            if text:
                text += text
                documents.append(Document(page_content=text, metadata={"title": "document"}))
           # Return a list of Document objects
            return documents      
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {e}")

    def load_docx(self, uploaded_file) -> list:
        """Extracts text from a DOCX file."""
        documents = []
        try:
            loader = Docx2txtLoader(uploaded_file)
            documents = loader.load()  # Load the document and return a list of Document objects
            return documents
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {e}")

    # def load_csv(self, uploaded_file) -> str:
    #     """Extracts text from a CSV file."""
    #     documents=[]
    #     try:
    #         loader = CSVLoader(uploaded_file)
    #         documents= loader.load()
    #         return documents          
    #     except Exception as e:
    #         raise ValueError(f"Error reading CSV file: {e}")

    # def load_html(self, uploaded_file) -> str:
    #     """Extracts text from an HTML file."""
    #     try:
    #         content = uploaded_file.read().decode("utf-8")
    #         soup = BeautifulSoup(content, "html.parser")
    #         return soup.get_text(separator="\n")  # Extract text with line breaks
    #     except Exception as e:
    #         raise ValueError(f"Error reading HTML file: {e}")

    # def load_url(self, url: str) -> list:
    #     """Extracts text from a URL."""
    #     try:
    #         response = requests.get(url)
    #         response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    #         soup = BeautifulSoup(response.text, "html.parser")
    #         return soup.get_text(separator="\n")  # Extract text with line breaks
    #     except Exception as e:
    #         raise ValueError(f"Error fetching content from URL '{url}': {e}")

    # def load_image(self, uploaded_file) -> list:
    #     """Extracts text from an image (placeholder for future implementation)."""
    #     try:
    #         documents=[]
    #         loader = UnstructuredImageLoader(uploaded_file)
    #         documents = loader.load()
    #         # Implement your image text extraction logic here, e.g., using OCR
    #         return documents
    #     except Exception as e:
    #         raise ValueError(f"Error reading image file: {e}")

    # def load_directory(self, directory_path: str) -> str:
    #     """Loads all files from a directory (placeholder for future implementation)."""
    #     try:
    #         # Implement your directory handling logic here
    #         return "Directory loading is not implemented yet."
    #     except Exception as e:
    #         raise ValueError(f"Error loading directory '{directory_path}': {e}")



