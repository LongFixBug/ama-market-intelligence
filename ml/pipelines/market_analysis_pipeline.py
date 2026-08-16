import os
import json
import asyncio
from datetime import datetime
from typing import Callable, Any
from ml.crawlers.tavily_search import search_and_scrape_sources
from ml.graphrag.indexer import create_market_property_graph
from ml.schemas.market_report import MarketReport
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def execute_market_pipeline(
    topic: str,
    event_emitter: Callable[[str, str, dict | None], Any],
) -> dict:
    """
    Executes the 7-Step Multi-Agent & GraphRAG workflow and streams state via callback.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not defined in environment!")

    genai.configure(api_key=api_key)

    # 1. PLANNER AGENT
    await event_emitter("planning", f"🔍 [Planner Agent] Phân rã bài toán & tạo bộ truy vấn đa chiều cho: '{topic}'...", None)
    planner_llm = genai.GenerativeModel("gemini-2.0-flash")
    plan_prompt = f"""
    Bạn là Chuyên gia Nghiên cứu Thị trường Doanh nghiệp. Với chủ đề '{topic}', hãy tạo đúng 4 search queries phục vụ:
    1. Danh sách đối thủ dẫn đầu và thương hiệu trực tiếp/gián tiếp
    2. Bảng giá, cơ cấu chi phí và mức giá thị trường
    3. Phân khúc khách hàng mục tiêu, nỗi đau và khoảng trống thị trường
    4. Rủi ro ngành và từ khóa xu hướng.
    Trả về định dạng JSON array: ["query 1", "query 2", "query 3", "query 4"]
    """
    plan_resp = planner_llm.generate_content(
        plan_prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    queries = json.loads(plan_resp.text)

    # 2. CRAWLER AGENT
    await event_emitter("scraping", f"🌐 [Crawler Agent] Đang cào dữ liệu từ các website và sàn TMĐT với {len(queries)} truy vấn...", None)
    scraped_docs = await search_and_scrape_sources(queries)

    # 3. KNOWLEDGE GRAPH AGENT (LlamaIndex + ChromaDB)
    await event_emitter("graph_rag", f"🧠 [Knowledge Engine] Đang trích xuất Thực thể & Mạng quan hệ GraphRAG từ {len(scraped_docs)} tài liệu...", None)
    kg_index = create_market_property_graph(scraped_docs)
    query_engine = kg_index.as_query_engine(similarity_top_k=4)

    # 4. CHIEF ANALYST AGENTS (Competitor, Pricing, Risk, SEO)
    await event_emitter("analyzing", "📊 [Analyst Agents] Đang tổng hợp phân vị giá, ma trận SWOT & rủi ro...", None)
    rag_retrieval = query_engine.query(
        f"Tổng hợp chi tiết đối thủ cạnh tranh, bảng giá, khoảng trống thị trường, SWOT và rủi ro cho {topic}"
    )

    # 5. CHIEF SYNTHESIZER AGENT
    await event_emitter("synthesizing", "✍️ [Chief Synthesizer] Đang biên soạn Báo cáo Chiến lược Doanh nghiệp...", None)
    synthesizer_llm = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": MarketReport,
        },
    )

    final_prompt = f"""
    Dựa trên dữ liệu thị trường thực tế thu được từ GraphRAG sau:
    {rag_retrieval.response}

    Hãy xuất bản báo cáo phân tích thị trường toàn diện và chuẩn xác cho: '{topic}'.
    ID: 'rep-{datetime.now().strftime('%Y%m%d%H%M%S')}', ngày: '{datetime.now().strftime('%d/%m/%Y %H:%M')}'.
    """

    final_resp = synthesizer_llm.generate_content(final_prompt)
    final_report = json.loads(final_resp.text)

    await event_emitter("completed", "✅ Đã hoàn tất báo cáo phân tích thị trường!", final_report)
    return final_report
