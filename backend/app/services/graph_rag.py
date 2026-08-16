import os
import chromadb
from llama_index.core import Document, PropertyGraphIndex
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import Settings
from dotenv import load_dotenv

load_dotenv()

def init_llama_settings():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=api_key)
        Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004", api_key=api_key)

def build_market_knowledge_graph(scraped_data: list):
    """
    Builds a Property Graph with ChromaDB Vector Store from scraped documents.
    """
    init_llama_settings()

    docs = [
        Document(text=f"Tiêu đề: {item['title']}\nNguồn: {item['url']}\nNội dung: {item['content']}")
        for item in scraped_data
    ]

    kg_extractor = SchemaLLMPathExtractor(
        llm=Settings.llm,
        possible_entities=["Competitor", "Product", "Feature", "Price", "Audience", "Risk", "Keyword"],
        possible_relations=["OFFERS", "COMPETES_WITH", "PRICED_AT", "TARGETS", "HAS_RISK", "KEYWORDS"],
        strict=False
    )

    chroma_client = chromadb.EphemeralClient()
    chroma_collection = chroma_client.get_or_create_collection("market_graph_rag")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = PropertyGraphIndex.from_documents(
        docs,
        kg_extractors=[kg_extractor],
        vector_store=vector_store,
        show_progress=False
    )
    
    return index
