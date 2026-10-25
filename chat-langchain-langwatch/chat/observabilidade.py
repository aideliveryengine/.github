"""Inicialização do LangWatch.

O SDK do LangWatch é construído sobre OpenTelemetry: cada `@langwatch.trace`
abre um trace, cada `langwatch.span` (ou callback do LangChain) abre spans
filhos, e um exporter OTLP envia tudo em lote para LANGWATCH_ENDPOINT.
"""

import os

import langwatch


def iniciar() -> bool:
    """Configura o SDK se houver LANGWATCH_API_KEY. Sem chave, o app roda igual,
    só que sem enviar traces (os decorators viram praticamente no-op)."""
    if not os.getenv("LANGWATCH_API_KEY"):
        print("[langwatch] LANGWATCH_API_KEY ausente: traces desligados")
        return False
    # setup() lê LANGWATCH_API_KEY e LANGWATCH_ENDPOINT (padrão: https://app.langwatch.ai).
    langwatch.setup()
    print(f"[langwatch] enviando traces para {os.getenv('LANGWATCH_ENDPOINT', 'https://app.langwatch.ai')}")
    return True
