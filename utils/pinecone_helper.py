# utils/pinecone_helper.py
import os
from pinecone import Pinecone

def get_pinecone_client():
    api_key = os.getenv("PINECONE_API_KEY")
    # Ensure the environment variable is used for the environment name as well if needed
    # environment = os.getenv("PINECONE_ENVIRONMENT")
    return Pinecone(api_key=api_key)

def check_connection():
    pc = get_pinecone_client()
    try:
        indexes = pc.list_indexes()
        print("Successfully connected to Pinecone. Found indexes:", indexes)
    except Exception as e:
        print(f"Failed to connect to Pinecone: {e}")

# Run this from the command line
# python -c "from utils.pinecone_helper import check_connection; check_connection()"