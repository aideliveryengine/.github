# Roteiro do vídeo

Vídeo: `tutorial.mp4` (13:32). Legendas: `tutorial.srt`. Trechos marcados com ⏩ são esperas do LLM local, aceleradas na montagem.


## Abertura

- **00:01** Objetivo: entender as chamadas de LangChain e, depois, o que o LangWatch mostra sobre elas.
- **00:08** O app é um chat que responde perguntas sobre pacotes Python/JS consultando as APIs públicas do PyPI e do npm.

## Parte 1 · LangChain

- **00:18** O glossário: um TXT com `termo = significado`. Ele traduz o jeito abreviado de perguntar.
- **00:25** Apelidos de pacotes: `lc` é langchain no PyPI, `lcjs` é langchain no npm…
- **00:32** …e abreviações comuns: `últ.`, `ver.`, `lic.`. Não é RAG: é busca exata de termos.
- **00:40** O roteiro de perguntas, escritas de propósito de forma abreviada. `cli.py --lote` roda todas.
- **00:50** `carregar()` lê o TXT e devolve um dict `{termo: significado}`.
- **00:56** `encontrar()` procura cada termo na mensagem com regex. Só os termos achados vão para o prompt.
- **01:04** Detalhe: lookarounds em vez de `\b`, porque termos como `últ.` terminam em ponto.
- **01:13** Primeira peça de LangChain: `@tool` transforma uma função comum numa tool que o LLM pode chamar.
- **01:21** O nome da função vira o nome da tool, a docstring vira a descrição e as type hints viram o JSON Schema.
- **01:29** É a docstring que o modelo lê para decidir QUANDO chamar a tool. Escreva para o LLM, não para humanos.
- **01:37** Por dentro é só HTTP: `GET pypi.org/pypi/<nome>/json`, a API pública e sem chave do PyPI.
- **01:45** Retorno enxuto: só os campos úteis. Menos tokens para o LLM e menos chance de ele se perder.
- **01:53** O mesmo para o npm. As duas tools ficam na lista `FERRAMENTAS`, entregue ao agente.
- **02:01** O coração: `pipeline.py`. Duas etapas — normalizar a pergunta e responder com um agente.
- **02:09** `init_chat_model("ollama:qwen3-4b")` escolhe a classe do provedor pela string (aqui ChatOllama).
- **02:16** Trocar para OpenAI, Anthropic etc. é só mudar `LLM_MODELO` no .env. O resto do código não muda.
- **02:24** `ChatPromptTemplate`: mensagens system + human com variáveis `{glossario}` e `{mensagem}`.
- **02:32** LCEL: o operador `|` encadeia Runnables. prompt → LLM → `StrOutputParser` (AIMessage → str).
- **02:39** Tudo em LangChain é Runnable: tem `.invoke()`, `.stream()`, `.batch()` e aceita um `config`.
- **02:46** `create_agent`: o agente pronto do LangChain 1.x. Recebe o modelo, as tools e o system prompt.
- **02:54** Por baixo é um grafo LangGraph: nó do modelo ↔ nó das tools, em loop, até o modelo responder sem pedir tool.
- **03:03** O `checkpointer` guarda o histórico por `thread_id`: é a memória da conversa.
- **03:09** `responder()`: acha os termos, e só chama o LLM de normalização se houver abreviação.
- **03:17** `.invoke(dict)` roda a cadeia: o dict preenche as variáveis do prompt.
- **03:24** O agente recebe o estado `{"messages": [...]}`; `configurable.thread_id` escolhe o histórico.
- **03:31** A resposta é a última mensagem do estado. As ToolMessages do turno dizem quais tools foram usadas.

## Parte 1 · rodando

- **03:48** `web.py`: uma UI Gradio de 30 linhas em cima do mesmo `Chat.responder()`.
- **03:57** ⏩ Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…
- **04:00** Resposta certa: licença e versão mínima do Python vieram da API do PyPI, não da memória do modelo.
- **04:09** Nos bastidores: termos encontrados, a pergunta normalizada pela cadeia LCEL e a tool chamada.
- **04:16** Funciona — mas é uma caixa-preta. Quanto tempo levou cada etapa? Que prompt foi enviado? Isso é o que o LangWatch mostra.

## Parte 2 · LangWatch

