"""Chat no navegador (Gradio). A lógica é a mesma do CLI: Chat.responder().

    python web.py   # abre em http://localhost:7860
"""

import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr

from chat import config, glossario, observabilidade
from chat.pipeline import Chat

observabilidade.iniciar()
chat = Chat()


def responder(mensagem: str, _historico: list, request: gr.Request) -> str:
    # O histórico fica no checkpointer do agente; a sessão do Gradio vira o thread_id.
    r = chat.responder(mensagem, thread_id=request.session_hash)
    bastidores = (
        f"glossário: {', '.join(r.termos) or '-'}  \n"
        f"normalizada: {r.pergunta}  \n"
        f"tools: {', '.join(r.ferramentas) or '-'}"
    )
    return f"{r.texto}\n\n<details><summary>bastidores</summary>\n\n{bastidores}\n</details>"


demo = gr.ChatInterface(
    responder,
    title="Chat de pacotes (LangChain)",
    description=f"Pergunte sobre pacotes do PyPI/npm, pode abreviar. Modelo: {config.LLM_MODELO}",
    examples=glossario.carregar_perguntas(config.ARQ_PERGUNTAS),
    cache_examples=False,
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
