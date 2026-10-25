"""Pipeline do chat em duas etapas:

1. Normalização: uma cadeia LCEL (prompt | llm | parser) reescreve a mensagem
   abreviada numa pergunta clara, usando só os termos do glossário encontrados.
2. Resposta: um agente (create_agent) decide quais tools chamar (PyPI/npm)
   e responde com base no retorno delas.

Fase 2: tudo é instrumentado com LangWatch (trace por mensagem, spans por etapa).
"""

from dataclasses import dataclass, field

import langwatch
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import InMemorySaver

from chat import config, glossario
from chat.ferramentas import FERRAMENTAS

PROMPT_NORMALIZACAO = ChatPromptTemplate.from_messages([
    ("system",
     "Você reescreve mensagens abreviadas em português claro e completo.\n"
     "Use o glossário para expandir as abreviações e trocar apelidos pelo nome exato do pacote.\n"
     "Responda SOMENTE com a pergunta reescrita. Não responda a pergunta.\n\n"
     "Glossário:\n{glossario}"),
    ("human", "{mensagem}"),
])

PROMPT_AGENTE = (
    "Você responde perguntas sobre pacotes de software usando as ferramentas disponíveis.\n"
    "- Sempre consulte a ferramenta antes de responder; nunca invente versões, datas ou licenças.\n"
    "- Pacote Python -> pypi_pacote. Pacote JavaScript/npm -> npm_pacote.\n"
    "- Responda em português, curto e direto."
)


@dataclass
class Resposta:
    mensagem: str                      # como o usuário escreveu
    termos: dict[str, str]             # abreviações encontradas no glossário
    pergunta: str                      # pergunta após a normalização
    texto: str                         # resposta final do agente
    ferramentas: list[str] = field(default_factory=list)  # tools chamadas neste turno


def criar_llm():
    """`init_chat_model("provedor:modelo")` instancia a classe certa (ChatOllama,
    ChatOpenAI, ...) a partir de uma string, então trocar de LLM é só mudar o .env."""
    extras = {}
    if config.LLM_MODELO.startswith("ollama:"):
        # reasoning=False desliga o modo "thinking" do Qwen3; num_ctx = janela de contexto.
        extras = {"base_url": config.OLLAMA_URL, "reasoning": False, "num_ctx": 8192}
        if config.OLLAMA_NUM_THREAD:
            extras["num_thread"] = config.OLLAMA_NUM_THREAD
    return init_chat_model(config.LLM_MODELO, temperature=0, **extras)


class Chat:
    def __init__(self):
        llm = criar_llm()
        self.glossario = glossario.carregar(config.ARQ_ABREVIACOES)

        # LCEL: `|` compõe Runnables. O dict de entrada preenche o prompt, o prompt
        # vira mensagens, o LLM devolve um AIMessage e o parser extrai a string.
        self.normalizar = PROMPT_NORMALIZACAO | llm | StrOutputParser()

        # create_agent monta um grafo (roda sobre LangGraph): nó do modelo <-> nó das
        # tools, em loop, até o modelo responder sem pedir tool. O checkpointer guarda
        # o histórico por thread_id, então o agente lembra dos turnos anteriores.
        self.agente = create_agent(
            model=llm,
            tools=FERRAMENTAS,
            system_prompt=PROMPT_AGENTE,
            checkpointer=InMemorySaver(),
        )

    # Cada chamada vira um trace no LangWatch. Por padrão o decorator captura os
    # argumentos e o retorno como input/output; aqui eles são definidos à mão com
    # trace.update(), o que tem precedência (o retorno é um dataclass, pouco legível).
    @langwatch.trace(name="chat-pacotes")
    def responder(self, mensagem: str, thread_id: str = "padrao") -> Resposta:
        trace = langwatch.get_current_trace()
        # thread_id agrupa os traces numa conversa; labels servem de filtro no painel.
        trace.update(
            input=mensagem,
            metadata={"thread_id": thread_id, "labels": ["tutorial"], "modelo": config.LLM_MODELO},
        )
        # Callback que converte os eventos do LangChain (chain/LLM/tool start/end)
        # em spans filhos deste trace. Precisa ir no config de cada .invoke().
        callbacks = [trace.get_langchain_callback()]

        # Span manual: etapa sem LangChain, que de outro modo não apareceria no trace.
        with langwatch.span(name="glossario", type="span") as span:
            termos = glossario.encontrar(mensagem, self.glossario)
            span.update(input=mensagem, output=termos)

        # Sem abreviação conhecida, não há o que traduzir: economiza uma chamada ao LLM.
        pergunta = mensagem
        if termos:
            pergunta = self.normalizar.invoke(
                {"glossario": glossario.formatar(termos), "mensagem": mensagem},
                config={"callbacks": callbacks, "run_name": "normalizacao"},
            ).strip()

        # Entrada do agente é o estado do grafo: {"messages": [...]}. O config
        # "configurable.thread_id" escolhe qual histórico o checkpointer usa.
        estado = self.agente.invoke(
            {"messages": [HumanMessage(pergunta)]},
            config={
                "configurable": {"thread_id": thread_id},
                "callbacks": callbacks,
                "run_name": "agente",
            },
        )
        resposta = Resposta(
            mensagem=mensagem,
            termos=termos,
            pergunta=pergunta,
            texto=estado["messages"][-1].content,
            ferramentas=_tools_do_turno(estado["messages"]),
        )

        trace.update(output=resposta.texto)
        # Avaliação client-side: aparece na aba Evaluations do trace. Aqui a regra é
        # simples (o agente consultou a API?), mas poderia ser qualquer métrica.
        langwatch.get_current_span().add_evaluation(
            name="consultou_api",
            passed=bool(resposta.ferramentas),
            details=f"tools chamadas: {resposta.ferramentas or 'nenhuma'}",
        )
        return resposta


def _tools_do_turno(mensagens) -> list[str]:
    """Nomes das tools chamadas depois da última mensagem do usuário."""
    ultimo_humano = max(i for i, m in enumerate(mensagens) if isinstance(m, HumanMessage))
    return [m.name for m in mensagens[ultimo_humano:] if isinstance(m, ToolMessage)]
