# Nivel 3: pedidos y rutas desde audios, fotos y mensajes

Genera `nivel-3/pedidos.json` y `nivel-3/rutas.json`.

## Uso

Desde la raíz del repo:

```bash
uv venv
uv pip install -r nivel-3/codigo/requirements.txt
.venv/bin/python nivel-3/codigo/transcribir_local.py   # o: OPENAI_API_KEY=... python3 nivel-3/codigo/transcribir_openai.py
python3 nivel-3/codigo/leer_fotos.py
python3 nivel-3/codigo/pedidos.py
.venv/bin/python nivel-3/codigo/resolver.py --segundos 60
python3 nivel-3/codigo/validar.py
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `transcribir_local.py` | Transcribe los audios con Whisper local (`large-v3-turbo`, CPU) |
| `transcribir_openai.py` | Misma salida con la API de OpenAI (`gpt-4o-transcribe`) |
| `leer_fotos.py` | Transcribe las listas manuscritas con Claude Haiku vía `claude -p` |
| `pedidos.py` | Interpretación de cada pedido, con las correcciones posteriores aplicadas, y escritura de `pedidos.json` |
| `datos.py`, `mapa.py` | Carga de datos, grafo del mapa del nivel 2 y caminos mínimos |
| `resolver.py` | Ruteo con OR-Tools y escritura de `rutas.json` |
| `validar.py` | Revisa `rutas.json` contra todas las condiciones |

## Criterios

- Las calles mal escritas o mal transcriptas se resuelven con el padrón y el barrio del cliente en `clientes.json`.
- Los mensajes posteriores reemplazan sólo el dato que corrigen (domicilio, franja o productos).
- Un límite horario que el cliente no expresa toma el extremo del horario de recepción (10:00 a 15:00).
- En los audios con horarios dudosos se compararon varias transcripciones, incluida una versión ralentizada del audio.
- Pedidos en un mismo domicilio no descargan a la vez, aunque vayan en camionetas distintas.
