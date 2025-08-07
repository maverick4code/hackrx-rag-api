# utils/document_loader.py
import requests
from langchain.document_loaders import PyMuPDFLoader, Docx2txtLoader
import os

def load_document_from_url(url: str, file_path: str):
    """
    Downloads a document from a URL and loads it using the appropriate LangChain loader.
    """
    print(f"Downloading document from {url}...")
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the file to the specified path
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded to {file_path}.")

        # Load the document based on its file extension
        if file_path.endswith('.pdf'):
            return PyMuPDFLoader(file_path).load()
        elif file_path.endswith('.docx'):
            return Docx2txtLoader(file_path).load()
        else:
            print(f"Warning: No loader found for file type {file_path}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error downloading document: {e}")
        return []
    except Exception as e:
        print(f"Error loading document: {e}")
        return []