from langchain_groq import ChatGroq
from langchain_community.embeddings import JinaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.schema import Document
from app.config import get_settings

settings = get_settings()

class RAGService:
    """Service RAG utilisant Groq et des embeddings gratuits."""
    
    def __init__(self):
        # 1. Initialisation des Embeddings (Jina - Gratuit)
        # IMPORTANT : Cette ligne crée self.embeddings. Sans elle, Chroma ne peut pas fonctionner.
        self.embeddings = JinaEmbeddings(
            jina_api_key=settings.jina_api_key, # On lit la clé dans config.py
            model_name="jina-embeddings-v2-base-en"
        )
        
        # 2. Initialisation du LLM (Groq - Gratuit)
        self.llm = ChatGroq(
            temperature=0,
            model="llama-3.3-70b-versatile", # Modèle Llama 3
            api_key=settings.groq_api_key # On lit la clé dans config.py
        )
        
        # 3. Initialisation de la Base Vectorielle (Chroma)
        # Ici, on utilise self.embeddings défini juste au-dessus.
        self.vector_store = Chroma(
            embedding_function=self.embeddings, 
            collection_name="health_collection"
        )
        
        # Création du retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

    def ingest_documents(self, texts: list) -> int:
        """Découpe et indexe les textes."""
        docs = [Document(page_content=t) for t in texts]
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)
        self.vector_store.add_documents(splits)
        return len(splits)

    def query(self, question: str) -> tuple:
        """Recherche et génère une réponse."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Réponds UNIQUEMENT avec le contexte suivant :\n{context}"),
            ("human", "{input}"),
        ])
        
        rag_chain = create_retrieval_chain(
            self.retriever, 
            create_stuff_documents_chain(self.llm, prompt)
        )
        result = rag_chain.invoke({"input": question})
        sources = [doc.page_content[:100] + "..." for doc in result.get("context", [])]
        return result["answer"], sources