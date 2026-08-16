from __future__ import annotations
import os
import json
import asyncio
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from ml.crawlers.tavily_search import search_and_scrape_sources
from ml.core.llm import get_async_openai_client, get_opencode_config, extract_json_from_response
from dotenv import load_dotenv

load_dotenv()

async def _safe_chat_completion(client: Any, preferred_model: str, messages: list, temperature: float = 0.2) -> str:
    """
    Calls OpenCode Go API with automatic resilience fallback to qwen3.7-plus / minimax-m3 if preferred model fails.
    """
    fallback_models = [preferred_model, "qwen3.7-plus", "qwen3.7-max", "minimax-m3", "gpt-5.6-luna"]
    # De-duplicate while preserving order
    seen = set()
    models_to_try = [m for m in fallback_models if not (m in seen or seen.add(m))]

    last_error = None
    for model in models_to_try:
        try:
            res = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = res.choices[0].message.content or ""
            if content.strip():
                return content
        except Exception as err:
            last_error = err
            print(f"[Model Warning] {model} failed: {err}. Trying next fallback...")

    raise RuntimeError(f"Tất cả các model LLM đều gặp sự cố: {last_error}")

async def execute_market_pipeline(
    topic: str,
    event_emitter: Callable[[str, str, Optional[Dict[str, Any]]], Any],
) -> Dict[str, Any]:
    """
    Executes the Pragmatic Market Analysis Multi-Agent Pipeline with high speed & resilience.
    """
    config = get_opencode_config()
    client = get_async_openai_client()
    preferred_model = config["model"]

    # 1. BƯỚC 1: XÁC THỰC & ĐỊNH TUYẾN (< 2s)
    await event_emitter(
        "planning",
        f"🔍 [Xác thực & Định tuyến] Đang đánh giá từ khóa & phạm vi kinh doanh: '{topic}'...",
        None,
    )
    
    plan_prompt = f"""
    Bạn là chuyên gia nghiên cứu thị trường thực chiến. Với chủ đề: '{topic}', hãy tạo 3 câu truy vấn tìm kiếm (search queries) bằng tiếng Việt để cào dữ liệu:
    1. Giá bán thực tế các dòng sản phẩm phổ biến nhất của '{topic}' tại thị trường Việt Nam (Shopee, Tiki, website chuyên ngành)
    2. Các thương hiệu/đối thủ cạnh tranh chính và phân khúc giá của họ
    3. Nhu cầu thực tế, điểm đau (pain points) và rủi ro kinh doanh của ngách '{topic}'.
    
    Trả về định dạng JSON array 3 phần tử: ["query 1", "query 2", "query 3"]
    """

    plan_text = await _safe_chat_completion(
        client=client,
        preferred_model=preferred_model,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia thị trường. Luôn trả về định dạng JSON mảng string."},
            {"role": "user", "content": plan_prompt},
        ],
        temperature=0.2,
    )
    queries: List[str] = extract_json_from_response(plan_text)
    if not isinstance(queries, list) or len(queries) == 0:
        queries = [f"giá {topic} việt nam", f"đối thủ {topic}", f"kinh doanh {topic}"]

    # 2. BƯỚC 2: THU THẬP DỮ LIỆU THỊ TRƯỜNG (< 2s song song)
    await event_emitter(
        "scraping",
        f"📈 [Thu thập Dữ liệu Thị trường] Đang cào dữ liệu giá, đối thủ & xu hướng từ {len(queries)} nguồn...",
        None,
    )
    scraped_docs = await search_and_scrape_sources(queries)

    # 3. BƯỚC 3: XÂY DỰNG BÁO CÁO CHIẾN LƯỢC (< 3s)
    await event_emitter(
        "synthesizing",
        f"📊 [Xây dựng Báo cáo Chiến lược] Đang trích xuất ngách, giá tối ưu, rủi ro & câu lệnh AI...",
        None,
    )

    context_text = "\n\n".join([f"Nguồn ({d.get('url', '')}): {d.get('content', '')[:1000]}" for d in scraped_docs[:4]])

    synth_prompt = f"""
    Dựa trên dữ liệu thị trường thực tế sau đây:
    ---
    {context_text}
    ---

    Hãy lập BÁO CÁO PHÂN TÍCH CHIẾN LƯỢC THỰC CHIẾN cho chủ đề: '{topic}'.
    YÊU CẦU ĐẶC BIỆT:
    - KHÔNG viết chung chung, mơ hồ, sáo rỗng.
    - Phải có tên sản phẩm cụ thể, thương hiệu đối thủ cụ thể, con số khoảng giá VNĐ thực tế ở thị trường Việt Nam.
    - Đi thẳng vào luận điểm kinh doanh, USP khác biệt, rủi ro thực tế (nguồn hàng, bảo hành, cạnh tranh) và 3 câu lệnh AI Prompt thực chiến để dùng ngay cho ChatGPT/Claude.

    Trả về DUY NHẤT 1 JSON Object tuân thủ đúng 100% cấu trúc sau (không kèm markdown bên ngoài):
    {{
      "id": "rep-{datetime.now().strftime('%Y%m%d%H%M%S')}",
      "topic": "{topic}",
      "createdAt": "{datetime.now().strftime('%d/%m/%Y %H:%M')}",
      "niche_analysis": {{
        "summary": "Mô tả súc tích và sắc bén: tệp khách hàng mục tiêu là ai, Điểm độc đáo (USP) của sản phẩm là gì, Cơ hội cạnh tranh cụ thể nằm ở đâu (dịch vụ, phụ kiện, bảo hành, hỗ trợ).",
        "growth_potential": "Cao trong ngách mục tiêu"
      }},
      "pricing": {{
        "price_range": "Khoảng giá tối ưu cụ thể (ví dụ: 80.000 VNĐ - 350.000 VNĐ)",
        "rationale": "Cơ sở & cơ chế định giá: Mức giá này phù hợp với các dòng sản phẩm nào cụ thể, cân bằng giữa sức mua người tiêu dùng Việt Nam và biên độ lợi nhuận sau khi trừ chi phí.",
        "tagline": "Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu"
      }},
      "risks": [
        {{
          "index": 1,
          "title": "Mô tả rủi ro #1 cụ thể."
        }},
        {{
          "index": 2,
          "title": "Mô tả rủi ro #2 cụ thể."
        }},
        {{
          "index": 3,
          "title": "Mô tả rủi ro #3 cụ thể."
        }}
      ],
      "seo_keywords": [
        "từ khóa 1",
        "từ khóa 2",
        "từ khóa 3",
        "từ khóa 4",
        "từ khóa 5"
      ],
      "ai_prompts": [
        {{
          "prompt": "Viết một bài đăng Facebook quảng cáo [sản phẩm] hướng đến đối tượng [khách hàng mục tiêu] nhấn mạnh vào [USP chính]."
        }},
        {{
          "prompt": "Lập bảng so sánh chi tiết giữa [sản phẩm chính] và [đối thủ cạnh tranh trực tiếp] để tư vấn khách hàng."
        }},
        {{
          "prompt": "Tạo kịch bản video ngắn (TikTok/Reels) 30 giây review 3 lý do tại sao nên chọn [sản phẩm]."
        }}
      ]
    }}
    """

    synth_text = await _safe_chat_completion(
        client=client,
        preferred_model=preferred_model,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia phân tích thị trường cao cấp. Luôn trả về 1 JSON Object duy nhất, không kèm giải thích bên ngoài."},
            {"role": "user", "content": synth_prompt},
        ],
        temperature=0.2,
    )

    final_report: Dict[str, Any] = extract_json_from_response(synth_text)

    await event_emitter("completed", "✅ Đã hoàn tất báo cáo chiến lược!", final_report)
    return final_report
