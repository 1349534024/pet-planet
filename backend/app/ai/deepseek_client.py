from langchain_community.chat_models import ChatOpenAI

from app.core.config import settings


def get_deepseek_chat() -> ChatOpenAI:
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.3,
    )
