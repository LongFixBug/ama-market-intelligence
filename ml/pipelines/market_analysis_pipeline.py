from __future__ import annotations
import os
import json
import asyncio
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from ml.crawlers.tavily_search import search_and_scrape_sources
from ml.graphrag.indexer import create_market_property_graph
from ml.core.llm import get_async_openai_client, get_opencode_config, extract_json_from_response
from dotenv import load_dotenv

load_dotenv()

async def execute_market_pipeline(
    topic: str,
    event_emitter: Callable[[str, str, Optional[Dict[str, Any]]], Any],
) -> Dict[str, Any]:
    """
    Executes the 7-Step Multi-Agent & GraphRAG workflow using OpenCode Go / DeepSeek.
    """
    config = get_opencode_config()
    client = get_async_openai_client()
    model_name = config["model"]

    # 1. PLANNER AGENT
    await event_emitter("planning", f"🔍 [Planner Agent - DeepSeek] Đang phân rã chiến lược tìm kiếm cho: '{topic}'...", None)
    plan_prompt = f"""
    Bạn là Chuyên gia Nghiên cứu Thị trường Cấp cao. Với chủ đề: '{topic}', hãy tạo đúng 4 câu truy vấn tìm kiếm (search queries) bằng tiếng Việt để:
    1. Tìm danh sách đối thủ cạnh tranh dẫn đầu thị trường và sản phẩm của họ
    2. Tìm thông tin bảng giá, cơ cấu chi phí và phân khúc định giá
    3. Tìm chân dung khách hàng mục tiêu, nỗi đau và khoảng trống thị trường (Market Gaps)
    4. Tìm từ khóa SEO và rủi ro thị trường.
    
    YÊU CẦU: Chỉ trả về mảng JSON chứa 4 string, ví dụ:
    ["query 1", "query 2", "query 3", "query 4"]
    """
    
    plan_res = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia phân tích thị trường. Luôn trả về định dạng JSON thuần túy."},
            {"role": "user", "content": plan_prompt}
        ],
        temperature=0.3,
    )
    plan_text = plan_res.choices[0].message.content or "[]"
    queries: List[str] = extract_json_from_response(plan_text)

    # 2. CRAWLER AGENT
    await event_emitter("scraping", f"🌐 [Crawler Agent] Đang cào dữ liệu từ các website và sàn TMĐT với {len(queries)} truy vấn...", None)
    scraped_docs = await search_and_scrape_sources(queries)

    # 3. KNOWLEDGE GRAPH AGENT (LlamaIndex + ChromaDB + DeepSeek)
    await event_emitter("graph_rag", f"🧠 [Knowledge Engine] Đang trích xuất Thực thể & Mạng quan hệ GraphRAG từ {len(scraped_docs)} tài liệu...", None)
    kg_index = create_market_property_graph(scraped_docs)
    query_engine = kg_index.as_query_engine(similarity_top_k=4)

    # 4. CHIEF ANALYST AGENTS (Competitor, Pricing, Risk, SEO)
    await event_emitter("analyzing", "📊 [Analyst Agents] Đang truy vấn GraphRAG & tổng hợp ma trận SWOT, định giá...", None)
    rag_retrieval = query_engine.query(
        f"Tổng hợp chi tiết đối thủ cạnh tranh, bảng giá, khoảng trống thị trường, SWOT và rủi ro cho {topic}"
    )

    # 5. CHIEF SYNTHESIZER AGENT
    await event_emitter("synthesizing", f"✍️ [Chief Synthesizer - {model_name}] Đang biên soạn Báo cáo Chiến lược Doanh nghiệp...", None)
    
    synth_prompt = f"""
    Dựa trên dữ liệu nghiên cứu thị trường thực tế thu được từ GraphRAG sau:
    {rag_retrieval.response}

    Hãy xuất bản bản báo cáo phân tích thị trường toàn diện và chuẩn xác cho chủ đề: '{topic}'.
    
    YÊU CẦU: Trả về duy nhất 1 JSON Object tuân thủ đúng cấu trúc sau (không kèm lời dẫn Markdown bên ngoài):
    {{
      "id": "rep-{datetime.now().strftime('%Y%m%d%H%M%S')}",
      "topic": "{topic}",
      "createdAt": "{datetime.now().strftime('%d/%m/%Y %H:%M')}",
      "executive_summary": "Tóm tắt tổng quan cơ hội thị trường và bối cảnh",
      "market_size_est": "Quy mô ước lượng (ví dụ: ~2,000 Tỷ VNĐ)",
      "growth_rate": "Tốc độ tăng trưởng (ví dụ: 18% CAGR)",
      "target_audience": [
        {{
          "title": "Tên nhóm khách hàng",
          "desc": "Mô tả hành vi và thu nhập",
          "pain_points": ["Nỗi đau 1", "Nỗi đau 2"]
        }}
      ],
      "market_gaps": [
        {{
          "title": "Tên khoảng trống thị trường",
          "opportunity": "Cơ hội chưa khai thác",
          "priority": "Cao"
        }}
      ],
      "swot": {{
        "strengths": ["Điểm mạnh 1", "Điểm mạnh 2"],
        "weaknesses": ["Điểm yếu 1", "Điểm yếu 2"],
        "opportunities": ["Cơ hội 1", "Cơ hội 2"],
        "threats": ["Thách thức 1", "Thách thức 2"]
      }},
      "competitors": [
        {{
          "name": "Tên đối thủ",
          "type": "Trực tiếp",
          "positioning": "Định vị thương hiệu",
          "strengths": ["Điểm mạnh"],
          "weaknesses": ["Điểm yếu"],
          "price_range": "100.000đ - 300.000đ",
          "market_share_est": "30%",
          "website": "https://example.com"
        }}
      ],
      "pricing": {{
        "min_market_price": 100000,
        "median_market_price": 250000,
        "recommended_price": 220000,
        "premium_market_price": 500000,
        "unit": "VNĐ / sản phẩm",
        "pricing_logic": "Lý do và căn cứ định giá đề xuất",
        "margin_est": "65% Gross Margin",
        "tiers": [
          {{
            "tier": "Gói Starter",
            "price": 120000,
            "description": "Gói dùng thử",
            "features": ["Tính năng cơ bản"]
          }},
          {{
            "tier": "Gói Core (Khuyên dùng)",
            "price": 220000,
            "description": "Gói tiêu chuẩn tối ưu",
            "features": ["Đầy đủ quyền lợi"]
          }},
          {{
            "tier": "Gói Premium",
            "price": 450000,
            "description": "Gói cao cấp / combo",
            "features": ["Ưu tiên đặc biệt"]
          }}
        ]
      }},
      "risks": [
        {{
          "category": "Pháp lý",
          "risk_title": "Tên rủi ro",
          "risk_level": "Cao",
          "impact": "Tác động cụ thể",
          "mitigation": "Biện pháp giảm thiểu"
        }}
      ],
      "seo_strategy": [
        {{
          "keyword": "từ khóa tìm kiếm",
          "intent": "Mua hàng (Commercial)",
          "search_volume_est": "Cao",
          "competition": "Trung bình",
          "content_angle": "Gợi ý góc bài viết"
        }}
      ],
      "gtm_roadmap": [
        {{
          "phase": "Giai đoạn 1",
          "timeline": "Tháng 1 - 2",
          "key_actions": ["Hành động then chốt 1", "Hành động 2"]
        }}
      ],
      "graph_data": {{
        "nodes": [
          {{"id": "market", "name": "{topic}", "category": "product", "size": 24}},
          {{"id": "comp1", "name": "Đối Thủ 1", "category": "competitor", "size": 18}}
        ],
        "links": [
          {{"source": "market", "target": "comp1", "relationship": "COMPETES_WITH"}}
        ]
      }}
    }}
    """

    synth_res = await client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia phân tích thị trường cao cấp. Luôn trả về 1 JSON Object duy nhất theo cấu trúc yêu cầu, không kèm text giải thích bên ngoài."},
            {"role": "user", "content": synth_prompt}
        ],
        temperature=0.2,
    )
    
    synth_text = synth_res.choices[0].message.content or "{}"
    final_report: Dict[str, Any] = extract_json_from_response(synth_text)

    await event_emitter("completed", "✅ Đã hoàn tất báo cáo phân tích thị trường!", final_report)
    return final_report
