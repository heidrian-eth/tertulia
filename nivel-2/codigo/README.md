# Nivel 2: rutas de reparto

Genera `nivel-2/rutas.json`: un recorrido por camioneta que entrega los 80 pedidos dentro de su franja, sin exceder la capacidad ni el turno de cada vehículo, con la menor distancia total posible.

## Uso

Requiere Python 3.12 y [uv](https://docs.astral.sh/uv/). Desde la raíz del repo:

```bash
uv venv
uv pip install -r nivel-2/codigo/requirements.txt
.venv/bin/python nivel-2/codigo/resolver.py --segundos 300
python3 nivel-2/codigo/validar.py
```

`--segundos` es el tiempo de búsqueda local; más tiempo suele dar menos kilómetros. `validar.py` no necesita dependencias.

## Archivos

| Archivo | Qué hace |
|---|---|
| `datos.py` | Lee pedidos, flota y operación, y calcula kg y m³ de cada pedido con el catálogo del nivel 1 |
| `mapa.py` | Arma el grafo dirigido del mapa y calcula caminos mínimos |
| `resolver.py` | Resuelve el ruteo y escribe `rutas.json` |
| `validar.py` | Revisa `rutas.json` contra todas las condiciones y calcula la distancia total |

## Método

**Mapa.** Cada `way` de `siracusa.osm` es una arista con `distancia_m`. `oneway=yes` se recorre en el sentido de los nodos, `oneway=-1` en el contrario y `oneway=no` en ambos. Las aristas con `access=no` se descartan. El tiempo de cada arista es `ceil(distancia_m * 3.6 / velocidad)` según el tipo de vía, calculado en enteros.

**Caminos.** Dijkstra desde el depósito y desde cada pedido, comparando el par (distancia, tiempo): gana la menor distancia y, a igual distancia, el menor tiempo. Así se obtienen las matrices de distancia y tiempo entre todos los puntos.

**Ruteo.** Es un problema de ruteo de vehículos con capacidad y franjas horarias (CVRPTW), resuelto con el solver de ruteo de Google OR-Tools:

- Costo: metros recorridos, incluida la salida y el regreso al depósito.
- Tiempo: viaje más descarga. La descarga de cada pedido empieza y termina dentro de su franja, y se permite esperar.
- Turno: cada camioneta sale y vuelve dentro de su horario.
- Capacidad: dos límites, kg y m³, por vehículo.
- Búsqueda: solución inicial por inserción y mejora con Guided Local Search. Omitir un pedido tiene una penalidad muy superior a cualquier distancia, para que la búsqueda pueda partir de un plan incompleto. Si al final queda alguno sin asignar, el programa falla.

**Horarios.** Con el orden de cada ruta definido, la salida se fija lo más tarde posible sin perder ninguna franja, y cada descarga empieza apenas se puede.
