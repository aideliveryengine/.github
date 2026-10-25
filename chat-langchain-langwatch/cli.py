"""Chat no terminal.

    python cli.py          # modo interativo
    python cli.py --lote   # roda todas as perguntas de data/perguntas.txt
"""

import argparse
import uuid

from chat import config, glossario
from chat.pipeline import Chat, Resposta


def imprimir(r: Resposta) -> None:
    if r.termos:
        print(f"  [glossário]   {', '.join(r.termos)}")
        print(f"  [normalizada] {r.pergunta}")
    print(f"  [tools]       {', '.join(r.ferramentas) or '-'}")
    print(f"\n{r.texto}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lote", action="store_true", help="roda data/perguntas.txt")
    args = parser.parse_args()

    chat = Chat()
    thread_id = uuid.uuid4().hex[:8]  # uma conversa por execução

    if args.lote:
        for pergunta in glossario.carregar_perguntas(config.ARQ_PERGUNTAS):
            print(f"> {pergunta}")
            # thread separada por pergunta: no lote cada uma é independente.
            imprimir(chat.responder(pergunta, thread_id=uuid.uuid4().hex[:8]))
        return

    print(f"Modelo: {config.LLM_MODELO} | conversa {thread_id} | Ctrl+C para sair")
    while True:
        try:
            mensagem = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if mensagem:
            imprimir(chat.responder(mensagem, thread_id=thread_id))


if __name__ == "__main__":
    main()
