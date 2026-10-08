"""Configuración compartida."""

import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()  # lee ANTHROPIC_API_KEY (y MODEL, opcional) del archivo .env

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")

# Máximo de decisiones del supervisor. Evita el "supervisor infinito".
MAX_PASOS = 6


def get_llm() -> ChatAnthropic:
    return ChatAnthropic(model=MODEL)
