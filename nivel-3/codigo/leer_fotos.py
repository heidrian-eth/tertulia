"""Transcribe las fotos de nivel-3/fotos con Claude Haiku vía `claude -p` y guarda nivel-3/fotos.json."""
import json
import subprocess
from pathlib import Path

N3 = Path(__file__).resolve().parents[1]
PROMPT = (
    "Leé la imagen {ruta} con la herramienta Read. Es una lista de compras manuscrita. "
    "Transcribí cada renglón tal como está escrito, uno por línea, sin corregir ortografía. "
    "Marcá el texto tachado como ~~texto~~ y los caracteres dudosos con [?]. "
    "Respondé sólo con la transcripción."
)


def main():
    salida = {}
    for foto in sorted((N3 / "fotos").glob("*.jpg")):
        ruta = f"fotos/{foto.name}"
        r = subprocess.run(
            ["claude", "-p", PROMPT.format(ruta=ruta), "--model", "haiku", "--allowedTools", "Read"],
            cwd=N3, capture_output=True, text=True, check=True,
        )
        salida[ruta] = r.stdout.strip()
        print(f"== {ruta}\n{salida[ruta]}", flush=True)
    (N3 / "fotos.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
