# Diario técnico del TFG EMPKG-lite
> Documento vivo de seguimiento del TFG.

---

## Estado actual del proyecto
**Fase:** 0 → 1 — Exploración de datos completada. Inicio de construcción de la tabla base de muestras.

**Lo que está hecho:**
- Entorno conda `empkg` creado y documentado en `environment.yml`.
- Descargados los dos archivos iniciales del EMP (ver sección "Archivos descargados").
- Script `inspect_data.py` completado y ejecutado con éxito:
  - Estructura HDF5 del BIOM inspeccionada con `h5py`.
  - Mapping file (76 columnas, 2.000 muestras) explorado con `pandas`.
  - BIOM cargado con `biom-format`: 155.002 ASVs × 2.000 muestras, densidad 0,28%.
  - Validación de IDs: los 2.000 IDs coinciden exactamente entre mapping file y BIOM.
  - Hallazgos de calidad de datos documentados (ver sección "Hallazgos de la inspección").
- Estructura básica del repositorio definida.

**Lo que está en curso:**
- Diseño del script `build_sample_table.py` para construir la tabla base de muestras.

**Lo que NO está hecho aún:**
- No se ha construido ningún componente del Knowledge Graph.
- No se ha realizado ningún procesamiento LLM.
- No se ha conectado a Neo4j.

---

## Próximas tareas
### Fase 0 — Setup y exploración ✓ completada

- [x] Crear entorno conda `empkg` con dependencias base.
- [x] Descargar `emp_qiime_mapping_subset_2k.tsv`.
- [x] Descargar `emp_deblur_90bp.subset_2k.rare_5000.biom`.
- [x] Completar `inspect_data.py`:
  - [x] Abrir el BIOM con `biom.load_table()`.
  - [x] Mostrar dimensiones (nº de ASVs × nº de muestras).
  - [x] Listar IDs de muestra y ASV.
  - [x] Inspeccionar estructura HDF5 con `h5py`.
  - [x] Verificar metadatos de observación (taxonomía presente) y de muestra (vacíos → en mapping file TSV).
- [x] Explorar columnas del mapping file: identificar campos relevantes para el KG.
- [x] Comprobar cobertura de campos clave (resultados en "Hallazgos de la inspección").
- [x] Validar que los IDs de muestra coinciden entre BIOM y mapping file (OK: 2.000/2.000).
- [ ] Crear `notebooks/explore_biom_data.ipynb` con exploración interactiva. *(aplazado: no es bloqueante para la Fase 1)*
- [ ] Resolver acceso a `empo_v3.csv` (ver dudas abiertas). *(no bloqueante para la tabla base)*

### Fase 1 — Tabla base de muestras y pipeline de normalización (en curso)

- [ ] Escribir `build_sample_table.py`: cruzar mapping file + BIOM → `data/processed/sample_table.csv`.
- [ ] Normalizar valores "not applicable" / "not provided" a NaN en la carga.
- [ ] Convertir campos numéricos (`ph`, `latitude_deg`, etc.) de string a float.
- [ ] Diseñar pipeline de normalización de metadatos con LLM (campos `env_biome`, `env_feature`, `env_material`).
- [ ] Mapear campos de metadatos a ontologías ENVO, NCBITaxon, GAZ, CHEBI.
- [ ] Documentar el esquema de nodos y relaciones del KG.

### Fase 2 — Knowledge Graph en Neo4j (pendiente)

- [ ] Instalar y configurar Neo4j.
- [ ] Definir esquema Cypher (nodos: `Sample`, `Location`, `EnvironmentalFeature`, `Taxon`).
- [ ] Implementar pipeline de ingestión.
- [ ] Escribir consultas Cypher de ejemplo.

---

## Registro de avances
| Fecha      | Avance                                                                                   |
| ---------- | ---------------------------------------------------------------------------------------- |
| *(sem. 1)* | Setup del entorno conda. Descarga de datos EMP. Estructura del repositorio.              |
| *(sem. 2)* | `inspect_data.py` completado. Inspección HDF5, mapping file, BIOM. Validación de IDs OK. |

> Añadir filas con fecha concreta al ir avanzando.

---

## Hallazgos de la inspección (inspection.txt)

Resultado de ejecutar `inspect_data.py` sobre el subset_2k.

### Estructura HDF5 del BIOM

```
/observation/ids               (155002,)      — IDs de ASVs (= secuencias nucleotídicas Deblur)
/observation/metadata/taxonomy (155002, 7)    — 7 niveles taxonómicos por ASV
/observation/matrix/           —              — matriz dispersa en formato CSC
/sample/ids                    (2000,)        — IDs de muestras
/sample/metadata/              — VACÍO        — metadatos en mapping file TSV
```

