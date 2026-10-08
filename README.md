# BIMSA ETL

Convierte reportes XML de BIMSA a archivos Excel (`.xlsx`).

## Requisitos

- Python 3.11 o posterior

## Preparación

Desde la carpeta del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Ejecución

El XML se recomienda pasar por la entrada estándar:

```bash
python Bimsa_Cli.py \
  --tipo CLASICO \
  --out-xlsx reporte.xlsx \
  --empresa "BIMSA" \
  --usuario "Usuario" \
  --logo-path logo_bimsa.jpg \
  < ClasicoPrueba.txt
```

Tipos de reporte contemplados por la herramienta: `CLASICO`, `OBRAS`,
`CONTACTOS`, `MAPAS` y `PROSPECCION`.

En el reporte `CLASICO`, los registros se separan por el campo XML `Origen`:

- Se crea una hoja `Construleads` cuando existen registros de esa fuente.
- Se crea una hoja `Explorer` cuando existen registros de esa fuente.
- Si el XML contiene una sola fuente, el archivo genera solamente esa hoja.
- Los XML anteriores que no incluyen `Origen` se consideran `Construleads`.

Las columnas `Latitud`, `Longitud` y `Precisión` se muestran dentro del bloque
"Ubicación del Proyecto". La hoja `Explorer` omite el bloque de datos de la
compañía.

Para consultar todas las opciones:

```bash
python Bimsa_Cli.py --help
```

### Artefactos opcionales

- `--save-json`: conserva el JSON intermedio dentro de `bimsa_runs/`.
- `--debug-save-excel`: conserva una copia adicional del Excel en
  `bimsa_runs/` para revisión.
- `--output-root RUTA`: cambia la carpeta donde se guardan esos artefactos.

## Uso desde Python

```python
from BIMSA_pipeline import process_bimsa

xml = "<datos><registro><campo>valor</campo></registro></datos>"
nombre, contenido = process_bimsa(xml, "CLASICO")

with open(nombre, "wb") as archivo:
    archivo.write(contenido)
```
