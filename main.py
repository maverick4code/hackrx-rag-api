# main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import shutil
from contextlib import asynccontextmanager

# We are now using the local ingestion function.
# The `ingest_document_to_pinecone` function is no longer needed.
# from utils.ingestion import ingest_document_to_pinecone 
from utils.ingestion import ingest_document_to_pinecone_local as ingest_document_to_pinecone
from utils.pinecone_helper import get_pinecone_client
from utils.rag_pipeline import generate_answers 

# --- Lifespan Manager for Pinecone and OpenAI ---
# This ensures a single connection to Pinecone is used across all requests
# to improve performance and reduce latency.
pinecone_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle startup and shutdown events.
    """
    global pinecone_client
    pinecone_client = get_pinecone_client()
    print("Application startup complete. Pinecone client initialized.")
    yield
    # Code after 'yield' runs on shutdown
    pinecone_client = None
    print("Application shutdown complete.")

# --- Pydantic Models for Request and Response ---
class Question(BaseModel):
    text: str

class HackRxRequest(BaseModel):
    documents: str # The URL of the document
    questions: List[str] # The array of questions

class AnswerDetail(BaseModel):
    answer: str
    justification: str
    sources: List[Dict[str, Any]]

class HackRxResponse(BaseModel):
    answers: List[AnswerDetail]

# --- FastAPI Application Instance ---
app = FastAPI(title="HackRx RAG API", version="1.0.0", lifespan=lifespan)

# --- The Main API Endpoint ---
@app.post("/hackrx/run", response_model=HackRxResponse)
async def run_submission(request: HackRxRequest):
    print(f"Received submission for document: {request.documents}")
    print(f"Questions: {request.questions}")

    # We are no longer ingesting from the URL in the request.
    # We will assume the index is already populated with the local file.
    index_name = "hackrx-index"

    # 2. Generate answers for all questions
    answers_list = await generate_answers(
        pinecone_index_name=index_name,
        questions=request.questions
    )

    return HackRxResponse(answers=answers_list)
