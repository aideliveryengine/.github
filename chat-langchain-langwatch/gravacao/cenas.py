"""Gera as páginas HTML usadas como "cenas" no vídeo (código, diff, cartões).

    python gravacao/cenas.py codigo <arquivo> <saida.html> [titulo]
    python gravacao/cenas.py diff   <arquivo.diff> <saida.html> [titulo]
    python gravacao/cenas.py card   <saida.html> <titulo> <subtitulo> [item ...]

As linhas de código ganham id="L<n>" para o roteiro (gravar.js) destacar e rolar até elas.
"""

import html
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import DiffLexer, TextLexer, get_lexer_for_filename

ESTILO = HtmlFormatter(style="one-dark").get_style_defs(".hl-code")

CSS = """
html,body{margin:0;background:#1e2127;color:#abb2bf;font-family:'JetBrains Mono','DejaVu Sans Mono',monospace}
header{position:sticky;top:0;z-index:5;background:#16181d;border-bottom:1px solid #2c313a;padding:14px 28px;
  font:600 18px 'JetBrains Mono',monospace;color:#e5c07b}
.cod{padding:16px 0 220px 0;font-size:19px;line-height:1.55}
.linha{display:flex;white-space:pre;padding-right:28px;border-left:4px solid transparent;transition:background .3s}
.linha .ln{width:58px;text-align:right;padding-right:18px;color:#4b5263;user-select:none;flex:none}
.linha.foco{background:#2f4566;border-left-color:#61afef}
.cod.focando .linha:not(.foco){opacity:.45}
.card{height:100vh;display:flex;flex-direction:column;justify-content:center;padding:0 110px;box-sizing:border-box;
  font-family:system-ui,'DejaVu Sans',sans-serif;background:radial-gradient(circle at 20% 20%,#2a3550,#15171c 70%)}
.card h1{font-size:54px;color:#fff;margin:0 0 14px}
.card h2{font-size:26px;color:#61afef;font-weight:500;margin:0 0 36px}
.card li{font-size:25px;color:#d7dae0;margin:12px 0}
.card code{font-family:'JetBrains Mono',monospace;color:#e5c07b}
"""


def _pagina(titulo: str, corpo: str) -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(titulo)}</title>"
            f"<style>{CSS}{ESTILO}</style></head><body>{corpo}</body></html>")


def _linhas(fonte: str, lexer) -> str:
    # nowrap=True devolve só os <span> coloridos; quebramos por linha para numerar.
    colorido = highlight(fonte, lexer, HtmlFormatter(nowrap=True, style="one-dark"))
    partes = colorido.rstrip("\n").split("\n")
    return "".join(
        f"<div class='linha' id='L{i}'><span class='ln'>{i}</span><span>{p or ' '}</span></div>"
        for i, p in enumerate(partes, 1)
    )


def codigo(arquivo: str, saida: str, titulo: str | None = None, lexer=None) -> None:
    fonte = Path(arquivo).read_text(encoding="utf-8")
    if lexer is None:
        try:
            lexer = get_lexer_for_filename(arquivo)
        except Exception:
            lexer = TextLexer()
    corpo = f"<header>{html.escape(titulo or arquivo)}</header><div class='cod hl-code'>{_linhas(fonte, lexer)}</div>"
    Path(saida).write_text(_pagina(titulo or arquivo, corpo), encoding="utf-8")


def card(saida: str, titulo: str, subtitulo: str, itens: list[str]) -> None:
    lis = "".join(f"<li>{i}</li>" for i in itens)  # itens aceitam HTML (ex.: <code>)
    corpo = f"<div class='card'><h1>{titulo}</h1><h2>{subtitulo}</h2><ul>{lis}</ul></div>"
    Path(saida).write_text(_pagina(titulo, corpo), encoding="utf-8")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    if cmd == "codigo":
        codigo(args[0], args[1], args[2] if len(args) > 2 else None)
    elif cmd == "diff":
        codigo(args[0], args[1], args[2] if len(args) > 2 else None, lexer=DiffLexer())
    elif cmd == "card":
        card(args[0], args[1], args[2], args[3:])
