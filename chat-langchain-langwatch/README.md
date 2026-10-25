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
| `chat/observabilidade.py` | `langwatch.setup()` e filtro de spans HTTP (Fase 2) |
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

## Fase 2 — LangWatch

LangWatch é uma plataforma de observabilidade/avaliação de LLM apps. O SDK Python é
OpenTelemetry por baixo: cada mensagem do chat vira um **trace**, e cada etapa vira
um **span** filho, enviado via OTLP para `LANGWATCH_ENDPOINT`.

### Pontos de LangWatch no código

| Chamada | Onde | O que gera no painel |
| --- | --- | --- |
| `langwatch.setup(span_exclude_rules=...)` | `observabilidade.iniciar` | Configura o exporter OTLP (lê `LANGWATCH_API_KEY`/`LANGWATCH_ENDPOINT`) e filtra spans |
| `@langwatch.trace(name="chat-pacotes")` | `Chat.responder` | Um trace por mensagem (span raiz) |
| `trace.update(input=, output=, metadata=)` | `Chat.responder` | Input/Output do trace; `thread_id` agrupa a conversa; `labels` vira filtro |
| `trace.get_langchain_callback()` | `config={"callbacks": [...]}` nos `.invoke()` | Spans automáticos de chain, LLM (mensagens, modelo, tokens) e tools |
| `langwatch.span(name="glossario")` | `Chat.responder` | Span manual para a etapa que não é LangChain |
| `span.add_evaluation(name="consultou_api", passed=...)` | `Chat.responder` | Avaliação Pass/Fail na coluna EVALS e no trace |

`run_name` no config do `.invoke()` dá nome aos spans (`normalizacao`, `agente`).

### Pegadinhas de OpenTelemetry (encontradas na prática)

- **Ordem do setup:** o `@langwatch.trace` faz um setup implícito quando o módulo é
  importado. Por isso `pipeline.py` importa `observabilidade` (que chama `setup()`)
  antes dos decorators; senão as `span_exclude_rules` não chegam ao exporter.
- **Provider global:** `setup()` registra um TracerProvider global. O FastAPI usado
  pelo Gradio também emite spans OTel, e as requisições HTTP (`GET /assets/...`,
  `POST /gradio_api/...`) iam parar no LangWatch. `span_exclude_rules` descarta esse ruído.
- **Trace aninhado:** pelo mesmo motivo, o `chat-pacotes` virava filho do span HTTP do
  Gradio. `web.py` roda cada mensagem num contexto OTel vazio
  (`otel_context.attach(Context())`) para ela ser um trace próprio.
- **Threads do llama.cpp:** com mais threads que cores livres (ex.: navegador gravando
  vídeo ao mesmo tempo), a geração caía de ~7 para ~0,25 token/s. `OLLAMA_NUM_THREAD` fixa o valor.

### Árvore de spans de uma mensagem

```
chat-pacotes                (trace — @langwatch.trace)
├─ glossario                (langwatch.span manual)
├─ normalizacao             (callback LangChain: RunnableSequence)
│  ├─ ChatPromptTemplate
│  ├─ llm                   (ChatOllama — mensagens de entrada/saída)
│  └─ StrOutputParser
├─ agente                   (callback LangChain: grafo do create_agent)
│  ├─ model → llm           (LLM pede a tool)
│  ├─ tools → pypi_pacote   (chamada à API do PyPI)
│  └─ model → llm           (LLM responde com o resultado)
└─ consultou_api            (evaluation)
```

### Subindo o LangWatch

Na gravação foi usado o LangWatch **self-hosted** (open source, Docker Compose),
porque o container não alcançava `app.langwatch.ai`:

```bash
git clone --depth 1 https://github.com/langwatch/langwatch && cd langwatch
cp .env.example .env   # troque NEXTAUTH_SECRET e CREDENTIALS_SECRET (openssl rand)
docker compose -f infra/compose.yml --project-directory . up -d
# http://localhost:5560 → criar conta → organização → "Manually" → Python → LangChain → Create a key
```

Com a nuvem é igual: crie a conta em https://app.langwatch.ai, gere a chave e use
`LANGWATCH_ENDPOINT=https://app.langwatch.ai`.

Depois, no `.env` do chat:

```bash
LANGWATCH_API_KEY=sk-lw-...
LANGWATCH_ENDPOINT=http://localhost:5560
```

### Caso real encontrado com o LangWatch

Na mesma conversa, `qual a últ. ver. do lw?` seguida de `qts rel. o lg já teve?`
fazia o agente responder "não há informação" no 2º turno. No painel:

1. **Trace Explorer**: o 2º trace com `consultou_api` = **Fail**.
2. **Waterfall**: dentro de `agente` só havia um `model → llm`, sem span `tools`.
   O LLM, com o histórico do checkpointer, achou que não precisava consultar de novo.
3. **Correção** (`gravacao/correcao_prompt.diff`): regra no system prompt
   ("cada pergunta é uma consulta nova").
4. Reteste: avaliação **Pass** e `tools → pypi_pacote` no waterfall.

Reproduzia 2/2 antes e passou 6/6 depois (temperatura 0).

## Gravação (vídeo + roteiro)

| Arquivo | O que é |
| --- | --- |
| `gravacao/tutorial.mp4` | Vídeo do tutorial, com legendas na tela; esperas do LLM aceleradas |
| `gravacao/ROTEIRO.md` | A explicação em texto, por parte, com timestamps do vídeo |
| `gravacao/tutorial.srt` | As mesmas legendas em SRT |
| `gravacao/gravar.js` | Roteiro em Playwright: cenas de código, cadastro no LangWatch, chat, traces |
| `gravacao/cenas.py` | Gera as páginas de código/cartões (Pygments) que aparecem no vídeo |
| `gravacao/montar.py` | ffmpeg: acelera esperas, gera MP4, SRT e o ROTEIRO.md |

Para regravar (LangWatch zerado, Ollama no ar, `.env` sem `LANGWATCH_API_KEY`):

```bash
PY=$(which python) node gravacao/gravar.js && python gravacao/montar.py
```

## Por que PyPI/npm como API pública

São abertas, sem chave e respostas objetivas (versão, licença, data), o que deixa
fácil conferir se o agente acertou. Também eram as únicas APIs públicas liberadas
na rede do ambiente da gravação (SWAPI, Marvel, Wikipedia etc. estavam bloqueadas).
