"""Gera a aula em vídeo a partir do roteiro.py.

    VOZ_DIR=.../vits-piper-pt_BR-faber-medium python video/gerar.py

Pipeline (determinístico, sem gravação em tempo real):
1. TTS de cada fala (Piper pt_BR "faber" via sherpa-onnx<2) → duração de cada passo.
2. Uma página HTML por cena; o Playwright aplica o estado de cada passo e tira um print.
3. ffmpeg: cada print fica na tela exatamente o tempo da sua fala; a trilha de áudio
   é a concatenação das falas. Áudio e imagem ficam sincronizados por construção.
Saídas em video/: aula.mp4, aula.srt e ROTEIRO.md.
"""

import html
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename, TextLexer

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
TMP = AQUI / "tmp"
sys.path.insert(0, str(AQUI))
from roteiro import CENAS  # noqa: E402

W, H = 1920, 1080
PAUSA = 0.7         # silêncio depois de cada fala (s)
PAUSA_CENA = 0.6    # silêncio extra no começo de cada cena (s)
VOZ = Path(os.getenv("VOZ_DIR", "tts/vits-piper-pt_BR-faber-medium"))

# Grafia "falada" para a voz pt_BR, escolhida transcrevendo o áudio de volta com Whisper.
PRONUNCIA = {
    "TypeScript": "Taipe Script", "Python": "Páifon", "mypy": "mai-pai", "Pyright": "Pai-raite",
    "Pydantic": "Pai-dêntic", "runtime": "rântaime", "zod": "zód", "pytest": "pai-teste",
    "GIL": "guil", "threads": "tréds", "thread": "tréd", "await": "auêit", "Promise": "prómis",
    "kwargs": "quêi-uórgs", "uv": "iú-vi", "npm": "éne-pê-ême", "nvm": "éne-vê-ême",
    "LangWatch": "Lang-uótch", "JSON": "djêison", "UUID": "iú-iú-ai-di",
    "timeout": "táimaut", "timer": "táimer", "asyncio": "ei-sínquio", "ruff": "râfi",
}


# ---------------------------------------------------------------- áudio

def sintetizar(falas: list[str]) -> tuple[list[np.ndarray], int]:
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=str(VOZ / "pt_BR-faber-medium.onnx"), tokens=str(VOZ / "tokens.txt"),
            data_dir=str(VOZ / "espeak-ng-data")),
        num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    audios, taxa = [], 22050
    for fala in falas:
        for nome, falado in PRONUNCIA.items():
            fala = re.sub(rf"\b{re.escape(nome)}\b", falado, fala)
        a = tts.generate(fala, sid=0, speed=1.0)
        taxa = a.sample_rate
        audios.append(np.array(a.samples, dtype=np.float32))
    return audios, taxa


# ---------------------------------------------------------------- HTML

CSS = """
*{box-sizing:border-box;font-variant-ligatures:none;font-feature-settings:"liga" 0,"calt" 0}
html,body{margin:0;width:%(W)dpx;height:%(H)dpx;overflow:hidden;background:#15171c;color:#d7dae0;
  font-family:system-ui,'DejaVu Sans',sans-serif}
.topo{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 32px;
  background:#0f1115;border-bottom:1px solid #2c313a}
.topo h1{font-size:28px;margin:0;color:#fff;font-weight:650}
.topo .n{font:600 18px system-ui;color:#61afef}
.panes{display:flex;height:calc(100%% - 64px - 132px)}
.pane{flex:1;display:flex;flex-direction:column;min-width:0;border-right:1px solid #2c313a}
.pane:last-child{border-right:0}
.rot{height:42px;display:flex;align-items:center;gap:12px;padding:0 20px;font:600 17px 'JetBrains Mono',monospace;
  background:#1b1e24;border-bottom:1px solid #2c313a}
.rot .tag{padding:3px 10px;border-radius:6px;font:700 14px system-ui;color:#0d1117}
.rot.ts .tag{background:#3178c6;color:#fff} .rot.py .tag{background:#ffd43b}
.rot.uni .tag{background:#98c379}
.cod{flex:1;overflow:hidden;padding:14px 0 40px;background:#1e2127;line-height:1.5;
  font-family:'JetBrains Mono','DejaVu Sans Mono',monospace}
.linha{display:flex;white-space:pre;border-left:5px solid transparent;transition:none}
.linha .ln{width:52px;flex:none;text-align:right;padding-right:16px;color:#4b5263}
.linha.foco{background:#2f4566;border-left-color:#61afef}
.cod.focando .linha:not(.foco){opacity:.38}
.leg{position:absolute;left:0;right:0;bottom:0;height:132px;display:flex;align-items:center;justify-content:center;
  padding:0 60px;background:#0f1115;border-top:1px solid #2c313a;font-size:31px;line-height:1.35;text-align:center;color:#fff}
.leg code,.card code,td code{font-family:'JetBrains Mono',monospace;color:#e5c07b;font-size:.92em}
.card{height:calc(100%% - 64px - 132px);display:flex;flex-direction:column;justify-content:center;padding:0 140px;
  background:radial-gradient(circle at 20%% 20%%,#2a3550,#15171c 70%%)}
.card h2{font-size:62px;color:#fff;margin:0 0 14px}
.card h3{font-size:30px;color:#61afef;font-weight:500;margin:0 0 40px}
.card li{font-size:30px;margin:14px 0;color:#d7dae0}
table{margin:28px auto;border-collapse:collapse;font-size:27px;width:1300px}
th{font-size:22px;text-transform:uppercase;letter-spacing:.06em;padding:10px 24px;text-align:left}
th.ts{color:#6ea8ff} th.py{color:#ffd43b}
td{padding:8px 24px;border-bottom:1px solid #2c313a;font-family:'JetBrains Mono',monospace}
tr.apaga td{opacity:.3} tr.foco td{background:#23324a}
""" % {"W": W, "H": H}

