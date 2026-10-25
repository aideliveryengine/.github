"""Monta o vídeo final a partir da gravação bruta.

    python gravacao/montar.py

Lê tmp/video.webm + tmp/eventos.json (gerados pelo gravar.js) e produz:
- tutorial.mp4   trechos de espera do LLM acelerados, H.264
- tutorial.srt   legendas com os tempos do vídeo final
- ROTEIRO.md     o texto explicativo, por parte, com timestamps
"""

import html
import json
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TMP = AQUI / "tmp"


def segmentos(duracao: float, aceleradas: list[dict]) -> list[tuple[float, float, float]]:
    """Divide [0, duracao] em (ini, fim, fator), com fator 1 fora dos trechos acelerados."""
    segs, cursor = [], 0.0
    for a in sorted(aceleradas, key=lambda a: a["ini"]):
        if a["ini"] > cursor:
            segs.append((cursor, a["ini"], 1.0))
        segs.append((a["ini"], a["fim"], float(a["fator"])))
        cursor = a["fim"]
    if cursor < duracao:
        segs.append((cursor, duracao, 1.0))
    return segs


def mapear(t: float, segs) -> float:
    """Tempo no vídeo bruto -> tempo no vídeo final."""
    final = 0.0
    for ini, fim, fator in segs:
        if t <= fim:
            return final + (max(t, ini) - ini) / fator
        final += (fim - ini) / fator
    return final


def montar_video(segs, entrada: Path, saida: Path) -> None:
    filtros, rotulos = [], []
    for i, (ini, fim, fator) in enumerate(segs):
        filtros.append(f"[0:v]trim=start={ini:.3f}:end={fim:.3f},setpts=(PTS-STARTPTS)/{fator}[v{i}]")
        rotulos.append(f"[v{i}]")
    filtros.append(f"{''.join(rotulos)}concat=n={len(segs)}:v=1:a=0,fps=25[out]")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(entrada),
        "-filter_complex", ";".join(filtros), "-map", "[out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(saida),
    ], check=True)


def texto_puro(t: str) -> str:
    t = re.sub(r"</?code>", "`", t)
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def ts(seg: float, srt: bool = False) -> str:
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    return f"{int(m):02d}:{int(s):02d}"


def main() -> None:
    ev = json.loads((TMP / "eventos.json").read_text(encoding="utf-8"))
    segs = segmentos(ev["duracao"], ev["aceleradas"])
    montar_video(segs, TMP / "video.webm", AQUI / "tutorial.mp4")

    legendas = []
    for i, l in enumerate(ev["legendas"]):
        ini = mapear(l["t"], segs)
        # Legenda acelerada fica até a próxima; as demais, pelo tempo de leitura.
        prox = ev["legendas"][i + 1]["t"] if i + 1 < len(ev["legendas"]) else ev["duracao"]
        fim = mapear(prox, segs) if l.get("acelerada") else mapear(l["t"] + l["dur"], segs)
        legendas.append({**l, "ini": ini, "fim": fim, "puro": texto_puro(l["texto"])})

    srt = "\n".join(f"{i}\n{ts(l['ini'], True)} --> {ts(l['fim'], True)}\n{l['puro']}\n"
                    for i, l in enumerate(legendas, 1))
    (AQUI / "tutorial.srt").write_text(srt, encoding="utf-8")

    total = mapear(ev["duracao"], segs)
    linhas = [
        "# Roteiro do vídeo",
        "",
        f"Vídeo: `tutorial.mp4` ({ts(total)}). Legendas: `tutorial.srt`. "
        "Trechos marcados com ⏩ são esperas do LLM local, aceleradas na montagem.",
        "",
    ]
    parte = None
    for l in legendas:
        if l["parte"] != parte:
            parte = l["parte"]
            linhas += ["", f"## {parte or 'Abertura'}", ""]
        marca = "⏩ " if l.get("acelerada") else ""
        linhas.append(f"- **{ts(l['ini'])}** {marca}{l['puro']}")
    (AQUI / "ROTEIRO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"ok: {total:.0f}s de vídeo, {len(legendas)} legendas")


if __name__ == "__main__":
    main()
