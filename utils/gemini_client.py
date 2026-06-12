from typing import Generator
import logging
import streamlit as st
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


@st.cache_resource
def get_client() -> genai.Client:
    """Gemini クライアントをキャッシュして返す"""
    return genai.Client(api_key=GEMINI_API_KEY)


def stream_generate(
    model_name: str,
    system_instruction: str,
    user_content: str,
    temperature: float = 0.7,
    max_output_tokens: int = 4096,
) -> Generator[str, None, None]:
    """Gemini APIでテキストをストリーミング生成する。
    system_instruction にはロール・出力形式などの固定指示のみを渡し、
    user_content にはユーザーが入力した自由記述テキストを渡すこと。
    この分離によりプロンプトインジェクションを抑制する。
    """
    try:
        client = get_client()
        response = client.models.generate_content_stream(
            model=model_name,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        yield "\n\n⚠️ エラーが発生しました。しばらく待ってから再試行してください。"
