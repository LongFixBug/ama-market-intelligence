import os
import json
import asyncio
from datetime import datetime
from app.services.crawler import search_and_scrape
from app.services.graph_rag import build_market_knowledge_graph
from app.schemas import MarketReport
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def run_market_pipeline(topic: str, event_callback):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in backend/.env")

    genai.configure(api_key=api_key)

    # 1. PLANNER AGENT
    await event_callback("planning", f"🔍 [Planner Agent] Đang phân rã chiến lược tìm kiếm cho: '{topic}'...")
    planner_model = genai.GenerativeModel("gemini-2.0-flash")
    plan_prompt = f"""
    Bạn là Chuyên gia Nghiên cứu Thị trường Cấp cao. Với chủ đề: '{topic}', hãy tạo 4 search queries cụ thể để:
    1. Tìm đối thủ cạnh tranh dẫn đầu và sản phẩm của họ
    2. Tìm thông tin bảng giá, cơ cấu phân khúc giá
    3. Tìm nhu cầu khách hàng, nỗi đau và khoảng trống thị trường
    4. Tìm từ khóa SEO và rủi ro thị trường.
    Trả về định dạng JSON array: ["query 1", "query 2", "query 3", "query 4"]
    """
    plan_resp = planner_model.generate_content(
        plan_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    queries = json.loads(plan_resp.text)

    # 2. CRAWLER & WEB SCRAPING AGENT
    await event_callback("scraping", f"🌐 [Web Crawler] Đang thu thập dữ liệu từ {len(queries)} truy vấn...")
    scraped_docs = await search_and_scrape(queries)

    # 3. KNOWLEDGE GRAPH RAG AGENT
    await event_callback("graph_rag", f"🧠 [Knowledge Engine] Đang trích xuất GraphRAG từ {len(scraped_docs)} nguồn dữ liệu...")
    kg_index = build_market_knowledge_graph(scraped_docs)
    query_engine = kg_index.as_query_engine(similarity_top_k=4)

    # 4. CHIEF SYNTHESIS AGENT
    await event_callback("analyzing", "📊 [Analyst Agent] Đang truy vấn đa chiều & phân tích đối thủ...")
    rag_context = query_engine.query(
        f"Tổng hợp chi tiết đối thủ cạnh tranh, bảng giá, khoảng trống thị trường, SWOT và rủi ro cho {topic}"
    )

    await event_callback("synthesizing", "✍️ [Chief Synthesizer] Đang hoàn thiện Báo cáo Chiến lược...")
    synth_model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": MarketReport
        }
    )

    final_prompt = f"""
    Dựa trên dữ liệu thực tế từ GraphRAG sau:
    {rag_context.response}

    Hãy xuất bản báo cáo phân tích thị trường toàn diện cho chủ đề: '{topic}'.
    Mã định danh ID: 'rep-{datetime.now().strftime('%Y%m%d%H%M%S')}', thời gian: '{datetime.now().strftime('%d/%m/%Y %H:%M')}'.
    """

    report_resp = synth_model.generate_content(final_prompt)
    final_report = json.loads(report_resp.text)

    await event_callback("completed", "✅ Đã hoàn tất báo cáo thị trường!", final_report)
    return final_report
