# Instagram agent skills

13 skills do Claude para gerenciar conteúdo de Instagram, instalados em
`.claude/skills/` deste repositório. Eles ficam disponíveis automaticamente em
qualquer sessão do Claude Code aberta neste repositório.

**Origem:** [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
(MIT, cópia da licença em `LICENSE` nesta pasta). Vendorizado em 2026-10-30 a
partir do commit `d03c56b`. Para atualizar, clone o repositório de origem e
copie `skills/ig-*` por cima de `.claude/skills/`.

## Os 13 comandos

| comando | o que faz |
| --- | --- |
| `/ig-reel` | Transforma uma ideia em Reel: 3 hooks a partir de 26 fórmulas, pontuados, + roteiro, texto na tela e beat sheet cronometrado |
| `/ig-viral` | Pesquisa o que está funcionando no seu nicho, ranqueado pelo múltiplo sobre a mediana de cada conta, e monta o swipe file |
| `/ig-caption` | Escreve e linta a legenda, mostrando os ~125 caracteres visíveis antes do "... mais" |
| `/ig-carousel` | Carrossel: capa que ganha o swipe, copy slide a slide, arquivos 1080x1350 |
| `/ig-story` | Sequência diária de stories, qual sticker usar onde, e o funil de DM |
| `/ig-profile` | Pontua o perfil contra uma rubrica de 100 pontos e reescreve o que perdeu ponto |
| `/ig-plan` | Planeja a semana: o que postar, formato, quando, e quem engajar |
| `/ig-human` | O humanizador: remove em dashes, vocabulário de IA e caracteres invisíveis, depois pontua em 5 checagens |
| `/ig-comment` | Comentários em posts de outras pessoas, 9 tipos, nunca "🔥🔥🔥" |
| `/ig-reply` | Triagem e resposta dos comentários nos seus próprios posts |
| `/ig-dm` | DMs: entrega de keyword, primeira mensagem, pitch de collab e os 2 follow-ups |
| `/ig-repurpose` | Um vídeo/podcast/newsletter vira uma semana de reels e carrosséis |
| `/ig-audit` | Post-mortem do que você já postou, ranqueado por múltiplo outlier e sends por alcance |

## O que estes skills NÃO fazem (por design)

- **Nada é postado automaticamente.** Todo skill termina com um bloco pronto
  para copiar; você posta.
- **Nenhum login, senha ou API key.** Nada de automação que viole os Termos de
  Uso do Instagram.
- **Os scripts Python rodam 100% localmente**, sem rede e sem dependências
  (apenas a biblioteca padrão do Python 3).
- **Nada é inventado**: se falta um número seu, o rascunho volta com
  `{{your number}}` e um aviso.

## Primeiro passo: preencha o `voice.md`

Edite [`voice.md`](voice.md) nesta pasta (10 minutos) — ou mande 3 reels ou
legendas suas para o Claude e peça "escreva meu voice.md a partir destes".
Todos os skills leem esse arquivo para escrever na SUA voz.

## Arquivos de estado (sessões na nuvem)

Os SKILL.md originais citam `~/.claude/instagram/` como pasta de estado. Em
sessões na nuvem o home é efêmero, então aqui usamos **esta pasta do
repositório** (`.claude/instagram/`) para `voice.md`, `swipe.md`, `log.md` e
`plan.md` — commitados, eles persistem entre sessões. O `CLAUDE.md` na raiz
instrui as sessões a fazer isso.
