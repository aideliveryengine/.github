"""Ferramentas (tools) que o agente pode chamar: APIs públicas do PyPI e do npm.

O decorator `@tool` do LangChain transforma a função num `StructuredTool`:
- nome da tool  = nome da função
- descrição     = docstring (é isso que o LLM lê para decidir quando chamar)
- schema JSON   = gerado a partir das type hints dos parâmetros
"""

import httpx
from langchain_core.tools import tool

_http = httpx.Client(timeout=15, headers={"User-Agent": "chat-langchain-langwatch/1.0"})


@tool
def pypi_pacote(nome: str) -> dict:
    """Consulta um pacote Python no PyPI. Retorna última versão, data dessa versão,
    licença, versão mínima do Python, total de releases e dependências.
    `nome` é o nome exato do pacote no PyPI (ex.: "langchain")."""
    resp = _http.get(f"https://pypi.org/pypi/{nome}/json")
    if resp.status_code == 404:
        return {"erro": f"pacote '{nome}' não existe no PyPI"}
    resp.raise_for_status()
    dados = resp.json()
    info = dados["info"]
    arquivos = dados.get("urls") or []
    return {
        "pacote": info["name"],
        "ultima_versao": info["version"],
        "data_ultima_versao": arquivos[0]["upload_time_iso_8601"] if arquivos else None,
        "descricao": info.get("summary"),
        "licenca": info.get("license_expression") or info.get("license"),
        "python_minimo": info.get("requires_python"),
        "total_releases": len(dados.get("releases", {})),
        # Só dependências obrigatórias (as com "extra ==" são opcionais).
        "dependencias": [d for d in (info.get("requires_dist") or []) if "extra ==" not in d],
    }


@tool
def npm_pacote(nome: str) -> dict:
    """Consulta um pacote JavaScript no registro do npm. Retorna última versão,
    licença, descrição e dependências. `nome` é o nome exato no npm (ex.: "langchain")."""
    resp = _http.get(f"https://registry.npmjs.org/{nome}/latest")
    if resp.status_code == 404:
        return {"erro": f"pacote '{nome}' não existe no npm"}
    resp.raise_for_status()
    dados = resp.json()
    return {
        "pacote": dados["name"],
        "ultima_versao": dados["version"],
        "descricao": dados.get("description"),
        "licenca": dados.get("license"),
        "dependencias": sorted((dados.get("dependencies") or {}).keys()),
    }


FERRAMENTAS = [pypi_pacote, npm_pacote]
