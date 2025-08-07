# utils/ingestion.py
import os
from utils.text_splitter import get_text_splitter
from utils.pinecone_helper import get_pinecone_client
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
import requests # We still need this for the request body in main.py to work

def ingest_document_to_pinecone_local(file_path: str, index_name: str, doc_type: str = "general"):
    """
    Ingests a document from a local file into Pinecone.
    """
    print("Starting local document ingestion process...")

    try:
        # 1. Load document from local file
        if file_path.endswith('.pdf'):
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
        elif file_path.endswith('.txt'):
            loader = TextLoader(file_path)
            docs = loader.load()
        else:
            print(f"Warning: No loader found for file type {file_path}")
            return

        if not docs:
            print("Document loading failed. Aborting ingestion.")
            return

        # 2. Extract text and split into chunks
        splitter = get_text_splitter(document_type=doc_type)
        
        # The MarkdownHeaderTextSplitter works on text directly, not Document objects
        if doc_type == 'structured_policy':
            raw_text = docs[0].page_content
            # The split_text method of MarkdownHeaderTextSplitter returns a list of Document objects
            chunks = splitter.split_text(raw_text)
        else:
            chunks = splitter.split_documents(docs)

        print(f"Document split into {len(chunks)} chunks.")

        # 3. Create embeddings for each chunk using an open-source model
        # The 'multi-qa-mpnet-base-dot-v1' model has a dimension of 768.
        # Your Pinecone index must be configured for this dimension.
        model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
        
        texts_to_embed = [chunk.page_content for chunk in chunks]
        embeddings = model.encode(texts_to_embed).tolist()
        print(f"Created {len(embeddings)} embeddings with dimension {len(embeddings[0])}.")

        # 4. Upsert vectors to Pinecone with metadata
        pc = get_pinecone_client()
        index = pc.Index(index_name)

        vectors_to_upsert = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
            
            vectors_to_upsert.append({
                'id': f"{os.path.basename(file_path)}-{i}",
                'values': embedding,
                'metadata': {
                    'text': chunk.page_content,
                    'document_id': os.path.basename(file_path),
                    'document_type': doc_type,
                    'page_number': str(metadata.get('page_number')) if metadata.get('page_number') is not None else "N/A",
                    'header': metadata.get('Header 1', metadata.get('Header 2', 'N/A'))
                }
            })

        index.upsert(vectors=vectors_to_upsert)
        print(f"Successfully ingested {len(chunks)} chunks into Pinecone index '{index_name}'.")

    except Exception as e:
        print(f"An error occurred during ingestion: {e}")





