# Nivel 1: Del WhatsApp al pedido

En La Palanca reciben pedidos por mensajes. Conviértanlos en registros que el equipo de reparto pueda usar y marquen lo que no se puede resolver con los datos disponibles.

## Qué reciben

Mensajes, catálogo, padrón de calles, lugares, clientes e historial de pedidos. Conserven esos archivos.

## Qué suben al repo

`nivel-1/pedidos.json`

## Qué revisa el juez

Que haya un registro por pedido, con productos, cantidades, domicilio y franja correctos, y un motivo por cada dato que no pudieron resolver.

## Instrucciones completas

Reciben `catalogo.json`, `padron.csv`, `lugares.json`, `clientes.json`, `historial.json` y `whatsapp.txt`. Todos los datos corresponden a La Palanca, en la ciudad ficticia de Siracusa, el 14 de noviembre de 2026. Conserven el material para las entregas posteriores.

Suban `nivel-1/pedidos.json`, en UTF-8, sin comentarios. Es una lista con una fila por pedido. Cada fila tiene exactamente estos campos:

```json
{
  "pedido": "P1-XX",
  "cliente": "CXXX",
  "estado": "confirmado",
  "items": [{"producto": "CODIGO", "cantidad": 1}],
  "direccion": {"calle": "Nombre del padrón", "altura": 100, "nodo": 100},
  "franja": {"desde": "HH:MM:SS", "hasta": "HH:MM:SS"},
  "motivos": []
}
```

Usen los identificadores recibidos. El orden de las filas y de los productos es libre; no los repitan. La cantidad se expresa en la unidad del catálogo, con hasta dos decimales. Sólo se admiten fracciones en los productos indicados como fraccionables. Calle, altura y nodo deben corresponder a una misma fila del padrón. Las horas son locales, de la misma jornada; no se admiten franjas que crucen medianoche.

`estado` es `confirmado` o `ambiguo`. Cuando un dato no pueda resolverse con lo recibido, pongan `null` en `items`, `direccion` o `franja`, según corresponda, y conserven los demás campos. Usen `ambiguo` si y sólo si hay al menos un campo así. Por cada campo nulo incluyan un motivo con exactamente `campo` y `detalle`; `campo` identifica ese campo y `detalle` explica el motivo en texto libre de 15 a 1.000 caracteres. No agreguen otros campos ni texto fuera del JSON.
