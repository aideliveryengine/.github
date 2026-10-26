# Roteiro da aula: Python para quem é sênior em Node

Vídeo: `aula.mp4` (11:00). Legendas completas: `aula.srt`.


## Python para quem já é sênior em Node

- **00:00** Fala! Este é um atalho para quem já é sênior em Node e TypeScript e quer programar Python de verdade, para o dia a dia e para entrevistas.  
  _Na tela:_ Sem for e if: o foco é como se escreve Python em produção.
- **00:08** Em cada tópico eu mostro como você faria em TypeScript, do lado esquerdo, e o equivalente em Python, do lado direito. E principalmente: onde a analogia quebra.  
  _Na tela:_ TypeScript à esquerda, Python à direita, e onde a analogia quebra.
- **00:18** Todo o código do vídeo está no repositório e foi executado: o TypeScript passa no tsc em modo strict, e o Python passa no mypy em modo strict.  
  _Na tela:_ Código real: tsc --strict e mypy --strict passando.

## Ecossistema: o mapa de-para

- **00:26** Primeiro, o mapa. O nvm vira o uv ou o pyenv. O npm vira o uv, que é o gerenciador moderno, escrito em Rust e muito rápido. O package.json vira o pyproject.toml, e o lockfile vira o uv.lock.  
  _Na tela:_ Hoje o padrão é o uv: faz o papel de nvm + npm + npx.
- **00:41** A diferença conceitual mais importante: em Node, cada projeto tem o seu node_modules automaticamente. Em Python, por padrão, os pacotes vão para uma instalação global. Por isso existe o virtualenv: a pasta ponto venv é o seu node_modules.  
  _Na tela:_ Sem .venv você instala no Python global. O uv cria a venv sozinho.
- **00:54** O tsc vira o mypy ou o Pyright. O ESLint e o Prettier viram um único ruff. O jest vira o pytest. E o zod vira o Pydantic, que é praticamente onipresente em Python moderno.  
  _Na tela:_ ruff substitui eslint + prettier; pydantic está em todo lugar.
- **01:05** No back-end: Express ou Nest viram FastAPI ou Django. Prisma vira SQLAlchemy. E filas como o BullMQ viram Celery ou RQ.  
  _Na tela:_ API nova em empresa: FastAPI + Pydantic + SQLAlchemy é a stack mais comum.

## Projeto e dependências

- **01:13** O pyproject.toml é o package.json. Nome, versão e a versão mínima do Python, que é o engines do Node.  
  _Na tela:_ [project] ≈ nome, versão e engines.
- **01:20** As dependências ficam numa lista, com a versão na mesma string. Não existe acento circunflexo: você escreve maior ou igual.  
  _Na tela:_ "fastapi>=0.115": versão dentro da string.
- **01:28** As dev dependencies viram grupos de dependência. E a configuração das ferramentas, como ruff e mypy, fica no mesmo arquivo, nas seções tool. É como se o eslintrc e o tsconfig morassem dentro do package.json.  
  _Na tela:_ [tool.*]: config do ruff/mypy no mesmo arquivo.
- **01:40** Atenção a uma diferença: o project scripts do Python não é o npm run. Ele cria um executável de linha de comando, como o campo bin do package.json. Para tarefas, a gente usa uv run, ou um Makefile.  
  _Na tela:_ [project.scripts] ≈ campo bin, não npm run.

## Comandos do dia a dia

- **01:53** No dia a dia: uv init cria o projeto, uv add instala e já salva no pyproject, e uv add dash dash dev é o save dev.  
  _Na tela:_ uv add ≈ npm install (e já atualiza o lock).
- **02:01** O uv sync com frozen é o npm ci. O uv run roda qualquer coisa dentro da venv, sem você precisar ativar nada. E o uvx é o npx.  
  _Na tela:_ uv run dispensa o source .venv/bin/activate.

## Módulos e imports

- **02:10** Em Python, como em Node, o arquivo é o módulo. Mas não existe export: tudo que está no nível do módulo é importável.  
  _Na tela:_ Não existe export: tudo no módulo é público.
- **02:18** Privado é convenção: um underline na frente do nome. Ninguém impede o import, mas o linter e o time entendem que é interno. O dunder all só controla o import asterisco.  
  _Na tela:_ _nome = privado por convenção. __all__ só afeta import *.
- **02:27** Os imports são absolutos, a partir do pacote: from pedidos api ponto precos import com imposto. E repare no estilo: funções e variáveis em snake case, classes em PascalCase.  
  _Na tela:_ snake_case para funções/variáveis, PascalCase para classes.