JS = """
window.estado = (p) => {
  document.getElementById('leg').firstChild.innerHTML = p.legenda;
  for (const [lado, alvo] of Object.entries(p.focos || {})) {
    const cod = document.getElementById('cod-' + lado);
    if (!cod) continue;
    const linhas = [...cod.querySelectorAll('.linha')];
    linhas.forEach((l) => l.classList.remove('foco'));
    if (!alvo) { cod.classList.remove('focando'); continue; }
    const [trecho, n] = alvo;
    const i = linhas.findIndex((l) => l.querySelector('.txt').textContent.includes(trecho));
    if (i < 0) throw new Error(lado + ': trecho não encontrado: ' + trecho);
    for (let k = i; k < i + n; k++) linhas[k].classList.add('foco');
    cod.classList.add('focando');
    // Rola só se o trecho não couber: deixa-o a ~20% do topo.
    // Rola o mínimo para o trecho caber com 3 linhas de folga embaixo,
    // alinhado em linha inteira (o +padding evita meia linha no topo).
    const h = linhas[0].offsetHeight, pad = linhas[0].offsetTop - cod.offsetTop;
    const cabem = Math.floor((cod.clientHeight - pad) / h);
    const ultima = Math.min(i + n, linhas.length) - 1;
    const topo = Math.max(0, Math.min(i - 1, ultima + 3 - cabem + 1));
    cod.scrollTop = topo === 0 ? 0 : topo * h + pad;
  }
  if (p.linhas) document.querySelectorAll('tbody tr').forEach((tr, k) => {
    tr.className = p.linhas.includes(k) ? 'foco' : 'apaga';
  });
};
"""


def _codigo(arquivo: Path, id_: str, largura: int) -> str:
    fonte = arquivo.read_text(encoding="utf-8")
    try:
        lexer = get_lexer_for_filename(arquivo.name)
    except Exception:
        lexer = TextLexer()
    colorido = highlight(fonte, lexer, HtmlFormatter(nowrap=True, style="one-dark")).rstrip("\n").split("\n")
    maior = max(len(l) for l in fonte.splitlines())
    # JetBrains Mono: cada caractere tem 0.6em. Fonte que faça a linha mais longa caber.
    fonte_px = min(21.0, (largura - 52 - 16 - 30) / (maior * 0.6))
    linhas = "".join(
        f"<div class='linha'><span class='ln'>{i}</span><span class='txt'>{p or ' '}</span></div>"
        for i, p in enumerate(colorido, 1))
    return f"<div class='cod' id='cod-{id_}' style='font-size:{fonte_px:.1f}px'>{linhas}</div>"


def pagina(cena: dict, n: int, total: int) -> str:
    estilo = HtmlFormatter(style="one-dark").get_style_defs(".cod")
    topo = f"<div class='topo'><h1>{cena['titulo']}</h1><span class='n'>{n}/{total}</span></div>"
    t = cena["tipo"]
    if t == "card":
        corpo = (f"<div class='card'><h2>{cena['titulo']}</h2><h3>{cena['subtitulo']}</h3><ul>"
                 + "".join(f"<li>{i}</li>" for i in cena["itens"]) + "</ul></div>")
        topo = f"<div class='topo'><h1>&nbsp;</h1><span class='n'>{n}/{total}</span></div>"
    elif t == "tabela":
        linhas = "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>" for a, b in cena["linhas"])
        corpo = (f"<div class='card' style='padding:0'><table><thead><tr><th class='ts'>Node / TypeScript</th>"
                 f"<th class='py'>Python</th></tr></thead><tbody>{linhas}</tbody></table></div>")
    elif t == "lado":
        ts, py = RAIZ / cena["ts"], RAIZ / cena["py"]
        rot_ts, rot_py = cena.get("rot_ts", ts.name), cena.get("rot_py", py.name)
        corpo = ("<div class='panes'>"
                 f"<div class='pane'><div class='rot ts'><span class='tag'>TypeScript</span>{rot_ts}</div>"
                 f"{_codigo(ts, 'ts', W // 2)}</div>"
                 f"<div class='pane'><div class='rot py'><span class='tag'>Python</span>{rot_py}</div>"
                 f"{_codigo(py, 'py', W // 2)}</div></div>")
    elif t == "unico":
        arq = RAIZ / cena["arq"]
        corpo = (f"<div class='panes'><div class='pane'><div class='rot uni'><span class='tag'>terminal</span>"
                 f"{cena['rot']}</div>{_codigo(arq, 'uni', W)}</div></div>")
    else:
        raise ValueError(t)
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}{estilo}</style>"
            f"<script>{JS}</script></head><body>{topo}{corpo}<div class='leg' id='leg'><span></span></div></body></html>")