El fichero fue generado con QIIME 1.9.1 (2016), por eso el atributo `type` dice "OTU table". Los IDs de observación son secuencias completas, confirmando que son ASVs de Deblur, no OTUs clásicos.

### Dimensiones del BIOM

| Métrica               | Valor   |
| --------------------- | ------- |
| ASVs (observaciones)  | 155.002 |
| Muestras              | 2.000   |
| Valores no nulos      | 858.173 |
| Densidad de la matriz | 0,28%   |

Una densidad del 0,28% es normal y esperada: la mayoría de taxones solo aparecen en una fracción pequeña de muestras.

### Distribución ambiental (EMPO)

| Nivel  | Categorías principales                                                      |
| ------ | --------------------------------------------------------------------------- |
| empo_1 | Host-associated (1.019), Free-living (981)                                  |
| empo_2 | Animal (640), Non-saline (595), Saline (386), Plant (379)                   |
| empo_3 | 17 tipos; los más frecuentes: Animal surface (143), Soil (non-saline) (129) |

La distribución está razonablemente balanceada. Ningún tipo de entorno domina de forma abrumadora.

### Cobertura de campos clave

| Campo               | Muestras con dato | Completitud |
| ------------------- | ----------------- | ----------- |
| `empo_3`            | 2.000 / 2.000     | 100%        |
| `env_biome`         | 2.000 / 2.000     | 100%        |
| `env_feature`       | 2.000 / 2.000     | 100%        |
| `env_material`      | 2.000 / 2.000     | 100%        |
| `latitude_deg`      | 1.998 / 2.000     | ~100%       |
| `longitude_deg`     | 1.998 / 2.000     | ~100%       |
| `temperature_deg_c` | 411 / 2.000       | 20,6%       |
| `ph`                | 284 / 2.000       | 14,2%       |
| `salinity_psu`      | 121 / 2.000       | 6,1%        |
| `oxygen_mg_per_l`   | 26 / 2.000        | 1,3%        |

**Interpretación:** Los campos fisicoquímicos tienen cobertura muy baja porque muchos estudios no los midieron. Los campos de texto libre `env_biome`, `env_feature` y `env_material` están completos al 100% y son el material principal para la armonización con LLM en la Fase 1.

### Taxonomía de ASVs

Los metadatos de observación contienen un campo `taxonomy` con 7 niveles (reino → especie) en notación Greengenes (`k__`, `p__`, `c__`, `o__`, `f__`, `g__`, `s__`). El nivel de especie suele estar vacío, lo que es habitual en datos de amplicones 16S.

Ejemplo:
```
['k__Bacteria', 'p__Proteobacteria', 'c__Gammaproteobacteria',
 'o__Alteromonadales', 'f__Alteromonadaceae', 'g__Marinimicrobium', 's__']
```

### Validación de IDs

Todos los IDs de muestra coinciden exactamente entre BIOM y mapping file (2.000/2.000). No hay muestras huérfanas en ninguna de las dos fuentes.

---

## Scripts del proyecto

### `scripts/inspect_data.py`
**Propósito:** diagnóstico y exploración inicial de los datos crudos. No transforma nada.

**Funciones:**
- `inspect_hdf5_structure(biom_path)` — recorre la jerarquía HDF5 con `h5py` e imprime grupos y datasets.
- `inspect_mapping_file(mapping_path)` — carga el TSV con `pandas`, imprime dimensiones, distribución EMPO y cobertura de campos.
- `inspect_biom_file()` — carga el BIOM con `biom.load_table()`, imprime dimensiones, densidad, IDs de muestra y ASV, taxonomía de la primera observación.
- `check_sample_ids(mapping, table)` — valida que los IDs de muestra sean idénticos en ambas fuentes.

**Output:** solo por pantalla. No escribe ficheros. Resultado guardado en `inspection.txt`.

**Uso:**
```bash
conda activate empkg
python scripts/inspect_data.py
```

---

## Decisiones técnicas tomadas
| Decisión                                 | Alternativas descartadas   | Motivo                                                                                            |
| ---------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------- |
| Usar ASVs de Deblur (no OTUs)            | Greengenes 13.8, Silva 123 | Los ASVs son el estándar actual; mayor resolución taxonómica                                      |
| Subconjunto 2k muestras para exploración | 5k, 10k, dataset completo  | Manejable para Fase 0; escalar después                                                            |
| Python 3.11 como versión base            | 3.12, 3.13                 | Mayor estabilidad con `biom-format` y `h5py` en bioinformática                                    |
| Miniconda con solver libmamba            | pip, poetry, venv          | Mejor compatibilidad con paquetes bioinformáticos (canales conda-forge, bioconda)                 |  |
| Usar Deblur 90bp, rarefaccionado a 5000  | otros parámetros           | Equilibrio entre resolución y manejabilidad; rarefacción permite comparar muestras de forma justa |