- **02:38** E este é o idioma que você vai ver em todo lugar: if dunder name igual a dunder main. É o equivalente de checar se o arquivo foi executado direto, e não importado.  
  _Na tela:_ if __name__ == "__main__": ≈ "rodando direto?"

## Existe um "TypeScript do Python"?

- **02:47** A pergunta que você fez: existe um TypeScript do Python? Existe, e ele já vem na linguagem. São os type hints. Não tem compilação: você escreve as anotações no próprio Python.  
  _Na tela:_ Type hints: a sintaxe é nativa, nada de transpilar.
- **02:58** Quem confere os tipos é uma ferramenta separada. O mypy é o clássico, e o Pyright é o do VS Code. Rodar o mypy no CI é o equivalente ao tsc no emit.  
  _Na tela:_ mypy --strict no CI ≈ tsc --noEmit com strict.
- **03:08** E igual ao TypeScript: os tipos somem em runtime. Para validar o que vem de fora, como JSON e variáveis de ambiente, você usa o Pydantic, que é o zod do Python.  
  _Na tela:_ Tipo não valida em runtime. Dado externo → pydantic.

## Tipagem: interface, union, generics

- **03:18** A interface do TypeScript é estrutural. Em Python, o equivalente exato é o Protocol: qualquer classe que tenha o método buscar com essa assinatura satisfaz o contrato.  
  _Na tela:_ interface → Protocol (tipagem estrutural).
- **03:28** A union de strings vira Literal. E o alias type existe em Python desde a versão três ponto doze, com a mesma palavra-chave.  
  _Na tela:_ "a" | "b" → Literal["a", "b"]; T | None é igual.
- **03:35** O tipo de um objeto literal vira um TypedDict. Na prática, para dados de domínio, você vai preferir dataclass ou Pydantic, que eu mostro já já.  
  _Na tela:_ Objeto tipado → TypedDict (ou dataclass/pydantic).
- **03:44** Repare que a classe Python não declara implements. O mypy confere a estrutura na atribuição lá embaixo. E o self é explícito, sempre o primeiro parâmetro do método.  
  _Na tela:_ Sem implements; self é explícito.
- **03:53** Generics: a partir do três ponto doze, o parâmetro de tipo fica entre colchetes, logo depois do nome. Muito parecido com o TypeScript.  
  _Na tela:_ function f<T> → def f[T] (Python 3.12+).

## Validação em runtime: zod → pydantic

- **04:01** No zod, você escreve o schema e deriva o tipo com z infer. No Pydantic é o contrário: a classe já é o tipo e o schema ao mesmo tempo.  
  _Na tela:_ zod: schema → tipo. pydantic: a classe é os dois.
- **04:10** As restrições vêm do Field: maior que zero, tamanho mínimo. E o tipo UUID é convertido de verdade: depois da validação, o campo id é um objeto UUID, não uma string.  
  _Na tela:_ Field(gt=0, min_length=1); tipos são convertidos.
- **04:21** Model validate json é o parse. Ele já faz o parse do JSON e a validação numa passada só, em Rust, e é bem rápido.  
  _Na tela:_ model_validate_json ≈ Pedido.parse(JSON.parse(...)).
- **04:28** Não tem um safe parse que devolve sucesso ou erro: em Python, a falha é uma exceção, a ValidationError. Esse é o estilo da linguagem: é mais fácil pedir perdão do que permissão.  
  _Na tela:_ Sem safeParse: falha = exceção ValidationError.

## Classes e dados: dataclass

- **04:39** Para objetos de dados, o Python tem a dataclass. Você declara os campos com tipo, e o construtor, a igualdade e a representação são gerados. Frozen é o readonly, e slots economiza memória.  
  _Na tela:_ @dataclass gera __init__, __eq__ e __repr__.
- **04:51** No TypeScript você escreve um equals na mão, porque o igual igual igual compara referência. Na dataclass, o igual igual compara os valores dos campos.  
  _Na tela:_ == compara valor (via __eq__); is compara identidade.
- **05:00** Os métodos com dois underlines, os dunder methods, são o protocolo da linguagem. Dunder add define o operador mais, e dunder str é o toString. É assim que o Python deixa sua classe se comportar como um tipo nativo.  
  _Na tela:_ Dunder methods: __add__ = +, __str__ ≈ toString.
- **05:13** E para dinheiro, use Decimal. Ele está na biblioteca padrão, e evita o clássico zero ponto um mais zero ponto dois.  
  _Na tela:_ Dinheiro: Decimal("10.50"), sempre a partir de string.

## Funções: argumentos nomeados e a armadilha do default

- **05:20** Em Node, para parâmetros opcionais, a gente usa um options object com destructuring. Em Python, isso é nativo: tudo depois do asterisco só pode ser passado pelo nome.  
  _Na tela:_ Options object → argumentos keyword-only (depois do *).