- **04:33** O LangWatch é open source. Aqui ele roda local via Docker Compose; na nuvem o fluxo é idêntico.
- **04:46** Instalação zerada. Primeiro passo: criar a conta (esta instalação não envia e-mail).
- **05:08** Depois, a organização. O projeto é criado junto.
- **05:38** Caso de uso: monitorar e avaliar um app com LLM.
- **06:01** Integração manual com o SDK: é o que nos interessa para entender o código.
- **06:33** Python + LangChain. O snippet sugerido é exatamente o padrão que vamos aplicar.
- **06:55** Chave gerada (aparece uma única vez). Ela só envia dados para este projeto; não lê nada.
- **07:05** No `.env` do chat: a chave e o endpoint (local aqui; na nuvem, `https://app.langwatch.ai`).
- **07:14** `langwatch.setup()` lê a chave e o endpoint do ambiente e registra um TracerProvider OTel com exporter OTLP.
- **07:23** Sem chave, o app segue igual e só não envia traces.
- **07:28** Pegadinha real: o provider é global, e o FastAPI (sob o Gradio) também emite spans. `span_exclude_rules` descarta esse ruído HTTP.
- **07:38** Outra: o setup precisa rodar antes do `@langwatch.trace` ser avaliado; senão o decorator faz um setup implícito sem as regras.
- **07:49** `@langwatch.trace`: cada chamada de `responder()` vira um trace (o span raiz).
- **07:56** `trace.update()`: input e metadata. `thread_id` agrupa as mensagens em conversa; `labels` viram filtro.
- **08:05** O ponto-chave: `get_langchain_callback()` converte eventos do LangChain em spans filhos deste trace.
- **08:13** Etapas fora do LangChain não aparecem sozinhas: `langwatch.span()` cria um span manual.
- **08:21** O callback entra no `config` de cada `.invoke()`. `run_name` dá nome ao span.
- **08:27** Mesma coisa no agente: o callback se propaga por todo o grafo (modelo, tools, sub-chamadas).
- **08:35** Uma avaliação client-side: `consultou_api` passa se o agente chamou alguma tool neste turno.
- **08:43** Regra simples de propósito: resposta sobre versão/licença sem consultar a API é chute. Vamos ver se acontece.

## Parte 2 · traces

- **08:59** Mesmo chat, agora com LangWatch ligado. Duas perguntas na mesma conversa.
- **09:08** ⏩ Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…
- **09:13** Primeira resposta ok.
- **09:19** ⏩ Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…
- **09:22** Opa: "não há informação"? O PyPI tem esse dado. Vamos investigar no LangWatch.
- **09:48** Trace Explorer: um trace por mensagem, com input, output, duração, modelo, labels e a coluna EVALS.
- **09:55** Repare: o segundo trace tem `consultou_api` = Fail. A avaliação pegou o problema.
- **10:05** Abrindo o primeiro trace (o que deu certo). Cabeçalho: duração, nº de spans, modelo e avaliação.
- **10:16** Aba Trace, visão Waterfall: a árvore de spans com o tempo de cada etapa.
- **10:22** `glossario` é o span manual. `normalizacao` é a cadeia LCEL: template → llm → parser.
- **10:28** `agente` é o grafo do create_agent: model (LLM pede a tool) → tools → pypi_pacote → model (responde).
- **10:38** Clicando na tool: input `{"nome": "langwatch"}` e o JSON que a API devolveu. 54 ms — o gargalo não é a API.
- **10:48** O span `llm` da normalização: modelo, mensagens enviadas (system com o glossário) e a pergunta reescrita.
- **10:58** Os atributos seguem a convenção OpenTelemetry GenAI: `gen_ai.input.messages`, `gen_ai.request.model`…
- **11:20** Agora o trace com Fail.
- **11:26** Diagnóstico pelo waterfall: dentro de `agente` há só um `model`. Não existe span de tool.
- **11:35** O LLM respondeu direto, sem chamar `pypi_pacote`: como já havia consultado um pacote, achou que bastava.
- **11:42** Isso só acontece no 2º turno da conversa (histórico no checkpointer). Sem os traces, seria difícil de achar.
- **11:52** Aba Conversation: os dois turnos agrupados pelo `thread_id` que enviamos na metadata.
- **11:59** Lado a lado fica claro: no turno 1 houve consulta; no turno 2 o modelo "respondeu" sem dados.

## Parte 2 · correção

- **12:11** Correção no system prompt: cada pergunta é uma consulta nova; nunca dizer "não há informação" sem consultar.
- **12:27** Patch aplicado e app reiniciado. Nova conversa, mesmas duas perguntas.
- **12:36** ⏩ Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…
- **12:44** ⏩ Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…
- **12:48** Agora veio o número de releases do langgraph, direto da API.
- **13:02** No LangWatch: os dois traces novos com `consultou_api` = Pass.
- **13:13** E o waterfall do 2º turno agora tem `tools → pypi_pacote`. Bug confirmado e corrigido com dados.

## Resumo

- **13:25** Código e README no repositório; o roteiro completo, com tempos, está em `gravacao/ROTEIRO.md`.
