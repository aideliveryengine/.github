"""Configuração lida do ambiente (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

LLM_MODELO = os.getenv("LLM_MODELO", "ollama:qwen3-4b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
# Threads do llama.cpp. Se passar do nº de cores livres, a geração despenca (spin-wait).
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD") or 0) or None

ARQ_ABREVIACOES = RAIZ / "data" / "abreviacoes.txt"
ARQ_PERGUNTAS = RAIZ / "data" / "perguntas.txt"
