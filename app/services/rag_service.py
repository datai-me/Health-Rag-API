from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.schema import Document
from app.config import get_settings

settings = get_settings()

class RAGService:
    """Service gérant le pipeline RAG (Vector DB + LLM)."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=settings.openai_api_key)
        self.vector_store = Chroma(embedding_function=self.embeddings, collection_name="health_collection")
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

    def ingest_documents(self, texts: list) -> int:
        """Découpe et vectorise les textes."""
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