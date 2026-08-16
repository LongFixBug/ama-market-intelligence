from __future__ import annotations
import os
import json
import re
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.core import Settings
from dotenv import load_dotenv

load_dotenv()

def get_opencode_config() -> Dict[str, str]:
    """
    Retrieves API Key, Base URL, and Model configuration for OpenCode Go / DeepSeek.
    """
    api_key = (
        os.getenv("OPENCODE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
        or ""
    )
    base_url = (
        os.getenv("OPENCODE_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or "https://api.deepseek.com/v1"
    )
    model = (
        os.getenv("OPENCODE_MODEL")
        or os.getenv("LLM_MODEL")
        or "deepseek-chat"
    )
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }

def get_async_openai_client() -> AsyncOpenAI:
    """
    Initializes AsyncOpenAI client configured for OpenCode Go / DeepSeek.
    """
    config = get_opencode_config()
    if not config["api_key"]:
        raise ValueError(
            "Chưa cấu hình API Key! Vui lòng thêm OPENCODE_API_KEY hoặc OPENAI_API_KEY vào file backend/.env"
        )
    return AsyncOpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )

def setup_llama_index_llm():
    """
    Configures LlamaIndex to use OpenCode Go / DeepSeek as the default LLM.
    """
    config = get_opencode_config()
    if config["api_key"]:
        Settings.llm = LlamaOpenAI(
            model=config["model"],
            api_key=config["api_key"],
            api_base=config["base_url"],
            temperature=0.2,
        )

def extract_json_from_response(text: str) -> Dict[str, Any] | list:
    """
    Robust JSON parser extracting json from markdown code fences or raw string.
    """
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        clean_text = match.group(1).strip()
    else:
        clean_text = text

    return json.loads(clean_text)