---

## Dudas abiertas
- [ ] **`empo_v3.csv` inaccesible:** el servidor devuelve 404 para v3 y 403 para v2. ¿Dónde conseguir la ontología EMPO actualizada? Opciones a investigar: repositorio GitHub de EMP, Qiita, contactar con autores. *No bloqueante para la Fase 1.*
- [x] **¿Es necesario EMPO ahora?** No. Los campos `empo_3` del mapping file ya están codificados como cadenas de texto. EMPO será necesario cuando se mapee a ENVO en la Fase 1.
- [x] **¿Los IDs coinciden entre BIOM y mapping file?** Sí. Validado: 2.000/2.000 coinciden exactamente.
- [ ] **Normalización de "not applicable":** ¿cuántos campos del mapping file usan este literal en lugar de NaN real? Verificar antes de construir la tabla base.
- [ ] **Extensión del TFG:** ¿A/B/C? Decidir antes del mes 4 según el ritmo de avance. No es urgente ahora.

---

## Notas sobre EMP y sus datos
### Resumen del proyecto EMP

El EMP Release 1 contiene ~25.000 muestras de 97 estudios (Thompson et al., *Nature* 2017, doi: `10.1038/nature24621`). Los datos están en el FTP: `ftp://ftp.microbio.me/emp/release1/`. El subset de 2k muestras es una submuestra estratificada representativa usada en análisis exploratorios.

Repo oficial: https://github.com/biocore/emp

### Estructura del FTP
release1/

├── mapping_files/        # Metadatos TSV por muestra

├── emp_ontology/         # relación con ENVO

├── otu_tables/

│   ├── deblur/           # ASVs ← opción elegida

│   ├── closed_ref_greengenes/

│   ├── closed_ref_silva/

│   └── open_ref_greengenes/

└── otu_info/             # Secuencias de referencia y árboles filogenéticos

### Mapping file

Archivo TSV donde cada fila es una muestra y cada columna es un campo de metadatos. La primera columna es `#SampleID`. Campos relevantes para el KG:

| Campo               | Descripción                |
| ------------------- | -------------------------- |
| `latitude_deg`      | Latitud GPS                |
| `longitude_deg`     | Longitud GPS               |
| `empo_3`            | Tipo de entorno según EMPO |
| `ph`                | pH de la muestra           |
| `temperature_deg_c` | Temperatura en °C          |

No todos los campos están rellenos en todas las muestras.

### Nomenclatura de archivos BIOM
*emp_<método>_<longitud_bp>.<tamaño>.<rarefacción>.biom*

Ejemplo: `emp_deblur_90bp.subset_2k.rare_5000.biom`

### Archivos descargados

| Archivo                                    | Ruta local                                 | Descripción                                                 |
| ------------------------------------------ | ------------------------------------------ | ----------------------------------------------------------- |
| `emp_qiime_mapping_subset_2k.tsv`          | `data/raw/emp/release1/mapping_files/`     | Metadatos de 2.000 muestras. Abrir con `pandas`.            |
| `emp_deblur_90bp.subset_2k.rare_5000.biom` | `data/raw/emp/release1/otu_tables/deblur/` | Tabla de abundancias ASVs. Requiere `biom-format` + `h5py`. |

### Comandos de descarga

```bash
# Mapping file
mkdir -p data/raw/emp/release1/mapping_files
wget -c \
  -O data/raw/emp/release1/mapping_files/emp_qiime_mapping_subset_2k.tsv \
  https://ftp.microbio.me/emp/release1/mapping_files/emp_qiime_mapping_subset_2k.tsv

# Tabla BIOM Deblur
mkdir -p data/raw/emp/release1/otu_tables/deblur
wget -c \
  -O data/raw/emp/release1/otu_tables/deblur/emp_deblur_90bp.subset_2k.rare_5000.biom \
  https://ftp.microbio.me/emp/release1/otu_tables/deblur/emp_deblur_90bp.subset_2k.rare_5000.biom
```

---

## Notas sobre BIOM / HDF5

### HDF5

Hierarchical Data Format. Organiza grandes volúmenes de datos en torno a dos objetos:
- **Datasets:** arrays multidimensionales (imágenes, series temporales, matrices de abundancia).
- **Grupos:** contenedores jerárquicos que organizan datasets y otros grupos, similar a un sistema de ficheros.

### BIOM 2.x

