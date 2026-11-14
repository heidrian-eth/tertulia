"""Carga de los archivos del nivel y utilidades de horario."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
N1, N2 = RAIZ / "nivel-1", RAIZ / "nivel-2"


def seg(hhmmss):
    h, m, s = map(int, hhmmss.split(":"))
    return h * 3600 + m * 60 + s


def hora(segundos):
    return f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"


def cargar():
    leer = lambda p: json.loads(p.read_text(encoding="utf-8"))
    catalogo = {p["producto"]: p for p in leer(N1 / "catalogo.json")}
    pedidos = leer(N2 / "pedidos.json")
    for p in pedidos:
        p["kg"] = sum(catalogo[i["producto"]]["kg"] * i["cantidad"] for i in p["items"])
        p["m3"] = sum(catalogo[i["producto"]]["m3"] * i["cantidad"] for i in p["items"])
    return pedidos, leer(N2 / "flota.json"), leer(N2 / "operacion.json")
