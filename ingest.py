# ingest.py
import os
from utils.ingestion import ingest_document_to_pinecone_local

# Set environment variables for the local run
# You need to replace the placeholders with your actual keys
os.environ['PINECONE_API_KEY'] = 'pcsk_48u71B_9xDnkLzSjoCMfst8agt7s4mSS8J8dmEsc56AeBMM9uuGshnCkJafeEqaH1ZGsDY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyAOnOz3B_SnddIfePBE_QM4Do-uSdkdPgU'

# The document you want to ingest
file_path = 'data/arogya_sanjeevani.pdf'
index_name = 'hackrx-index'

# Ingest the document
ingest_document_to_pinecone_local(
    file_path=file_path,
    index_name=index_name,
    doc_type='structured_policy'
)