El formato BIOM 2.x almacena la tabla de abundancias como una **matriz dispersa dentro de un HDF5**. La forma estándar de abrirlo en Python es `biom.load_table()`.

Especificación del formato: https://biom-format.org/documentation/format_versions/biom-2.1.html

Referencia útil de código (extracción de metadatos desde BIOM):
https://github.com/acotanor/biom-ld/blob/develop/scripts/extractBiomMetadata.py

Librería Python: https://github.com/biocore/biom-format

### OTUs vs ASVs

- **OTUs:** agrupan secuencias al 97% de similitud. Introducen ruido. Metodología más antigua.
- **ASVs (Amplicon Sequence Variants):** representan secuencias exactas. Estándar actual en microbiomía. En Deblur, el ID de cada ASV es la propia secuencia nucleotídica.

### Rarefacción

Normalización que submuestrea todas las muestras al mismo número de lecturas (aquí: 5.000). Permite comparar diversidad microbiana de forma justa entre muestras. El coste es que las muestras con pocas lecturas se eliminan.

---

## Notas sobre ontologías (EMPO, ENVO, NCBITaxon…)

### EMPO (EMP Ontology)

Ontología propia del EMP. Clasificación jerárquica de tipos de entorno: `Free-living aquatic`, `Animal corpus`, `Plant corpus`, etc. Más gruesa y específica del EMP que ENVO. Los campos `empo_3` del mapping file asignan cada muestra a un nodo EMPO.

Archivo: `emp_ontology/empo_v3.csv` en el FTP (inaccesible actualmente — ver dudas).
Grafo EMPO–ENVO: `emp_ontology/envoEmpo_graph_v3.vue`.

### ENVO (Environment Ontology)

Ontología estándar de entornos ambientales. Más detallada y actualizada que EMPO.
Ejemplo de uso: "suelo, bosque, templado" → `ENVO:00002258` (soil) + `ENVO:01000174` (temperate broadleaf forest).
Se usará en la Fase 1 para normalizar metadatos con el LLM.

### Otras ontologías previstas en el KG

| Ontología | Dominio                 |
| --------- | ----------------------- |
| NCBITaxon | Taxonomía microbiana    |
| GAZ       | Geografía / ubicaciones |
| CHEBI     | Sustancias químicas     |

## Notas sobre Knowledge Graph / Neo4j (vacío por ahora)
Esquema previsto de nodos: `Sample`, `Location`, `EnvironmentalFeature`, `Taxon`.
Relaciones previstas: `was_collected_at`, `has_feature`, `contains_taxon_with_abundance_X`.

## Entorno y configuración
| Elemento             | Valor                                    |
| -------------------- | ---------------------------------------- |
| Gestor de entornos   | Miniconda 25.11.1 con solver libmamba    |
| Entorno del proyecto | `empkg` (Python 3.11)                    |
| Canales conda        | conda-forge > bioconda > defaults        |
| Dependencias base    | `biom-format`, `h5py`, `pandas`, `numpy` |

```bash
# Activar entorno
conda activate empkg

# Reproducir entorno desde cero
conda env create -f environment.yml
```

## Estructura del repositorio
empkg-lite/

├── data/

│   └── raw/emp/release1/     # Datos originales (en .gitignore)

├── notebooks/                # Exploración interactiva

├── src/empkg/                # Código modular reutilizable

├── scripts/                  # Scripts de ingesta, inspección, etc.

├── docs/                     # Memoria y documentación

└── tests/                    # Tests básicos

**Criterio utilizado**: separar `src/` (código modular) de `notebooks/` (exploración). Solo guardar en Git pequeños ejemplos de datos bajo `data/samples/`.

---

## Recursos útiles

### EMP y datos microbianos
- Repo oficial EMP: https://github.com/biocore/emp
- FTP EMP Release 1: `ftp://ftp.microbio.me/emp/release1/`
- Thompson et al. 2017 (paper EMP): doi `10.1038/nature24621`

### BIOM / HDF5
- Documentación biom-format: https://biom-format.org/documentation/format_versions/biom-2.1.html
- Repo biom-format Python: https://github.com/biocore/biom-format
- Ejemplo de extracción de metadatos BIOM: https://github.com/acotanor/biom-ld/blob/develop/scripts/extractBiomMetadata.py
- Apuntes adicionales (Obsidian-compatible): https://github.com/acotanor/biom-ld/tree/develop/doc/Apuntes_TFG

### Ontologías
- ENVO: https://obofoundry.org/ontology/envo.html
- NCBITaxon: https://obofoundry.org/ontology/ncbitaxon.html
- CHEBI: https://www.ebi.ac.uk/chebi/

### Documentación Python
- `help(biom)` en intérprete Python para API de biom-format.