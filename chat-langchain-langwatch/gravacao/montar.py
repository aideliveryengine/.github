"""Monta o vídeo final a partir da gravação bruta.

    python gravacao/montar.py

Lê tmp/video.webm + tmp/eventos.json (gerados pelo gravar.js) e produz:
- tutorial.mp4   trechos de espera do LLM acelerados, H.264
- tutorial.srt   legendas com os tempos do vídeo final
- ROTEIRO.md     o texto explicativo, por parte, com timestamps

Edição opcional pós-gravação em tmp/edicao.json (tempos do vídeo bruto):
    {"aceleradas": [{"ini": 321, "fim": 419, "fator": 8}],
     "cortes": [{"ini": 883, "fim": 1012,
                 "inserir": {"arquivo": "insercao.webm", "ini": 14, "fim": 29,
                             "legendas": [{"t": 1.5, "dur": 6, "texto": "...", "parte": "..."}]}}]}
Legendas do bruto que caem dentro de um corte são descartadas.
"""

import html
import json
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TMP = AQUI / "tmp"
BRUTO = "video.webm"


def segmentos(duracao: float, aceleradas: list[dict], cortes: list[dict]) -> list[dict]:
    """Linha do tempo final: trechos do bruto (com fator de velocidade) e inserções."""
    marcos = [{"ini": a["ini"], "fim": a["fim"], "fator": float(a["fator"])} for a in aceleradas]
    marcos += [{**c, "corte": True} for c in cortes]
    segs, cursor = [], 0.0
    for m in sorted(marcos, key=lambda m: m["ini"]):
        if m["ini"] > cursor:
            segs.append({"src": BRUTO, "ini": cursor, "fim": m["ini"], "fator": 1.0})
        if m.get("corte"):
            ins = m.get("inserir")
            if ins:
                segs.append({"src": ins["arquivo"], "ini": ins["ini"], "fim": ins["fim"], "fator": 1.0,
                             "legendas": ins.get("legendas", [])})
        else:
            segs.append({"src": BRUTO, "ini": m["ini"], "fim": m["fim"], "fator": m["fator"]})
        cursor = m["fim"]
    if cursor < duracao:
        segs.append({"src": BRUTO, "ini": cursor, "fim": duracao, "fator": 1.0})
    return segs


def mapear(t: float, segs) -> float | None:
    """Tempo no vídeo bruto -> tempo no vídeo final (None se caiu num corte)."""
    final = 0.0
    for s in segs:
        if s["src"] == BRUTO and s["ini"] <= t <= s["fim"]:
            return final + (t - s["ini"]) / s["fator"]
        if s["src"] == BRUTO and t < s["ini"]:
            return None  # passou do ponto sem achar: estava dentro de um corte
        final += (s["fim"] - s["ini"]) / s["fator"]
    return final


def inicio_final(seg_alvo, segs) -> float:
    final = 0.0
    for s in segs:
        if s is seg_alvo:
            return final
        final += (s["fim"] - s["ini"]) / s["fator"]
    raise ValueError("segmento não encontrado")


def montar_video(segs, saida: Path) -> None:
    # Um arquivo por trecho (seek na entrada) e depois concat sem recodificar.
    # Um filter_complex único com vários trim do mesmo stream guarda frames demais na RAM.
    partes = []
    for i, s in enumerate(segs):
        parte = TMP / f"seg{i:02d}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s['ini']:.3f}", "-to", f"{s['fim']:.3f}",
            "-i", str(TMP / s["src"]), "-vf", f"setpts=(PTS-STARTPTS)/{s['fator']},fps=25", "-an",
            "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", str(parte),
        ], check=True)
        partes.append(parte)
    lista = TMP / "partes.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
        "-c", "copy", "-movflags", "+faststart", str(saida),
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
    arq_edicao = TMP / "edicao.json"
    edicao = json.loads(arq_edicao.read_text(encoding="utf-8")) if arq_edicao.exists() else {}
    segs = segmentos(ev["duracao"], ev["aceleradas"] + edicao.get("aceleradas", []), edicao.get("cortes", []))
    montar_video(segs, AQUI / "tutorial.mp4")

    legendas = []
    for i, l in enumerate(ev["legendas"]):
        ini = mapear(l["t"], segs)
        if ini is None:
            continue
        # Legenda acelerada fica até a próxima; as demais, pelo tempo de leitura.
        prox = ev["legendas"][i + 1]["t"] if i + 1 < len(ev["legendas"]) else ev["duracao"]
        fim = mapear(prox if l.get("acelerada") else l["t"] + l["dur"], segs)
        legendas.append({**l, "ini": ini, "fim": fim if fim is not None else ini + l["dur"]})
    for s in segs:
        base = inicio_final(s, segs) if s.get("legendas") else 0
        for l in s.get("legendas", []):
            legendas.append({**l, "ini": base + l["t"], "fim": base + l["t"] + l["dur"]})
    legendas.sort(key=lambda l: l["ini"])
    for l in legendas:
        l["puro"] = texto_puro(l["texto"])

    srt = "\n".join(f"{i}\n{ts(l['ini'], True)} --> {ts(l['fim'], True)}\n{l['puro']}\n"
                    for i, l in enumerate(legendas, 1))
    (AQUI / "tutorial.srt").write_text(srt, encoding="utf-8")

    total = sum((s["fim"] - s["ini"]) / s["fator"] for s in segs)
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
