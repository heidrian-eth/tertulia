"""Grafo dirigido de Siracusa y caminos mínimos según operacion.json."""
import heapq
import xml.etree.ElementTree as ET


def cargar_grafo(osm_path, velocidades_kmh):
    """Devuelve {nodo: [(vecino, distancia_m, segundos)]} con las aristas transitables."""
    grafo = {}
    for way in ET.parse(osm_path).getroot().iter("way"):
        nds = [int(nd.get("ref", "")) for nd in way.iter("nd")]
        tags = {t.get("k"): t.get("v") for t in way.iter("tag")}
        if tags.get("access") == "no":
            continue
        dist = int(tags["distancia_m"] or 0)
        # entero exacto: con 3.6 en coma flotante el ceil puede sumar un segundo de más
        seg = -(-dist * 36 // (velocidades_kmh[tags["highway"]] * 10))
        oneway = tags.get("oneway", "no")
        for a, b in zip(nds, nds[1:]):
            if oneway in ("no", "yes"):
                grafo.setdefault(a, []).append((b, dist, seg))
            if oneway in ("no", "-1"):
                grafo.setdefault(b, []).append((a, dist, seg))
    return grafo


def dijkstra(grafo, origen):
    """Camino de menor distancia; a igual distancia, menor tiempo."""
    mejor = {origen: (0, 0)}
    cola = [(0, 0, origen)]
    while cola:
        d, t, u = heapq.heappop(cola)
        if (d, t) > mejor[u]:
            continue
        for v, dist, seg in grafo.get(u, ()):
            cand = (d + dist, t + seg)
            if v not in mejor or cand < mejor[v]:
                mejor[v] = cand
                heapq.heappush(cola, (cand[0], cand[1], v))
    return mejor


def matrices(grafo, nodos):
    """Distancia (m) y tiempo (s) entre cada par de nodos de la lista."""
    dist, tiempo = [], []
    for o in nodos:
        mejor = dijkstra(grafo, o)
        faltan = [n for n in nodos if n not in mejor]
        if faltan:
            raise ValueError(f"Desde el nodo {o} no se llega a {faltan}")
        dist.append([mejor[n][0] for n in nodos])
        tiempo.append([mejor[n][1] for n in nodos])
    return dist, tiempo