- **05:30** O asterisco args é o rest parameter, e o dois asteriscos kwargs recebe argumentos nomeados soltos, como um objeto de opções livre. No spread de objeto, você usa dois asteriscos dentro do dicionário.  
  _Na tela:_ *args ≈ ...rest; {**base} ≈ {...base}.
- **05:42** E aqui está a pegadinha número um de entrevista. Em Python, o valor default é criado uma vez só, quando a função é definida. Se ele for uma lista, todas as chamadas compartilham a mesma lista.  
  _Na tela:_ ⚠️ Default mutável é criado uma vez e compartilhado.
- **05:53** No JavaScript, a segunda chamada devolve só b. No Python, devolve a e b. A correção é usar None como default e criar a lista dentro da função.  
  _Na tela:_ JS: ["b"]. Python: ['a', 'b']. Use None como default.

## Decorators: funções que embrulham funções

- **06:02** Em Node, para adicionar retry a uma função, você escreve uma higher order function. Em Python a ideia é exatamente a mesma: o decorator é só uma função que recebe uma função e devolve outra.  
  _Na tela:_ Decorator = higher-order function + açúcar @.
- **06:14** A diferença é o açúcar sintático. Arroba com retry em cima da função é a mesma coisa que buscar igual com retry de buscar. Foi exatamente isso que usamos no tutorial do LangWatch, com o arroba langwatch ponto trace.  
  _Na tela:_ @d def f ≡ f = d(f). (É o @langwatch.trace.)
- **06:26** Dois detalhes de sênior. Functools wraps preserva o nome e a docstring da função original. E o ParamSpec, os dois asteriscos P, preserva a assinatura para o type checker, como o tipo A extends unknown array do TypeScript.  
  _Na tela:_ functools.wraps + ParamSpec (**P) mantêm a assinatura.

## Iteração idiomática e truthiness

- **06:38** Filter mais map vira uma list comprehension. Object from entries vira uma dict comprehension. E sum com uma generator expression soma sem criar uma lista intermediária.  
  _Na tela:_ Comprehensions: [x for x in xs if cond], {k: v for ...}.
- **06:48** Generators funcionam como os do JavaScript: yield produz valores sob demanda, e yield from é o yield asterisco. O operador morsa, dois pontos igual, atribui e testa na mesma expressão.  
  _Na tela:_ yield from ≈ yield*; walrus := atribui e testa.
- **06:58** E cuidado com a truthiness: em JavaScript, array e objeto vazios são verdadeiros. Em Python, lista vazia, dicionário vazio, string vazia, zero e None são falsos. Por isso, em Python, o idioma é if not lista.  
  _Na tela:_ Em Python, [], {}, "", 0 e None são falsy.

## Erros e recursos: using → with

- **07:12** Exceções de domínio são classes que herdam de Exception. Em Python é muito comum criar uma hierarquia, porque o tratamento é feito pelo tipo.  
  _Na tela:_ Hierarquia de exceções: class X(ErroDominio).
- **07:20** O using do TypeScript cinco ponto dois é a mesma ideia do with do Python. O with garante que o recurso é fechado ao sair do bloco, mesmo com exceção. Conexão, arquivo, lock, transação: tudo usa with.  
  _Na tela:_ with ≈ using: fecha o recurso ao sair do bloco.
- **07:32** O jeito mais simples de criar um é o decorator contextmanager: tudo antes do yield é a abertura, e o finally é o dispose.  
  _Na tela:_ @contextmanager: antes do yield abre, finally fecha.
- **07:39** O except filtra pelo tipo, sem instanceof. Raise from encadeia a causa, como o cause do Error. E tem o else, que só roda se não houve exceção.  
  _Na tela:_ except Tipo as e, raise ... from e e o bloco else.

## Async: Promise ansiosa × coroutine preguiçosa

- **07:48** Async e await são quase iguais. Mas tem uma diferença fundamental, que cai muito em entrevista.  
  _Na tela:_ async/await: a sintaxe é quase igual…
- **07:54** Em JavaScript, a Promise é ansiosa: chamou a função, ela já está rodando. Em Python, chamar uma função async só cria um objeto coroutine. Nada roda até alguém dar await, ou criar uma task.  
  _Na tela:_ …mas Promise é ansiosa e coroutine é preguiçosa.
- **08:05** O Promise all vira o asyncio gather, ou, melhor ainda, o TaskGroup. Ele roda em paralelo e, se uma task falhar, cancela as outras. É concorrência estruturada.  
  _Na tela:_ Promise.all → TaskGroup (cancela as irmãs) ou gather.
