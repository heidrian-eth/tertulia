"""Transcribe los audios de nivel-3/audios con la API de OpenAI y guarda nivel-3/transcripciones.json."""
import json
import os
import subprocess
from pathlib import Path

N3 = Path(__file__).resolve().parents[1]


def transcribir(mp3, clave, modelo):
    r = subprocess.run(
        ["curl", "-sS", "--fail-with-body", "https://api.openai.com/v1/audio/transcriptions",
         "-H", f"Authorization: Bearer {clave}",
         "-F", f"file=@{mp3}", "--form-string", f"model={modelo}", "--form-string", "language=es"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)["text"].strip()


def main():
    clave = os.environ["OPENAI_API_KEY"]
    modelo = os.environ.get("MODELO_TRANSCRIPCION", "gpt-4o-transcribe")
    salida = {}
    for mp3 in sorted((N3 / "audios").glob("*.mp3")):
        salida[f"audios/{mp3.name}"] = transcribir(mp3, clave, modelo)
        print(mp3.name, salida[f"audios/{mp3.name}"], flush=True)
    (N3 / "transcripciones.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
