"""
RAG (Retrieval-Augmented Generation) service for question answering.
"""
from typing import List, Tuple

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.schema import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import JinaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RAGService:
    """Service for RAG operations using LangChain, Groq, and Jina embeddings."""
    
    def __init__(self):
        """Initialize RAG service with embeddings, LLM, and vector store."""
        logger.info("Initializing RAG service")
        
        try:
            # Initialize embeddings
            self.embeddings = JinaEmbeddings(
                jina_api_key=settings.jina_api_key,
                model_name=settings.rag_embedding_model
            )
            logger.info(f"Initialized Jina embeddings: {settings.rag_embedding_model}")
            
            # Initialize LLM
            self.llm = ChatGroq(
                temperature=settings.rag_llm_temperature,
                model=settings.rag_llm_model,
                api_key=settings.groq_api_key
            )
            logger.info(f"Initialized Groq LLM: {settings.rag_llm_model}")
            
            # Initialize vector store
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                collection_name="health_collection"
            )
            logger.info("Initialized ChromaDB vector store")
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": settings.rag_top_k_results}
            )
            logger.info(f"Initialized retriever with k={settings.rag_top_k_results}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise ExternalServiceError(
                message="Failed to initialize RAG service",
                service_name="RAG",
                details={"error": str(e)}
            )
    
    def ingest_documents(self, texts: List[str]) -> int:
        """
        Ingest and index text documents.
        
        Args:
            texts: List of text documents to ingest
            
        Returns:
            Number of chunks created and indexed
            
        Raises:
            ExternalServiceError: If ingestion fails
        """
        logger.info(f"Starting ingestion of {len(texts)} documents")
        
        try:
            # Convert texts to Document objects
            documents = [Document(page_content=text) for text in texts]
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.rag_chunk_size,
                chunk_overlap=settings.rag_chunk_overlap
            )
            splits = text_splitter.split_documents(documents)
            
            logger.info(f"Split documents into {len(splits)} chunks")
            
            # Add to vector store
            self.vector_store.add_documents(splits)
            
            logger.info(f"Successfully ingested {len(splits)} chunks")
            return len(splits)
            
        except Exception as e:
            logger.error(f"Failed to ingest documents: {e}")
            raise ExternalServiceError(
                message="Failed to ingest documents",
                service_name="RAG",
                details={"error": str(e), "num_documents": len(texts)}
            )
    
    def query(self, question: str) -> Tuple[str, List[str]]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User question in natural language
            
        Returns:
            Tuple of (answer, list of source previews)
            
        Raises:
            ExternalServiceError: If query fails
        """
        logger.info(f"Processing query: {question[:100]}...")
        
        try:
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    "You are a helpful medical information assistant. "
                    "Answer the question based ONLY on the following context. "
                    "If the answer is not in the context, say 'I don't have enough information to answer that question.'\n\n"
                    "Context:\n{context}"
                ),
                ("human", "{input}"),
            ])
            
            # Create RAG chain
            rag_chain = create_retrieval_chain(
                self.retriever,
                create_stuff_documents_chain(self.llm, prompt)
            )
            
            # Execute query
            result = rag_chain.invoke({"input": question})
            
            # Extract answer and sources
            answer = result.get("answer", "No answer generated")
            context_docs = result.get("context", [])
            
            # Create source previews
            sources = [
                self._create_source_preview(doc.page_content)
                for doc in context_docs
            ]
            
            logger.info(f"Successfully generated answer with {len(sources)} sources")
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise ExternalServiceError(
                message="Failed to process query",
                service_name="RAG",
                details={"error": str(e), "question": question[:100]}
            )
    
    def _create_source_preview(self, content: str, max_length: int = 150) -> str:
        """
        Create a preview of source content.
        
        Args:
            content: Full source content
            max_length: Maximum length of preview
            
        Returns:
            Preview string with ellipsis if truncated
        """
        if len(content) <= max_length:
            return content
        
        return content[:max_length].rsplit(" ", 1)[0] + "..."
    
    def clear_collection(self) -> None:
        """
        Clear all documents from the vector store.
        
        Useful for testing or resetting the knowledge base.
        """
        logger.warning("Clearing vector store collection")
        
        try:
            # This is a simplified approach - in production you might want
            # to recreate the collection or use ChromaDB's delete methods
            self.vector_store = Chroma(
                embedding_function=self.embeddings,
                collection_name="health_collection"
            )
            logger.info("Vector store cleared successfully")
            
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise ExternalServiceError(
                message="Failed to clear vector store",
                service_name="RAG",
                details={"error": str(e)}
            )
