# Chat de pacotes — LangChain (+ LangWatch)

Tutorial prático. Um chat responde perguntas sobre pacotes Python/JavaScript
consultando APIs públicas (PyPI e npm). As perguntas podem vir abreviadas
("qual a últ. ver. do lc?"); um glossário em TXT traduz os termos antes do agente responder.

- **Fase 1:** LangChain puro (este README).
- **Fase 2:** observabilidade com LangWatch (seção [LangWatch](#fase-2--langwatch)).

## Fluxo

```
mensagem abreviada
   │
   ├─ glossario.encontrar()        → termos do data/abreviacoes.txt presentes na mensagem
   │
   ├─ cadeia de normalização (LCEL) → prompt | llm | StrOutputParser
   │      "qual a últ. ver. do lc?" → "Qual a última versão do pacote "langchain"?"
   │
   └─ agente (create_agent)         → LLM decide chamar pypi_pacote / npm_pacote
          ↺ LLM ↔ tools até ter a resposta
```

## Arquivos

| Arquivo | O que tem |
| --- | --- |
| `data/abreviacoes.txt` | Glossário `termo = significado` |
| `data/perguntas.txt` | Perguntas do roteiro (uma por linha) |
| `chat/glossario.py` | Lê o TXT e acha os termos na mensagem (regex, sem embeddings) |
| `chat/ferramentas.py` | Tools `@tool`: `pypi_pacote`, `npm_pacote` |
| `chat/pipeline.py` | `init_chat_model`, cadeia LCEL de normalização, `create_agent` |
| `cli.py` | Chat no terminal; `--lote` roda o TXT de perguntas |
| `web.py` | Mesmo chat em Gradio (http://localhost:7860) |
| `infra/` | Ollama (LLM local) em Docker + script do modelo |

## Pontos de LangChain no código

| Chamada | Onde | Por quê |
| --- | --- | --- |
| `init_chat_model("ollama:qwen3-4b", ...)` | `pipeline.criar_llm` | Instancia o chat model a partir de `provedor:modelo`; trocar de LLM é só mudar `LLM_MODELO` |
| `ChatPromptTemplate.from_messages` | `PROMPT_NORMALIZACAO` | Template com variáveis `{glossario}` e `{mensagem}` |
| `prompt \| llm \| StrOutputParser()` | `Chat.__init__` | LCEL: compõe Runnables; `.invoke(dict)` roda a cadeia |
| `@tool` | `ferramentas.py` | Docstring vira descrição e type hints viram o schema que o LLM recebe |
| `create_agent(model, tools, system_prompt, checkpointer)` | `Chat.__init__` | Agente ReAct pronto (grafo LangGraph por baixo) |
| `InMemorySaver` + `configurable.thread_id` | `Chat.responder` | Memória da conversa por thread |

## Como rodar

Pré-requisitos: Python 3.10+, Docker.

```bash
pip install -r requirements.txt
cp .env.example .env

# LLM local (Qwen3 4B Instruct, ~2.5 GB, roda em CPU)
docker compose -f infra/docker-compose.yml up -d
./infra/baixar_modelo.sh

python cli.py --lote    # roda data/perguntas.txt
python cli.py           # interativo
python web.py           # navegador
```

Quer usar um LLM de nuvem? `pip install langchain-openai`, defina `OPENAI_API_KEY`
e `LLM_MODELO=openai:gpt-4.1-mini`. Nada mais muda.

### Exemplo de saída (`cli.py --lote`)

```
> qts rel. o lco já teve?
  [glossário]   lco, rel., qts
  [normalizada] Quantas versões publicadas o pacote "langchain-ollama" já teve?
  [tools]       pypi_pacote

O pacote "langchain-ollama" já teve 26 versões publicadas.
```

## Por que PyPI/npm como API pública

São abertas, sem chave e respostas objetivas (versão, licença, data), o que deixa
fácil conferir se o agente acertou. Também eram as únicas APIs públicas liberadas
na rede do ambiente da gravação (SWAPI, Marvel, Wikipedia etc. estavam bloqueadas).
