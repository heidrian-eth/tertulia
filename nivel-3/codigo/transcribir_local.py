"""Transcribe localmente los audios de nivel-3/audios con Whisper y guarda nivel-3/transcripciones.json."""
import argparse
import json
from pathlib import Path

import whisper

N3 = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="large-v3-turbo")
    args = ap.parse_args()
    modelo = whisper.load_model(args.modelo, device="cpu")
    salida = {}
    for mp3 in sorted((N3 / "audios").glob("*.mp3")):
        salida[f"audios/{mp3.name}"] = modelo.transcribe(str(mp3), language="es", fp16=False, temperature=0)["text"].strip()
        print(mp3.name, salida[f"audios/{mp3.name}"], flush=True)
    (N3 / "transcripciones.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
