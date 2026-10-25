// Roteiro da gravação do tutorial (Playwright).
//
//   node gravacao/gravar.js
//
// Pré-requisitos: Ollama com o modelo, LangWatch zerado em LW_URL, e o .env do chat
// SEM LANGWATCH_API_KEY (a chave é criada durante a gravação).
// Saídas em gravacao/tmp/: video.webm (bruto) e eventos.json (legendas e trechos
// acelerados), que o montar.py usa para gerar o MP4, as legendas .srt e o roteiro.

const { chromium } = require('playwright');
const { execFileSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');
const REPO = path.resolve(RAIZ, '..');
const TMP = path.join(__dirname, 'tmp');
const CENAS = path.join(TMP, 'cenas');
const PY = process.env.PY || 'python3';
const LW = process.env.LW_URL || 'http://localhost:5560';
const CHAT = 'http://localhost:7860';
const COMMIT_FASE1 = process.env.COMMIT_FASE1 || 'HEAD~1';
const W = 1440, H = 900;

let page, t0, parteAtual = '', legendaAtual = '';
const eventos = { legendas: [], aceleradas: [] };
const agora = () => (Date.now() - t0) / 1000;
const esperar = (ms) => page.waitForTimeout(ms);

// ---------- overlay de legenda / capítulo ----------

const OVERLAY = `
(() => {
  const montar = () => {
    if (document.getElementById('__leg')) return;
    const css = document.createElement('style');
    css.textContent = \`
      #__leg{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);max-width:1180px;z-index:2147483647;
        background:rgba(12,14,18,.93);color:#fff;font:500 23px/1.45 system-ui,'DejaVu Sans',sans-serif;
        padding:14px 26px;border-radius:12px;box-shadow:0 6px 30px rgba(0,0,0,.45);border:1px solid #3a4150}
      #__leg.topo{bottom:auto;top:64px}
      #__leg,#__parte,#__ff{pointer-events:none}
      #__leg:empty{display:none}
      #__leg code{font-family:'JetBrains Mono',monospace;color:#e5c07b;font-size:21px}
      #__parte{position:fixed;right:18px;top:14px;z-index:2147483647;background:#61afef;color:#0d1117;
        font:700 15px system-ui,sans-serif;padding:6px 12px;border-radius:999px}
      #__parte:empty{display:none}
      #__ff{position:fixed;left:18px;top:14px;z-index:2147483647;background:#e06c75;color:#fff;
        font:700 15px system-ui,sans-serif;padding:6px 12px;border-radius:999px}
      #__ff:empty{display:none}\`;
    document.head.appendChild(css);
    for (const id of ['__leg', '__parte', '__ff']) {
      const d = document.createElement('div'); d.id = id; document.body.appendChild(d);
    }
    // No chat (Gradio) a caixa de texto fica embaixo: legenda vai para o topo.
    if (location.port === '7860') document.getElementById('__leg').classList.add('topo');
  };
  window.__overlay = (leg, parte, ff) => {
    montar();
    document.getElementById('__leg').innerHTML = leg || '';
    document.getElementById('__parte').textContent = parte || '';
    document.getElementById('__ff').textContent = ff || '';
  };
  if (document.readyState !== 'loading') montar();
  else document.addEventListener('DOMContentLoaded', montar);
})();`;

let ffAtual = '';
async function aplicarOverlay() {
  await page.evaluate(([l, p, f]) => window.__overlay && window.__overlay(l, p, f),
    [legendaAtual, parteAtual, ffAtual]).catch(() => {});
}

// Mostra a legenda e espera o tempo de leitura (~55 ms por caractere).
async function legenda(texto, minMs = 0) {
  const ms = Math.max(minMs, 2200 + texto.replace(/<[^>]+>/g, '').length * 55);
  legendaAtual = texto;
  eventos.legendas.push({ t: agora(), dur: ms / 1000, texto, parte: parteAtual });
  await aplicarOverlay();
  await esperar(ms);
}

async function parte(nome) { parteAtual = nome; await aplicarOverlay(); }

async function ir(url) {
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await esperar(1200);
  await aplicarOverlay();
}

// Trecho de espera (LLM rodando em CPU): marcado para ser acelerado na montagem.
async function acelerado(texto, fn, fator = 10) {
  legendaAtual = texto; ffAtual = `⏩ acelerado ×${fator}`;
  await aplicarOverlay();
  const ini = agora();
  eventos.legendas.push({ t: ini, dur: 0, texto, parte: parteAtual, acelerada: true });
  await fn();
  eventos.aceleradas.push({ ini, fim: agora(), fator });
  ffAtual = '';
  await aplicarOverlay();
}

// ---------- cenas de código ----------

function gerarCena(tipo, args) { execFileSync(PY, [path.join(__dirname, 'cenas.py'), tipo, ...args]); }

function cenaCodigo(nome, arquivo, titulo) {
  const saida = path.join(CENAS, nome + '.html');
  gerarCena('codigo', [arquivo, saida, titulo]);
  return 'file://' + saida;
}

function cenaCard(nome, titulo, subtitulo, itens) {
  const saida = path.join(CENAS, nome + '.html');
  gerarCena('card', [saida, titulo, subtitulo, ...itens]);
  return 'file://' + saida;
}

// Arquivo como estava no commit da Fase 1 (sem LangWatch).
function versaoFase1(rel) {
  const destino = path.join(TMP, 'fase1', rel);
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  const conteudo = execFileSync('git', ['-C', REPO, 'show', `${COMMIT_FASE1}:chat-langchain-langwatch/${rel}`]);
  fs.writeFileSync(destino, conteudo);
  return destino;
}

// Destaca `n` linhas a partir da primeira que contém `trecho` (+ `desloc`) e rola até ela.
async function foco(trecho, n = 1, desloc = 0) {
  await page.evaluate(([trecho, n, desloc]) => {
    const linhas = [...document.querySelectorAll('.linha')];
    linhas.forEach((l) => l.classList.remove('foco'));
    let i = linhas.findIndex((l) => l.textContent.includes(trecho));
    if (i < 0) throw new Error('trecho não encontrado: ' + trecho);
    i += desloc;
    for (let k = i; k < i + n && k < linhas.length; k++) linhas[k].classList.add('foco');
    document.querySelector('.cod').classList.add('focando');
    const alvo = linhas[Math.max(0, i - 4)];
    window.scrollTo({ top: alvo.offsetTop - 70, behavior: 'smooth' });
  }, [trecho, n, desloc]);
  await esperar(700);
}

async function semFoco() {
  await page.evaluate(() => {
    document.querySelectorAll('.linha.foco').forEach((l) => l.classList.remove('foco'));
    document.querySelector('.cod')?.classList.remove('focando');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  await esperar(600);
}

// ---------- app de chat ----------

let web = null;
function subirWeb() {
  web = spawn(PY, ['web.py'], { cwd: RAIZ, stdio: 'ignore' });
}
async function derrubarWeb() {
  if (!web) return;
  web.kill('SIGINT');
  await new Promise((r) => web.once('exit', r));
  web = null;
}
async function esperarWeb() {
  for (let i = 0; i < 120; i++) {
    try { const r = await fetch(CHAT); if (r.ok) return; } catch {}
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error('web.py não subiu');
}

async function perguntar(texto) {
  const antes = await page.locator('text=bastidores').count();
  // Sem animação nem cronômetro do Gradio: menos repaint = menos CPU no navegador,
  // que senão disputa os cores com o llama.cpp e derruba a geração.
  await page.addStyleTag({ content: '.progress-text,.eta-bar,.meta-text,.timer,.progress-level{display:none!important}'
    + ' *{animation:none!important;transition:none!important}' });
  const caixa = page.locator('textarea').first();
  await caixa.click();
  await caixa.pressSequentially(texto, { delay: 70 });
  await esperar(500);
  await caixa.press('Enter');
  await acelerado('Esperando o LLM local (Qwen3 4B em CPU): normalização + agente + tool…', async () => {
    await page.waitForFunction((n) => {
      return [...document.querySelectorAll('summary')].filter((s) => s.textContent.includes('bastidores')).length > n;
    }, antes, { timeout: 300000 });
  });
  await esperar(800);
}

async function abrirBastidores() {
  const s = page.locator('summary', { hasText: 'bastidores' }).last();
  await s.click();
  await esperar(600);
}

// ---------- LangWatch ----------

async function pularTour() {
  for (let i = 0; i < 3; i++) {
    const b = page.getByText('Skip tour');
    if (await b.isVisible().catch(() => false)) { await b.click(); await esperar(500); }
  }
}

async function clicarSpan(nome, indice = 0) {
  await page.getByText(nome, { exact: true }).nth(indice).click();
  await esperar(1500);
}

// Recarrega o Trace Explorer até existirem `n` traces com esse input (o SDK envia em lote).
async function esperarTraces(slug, input, n) {
  for (let i = 0; i < 30; i++) {
    await ir(`${LW}/${slug}/messages`);
    await esperar(2500);
    await pularTour();
    if (await page.getByText(input, { exact: true }).count() >= n) return;
  }
  throw new Error('trace não chegou: ' + input);
}

// ================================================================
async function main() {
  fs.rmSync(TMP, { recursive: true, force: true });
  fs.mkdirSync(CENAS, { recursive: true });

  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    recordVideo: { dir: TMP, size: { width: W, height: H } },
    locale: 'pt-BR',
  });
  await ctx.addInitScript(OVERLAY);
  page = await ctx.newPage();
  page.setDefaultTimeout(120000);  // a UI do LangWatch demora a hidratar com a CPU dividida
  t0 = Date.now();

  // ---------------- abertura ----------------
  await ir(cenaCard('00_abertura', 'Chat de pacotes', 'LangChain + LangWatch, na prática', [
    'Perguntas abreviadas → glossário em TXT → pergunta clara',
    'Agente LangChain consulta APIs públicas (PyPI e npm)',
    'LangWatch: traces, spans, conversas e avaliações',
    'Tudo local: LLM Qwen3 4B no Ollama + LangWatch self-hosted',
  ]));
  await legenda('Objetivo: entender as chamadas de LangChain e, depois, o que o LangWatch mostra sobre elas.');
  await legenda('O app é um chat que responde perguntas sobre pacotes Python/JS consultando as APIs públicas do PyPI e do npm.');

  // ---------------- parte 1: LangChain ----------------
  await parte('Parte 1 · LangChain');
  await ir(cenaCodigo('01_abrev', path.join(RAIZ, 'data/abreviacoes.txt'), 'data/abreviacoes.txt'));
  await legenda('O glossário: um TXT com <code>termo = significado</code>. Ele traduz o jeito abreviado de perguntar.');
  await foco('lc = pacote', 5);
  await legenda('Apelidos de pacotes: <code>lc</code> é langchain no PyPI, <code>lcjs</code> é langchain no npm…');
  await foco('últ. = última', 6);
  await legenda('…e abreviações comuns: <code>últ.</code>, <code>ver.</code>, <code>lic.</code>. Não é RAG: é busca exata de termos.');

  await ir(cenaCodigo('02_perguntas', path.join(RAIZ, 'data/perguntas.txt'), 'data/perguntas.txt'));
  await foco('qual a últ. ver. do lc?', 6);
  await legenda('O roteiro de perguntas, escritas de propósito de forma abreviada. <code>cli.py --lote</code> roda todas.');

  await ir(cenaCodigo('03_glossario', versaoFase1('chat/glossario.py'), 'chat/glossario.py'));
  await foco('def carregar(', 11);
  await legenda('<code>carregar()</code> lê o TXT e devolve um dict <code>{termo: significado}</code>.');
  await foco('def encontrar(', 15);
  await legenda('<code>encontrar()</code> procura cada termo na mensagem com regex. Só os termos achados vão para o prompt.');
  await foco('padrao = rf', 1);
  await legenda('Detalhe: lookarounds em vez de <code>\\b</code>, porque termos como <code>últ.</code> terminam em ponto.');

  await ir(cenaCodigo('04_ferramentas', versaoFase1('chat/ferramentas.py'), 'chat/ferramentas.py'));
  await foco('O decorator `@tool`', 4);
  await legenda('Primeira peça de LangChain: <code>@tool</code> transforma uma função comum numa tool que o LLM pode chamar.');
  await foco('def pypi_pacote', 6, -1);
  await legenda('O nome da função vira o nome da tool, a docstring vira a descrição e as type hints viram o JSON Schema.');
  await legenda('É a docstring que o modelo lê para decidir QUANDO chamar a tool. Escreva para o LLM, não para humanos.');
  await foco('resp = _http.get(f"https://pypi.org', 6);
  await legenda('Por dentro é só HTTP: <code>GET pypi.org/pypi/&lt;nome&gt;/json</code>, a API pública e sem chave do PyPI.');
  await foco('"pacote": info["name"]', 13, -1);
  await legenda('Retorno enxuto: só os campos úteis. Menos tokens para o LLM e menos chance de ele se perder.');
  await foco('FERRAMENTAS = ', 1);
  await legenda('O mesmo para o npm. As duas tools ficam na lista <code>FERRAMENTAS</code>, entregue ao agente.');

  const pipe1 = versaoFase1('chat/pipeline.py');
  await ir(cenaCodigo('05_pipeline', pipe1, 'chat/pipeline.py  (Fase 1)'));
  await legenda('O coração: <code>pipeline.py</code>. Duas etapas — normalizar a pergunta e responder com um agente.');
  await foco('def criar_llm', 9);
  await legenda('<code>init_chat_model("ollama:qwen3-4b")</code> escolhe a classe do provedor pela string (aqui ChatOllama).');
  await legenda('Trocar para OpenAI, Anthropic etc. é só mudar <code>LLM_MODELO</code> no .env. O resto do código não muda.');
  await foco('PROMPT_NORMALIZACAO = ', 8);
  await legenda('<code>ChatPromptTemplate</code>: mensagens system + human com variáveis <code>{glossario}</code> e <code>{mensagem}</code>.');
  await foco('self.normalizar = ', 1);
  await legenda('LCEL: o operador <code>|</code> encadeia Runnables. prompt → LLM → <code>StrOutputParser</code> (AIMessage → str).');
  await legenda('Tudo em LangChain é Runnable: tem <code>.invoke()</code>, <code>.stream()</code>, <code>.batch()</code> e aceita um <code>config</code>.');
  await foco('self.agente = create_agent(', 6);
  await legenda('<code>create_agent</code>: o agente pronto do LangChain 1.x. Recebe o modelo, as tools e o system prompt.');
  await legenda('Por baixo é um grafo LangGraph: nó do modelo ↔ nó das tools, em loop, até o modelo responder sem pedir tool.');
  await foco('checkpointer=InMemorySaver()', 1);
  await legenda('O <code>checkpointer</code> guarda o histórico por <code>thread_id</code>: é a memória da conversa.');
  await foco('def responder(', 6);
  await legenda('<code>responder()</code>: acha os termos, e só chama o LLM de normalização se houver abreviação.');
  await foco('pergunta = self.normalizar.invoke(', 3);
  await legenda('<code>.invoke(dict)</code> roda a cadeia: o dict preenche as variáveis do prompt.');
  await foco('estado = self.agente.invoke(', 4);
  await legenda('O agente recebe o estado <code>{"messages": [...]}</code>; <code>configurable.thread_id</code> escolhe o histórico.');
  await legenda('A resposta é a última mensagem do estado. As ToolMessages do turno dizem quais tools foram usadas.');

  // ---------------- demo fase 1 ----------------
  await parte('Parte 1 · rodando');
  subirWeb(); await esperarWeb();
  await ir(CHAT);
  await legenda('<code>web.py</code>: uma UI Gradio de 30 linhas em cima do mesmo <code>Chat.responder()</code>.');
  await perguntar('qual a lic. do lw e a req. py?');
  await legenda('Resposta certa: licença e versão mínima do Python vieram da API do PyPI, não da memória do modelo.');
  await abrirBastidores();
  await legenda('Nos bastidores: termos encontrados, a pergunta normalizada pela cadeia LCEL e a tool chamada.');
  await legenda('Funciona — mas é uma caixa-preta. Quanto tempo levou cada etapa? Que prompt foi enviado? Isso é o que o LangWatch mostra.');
  await derrubarWeb();

  // ---------------- parte 2: LangWatch ----------------
  await parte('Parte 2 · LangWatch');
  await ir(cenaCard('10_langwatch', 'LangWatch', 'Observabilidade e avaliação de apps com LLM', [
    'Trace = uma requisição (aqui: uma mensagem do chat)',
    'Span = uma etapa dentro dela (chain, chamada de LLM, tool…)',
    'SDK Python sobre OpenTelemetry, exporta via OTLP',
    'Rodando self-hosted (Docker Compose) em <code>localhost:5560</code>',
  ]));
  await legenda('O LangWatch é open source. Aqui ele roda local via Docker Compose; na nuvem o fluxo é idêntico.');

  await ir(LW + '/auth/signup');
  await legenda('Instalação zerada. Primeiro passo: criar a conta (esta instalação não envia e-mail).');
  await page.fill('input[type=email]', '');
  await page.locator('input[type=email]').pressSequentially('tutorial@langwatch.local', { delay: 40 });
  await page.click('button[type=submit]');
  await esperar(1500);
  await page.locator('input[name=password]').pressSequentially('tutorial-123456', { delay: 40 });
  await page.locator('input[name=confirmPassword]').pressSequentially('tutorial-123456', { delay: 40 });
  await esperar(500);
  await page.click('button[type=submit]');
  await page.waitForURL(/onboarding/, { timeout: 60000 });
  await esperar(1500); await aplicarOverlay();
  await legenda('Depois, a organização. O projeto é criado junto.');
  await page.locator('input[placeholder="Company or your name"]').pressSequentially('Tutorial', { delay: 60 });
  await page.click('[data-testid=terms-agreement-box]');
  await page.getByRole('button', { name: 'Next' }).click();
  await esperar(1500);
  await legenda('Caso de uso: monitorar e avaliar um app com LLM.');
  await page.getByText('Monitor & evaluate my LLM app').click();
  await esperar(700);
  await page.getByRole('button', { name: 'Finish' }).click();
  await page.waitForURL(/onboarding\/product/, { timeout: 60000 });
  await esperar(1500); await aplicarOverlay();
  const slug = new URL(page.url()).searchParams.get('projectSlug');
  await legenda('Integração manual com o SDK: é o que nos interessa para entender o código.');
  await page.getByRole('button', { name: /Manually/ }).click();
  await esperar(2000); await aplicarOverlay();
  await page.getByRole('button', { name: 'Python language' }).click();
  await esperar(800);
  await page.getByRole('button', { name: 'LangChain framework' }).click();
  await esperar(1500);
  await legenda('Python + LangChain. O snippet sugerido é exatamente o padrão que vamos aplicar.');
  await page.getByRole('button', { name: 'Create a key' }).click();
  await esperar(2500);
  const texto = await page.locator('body').innerText();
  const chave = (texto.match(/LANGWATCH_API_KEY=(sk-lw-\S+)/) || [])[1];
  if (!chave) throw new Error('chave não encontrada');
  await page.getByText('LANGWATCH_API_KEY=').first().scrollIntoViewIfNeeded();
  await legenda('Chave gerada (aparece uma única vez). Ela só envia dados para este projeto; não lê nada.');

  // .env com a chave
  const envPath = path.join(RAIZ, '.env');
  let env = fs.readFileSync(envPath, 'utf8').replace(/^#?LANGWATCH_(API_KEY|ENDPOINT)=.*\n?/gm, '');
  env = env.trimEnd() + `\nLANGWATCH_API_KEY=${chave}\nLANGWATCH_ENDPOINT=${LW}\n`;
  fs.writeFileSync(envPath, env);
  await ir(cenaCodigo('11_env', envPath, '.env'));
  await foco('LANGWATCH_API_KEY', 2);
  await legenda('No <code>.env</code> do chat: a chave e o endpoint (local aqui; na nuvem, <code>https://app.langwatch.ai</code>).');

  // código da fase 2
  await ir(cenaCodigo('12_obs', path.join(RAIZ, 'chat/observabilidade.py'), 'chat/observabilidade.py  (novo)'));
  await foco('langwatch.setup(span', 1);
  await legenda('<code>langwatch.setup()</code> lê a chave e o endpoint do ambiente e registra um TracerProvider OTel com exporter OTLP.');
  await legenda('Sem chave, o app segue igual e só não envia traces.');
  await foco('_RUIDO_HTTP = [', 4);
  await legenda('Pegadinha real: o provider é global, e o FastAPI (sob o Gradio) também emite spans. <code>span_exclude_rules</code> descarta esse ruído HTTP.');
  await foco('Importado no topo', 2);
  await legenda('Outra: o setup precisa rodar antes do <code>@langwatch.trace</code> ser avaliado; senão o decorator faz um setup implícito sem as regras.');

  await ir(cenaCodigo('13_pipeline2', path.join(RAIZ, 'chat/pipeline.py'), 'chat/pipeline.py  (Fase 2)'));
  await foco('@langwatch.trace(', 2);
  await legenda('<code>@langwatch.trace</code>: cada chamada de <code>responder()</code> vira um trace (o span raiz).');
  await foco('input=mensagem,', 4, -1);
  await legenda('<code>trace.update()</code>: input e metadata. <code>thread_id</code> agrupa as mensagens em conversa; <code>labels</code> viram filtro.');
  await foco('callbacks = [trace.get_langchain_callback()]', 1);
  await legenda('O ponto-chave: <code>get_langchain_callback()</code> converte eventos do LangChain em spans filhos deste trace.');
  await foco('with langwatch.span(name="glossario"', 3);
  await legenda('Etapas fora do LangChain não aparecem sozinhas: <code>langwatch.span()</code> cria um span manual.');
  await foco('config={"callbacks": callbacks, "run_name": "normalizacao"}', 1);
  await legenda('O callback entra no <code>config</code> de cada <code>.invoke()</code>. <code>run_name</code> dá nome ao span.');
  await foco('"callbacks": callbacks,', 2);
  await legenda('Mesma coisa no agente: o callback se propaga por todo o grafo (modelo, tools, sub-chamadas).');
  await foco('add_evaluation(', 4);
  await legenda('Uma avaliação client-side: <code>consultou_api</code> passa se o agente chamou alguma tool neste turno.');
  await legenda('Regra simples de propósito: resposta sobre versão/licença sem consultar a API é chute. Vamos ver se acontece.');

  // demo com traces
  await parte('Parte 2 · traces');
  subirWeb(); await esperarWeb();
  await ir(CHAT);
  await legenda('Mesmo chat, agora com LangWatch ligado. Duas perguntas na mesma conversa.');
  await perguntar('qual a últ. ver. do lw?');
  await legenda('Primeira resposta ok.');
  await perguntar('qts rel. o lg já teve?');
  await legenda('Opa: "não há informação"? O PyPI tem esse dado. Vamos investigar no LangWatch.');

  await esperarTraces(slug, 'qts rel. o lg já teve?', 1); await aplicarOverlay();
  await legenda('Trace Explorer: um trace por mensagem, com input, output, duração, modelo, labels e a coluna EVALS.');
  await legenda('Repare: o segundo trace tem <code>consultou_api</code> = Fail. A avaliação pegou o problema.');

  // trace 1 (ok)
  await page.getByText('qual a últ. ver. do lw?').first().click();
  await esperar(3000); await aplicarOverlay();
  await legenda('Abrindo o primeiro trace (o que deu certo). Cabeçalho: duração, nº de spans, modelo e avaliação.');
  await page.keyboard.press('t');
  await esperar(2000);
  await legenda('Aba Trace, visão Waterfall: a árvore de spans com o tempo de cada etapa.');
  await legenda('<code>glossario</code> é o span manual. <code>normalizacao</code> é a cadeia LCEL: template → llm → parser.');
  await legenda('<code>agente</code> é o grafo do create_agent: model (LLM pede a tool) → tools → pypi_pacote → model (responde).');
  await clicarSpan('pypi_pacote');
  await legenda('Clicando na tool: input <code>{"nome": "langwatch"}</code> e o JSON que a API devolveu. 54 ms — o gargalo não é a API.');
  await clicarSpan('llm', 0);
  await legenda('O span <code>llm</code> da normalização: modelo, mensagens enviadas (system com o glossário) e a pergunta reescrita.');
  await page.mouse.move(1150, 520); await page.mouse.wheel(0, 400); await esperar(1500);
  await legenda('Os atributos seguem a convenção OpenTelemetry GenAI: <code>gen_ai.input.messages</code>, <code>gen_ai.request.model</code>…');
  await page.keyboard.press('Escape'); await esperar(1000);

  // trace 2 (bug)
  await ir(`${LW}/${slug}/messages`);
  await esperar(2000); await pularTour();
  await page.getByText('qts rel. o lg já teve?').first().click();
  await esperar(3000); await aplicarOverlay();
  await legenda('Agora o trace com Fail.');
  await page.keyboard.press('t');
  await esperar(2000);
  await legenda('Diagnóstico pelo waterfall: dentro de <code>agente</code> há só um <code>model</code>. Não existe span de tool.');
  await clicarSpan('llm', 1);
  await legenda('O LLM respondeu direto, sem chamar <code>pypi_pacote</code>: como já havia consultado um pacote, achou que bastava.');
  await legenda('Isso só acontece no 2º turno da conversa (histórico no checkpointer). Sem os traces, seria difícil de achar.');
  await page.getByText('Conversation', { exact: true }).first().click().catch(() => {});
  await esperar(2500);
  await legenda('Aba Conversation: os dois turnos agrupados pelo <code>thread_id</code> que enviamos na metadata.');
  await page.keyboard.press('Escape'); await esperar(800);

  // correção
  await parte('Parte 2 · correção');
  await derrubarWeb();
  const patch = path.join(__dirname, 'correcao_prompt.diff');
  await ir(cenaCodigo('14_fix', patch, 'correção do system prompt do agente'));
  await foco('+    "- Cada pergunta', 2);
  await legenda('Correção no system prompt: cada pergunta é uma consulta nova; nunca dizer "não há informação" sem consultar.');
  execFileSync('git', ['-C', REPO, 'apply', patch]);
  subirWeb(); await esperarWeb();
  await ir(CHAT);
  await legenda('Patch aplicado e app reiniciado. Nova conversa, mesmas duas perguntas.');
  await perguntar('qual a últ. ver. do lw?');
  await perguntar('qts rel. o lg já teve?');
  await legenda('Agora veio o número de releases do langgraph, direto da API.');

  await esperarTraces(slug, 'qts rel. o lg já teve?', 2); await aplicarOverlay();
  await legenda('No LangWatch: os dois traces novos com <code>consultou_api</code> = Pass.');
  await page.getByText('qts rel. o lg já teve?').first().click();
  await esperar(3000);
  await page.keyboard.press('t');
  await esperar(2000); await aplicarOverlay();
  await legenda('E o waterfall do 2º turno agora tem <code>tools → pypi_pacote</code>. Bug confirmado e corrigido com dados.');
  await page.keyboard.press('Escape'); await esperar(800);
  await derrubarWeb();

  // ---------------- encerramento ----------------
  await parte('Resumo');
  await ir(cenaCard('20_resumo', 'Resumo', 'O que cada chamada faz', [
    'LangChain: <code>init_chat_model</code>, <code>ChatPromptTemplate</code>, LCEL <code>|</code>, <code>@tool</code>, <code>create_agent</code>, checkpointer',
    'LangWatch: <code>setup()</code>, <code>@trace</code>, <code>trace.update(metadata)</code>, <code>get_langchain_callback()</code>',
    '<code>langwatch.span()</code> para etapas manuais e <code>add_evaluation()</code> para métricas',
    'Fluxo de trabalho: avaliação falha → waterfall mostra a causa → corrige → avaliação passa',
  ]));
  await legenda('Código e README no repositório; o roteiro completo, com tempos, está em <code>gravacao/ROTEIRO.md</code>.', 6000);

  const duracao = agora();
  await ctx.close();
  await browser.close();
  const bruto = fs.readdirSync(TMP).find((f) => f.endsWith('.webm'));
  fs.renameSync(path.join(TMP, bruto), path.join(TMP, 'video.webm'));
  fs.writeFileSync(path.join(TMP, 'eventos.json'), JSON.stringify({ duracao, ...eventos }, null, 2));
  console.log('ok', duracao.toFixed(1), 's');
}

main().catch(async (e) => {
  console.error(e);
  try { await page.screenshot({ path: path.join(TMP, 'erro.png') }); } catch {}
  if (web) web.kill('SIGKILL');
  process.exit(1);
});
