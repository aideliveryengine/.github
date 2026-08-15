# AI Delivery Engine

**Esteira de entrega de software operada por agentes, com gates humanos.**

Escrever código deixou de ser o gargalo. O que continua caro é tudo em volta:
transformar uma demanda crua em algo que dá para construir, provar que o que
foi construído funciona, e levar isso até a entrega sem perder o rastro.

O AIDE ataca esse trecho. Uma demanda entra crua e sai como card entregue —
destrinchada, refinada, desenvolvida, testada, revisada — com agentes
executando as etapas e uma pessoa decidindo nos pontos que importam.

## Como pensamos

**Markdown-first.** O estado do trabalho são arquivos em pastas, não linhas
num banco. A pasta é a coluna do kanban, o arquivo é o card. Legível por
humano, versionado por git, revisável em diff, sem lock-in.

**Gate humano onde é irreversível.** Agente propõe, pessoa aprova. Push, merge
e qualquer coisa que cruza o perímetro passam por um juiz que é fail-closed:
na dúvida, bloqueia.

**Estado vazio honesto.** O que não tem fonte mostra "—", nunca um número
inventado. Não existe mock dentro do sistema — só na fronteira, como artefato
de mesma assinatura trocado por configuração.

**Nada de credencial no repo.** Chave vem de variável de ambiente, sempre. Há
teste que falha se dado de cliente, e-mail corporativo ou caminho de máquina
entrar no versionamento.

## Repositórios

| Repo | O que é |
|---|---|
| [`aide`](https://github.com/aideliveryengine/aide) | A esteira: board, skills, kernel de contratos, cockpit e runner |

---

<sub>Contribuições seguem o `CONTRIBUTING.md` de cada repositório.</sub>
