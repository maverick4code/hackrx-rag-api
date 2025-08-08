        # main.py
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field
        from typing import List, Dict, Any
        import os
        from contextlib import asynccontextmanager

        # We only need to import the RAG pipeline components
        from utils.pinecone_helper import get_pinecone_client
        from utils.rag_pipeline import generate_answers

        # --- Lifespan Manager for Pinecone ---
        pinecone_client = None

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            global pinecone_client
            pinecone_client = get_pinecone_client()
            print("Application startup complete. Pinecone client initialized.")
            yield
            pinecone_client = None
            print("Application shutdown complete.")

        # --- Pydantic Models ---
        class HackRxRequest(BaseModel):
            documents: str
            questions: List[str]

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
            
            # The index must be pre-populated. We do NOT run ingestion here.
            index_name = "hackrx-index"

            # Generate answers for all questions
            answers_list = await generate_answers(
                pinecone_index_name=index_name,
                questions=request.questions
            )

            return HackRxResponse(answers=answers_list)
        