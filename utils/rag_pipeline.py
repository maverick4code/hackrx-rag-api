# utils/rag_pipeline.py
import os
import json
from typing import List, Dict, Any

from utils.pinecone_helper import get_pinecone_client
import google.generativeai as genai

# --- Configuration for Gemini API ---
def configure_gemini():
    """Configures the Gemini API with the environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)

async def get_relevant_chunks(question: str, index_name: str, top_k: int = 5) -> List[str]:
    """
    Queries Pinecone to find the most relevant document chunks for a given question.
    """
    print(f"Retrieving top {top_k} chunks for question: '{question}'")
    try:
        # Get the Pinecone index
        pc = get_pinecone_client()
        index = pc.Index(index_name)

        # Create an embedding for the user's question using Gemini's embedding model
        embedding_model = 'models/embedding-001'
        response = genai.embed_content(
            model=embedding_model,
            content=question,
            task_type='RETRIEVAL_QUERY'
        )
        query_embedding = response['embedding']

        # Query the index to get the most similar chunks
        query_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Extract the text and metadata from the results
        relevant_chunks = [match['metadata']['text'] for match in query_results.matches]
        return relevant_chunks

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return []

async def generate_answer_with_llm(question: str, context: List[str]) -> Dict[str, Any]:
    """
    Uses an LLM (Gemini) to generate a grounded answer based on the retrieved context.
    """
    print("Generating answer with LLM...")
    configure_gemini()
    
    # Construct the detailed prompt from your design document
    context_str = "\n---\n".join([f"CONTEXT: {c}" for c in context])

    prompt = f"""
    You are an expert on the provided policy documents and your goal is to answer user questions using only the information provided.
    
    ---
    {context_str}
    ---

    INSTRUCTIONS:
    1. Answer the user's QUESTION based SOLELY on the provided CONTEXT.
    2. If the CONTEXT does not contain the answer, you MUST respond with "The information is not available in the provided documents." Do not guess.
    3. Your answer must be accurate, concise, and directly address the question.
    4. For every piece of information you provide, you must cite the specific source from the CONTEXT.
    5. Provide the final answer in a structured JSON format.
    
    QUESTION:
    {question}
    
    The JSON output should have the following structure:
    {{
        "answer": "...",
        "justification": "...",
        "sources": [
            {{ "document_id": "...", "page_number": "..." }},
            ...
        ]
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # Fast and cost-effective
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        # The LLM is instructed to return JSON, so we can parse it directly
        llm_response = response.text
        return json.loads(llm_response)

    except Exception as e:
        print(f"Error generating answer with LLM: {e}")
        return {"answer": "An error occurred while generating the answer.", "justification": "", "sources": []}

async def generate_answers(pinecone_index_name: str, questions: List[str]) -> List[Dict[str, Any]]:
    """
    Orchestrates the full RAG pipeline for a list of questions.
    """
    all_answers = []
    for question in questions:
        context_chunks = await get_relevant_chunks(question, pinecone_index_name)
        generated_answer = await generate_answer_with_llm(question, context_chunks)
        all_answers.append(generated_answer)
    
    return all_answers
