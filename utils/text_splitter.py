# utils/text_splitter.py
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

def get_text_splitter(document_type: str):
    """
    Returns the appropriate text splitter based on the document type.
    This is part of the hybrid chunking strategy.
    """
    # If the document is a structured policy (like an insurance policy)
    if document_type == 'structured_policy':
        # This splitter preserves headings and sections, which is great for legal documents
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        return MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    else:
        # This is a more general-purpose splitter for unstructured text
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )