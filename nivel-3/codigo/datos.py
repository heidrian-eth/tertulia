"""Carga de los archivos del nivel 3 y utilidades de horario."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
N1, N2, N3 = RAIZ / "nivel-1", RAIZ / "nivel-2", RAIZ / "nivel-3"


def seg(hhmmss):
    h, m, s = map(int, hhmmss.split(":"))
    return h * 3600 + m * 60 + s


def hora(segundos):
    return f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}:{segundos % 60:02d}"


def leer(p):
    return json.loads(p.read_text(encoding="utf-8"))


def cargar():
    """Pedidos ruteables de nivel-3/pedidos.json con descarga, kg y m3; flota y operación del lote."""
    catalogo = {p["producto"]: p for p in leer(N1 / "catalogo.json")}
    descarga = {c["pedido"]: c["descarga_segundos"] for c in leer(N3 / "clientes.json")}
    pedidos = [p for p in leer(N3 / "pedidos.json") if p["estado"] == "confirmado"]
    for p in pedidos:
        p["descarga_segundos"] = descarga[p["pedido"]]
        p["kg"] = sum(catalogo[i["producto"]]["kg"] * i["cantidad"] for i in p["items"])
        p["m3"] = sum(catalogo[i["producto"]]["m3"] * i["cantidad"] for i in p["items"])
    return pedidos, leer(N3 / "flota.json"), leer(N3 / "operacion.json")
