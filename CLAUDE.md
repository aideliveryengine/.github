# CLAUDE.md

Repositório `.github` da organização AI Delivery Engine: perfil da organização
(`profile/`) e configuração do Claude para as sessões abertas aqui.

## Skills de Instagram (`/ig-*`)

Em `.claude/skills/` estão os 13 skills do pacote
[instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
(MIT): `/ig-reel`, `/ig-viral`, `/ig-caption`, `/ig-carousel`, `/ig-story`,
`/ig-profile`, `/ig-plan`, `/ig-human`, `/ig-comment`, `/ig-reply`, `/ig-dm`,
`/ig-repurpose`, `/ig-audit`. Documentação em `.claude/instagram/README.md`.

Regras para estes skills neste repositório:

- Onde os SKILL.md citam `~/.claude/instagram/` (voice.md, swipe.md, log.md,
  plan.md), use **`.claude/instagram/` deste repositório** no lugar — o home da
  sessão na nuvem é efêmero e esta pasta persiste no git.
- O perfil de voz do usuário é `.claude/instagram/voice.md`. Se ainda estiver
  em branco, ofereça preenchê-lo a partir de 3 reels ou legendas do usuário
  antes de escrever qualquer conteúdo.
- Os scripts Python dos skills rodam com `python3` sem dependências externas.
- Como os próprios skills exigem: nada é postado, logado ou automatizado no
  Instagram — todo resultado é um bloco para o usuário copiar e postar.
