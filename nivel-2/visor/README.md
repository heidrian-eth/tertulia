# Visor del nivel 2

`mapa.html` dibuja el plano de Siracusa con las rutas de `nivel-2/rutas.json`: cada tramo sigue el camino mínimo sobre el mapa, con paradas numeradas, franjas y un control de hora para ver dónde está cada camioneta. Es una página autocontenida; se abre en cualquier navegador.

El plano usa las coordenadas `x_m`/`y_m` del OSM, porque sus latitudes y longitudes son sintéticas y no tienen mapa de fondo real.

## Uso

Desde la raíz del repo, después de regenerar `rutas.json`:

```bash
python3 nivel-2/visor/generar.py
```

No necesita dependencias. Reutiliza `datos.py` y `mapa.py` de `nivel-2/codigo/`.

| Archivo | Qué hace |
|---|---|
| `generar.py` | Calcula los caminos de cada ruta e inserta los datos en la plantilla |
| `plantilla.html` | Página del visor, sin datos |
| `mapa.html` | Resultado generado |
