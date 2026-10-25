"""Leitura do glossário de abreviações (TXT) e busca dos termos usados numa mensagem.

Não é RAG: o glossário é pequeno e a busca é por correspondência exata de termo.
Só os termos encontrados vão para o prompt, para não gastar contexto à toa.
"""

import re
from pathlib import Path


def carregar(caminho: Path) -> dict[str, str]:
    """Lê linhas `termo = significado` e devolve {termo_minúsculo: significado}."""
    glossario = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        termo, significado = (p.strip() for p in linha.split("=", 1))
        glossario[termo.lower()] = significado
    return glossario


def encontrar(mensagem: str, glossario: dict[str, str]) -> dict[str, str]:
    """Devolve os termos do glossário que aparecem na mensagem.

    Usa lookarounds em vez de \\b porque vários termos terminam em "." ou "/"
    (ex.: "últ.", "c/"), e \\b não casa depois desses caracteres.
    """
    texto = mensagem.lower()
    achados = {}
    for termo, significado in glossario.items():
        padrao = rf"(?<![\w.]){re.escape(termo)}(?![\w])"
        if re.search(padrao, texto):
            achados[termo] = significado
    return achados


def formatar(termos: dict[str, str]) -> str:
    """Formata os termos como lista para entrar no prompt."""
    if not termos:
        return "(nenhuma abreviação conhecida encontrada)"
    return "\n".join(f"- {t} = {s}" for t, s in termos.items())


def carregar_perguntas(caminho: Path) -> list[str]:
    """Lê o TXT de perguntas (uma por linha, # é comentário)."""
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in linhas if l.strip() and not l.lstrip().startswith("#")]
