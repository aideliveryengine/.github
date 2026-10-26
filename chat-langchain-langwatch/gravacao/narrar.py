"""Gera a versão narrada do vídeo.

    python gravacao/narrar.py

Entrada: tutorial.mp4 + tutorial.srt (do montar.py) e narracao.json (uma fala por
legenda, na mesma ordem; "" = sem fala). Saída: tutorial_narrado.mp4 e tutorial_narrado.srt.

Voz: Piper pt_BR "faber" (VITS) rodando local via sherpa-onnx. Modelo em
https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2
(caminho em VOZ_DIR). Requer `sherpa-onnx<2`
(a 2.x tirou o fonemizador espeak embutido).

Quando a fala não cabe no tempo da legenda, o último quadro antes da próxima legenda
é congelado pelo tempo que faltar, em vez de acelerar a voz.
"""

import json
import os
import re
import subprocess
import wave
from pathlib import Path

import numpy as np
import sherpa_onnx

AQUI = Path(__file__).resolve().parent
TMP = AQUI / "tmp" / "narracao"
VOZ = Path(os.getenv("VOZ_DIR", "tts/vits-piper-pt_BR-faber-medium"))
FPS = 25
# Grafia "falada" para a voz pt_BR (o espeak lê "ch" como "x", por exemplo). Ajustada
# ouvindo de volta com Whisper: as variantes que ele transcrevia mais perto do nome real.
PRONUNCIA = {
    "LangChain": "Lang Tchêin", "LangWatch": "Lang-uótch", "LangGraph": "Lang Gréf",
    "langgraph": "Lang Gréf", "langchain": "Lang Tchêin", "PyPI": "pai-pi-ai",
    "traces": "treices", "trace": "treice", "Trace": "Treice",
}
ANTES = 0.25   # respiro entre a legenda aparecer e a fala começar (s)
DEPOIS = 0.45  # silêncio mínimo depois de cada fala (s)


def ler_srt(caminho: Path) -> list[dict]:
    def seg(t):
        h, m, s = t.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    itens = []
    for bloco in caminho.read_text(encoding="utf-8").strip().split("\n\n"):
        linhas = bloco.split("\n")
        ini, fim = (seg(x.strip()) for x in linhas[1].split("-->"))
        itens.append({"ini": ini, "fim": fim, "texto": " ".join(linhas[2:])})
    return itens


def ts_srt(s: float) -> str:
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


def sintetizar(falas: list[str]) -> tuple[list[np.ndarray | None], int]:
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model=str(VOZ / "pt_BR-faber-medium.onnx"), tokens=str(VOZ / "tokens.txt"),
            data_dir=str(VOZ / "espeak-ng-data")),
        num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    audios, taxa = [], 22050
    for fala in falas:
        if not fala.strip():
            audios.append(None)
            continue
        for nome, falado in PRONUNCIA.items():
            fala = re.sub(rf"\b{nome}\b", falado, fala)
        a = tts.generate(fala, sid=0, speed=1.0)
        taxa = a.sample_rate
        audios.append(np.array(a.samples, dtype=np.float32))
    return audios, taxa


def duracao_video(caminho: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(caminho)], capture_output=True, text=True, check=True)
    return float(out.stdout)


def codificar(args: list[str], saida: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args, "-an", "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
                    str(saida)], check=True)


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    video = AQUI / "tutorial.mp4"
    legendas = ler_srt(AQUI / "tutorial.srt")
    falas = json.loads((AQUI / "narracao.json").read_text(encoding="utf-8"))
    assert len(falas) == len(legendas), f"{len(falas)} falas para {len(legendas)} legendas"

    audios, taxa = sintetizar(falas)
    total = duracao_video(video)

    # Para cada legenda: onde a fala começa no vídeo final e quanto congelar antes da próxima.
    congelar = []          # (tempo no vídeo original, segundos)
    desloc = 0.0           # quanto o vídeo final já está "atrasado" em relação ao original
    posicoes, novas = [], []
    for i, (leg, audio) in enumerate(zip(legendas, audios)):
        prox = legendas[i + 1]["ini"] if i + 1 < len(legendas) else total
        dur = 0.0 if audio is None else len(audio) / taxa
        falta = (ANTES + dur + DEPOIS) - (prox - leg["ini"]) if audio is not None else 0.0
        ini_final = leg["ini"] + desloc
        posicoes.append(ini_final + ANTES)
        extra = max(0.0, falta)
        novas.append({**leg, "ini": ini_final, "fim": prox + desloc + extra})
        if extra > 0:
            congelar.append((max(leg["ini"], prox - 1.0 / FPS), extra))
            desloc += extra

    # Vídeo: trechos do original intercalados com quadros congelados.
    partes, cursor = [], 0.0
    for k, (t, seg) in enumerate(congelar):
        if t > cursor:
            p = TMP / f"v{k:03d}a.mp4"
            codificar(["-ss", f"{cursor:.3f}", "-to", f"{t:.3f}", "-i", str(video)], p)
            partes.append(p)
        quadro = TMP / f"q{k:03d}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                        "-frames:v", "1", str(quadro)], check=True)
        p = TMP / f"v{k:03d}b.mp4"
        codificar(["-loop", "1", "-t", f"{seg:.3f}", "-i", str(quadro)], p)
        partes.append(p)
        cursor = t
    p = TMP / "vfim.mp4"
    codificar(["-ss", f"{cursor:.3f}", "-i", str(video)], p)
    partes.append(p)
    lista = TMP / "partes.txt"
    lista.write_text("".join(f"file '{x}'\n" for x in partes))
    so_video = TMP / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-c", "copy", str(so_video)], check=True)

    # Áudio: uma trilha do tamanho do vídeo com cada fala na sua posição.
    dur_final = duracao_video(so_video)
    trilha = np.zeros(int(dur_final * taxa) + taxa, dtype=np.float32)
    for pos, audio in zip(posicoes, audios):
        if audio is not None:
            i = int(pos * taxa)
            trilha[i:i + len(audio)] += audio[: len(trilha) - i]
    trilha = np.clip(trilha / max(1e-6, np.abs(trilha).max()) * 0.9, -1, 1)
    wav = TMP / "narracao.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes((trilha * 32767).astype(np.int16).tobytes())

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(so_video), "-i", str(wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-movflags", "+faststart", str(AQUI / "tutorial_narrado.mp4")], check=True)

    srt = "\n".join(f"{i}\n{ts_srt(l['ini'])} --> {ts_srt(l['fim'])}\n{l['texto']}\n"
                    for i, l in enumerate(novas, 1))
    (AQUI / "tutorial_narrado.srt").write_text(srt, encoding="utf-8")
    print(f"ok: {dur_final:.0f}s ({len(congelar)} congelamentos, +{desloc:.0f}s), "
          f"{sum(a is not None for a in audios)} falas")


if __name__ == "__main__":
    main()