- **08:15** Para timeout, em vez de uma corrida com um timer, existe o asyncio timeout, como context manager.  
  _Na tela:_ Timeout: async with asyncio.timeout(s).
- **08:21** E no Node o event loop já existe. Em Python, você liga o loop com asyncio run. Cuidado: uma chamada bloqueante, como time sleep ou a biblioteca requests, trava o loop inteiro. Use as versões async, como o httpx.  
  _Na tela:_ Você liga o loop: asyncio.run. Nada de I/O bloqueante dentro dele.

## Concorrência e o GIL

- **08:34** O CPython tem o GIL, um lock global: só uma thread executa bytecode Python por vez. É parecido com o Node ser single thread para o seu código.  
  _Na tela:_ GIL: uma thread executa Python por vez (≈ JS single-thread).
- **08:43** Mas o GIL é liberado durante o I/O. Então threads funcionam bem para chamadas bloqueantes de rede e disco, por exemplo com bibliotecas síncronas.  
  _Na tela:_ Threads servem para I/O bloqueante (o GIL é solto no I/O).
- **08:51** Para CPU pesada, threads não escalam. A saída são processos, com o ProcessPoolExecutor, que é o seu worker threads ou cluster. O Python três ponto treze tem uma versão experimental sem GIL, mas em produção ainda vale a regra.  
  _Na tela:_ CPU pesada → processos (≈ worker_threads/cluster).

## Testes: jest/node:test → pytest

- **09:04** No pytest, o setup é feito com fixtures. Em vez de um beforeEach que preenche uma variável, a fixture é injetada pelo nome do parâmetro do teste. É injeção de dependência.  
  _Na tela:_ beforeEach → @pytest.fixture, injetada pelo nome.
- **09:15** O test each vira o parametrize. E repare que é só assert, puro. O pytest reescreve o assert para mostrar os valores quando falha, então você não precisa de expect.  
  _Na tela:_ test.each → parametrize; assert puro, sem expect.
- **09:24** Mock: a fixture monkeypatch troca um atributo e desfaz no fim do teste. Para mocks mais completos, existe o unittest mock, com patch.  
  _Na tela:_ monkeypatch (desfeito no fim) ou unittest.mock.patch.
- **09:32** E para testar exceção, pytest raises como context manager. De novo o with.  
  _Na tela:_ with pytest.raises(ValueError, match=...).

## API: Express + zod → FastAPI

- **09:37** No FastAPI, o Pydantic é o contrato da API. O mesmo modelo valida o body e gera a documentação OpenAPI automaticamente.  
  _Na tela:_ Model Pydantic = validação + OpenAPI (Swagger em /docs).
- **09:46** A rota é declarada com decorator. O parâmetro tipado com o modelo vira o body validado: se for inválido, o FastAPI já responde quatrocentos e vinte e dois. E o tipo de retorno vira o schema da resposta.  
  _Na tela:_ Body inválido → 422 automático; o tipo de retorno vira o schema.
- **09:57** E o Depends é a injeção de dependência do FastAPI, parecida com a do Nest. Nos testes, você troca a dependência com dependency overrides, sem mock global.  
  _Na tela:_ Depends ≈ DI do Nest; nos testes: dependency_overrides.

## Pegadinhas de entrevista

- **10:07** Para fechar, as pegadinhas que mais pegam quem vem do JavaScript. A primeira, você já viu: o default mutável.  
  _Na tela:_ Default mutável: use None.
- **10:14** O operador is compara identidade, e o igual igual compara valor. O is não é o triplo igual: use is só para None, e igual igual para o resto.  
  _Na tela:_ x is None; para valores, ==.
- **10:23** Coleções vazias são falsas, a barra sempre devolve float, e a barra dupla é a divisão inteira.  
  _Na tela:_ 7 / 2 == 3.5; 7 // 2 == 3.
- **10:29** Coroutine sem await não roda, e o GIL define threads para I/O e processos para CPU. Por fim: lista é mutável e tupla não, e chave de dicionário precisa ser imutável.  
  _Na tela:_ Tupla é imutável e pode ser chave de dict; lista não.

## Próximos passos

- **10:39** Próximos passos: rode o script verificar, que executa todas as lições, e altere o código para ver o que quebra.  
  _Na tela:_ ./verificar.sh: roda e checa tudo.
- **10:46** Depois, monte um projeto pequeno com FastAPI, Pydantic, SQLAlchemy e pytest, gerenciado com uv, e com ruff e mypy strict no CI desde o primeiro commit. É o que você vai encontrar nas empresas. Bons estudos!  
  _Na tela:_ FastAPI + Pydantic + SQLAlchemy + pytest, com uv, ruff e mypy.