def estado_do_passo(cena: dict, passo: dict) -> dict:
    t = cena["tipo"]
    e: dict = {"legenda": passo["legenda"]}
    if t == "lado":
        e["focos"] = {"ts": passo.get("ts"), "py": passo.get("py")}
    elif t == "unico":
        e["focos"] = {"uni": passo.get("foco")}
    elif t == "tabela":
        e["linhas"] = passo.get("foco", [])
    return e


# ---------------------------------------------------------------- main

def texto_puro(t: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def ts(s: float, srt: bool = False) -> str:
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(m):02d}:{int(s):02d}"


def main() -> None:
    TMP.mkdir(exist_ok=True)
    passos = [(ci, cena, p) for ci, cena in enumerate(CENAS) for p in cena["passos"]]

    # 1. telas
    for ci, cena in enumerate(CENAS, 1):
        (TMP / f"cena{ci:02d}.html").write_text(pagina(cena, ci, len(CENAS)), encoding="utf-8")
    plano = [{"html": str(TMP / f"cena{ci + 1:02d}.html"), "estado": estado_do_passo(cena, p),
              "png": str(TMP / f"p{k:03d}.png")} for k, (ci, cena, p) in enumerate(passos)]
    (TMP / "plano.json").write_text(json.dumps(plano, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["node", str(AQUI / "prints.cjs"), str(TMP / "plano.json"), str(W), str(H)], check=True)

    # 2. áudio
    audios, taxa = sintetizar([p["fala"] for _, _, p in passos])
    duracoes, trilha, t = [], [], 0.0
    legendas = []
    for k, ((ci, cena, p), audio) in enumerate(zip(passos, audios)):
        novo = k == 0 or passos[k - 1][0] != ci
        antes = PAUSA_CENA if novo else 0.0
        dur = antes + len(audio) / taxa + PAUSA
        trilha += [np.zeros(int(antes * taxa), np.float32), audio,
                   np.zeros(int(round(dur * taxa)) - int(antes * taxa) - len(audio), np.float32)]
        legendas.append({"ini": t, "fim": t + dur, "fala": p["fala"], "legenda": p["legenda"],
                         "cena": cena["titulo"], "novo": novo})
        duracoes.append(dur)
        t += dur
    pcm = np.concatenate(trilha)
    pcm = np.clip(pcm / max(1e-6, np.abs(pcm).max()) * 0.9, -1, 1)
    wav = TMP / "narracao.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes((pcm * 32767).astype(np.int16).tobytes())

    # 3. vídeo: cada print pelo tempo exato da sua fala
    lista = TMP / "imagens.txt"
    corpo = "".join(f"file '{pl['png']}'\nduration {d:.3f}\n" for pl, d in zip(plano, duracoes))
    lista.write_text(corpo + f"file '{plano[-1]['png']}'\n")  # o último quadro precisa repetir
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-i", str(wav),
        "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
        str(AQUI / "aula.mp4")], check=True)

    srt = "\n".join(f"{i}\n{ts(l['ini'], True)} --> {ts(l['fim'], True)}\n{l['fala']}\n"
                    for i, l in enumerate(legendas, 1))
    (AQUI / "aula.srt").write_text(srt, encoding="utf-8")
    md = ["# Roteiro da aula: Python para quem é sênior em Node", "",
          f"Vídeo: `aula.mp4` ({ts(t)}). Legendas completas: `aula.srt`.", ""]
    for l in legendas:
        if l["novo"]:
            md += ["", f"## {texto_puro(l['cena'])}", ""]
        md.append(f"- **{ts(l['ini'])}** {l['fala']}  \n  _Na tela:_ {texto_puro(l['legenda'])}")
    (AQUI / "ROTEIRO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"ok: {t:.0f}s, {len(passos)} passos")


if __name__ == "__main__":
    main()
