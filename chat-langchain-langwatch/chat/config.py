"""Configuração lida do ambiente (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

LLM_MODELO = os.getenv("LLM_MODELO", "ollama:qwen3-4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

ARQ_ABREVIACOES = RAIZ / "data" / "abreviacoes.txt"
ARQ_PERGUNTAS = RAIZ / "data" / "perguntas.txt"
