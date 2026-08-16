import os
import chromadb
from typing import List, Dict
from llama_index.core import Document, PropertyGraphIndex, Settings
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from dotenv import load_dotenv

load_dotenv()

def init_gemini_settings():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        Settings.llm = Gemini(model="models/gemini-2.0-flash", api_key=api_key)
        Settings.embed_model = GeminiEmbedding(model_name="models/text-embedding-004", api_key=api_key)

def create_market_property_graph(scraped_docs: List[Dict[str, str]]) -> PropertyGraphIndex:
    """
    Constructs a Property Graph Index using LlamaIndex and ChromaDB Vector Store.
    """
    init_gemini_settings()

    documents = [
        Document(text=f"Tiêu đề: {d['title']}\nNguồn: {d['url']}\nNội dung: {d['content']}")
        for d in scraped_docs
    ]

    kg_extractor = SchemaLLMPathExtractor(
        llm=Settings.llm,
        possible_entities=["Competitor", "Product", "Feature", "Price", "Audience", "Risk", "Keyword"],
        possible_relations=["OFFERS", "COMPETES_WITH", "PRICED_AT", "TARGETS", "HAS_RISK", "KEYWORDS"],
        strict=False,
    )

    chroma_client = chromadb.EphemeralClient()
    collection = chroma_client.get_or_create_collection("market_graph_rag_collection")
    vector_store = ChromaVectorStore(chroma_collection=collection)

    index = PropertyGraphIndex.from_documents(
        documents,
        kg_extractors=[kg_extractor],
        vector_store=vector_store,
        show_progress=False,
    )

    return index
