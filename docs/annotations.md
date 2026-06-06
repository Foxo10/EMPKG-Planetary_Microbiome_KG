# Apuntes

## Tareas por llevar a cabo
* Buscar más información sobre EMP
* Bajar los datos de EMP y abrirlos programaticamente (HDF5)

## Plan de trabajo
### Fase 0 (sem. 1-3): setup + explorar datos BIOM

### Fase 1 (sem. 4-10): pipeline limpieza + normalización LLM + ontologías
### Fase 2 (sem. 11-17): esquema KG + ingestión Neo4j + consultas Cypher
### Extensión (sem. 18-20): elegir A/B/C según tiempo disponible
[Workflow](workflow.md)

## Información recabada
### HDF5
Hierarchical Data Format. Organiza cantidades inmensas de datos en base a dos objetos principales:
* Datasets: Arrays multidimensionales de elementos de datos (imágenes, serie temporal, etc.)
* Grupos: contenedores estructurales que organizan los datasets y otros grupos, similar a un sistema de ficheros.

### Biom
Apuntes sobre los datos BIOM y biom-format:
- Mirate este script de la linea 35 a la 66 que saco metadatos y tal: https://github.com/acotanor/biom-ld/blob/develop/scripts/extractBiomMetadata.py
- Si tienes obsidian puedes abrir esta carpeta con un vault y mirar de forma más comoda los apuntes, si no mira los .md de uno en uno: https://github.com/acotanor/biom-ld/tree/develop/doc/Apuntes_TFG
- El formato en la versión de hdf5: https://biom-format.org/documentation/format_versions/biom-2.1.html
- La librería de python, sin más, solo pone como instalarlo: https://github.com/biocore/biom-format


## Estructura del repositorio
En bioinformática y ciencia de datos, hay una tensión habitual entre **notebooks** (rápidos, exploratorios, difíciles de mantener) y **scripts modulares** (lentos de escribir, pero reutilizables). Para el TFG, una solución práctica es mantener ambos en carpetas separadas con un propósito claro cada uno.
* `data/`—
* `notebooks/`—
* `src/empkg/`—
* `scripts/`—
* `docs/`—
* `tests/`—

Separar `src/` (código modular) de `notebooks/` (exploración)
Solo guardamos `data/samples` en el repositorio git, con ejemplos pequeños.

## Entorno
- Gestor: conda, entorno `empkg`, Python 3.11
- Dependencias: biom-format, h5py, pandas, numpy
```bash 
conda env create -f environment.yml
conda activate empkg
```
La documentación oficial de BIOM recomienda instalar `numpy`, `biom-format` y `h5py` para trabajar con BIOM 2.0+. Además, `biom-format` incluye tanto CLI como API de Python.

## Descargar datos EMP


## Recursos
* Documentacion de biom y biom-format: ```help(biom)```
* Repo oficial de EMP: https://github.com/biocore/emp?tab=readme-ov-file


## Dudas varias
* Entorno y gestor de paquetes para scripts y programas que manejan datos biológicos.