from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.models import User
from app.dependencies import get_current_user
router=APIRouter(prefix="/api/ai",tags=["AI Assistant & RAG"])
class QuestionIn(BaseModel): question:str=Field(min_length=3,max_length=2000)
@router.post("/ask")
def ask_financial_question(data:QuestionIn,user:User=Depends(get_current_user)):
    # Provider-neutral integration point: add your selected LLM API here.
    # Personal finance answers must first be grounded in this user's own DB data.
    raise HTTPException(501,"LLM provider is not configured yet. Core financial, analytics and ML APIs are available.")
@router.post("/knowledge")
def ask_knowledge_question(data:QuestionIn,user:User=Depends(get_current_user)):
    # RAG integration point: ingest financial PDFs, create embeddings and retrieve from FAISS/ChromaDB.
    raise HTTPException(501,"RAG embeddings/vector store are not configured yet. Select the team's LLM and embedding provider first.")
