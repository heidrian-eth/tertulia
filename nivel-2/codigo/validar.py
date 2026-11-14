"""Revisa nivel-2/rutas.json contra todas las condiciones y calcula su distancia total."""
import json
import sys

from datos import N2, cargar, seg
from mapa import cargar_grafo, dijkstra


def main():
    pedidos, flota, op = cargar()
    por_id = {p["pedido"]: p for p in pedidos}
    flota = {f["vehiculo"]: f for f in flota}
    grafo = cargar_grafo(N2 / "siracusa.osm", op["velocidades_kmh"])
    caminos = {}

    def tramo(a, b):
        if a not in caminos:
            caminos[a] = dijkstra(grafo, a)
        return caminos[a][b]

    plan = json.loads((N2 / "rutas.json").read_text(encoding="utf-8"))
    errores, vistos, total = [], [], 0
    if set(plan) != {"rutas"} or sorted(r["vehiculo"] for r in plan["rutas"]) != sorted(flota):
        errores.append("El JSON debe tener sólo 'rutas' con una fila por vehículo")
    for r in plan["rutas"]:
        v, f = r["vehiculo"], flota[r["vehiculo"]]
        if set(r) != {"vehiculo", "salida", "paradas", "regreso"}:
            errores.append(f"{v}: campos de más o de menos")
        t, nodo, kg, m3, km = seg(r["salida"]), op["deposito"], 0, 0, 0
        if t < seg(f["desde"]):
            errores.append(f"{v}: sale antes de su turno")
        for s in r["paradas"]:
            p = por_id[s["pedido"]]
            vistos.append(s["pedido"])
            d, dt = tramo(nodo, p["direccion"]["nodo"])
            km, t, nodo = km + d, t + dt, p["direccion"]["nodo"]
            ini, fin = seg(s["inicio"]), seg(s["inicio"]) + p["descarga_segundos"]
            if ini < t:
                errores.append(f"{v} {s['pedido']}: inicia {s['inicio']} antes de llegar")
            if ini < seg(p["franja"]["desde"]) or fin > seg(p["franja"]["hasta"]):
                errores.append(f"{v} {s['pedido']}: descarga fuera de franja")
            t, kg, m3 = fin, kg + p["kg"], m3 + p["m3"]
        d, dt = tramo(nodo, op["deposito"])
        km, t = km + d, t + dt
        if t > seg(r["regreso"]) or seg(r["regreso"]) > seg(f["hasta"]):
            errores.append(f"{v}: regreso {r['regreso']} inválido (llega {t}s)")
        if kg > f["capacidad_kg"] + 1e-9 or m3 > f["capacidad_m3"] + 1e-9:
            errores.append(f"{v}: excede capacidad ({kg:.2f} kg, {m3:.4f} m3)")
        total += km
        print(f"{v}: {len(r['paradas'])} pedidos, {km / 1000:.3f} km, {kg:.2f}/{f['capacidad_kg']} kg, "
              f"{m3:.4f}/{f['capacidad_m3']} m3, {r['salida']}-{r['regreso']}")
    if sorted(vistos) != sorted(por_id):
        errores.append("Cada pedido debe aparecer exactamente una vez")
    print(f"Distancia total: {total / 1000:.3f} km")
    print("\n".join(errores) or "Plan válido")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
