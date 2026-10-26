# Python para quem já é sênior em Node

Aula em vídeo (11 min, narrada) + código lado a lado: cada conceito como você faz em
**TypeScript** e o equivalente em **Python**, no nível pleno→sênior (projeto, tipos,
dados, async, concorrência, testes, API) e com as pegadinhas de entrevista.

- 🎬 `video/aula.mp4` (1080p, narração pt-BR, legendas na tela)
- 📝 `video/ROTEIRO.md`: tudo o que é dito, com timestamps · `video/aula.srt`: legendas
- 💻 `licoes/ts/` e `licoes/py/`: o código mostrado no vídeo, executável

## "Existe um TypeScript do Python?"

Sim: **type hints** são sintaxe nativa do Python (PEP 484, generics da PEP 695 no 3.12+).
O que muda é que o checker é uma ferramenta à parte: `mypy` ou `pyright` (≈ `tsc --noEmit`).
Como no TS, tipos não validam nada em runtime. Para dados externos use `pydantic` (≈ `zod`).

## Cola rápida

| Node / TypeScript | Python |
| --- | --- |
| `nvm`, `npm`, `npx` | `uv` (`uv python install`, `uv add`, `uvx`) |
| `package.json` / lock | `pyproject.toml` / `uv.lock` |
| `node_modules/` | `.venv/` (virtualenv) |
| `tsc --noEmit` | `mypy --strict` / `pyright` |
| eslint + prettier | `ruff` |
| `interface` | `Protocol` (estrutural) |
| `"a" \| "b"` | `Literal["a", "b"]` |
| `function f<T>()` | `def f[T]()` (3.12+) |
| zod schema → `z.infer` | classe `pydantic.BaseModel` (é tipo e schema) |
| classe value object | `@dataclass(frozen=True, slots=True)` |
| options object `{ a = 1 }` | keyword-only: `def f(*, a=1)` |
| `...rest` / `{...obj}` | `*args` / `{**obj}` |
| higher-order function | decorator `@` (+ `functools.wraps`, `ParamSpec`) |
| `filter().map()` | `[x for x in xs if cond]` |
| `using` (TS 5.2) | `with` / `@contextmanager` |
| `new Error(m, { cause })` | `raise X(m) from e` |
| Promise (ansiosa) | coroutine (preguiçosa: só roda com `await`/task) |
| `Promise.all` | `asyncio.TaskGroup` / `gather` |
| `worker_threads` / cluster | `ProcessPoolExecutor` (GIL) |
| jest/vitest, `beforeEach`, `test.each` | pytest, `@fixture`, `@parametrize` |
| Express/Nest + zod | FastAPI + Pydantic (`Depends` ≈ DI do Nest) |

## Lições

| # | TypeScript | Python | Assunto |
| --- | --- | --- | --- |
| 1 | `projeto/package.json` | `projeto/pyproject.toml` | projeto, dependências, comandos (`projeto/comandos.txt`) |
| 2 | `02_modulos.ts` | `m02_modulos.py` | módulos, privado por convenção, `__name__ == "__main__"` |
| 3 | `03_tipos.ts` | `m03_tipos.py` | `Protocol`, `Literal`, `TypedDict`, generics |
| 4 | `04_validacao.ts` | `m04_validacao.py` | zod → pydantic |
| 5 | `05_classes.ts` | `m05_classes.py` | dataclass, dunder methods, `Decimal` |
| 6 | `06_funcoes.ts` | `m06_funcoes.py` | keyword-only, `*args/**kwargs`, default mutável |
| 7 | `07_decorators.ts` | `m07_decorators.py` | decorators tipados (`ParamSpec`) |
| 8 | `08_iteracao.ts` | `m08_iteracao.py` | comprehensions, generators, truthiness |
| 9 | `09_erros.ts` | `m09_erros.py` | exceções, `with`, `raise from`, `else` |
| 10 | `10_async.ts` | `m10_async.py` | coroutine preguiçosa, `TaskGroup`, `timeout` |
| 11 | `11_concorrencia.ts` | `m11_concorrencia.py` | GIL: threads para I/O, processos para CPU |
| 12 | `12_testes.test.ts` | `test_m12_testes.py` | pytest: fixtures, parametrize, monkeypatch |
| 13 | `13_api.ts` | `m13_api.py` | Express + zod → FastAPI |

Os arquivos Python começam com `m` porque nome de módulo não pode começar com dígito.

## Rodar e conferir

```bash
npm install
uv venv && uv pip install mypy pydantic pytest fastapi httpx   # ou pip
PY=.venv/bin/python ./verificar.sh
```

`verificar.sh` compila o TS com `tsc` (strict) e roda cada lição, roda `node --test`,
passa o Python no `mypy --strict`, roda cada lição e o `pytest`, e chama as duas APIs
(esperado: `201 422` nos dois lados). Testado com Node 22, TypeScript 5.9, Python 3.13 e mypy 2.4.

## Como o vídeo é gerado

`video/roteiro.py` tem as cenas e, para cada passo, a fala, a legenda da tela e as linhas
a destacar em cada coluna. `video/gerar.py`:

1. sintetiza cada fala com uma voz neural pt-BR local (Piper "faber" via `sherpa-onnx<2`);
2. monta uma página HTML por cena e o Playwright tira um print por passo (`video/prints.cjs`);
3. o ffmpeg deixa cada print na tela exatamente pelo tempo da sua fala, então áudio e imagem
   ficam sincronizados por construção.

```bash
pip install "sherpa-onnx<2" numpy pygments
curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2 | tar xj
VOZ_DIR=vits-piper-pt_BR-faber-medium python video/gerar.py
```

Os termos em inglês têm uma grafia "falada" em `gerar.py` (`TypeScript` → "Taipe Script",
`Python` → "Páifon"), escolhida transcrevendo o áudio de volta com Whisper. Ainda assim,
saem com sotaque brasileiro.
