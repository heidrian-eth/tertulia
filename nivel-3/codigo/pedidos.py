"""Arma nivel-3/pedidos.json a partir de la lectura de mensajes, audios, fotos y correcciones."""
import csv
import json

from datos import N1, N3, leer

RECEPCION = ("10:00", "15:00")

# pedido: (items, (calle, altura), (desde, hasta)), con las correcciones posteriores ya aplicadas
PEDIDOS = {
    # audios
    "P3-001": ({"PAP-B5": 1, "HUE-M30": 2}, ("Wendarpa", 3310), ("10:00", "11:05")),
    "P3-002": ({"BAN-KG": 3, "RUC-AT": 4}, ("Xiloria", 2110), ("10:10", "11:30")),
    "P3-003": ({"BAT-B5": 2, "HUE-M30": 1}, ("Yerralma", 2610), ("10:05", "11:10")),
    "P3-004": ({"ACEL-AT": 6, "HUE-D12": 0.5}, ("Orvencia", 2810), ("10:00", "11:40")),
    "P3-005": ({"PAP-B5": 1, "HUE-M30": 3}, ("Yerralma", 2510), ("10:15", "11:45")),
    "P3-006": ({"BAN-KG": 3, "RUC-AT": 4}, ("Quiranda", 3210), ("10:00", "11:15")),
    "P3-007": ({"BAT-B5": 2, "HUE-M30": 1}, ("Wendarpa", 2810), ("10:10", "11:50")),
    "P3-008": ({"ACEL-AT": 6, "HUE-D12": 0.5}, ("Valdoria", 3410), ("10:05", "11:25")),
    "P3-009": ({"PAP-B5": 1, "HUE-M30": 1}, ("Wendarpa", 2310), ("10:00", "11:55")),
    "P3-010": ({"BAN-KG": 3, "RUC-AT": 4}, ("Rieluma", 2810), ("10:15", "11:38")),
    "P3-011": ({"BAT-B5": 2, "HUE-M30": 1}, ("Almunela", 2010), ("10:00", "11:10")),
    "P3-012": ({"ACEL-AT": 6, "HUE-D12": 0.5}, ("Rieluma", 3010), ("10:10", "11:45")),
    "P3-013": ({"PAP-B5": 1, "HUE-M30": 2}, ("Zafralia", 1810), ("10:05", "11:30")),
    "P3-014": ({"BAN-KG": 3, "RUC-AT": 4}, ("Zafralia", 3010), ("10:00", "11:50")),
    "P3-015": ({"BAT-B5": 2, "HUE-M30": 1}, ("Serralvia", 2710), ("10:15", "11:55")),
    "P3-016": ({"ACEL-AT": 6, "HUE-D12": 0.5}, ("Rieluma", 3110), ("10:00", "11:40")),
    "P3-017": ({"TOM-CJ": 2}, ("Valdoria", 2610), ("10:15", "14:00")),
    "P3-018": ({"TOM-CJ": 1, "PAP-B5": 4}, ("Wendarpa", 2710), ("10:30", "14:15")),
    "P3-019": ({"TOM-CJ": 1, "BAT-B5": 3, "PAP-B5": 1}, ("Yerralma", 1910), ("10:00", "14:40")),
    "P3-020": ({"PAP-B5": 8}, ("Wendarpa", 3110), ("10:20", "14:10")),
    # fotos
    "P3-021": ({"MAN-CJ": 1, "HUE-M30": 5, "PAP-B5": 2, "BAN-KG": 3}, ("Quiranda", 1910), (RECEPCION[0], "12:00")),
    "P3-022": ({"TOM-CJ": 1, "PAP-B5": 3, "BAT-B5": 1}, ("Xiloria", 2710), ("10:15", "14:45")),
    "P3-023": ({"TOM-CJ": 2}, ("Zafralia", 2110), ("12:00", RECEPCION[1])),
    "P3-024": ({"PAP-B5": 6, "BAT-B5": 2}, ("Umbralia", 3110), ("10:10", "13:55")),
    "P3-025": ({"LEC-CJ": 2, "TOM-CJ": 1, "BAN-KG": 4}, ("Orvencia", 2010), ("10:30", "14:10")),
    "P3-026": ({"TOM-CJ": 1, "PAP-B5": 2, "BAT-B5": 2}, ("Serralvia", 2610), ("10:00", "14:25")),
    # texto
    "P3-027": ({"TOM-CJ": 2}, ("Valdoria", 2810), ("10:20", "14:05")),
    "P3-028": ({"PAP-B5": 8}, ("Wendarpa", 2010), ("10:45", "14:50")),
    "P3-029": ({"PAP-B5": 8}, ("Valdoria", 2610), ("10:15", "14:00")),
    "P3-030": ({"PAP-B5": 8}, ("Serralvia", 3110), ("10:35", "14:35")),
    "P3-031": ({"PAP-B5": 7, "BAT-B5": 1}, ("Wendarpa", 2710), ("10:30", "14:15")),
    "P3-032": ({"PAP-B5": 8}, ("Umbralia", 2010), ("10:05", "14:55")),
    "P3-033": ({"TOM-CJ": 2}, ("Wendarpa", 2210), ("10:25", "14:20")),
    "P3-034": ({"PAP-B5": 6, "BAT-B5": 2}, ("Yerralma", 1910), ("10:00", "14:40")),
    "P3-035": ({"TOM-CJ": 2}, ("Rieluma", 2210), ("10:15", "14:50")),
    "P3-036": ({"PAP-B5": 8}, ("Wendarpa", 2510), ("10:40", "14:10")),
    "P3-037": ({"PAP-B5": 5, "BAT-B5": 3}, ("Xiloria", 2710), ("10:15", "14:45")),
    "P3-038": ({"PAP-B5": 8}, ("Wendarpa", 1810), ("10:05", "14:35")),
    "P3-039": ({"PAP-B5": 4, "BAT-B5": 4}, ("Umbralia", 3110), ("10:10", "13:55")),
    "P3-040": ({"PAP-B5": 3, "BAT-B5": 5}, ("Serralvia", 2610), ("10:00", "14:25")),
}


def main():
    catalogo = {p["producto"]: p for p in leer(N1 / "catalogo.json")}
    padron = {(r["calle"], int(r["altura"])): int(r["nodo"]) for r in csv.DictReader(open(N1 / "padron.csv", encoding="utf-8"))}
    clientes = {c["pedido"]: c["cliente"] for c in leer(N3 / "clientes.json")}
    salida = []
    for pedido, (items, (calle, altura), (desde, hasta)) in sorted(PEDIDOS.items()):
        for prod, cant in items.items():
            assert prod in catalogo and (catalogo[prod]["fraccionable"] or float(cant).is_integer()), (pedido, prod)
        assert desde < hasta, pedido
        salida.append({
            "pedido": pedido,
            "cliente": clientes[pedido],
            "estado": "confirmado",
            "items": [{"producto": p, "cantidad": c} for p, c in items.items()],
            "direccion": {"calle": calle, "altura": altura, "nodo": padron[(calle, altura)]},
            "franja": {"desde": desde + ":00", "hasta": hasta + ":00"},
            "motivos": [],
        })
    faltan = sorted(set(clientes) - set(PEDIDOS))
    if faltan:
        print("Sin cargar:", faltan)
    (N3 / "pedidos.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(len(salida), "pedidos")


if __name__ == "__main__":
    main()
