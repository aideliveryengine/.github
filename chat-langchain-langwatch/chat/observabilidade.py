"""Inicialização do LangWatch.

O SDK do LangWatch é construído sobre OpenTelemetry: cada `@langwatch.trace`
abre um trace, cada `langwatch.span` (ou callback do LangChain) abre spans
filhos, e um exporter OTLP envia tudo em lote para LANGWATCH_ENDPOINT.

Importado no topo de pipeline.py: o setup() precisa rodar ANTES de o Python avaliar
o `@langwatch.trace`, senão o decorator faz um setup implícito (sem as regras abaixo).
"""

import os

import langwatch

from chat import config  # noqa: F401  (carrega o .env)
from langwatch.domain import SpanProcessingExcludeRule

# setup() registra um TracerProvider global do OpenTelemetry. Bibliotecas que já
# emitem spans OTel (o FastAPI usado pelo Gradio, por exemplo) passam a mandar as
# requisições HTTP para o LangWatch também. Estas regras descartam esse ruído.
_RUIDO_HTTP = [
    SpanProcessingExcludeRule(field_name="span_name", match_value=v, match_operation="starts_with")
    for v in ("fastapi.", "GET ", "POST ", "HEAD ")
]


def iniciar() -> bool:
    """Configura o SDK se houver LANGWATCH_API_KEY. Sem chave, o app roda igual,
    só que sem enviar traces (os decorators viram praticamente no-op)."""
    if not os.getenv("LANGWATCH_API_KEY"):
        print("[langwatch] LANGWATCH_API_KEY ausente: traces desligados")
        return False
    # setup() lê LANGWATCH_API_KEY e LANGWATCH_ENDPOINT (padrão: https://app.langwatch.ai).
    langwatch.setup(span_exclude_rules=_RUIDO_HTTP)
    print(f"[langwatch] enviando traces para {os.getenv('LANGWATCH_ENDPOINT', 'https://app.langwatch.ai')}")
    return True


ATIVO = iniciar()
