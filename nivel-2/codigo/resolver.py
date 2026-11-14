"""Arma nivel-2/rutas.json resolviendo un ruteo de vehículos con capacidad y franjas (CVRPTW) con OR-Tools."""
import argparse
import json

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from datos import N2, cargar, hora, seg
from mapa import cargar_grafo, matrices

ESCALA_KG, ESCALA_M3 = 100, 10000
PENALIDAD = 10**8


def modelo(pedidos, flota, dist, tiempo):
    n, nv = len(pedidos) + 1, len(flota)
    mgr = pywrapcp.RoutingIndexManager(n, nv, 0)
    rt = pywrapcp.RoutingModel(mgr)
    servicio = [0] + [p["descarga_segundos"] for p in pedidos]

    dist_cb = rt.RegisterTransitCallback(lambda i, j: dist[mgr.IndexToNode(i)][mgr.IndexToNode(j)])
    rt.SetArcCostEvaluatorOfAllVehicles(dist_cb)

    def transito(i, j):
        a, b = mgr.IndexToNode(i), mgr.IndexToNode(j)
        return servicio[a] + tiempo[a][b]

    t_cb = rt.RegisterTransitCallback(transito)
    rt.AddDimension(t_cb, 24 * 3600, 24 * 3600, False, "Tiempo")
    td = rt.GetDimensionOrDie("Tiempo")
    for k, p in enumerate(pedidos, start=1):
        td.CumulVar(mgr.NodeToIndex(k)).SetRange(seg(p["franja"]["desde"]), seg(p["franja"]["hasta"]) - servicio[k])
    for v, f in enumerate(flota):
        td.CumulVar(rt.Start(v)).SetRange(seg(f["desde"]), seg(f["hasta"]))
        td.CumulVar(rt.End(v)).SetRange(seg(f["desde"]), seg(f["hasta"]))

    for campo, escala, cap in (("kg", ESCALA_KG, "capacidad_kg"), ("m3", ESCALA_M3, "capacidad_m3")):
        demanda = [0] + [round(p[campo] * escala) for p in pedidos]
        cb = rt.RegisterUnaryTransitCallback(lambda i, d=demanda: d[mgr.IndexToNode(i)])
        rt.AddDimensionWithVehicleCapacity(cb, 0, [int(f[cap] * escala) for f in flota], True, campo)
    # la inserción inicial no arma un plan completo; omitir un pedido se penaliza muy por encima de cualquier distancia
    for k in range(1, n):
        rt.AddDisjunction([mgr.NodeToIndex(k)], PENALIDAD)
    return mgr, rt


def horario(orden, pedidos, f, tiempo):
    """Salida lo más tarde posible sin perder franjas; luego descargas lo antes posible."""
    if not orden:
        return seg(f["desde"]), [], seg(f["desde"])
    nodos = [0] + orden + [0]
    serv = lambda k: pedidos[k - 1]["descarga_segundos"]
    tarde = seg(f["hasta"]) - tiempo[orden[-1]][0] - serv(orden[-1])
    for idx in range(len(orden) - 1, -1, -1):
        k = orden[idx]
        tarde = min(tarde, seg(pedidos[k - 1]["franja"]["hasta"]) - serv(k))
        tarde -= tiempo[nodos[idx]][k] + (serv(nodos[idx]) if idx else 0)
    salida = max(seg(f["desde"]), tarde)
    t, inicios, previo = salida, [], 0
    for k in orden:
        t = max(t + tiempo[previo][k], seg(pedidos[k - 1]["franja"]["desde"]))
        inicios.append(t)
        t += serv(k)
        previo = k
    return salida, inicios, t + tiempo[previo][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segundos", type=int, default=120, help="tiempo de búsqueda local")
    args = ap.parse_args()

    pedidos, flota, op = cargar()
    nodos = [op["deposito"]] + [p["direccion"]["nodo"] for p in pedidos]
    dist, tiempo = matrices(cargar_grafo(N2 / "siracusa.osm", op["velocidades_kmh"]), nodos)

    mgr, rt = modelo(pedidos, flota, dist, tiempo)
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.seconds = args.segundos
    sol = rt.SolveWithParameters(params)
    omitidos = [pedidos[k - 1]["pedido"] for k in range(1, len(nodos)) if sol and sol.Value(rt.NextVar(mgr.NodeToIndex(k))) == mgr.NodeToIndex(k)]
    if sol is None or omitidos:
        raise SystemExit(f"No se encontró un plan que entregue todos los pedidos; faltan {omitidos}")

    rutas, total = [], 0
    for v, f in enumerate(flota):
        i, orden = rt.Start(v), []
        while not rt.IsEnd(i):
            j = sol.Value(rt.NextVar(i))
            total += dist[mgr.IndexToNode(i)][mgr.IndexToNode(j)]
            if not rt.IsEnd(j):
                orden.append(mgr.IndexToNode(j))
            i = j
        salida, inicios, regreso = horario(orden, pedidos, f, tiempo)
        rutas.append({
            "vehiculo": f["vehiculo"],
            "salida": hora(salida),
            "paradas": [{"pedido": pedidos[k - 1]["pedido"], "inicio": hora(t)} for k, t in zip(orden, inicios)],
            "regreso": hora(regreso),
        })
        print(f"{f['vehiculo']}: {len(orden)} pedidos, {sum(pedidos[k - 1]['kg'] for k in orden):.2f} kg")
    (N2 / "rutas.json").write_text(json.dumps({"rutas": rutas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Distancia total: {total / 1000:.3f} km")


if __name__ == "__main__":
    main()
