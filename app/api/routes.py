from fastapi import APIRouter, HTTPException, status
from app.models import IngestRequest, AskRequest, AnswerResponse, SourceInfo
from app.services.fda_service import FDAService
from app.services.rag_service import RAGService

fda_service = FDAService()
rag_service = RAGService()
router = APIRouter()

@router.post("/ingest", summary="Ingestion de médicament")
async def ingest_data(req: IngestRequest):
    """Charge les données d'un médicament depuis OpenFDA."""
    raw = fda_service.fetch_drug_data(req.drug_name)
    if not raw:
        raise HTTPException(status_code=404, detail="Médicament non trouvé")
    
    texts = fda_service.clean_and_format_data(raw)
    count = rag_service.ingest_documents(texts)
    return {"message": "Ingestion OK", "chunks": count}

@router.post("/ask", response_model=AnswerResponse, summary="Poser une question")
async def ask_question(req: AskRequest):
    """Interroge la base de connaissances RAG."""
    answer, raw_sources = rag_service.query(req.question)
    sources = [SourceInfo(content_preview=s) for s in raw_sources]
    return AnswerResponse(answer=answer, sources=sources)