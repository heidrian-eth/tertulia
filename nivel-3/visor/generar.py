"""Genera visor/mapa.html con el plano de Siracusa y las rutas de nivel-3/rutas.json."""
import heapq
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "codigo"))
from datos import N2, N3, cargar, seg  # noqa: E402
from mapa import cargar_grafo  # noqa: E402

pedidos, flota, op = cargar()
root = ET.parse(N2 / "siracusa.osm").getroot()
nodes = {}
for n in root.iter("node"):
    t = {x.get("k"): x.get("v") for x in n.iter("tag")}
    nodes[int(n.get("id"))] = (int(t["x_m"]), int(t["y_m"]))
ways = []
for w in root.iter("way"):
    nds = [int(nd.get("ref")) for nd in w.iter("nd")]
    t = {x.get("k"): x.get("v") for x in w.iter("tag")}
    hw = {"residential": 0, "tertiary": 1, "service": 2}[t["highway"]]
    ow = {"no": 0, "yes": 1, "-1": -1}[t.get("oneway", "no")]
    for a, b in zip(nds, nds[1:]):
        ways.append([a, b, hw, ow, 1 if t.get("access") == "no" else 0, t["name"]])
g = cargar_grafo(N2 / "siracusa.osm", op["velocidades_kmh"])

def path(o, d):
    best, prev, q = {o: (0, 0)}, {}, [(0, 0, o)]
    while q:
        dd, tt, u = heapq.heappop(q)
        if (dd, tt) > best[u]: continue
        if u == d: break
        for v, di, s in g.get(u, ()):
            c = (dd + di, tt + s)
            if v not in best or c < best[v]:
                best[v], prev[v] = c, (u, s)
                heapq.heappush(q, (c[0], c[1], v))
    seq, u = [(d, 0)], d
    while u != o:
        u, s = prev[u]; seq.append((u, s))
    seq.reverse()
    out, acc = [], 0
    for i, (n, _) in enumerate(seq):
        out.append([n, acc])
        if i + 1 < len(seq):
            acc += prev[seq[i + 1][0]][1]
    return out, best[d][0]

por_id = {p["pedido"]: p for p in pedidos}
plan = json.loads((N3 / "rutas.json").read_text())
dep = op["deposito"]
rutas = []
for r in plan["rutas"]:
    f = next(x for x in flota if x["vehiculo"] == r["vehiculo"])
    t, cur, track, stops, km, kg, m3 = seg(r["salida"]), dep, [], [], 0, 0, 0
    legs = [(s, por_id[s["pedido"]]["direccion"]["nodo"]) for s in r["paradas"]] + [(None, dep)]
    for s, nd in legs:
        pth, d = path(cur, nd)
        km += d
        for n, dt in pth:
            track.append([t + dt, n])
        t += pth[-1][1]
        if s:
            p = por_id[s["pedido"]]
            ini = seg(s["inicio"])
            stops.append({"id": p["pedido"], "cliente": p["cliente"], "nodo": nd,
                          "dir": f'{p["direccion"]["calle"]} {p["direccion"]["altura"]}',
                          "llega": t, "ini": ini, "fin": ini + p["descarga_segundos"],
                          "fd": seg(p["franja"]["desde"]), "fh": seg(p["franja"]["hasta"]),
                          "kg": round(p["kg"], 2), "m3": round(p["m3"], 4),
                          "items": [[i["producto"], i["cantidad"]] for i in p["items"]]})
            kg += p["kg"]; m3 += p["m3"]
            t = ini + p["descarga_segundos"]
            track.append([ini, nd]); track.append([t, nd])
        cur = nd
    rutas.append({"v": r["vehiculo"], "chofer": f["chofer"], "salida": seg(r["salida"]), "regreso": seg(r["regreso"]),
                  "desde": seg(f["desde"]), "hasta": seg(f["hasta"]), "capkg": f["capacidad_kg"], "capm3": f["capacidad_m3"],
                  "kg": round(kg, 2), "m3": round(m3, 4), "m": km, "stops": stops, "track": track})

used = {n for r in rutas for _, n in r["track"]} | {a for w in ways for a in w[:2]}
data = {"nodes": {k: v for k, v in nodes.items() if k in used}, "ways": ways, "dep": dep, "fecha": op["fecha"],
        "vel": op["velocidades_kmh"], "rutas": rutas}
tpl = (AQUI / "plantilla.html").read_text(encoding="utf-8")
(AQUI / "mapa.html").write_text(tpl.replace("/*DATA*/null", json.dumps(data, separators=(",", ":"))), encoding="utf-8")
for r in rutas:
    print(f'{r["v"]}: {len(r["stops"])} pedidos, {r["m"] / 1000:.3f} km')
print(f'Distancia total: {sum(r["m"] for r in rutas) / 1000:.3f} km')
