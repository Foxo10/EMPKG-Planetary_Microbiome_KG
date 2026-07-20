# Diario técnico del TFG EMPKG-lite
> Documento vivo de seguimiento del TFG.

---

## Estado actual del proyecto

**Fase:** RDF v0 completada → pipeline reproducible CSV → RDF/Turtle entregado y validado.

La exploración inicial de datos, la generación de `data/processed/sample_table.csv`, el análisis dirigido de ese artefacto, el diseño conceptual del KG v0, el notebook `notebooks/03_to_rdf.ipynb` y el script reproducible `scripts/csv_to_rdf.py` están todos completados. El artefacto oficial de la fase es `data/processed/empkg_v0_test.ttl`.

GraphDB ya está instalado pero el repositorio EMPKG-lite todavía no ha sido configurado ni cargado.

Siguiente paso inmediato:
```text
Fase 1C — Validación del KG v0 en GraphDB/SPARQL
```
Siguiente bloque de construcción:
```text
Fase 1D — Datos microbianos: ASVs, taxonomía y abundancias
```

**Lo que está hecho:**

* Entorno conda `empkg` creado y documentado en `environment.yml`.
* Descargados los dos archivos iniciales del EMP:
  * `emp_qiime_mapping_subset_2k.tsv`
  * `emp_deblur_90bp.subset_2k.rare_5000.biom`
* Script `inspect_data.py` creado y ejecutado: inspecciona mapping file, BIOM, estructura HDF5 y valida IDs. Exporta CSVs de diagnóstico a `data/inspection/`.
* Script `inspect_missing_values.py` creado y ejecutado: detecta marcadores de valores ausentes no estándar en el mapping file.
* Notebook `notebooks/00_explore_biom.ipynb` desarrollado como exploración técnica y didáctica del formato BIOM, HDF5 y `biom-format`.
* Validado formalmente que los 2.000 IDs de muestra coinciden exactamente entre el BIOM y el mapping file.
* Script `build_sample_table.py` finalizado como pipeline reproducible.
* Generado `data/processed/sample_table.csv`, con una fila por muestra y columnas seleccionadas para el futuro KG.
* Decidido que el KG se construirá con RDF/Turtle y GraphDB/SPARQL, no con Neo4j/Cypher.
* Creado y ejecutado `notebooks/01_analyze_sample_table.ipynb`: valida `sample_id`, tipos de datos, cobertura, jerarquía EMPO, coordenadas duplicadas y campos fisicoquímicos sobre el artefacto final (no sobre el mapping crudo).
* Seleccionado `data/samples/kg_v0_test_samples.csv`: 17 muestras, una por cada categoría `empo_3`, elegidas de forma determinista por completitud de campos.
* Redactado `docs/kg_design_v0.md` con el diseño v0: entidades `Sample`, `Study`, `Location`, `EMPOCategory`, `EnvironmentDescription`.
* Creado y ejecutado `notebooks/03_to_rdf.ipynb`: convierte `kg_v0_test_samples.csv` a RDF/Turtle usando `rdflib`. Sirve como documento didáctico y de referencia.
* **Creado `scripts/csv_to_rdf.py`**: script reproducible que consolida la lógica del notebook. Transforma cualquier CSV de muestras compatible en RDF/Turtle. Probado también sobre las 2.000 muestras de `sample_table.csv`.
* Generado y validado `data/processed/empkg_v0_test.ttl`: 588 triples, 17 `Sample`, 15 `Study`, 15 `Location`, 17 `EMPOCategory`, 17 `EnvironmentDescription`, 0 literales problemáticos.
* Las URIs de `Location` usan un hash SHA-256 abreviado generado a partir de una clave canónica (country, lat, lon, depth, alt, elev). Si faltan lat/lon, se añade `sample_id` como fallback para evitar fusiones incorrectas.

**Lo que está en curso:**

* Configuración del repositorio EMPKG-lite en GraphDB.
* Carga de `empkg_v0_test.ttl` en GraphDB.
* Escritura y documentación de consultas SPARQL básicas de validación sobre el KG v0.

**Lo que NO está hecho aún:**

* No se ha configurado todavía el repositorio GraphDB EMPKG-lite.
* No se ha cargado todavía el Turtle generado en GraphDB.
* No se han escrito todavía consultas SPARQL sobre el KG v0.
* No se ha construido todavía `asv_table.csv` (tabla maestra de ASVs y taxonomía).
* No se ha construido todavía `abundance_table.csv` (tabla de abundancias muestra–ASV).
* No se ha construido todavía `docs/kg_design_v1.md`.
* No se ha realizado todavía procesamiento LLM ni mapeo automático a ontologías.
* No se ha modularizado todavía código común en `src/empkg/`. Aplazado para el final de la Fase 1.

---

## Próximas tareas

### Fase 0 — Setup y exploración inicial ✅ Completada

* [x] Crear entorno conda `empkg` con dependencias base.
* [x] Descargar `emp_qiime_mapping_subset_2k.tsv`.
* [x] Descargar `emp_deblur_90bp.subset_2k.rare_5000.biom`.
* [x] Crear y ejecutar `inspect_data.py`.
* [x] Crear y ejecutar `inspect_missing_values.py`.
* [x] Crear `notebooks/00_explore_biom.ipynb`.
* [x] Validar coincidencia exacta de IDs entre BIOM y mapping file.
* [x] Documentar diferencias entre muestra, lectura, ASV y abundancia.
* [ ] Intentar descargar `empo_v3.csv` o encontrar una fuente alternativa. No bloqueante.

### Fase 1A — Tabla base de muestras ✅ Completada

* [x] Cargar mapping file con normalización controlada de valores ausentes.
* [x] Convertir columnas numéricas relevantes.
* [x] Cargar el BIOM con `biom.load_table()`.
* [x] Construir `sample_stats` (`biom_total_reads`, `biom_observed_asvs`).
* [x] Validar IDs entre mapping file y BIOM.
* [x] Cruzar mapping file + estadísticas BIOM.
* [x] Seleccionar columnas relevantes para el KG inicial.
* [x] Validar la tabla final.
* [x] Exportar `data/processed/sample_table.csv`.

### Fase 1B — Diseño y construcción del RDF v0 ✅ Completada

* [x] Análisis dirigido de `sample_table.csv` en `notebooks/01_analyze_sample_table.ipynb`.
* [x] Validar `sample_id`, tipos de datos y cobertura sobre el artefacto final.
* [x] Comprobar consistencia jerárquica `empo_1`/`empo_2`/`empo_3`.
* [x] Analizar duplicidad de coordenadas → decidido: `Location` compartida y deduplicada.
* [x] Seleccionar subconjunto de 17 muestras representativas (`kg_v0_test_samples.csv`).
* [x] Redactar `docs/kg_design_v0.md`.
* [x] Definir prefijos, clases y relaciones iniciales del modelo RDF.
* [x] Crear y ejecutar `notebooks/03_to_rdf.ipynb` (exploración y validación).
* [x] Crear `scripts/csv_to_rdf.py` (pipeline reproducible).
* [x] Generar `data/processed/empkg_v0_test.ttl`.
* [x] Validar el Turtle: parseo sin errores, 17 `Sample`, relaciones completas, 0 literales problemáticos.

### Fase 1C — GraphDB/SPARQL sobre KG v0 ← siguiente

* [ ] Crear o terminar de configurar el repositorio EMPKG-lite en GraphDB.
* [ ] Cargar `empkg_v0_test.ttl` en GraphDB.
* [ ] Verificar integridad básica con consultas SPARQL:
  * contar tripletas totales;
  * listar clases presentes;
  * listar 17 `Sample` con su `EMPOCategory`;
  * verificar que las 4 relaciones principales existen para cada muestra.
* [ ] Documentar resultados y limitaciones del KG v0.
* [ ] Decidir si escalar a las 2.000 muestras antes de pasar a la fase de ASVs.

### Fase 1D — Datos microbianos: ASVs, taxonomía y abundancias

* [ ] Crear `scripts/build_asv_table.py`: extrae todos los ASVs del BIOM con su taxonomía en 7 niveles.
* [ ] Generar `data/processed/asv_table.csv` (una fila por ASV).
* [ ] Analizar `asv_table.csv` en un notebook: cobertura taxonómica, distribución por filo, ASVs dominantes.
* [ ] Crear `scripts/build_abundance_table.py`: extrae pares muestra–ASV con sus lecturas.
* [ ] Generar `data/processed/abundance_table.csv`.
* [ ] Analizar abundancias: distribución de cola larga, filtrado de singletons, ASVs por muestra.
* [ ] Usar los resultados para redactar `docs/kg_design_v1.md`.

### Fase 1E — Modularización ligera (al final de la Fase 1)

* [ ] Identificar funciones realmente repetidas entre scripts estables.
* [ ] Crear estructura `src/empkg/` solo cuando haya funciones suficientemente consolidadas.
* [ ] Mover funciones comunes sin romper la ejecución actual.

### Fase 2 — Mapeo a ontologías externas y LLM (posterior)

* [ ] Diseñar prompts para mapear campos ambientales (`env_biome`, `env_feature`, `env_material`) a términos ENVO reales.
* [ ] Empezar con un subconjunto pequeño de valores únicos, no con las 2.000 muestras.
* [ ] Guardar resultados en tabla intermedia revisable.
* [ ] No insertar resultados LLM directamente en el KG sin validación manual parcial.
* [ ] Mapear `country` a URIs GAZ o Wikidata.
* [ ] Mapear taxonomía de ASVs a URIs NCBITaxon.

---

## Artefacto generado: `sample_table.csv`

`data/processed/sample_table.csv` es el primer artefacto procesado reproducible del proyecto.

Fue generado por `scripts/build_sample_table.py` a partir de:

* mapping file TSV: metadatos ambientales de muestra.
* BIOM: estadísticas agregadas por muestra.

### Propósito

La tabla sirve como base para construir el primer Knowledge Graph mínimo, centrado en muestras, estudios, localización y ambiente.

No incluye todavía relaciones muestra-ASV. Esas relaciones se generarán más adelante en una tabla separada (`abundance_table.csv`).

### Estructura conceptual

Cada fila representa una muestra del EMP:

```text
1 fila = 1 sample_id = 1 muestra real
```

`sample_id` se mantiene como índice de la tabla y será el futuro nodo `empkg:Sample`.

`study_id` se mantiene como columna normal y se convierte en nodo `empkg:Study` en el KG.

### Columnas principales

* Identidad: `study_id`
* Clasificación EMPO: `empo_1`, `empo_2`, `empo_3`
* Descripción ambiental: `env_biome`, `env_feature`, `env_material`, `envo_biome_0`–`envo_biome_3`
* Localización: `country`, `latitude_deg`, `longitude_deg`, `depth_m`, `altitude_m`, `elevation_m`
* Mediciones físico-químicas: `temperature_deg_c`, `ph`, `salinity_psu`, `oxygen_mg_per_l`
* Estadísticas BIOM: `biom_total_reads`, `biom_observed_asvs`

### Validaciones realizadas

El script valida que el índice es `sample_id`, que no hay duplicados, que los IDs coinciden entre mapping file y BIOM, que `biom_total_reads = 5000` en todas las muestras y que `biom_observed_asvs` es positivo.

---

## Artefacto generado: `empkg_v0_test.ttl`

`data/processed/empkg_v0_test.ttl` es el primer artefacto RDF/Turtle del proyecto y cierra formalmente el hito RDF v0.

Fue generado por `scripts/csv_to_rdf.py` a partir de `data/samples/kg_v0_test_samples.csv`.

El notebook `notebooks/03_to_rdf.ipynb` sirve como documentación didáctica del proceso de desarrollo de ese script.

### Contenido del grafo

| Métrica                           | Valor |
| --------------------------------- | ----- |
| Triples totales                   | 588   |
| `empkg:Sample`                    | 17    |
| `empkg:Study`                     | 15    |
| `empkg:Location`                  | 15    |
| `empkg:EMPOCategory`              | 17    |
| `empkg:EnvironmentDescription`    | 17    |
| `empkg:belongsToStudy`            | 17    |
| `empkg:wasCollectedAt`            | 17    |
| `empkg:hasEMPOCategory`           | 17    |
| `empkg:hasEnvironmentDescription` | 17    |
| Literales problemáticos           | 0     |

El número de estudios (15) es menor que el de muestras (17) porque varias muestras comparten `study_id`. El número de localizaciones (15) es también menor porque `Location` se deduplica mediante hash de la clave geográfica.

### Validaciones realizadas

* Parseo correcto con `rdflib`.
* 17 `Sample`, cada uno con las 4 relaciones principales.
* No se generan triples para valores ausentes.
* URIs de `Location` son deterministas (hash SHA-256 abreviado).
* Si faltan latitud o longitud, se añade `sample_id` como fallback.
* Probado también sobre las 2.000 muestras de `sample_table.csv`.

---

## Flujo de trabajo aplicado hasta ahora

```text
Datos EMP brutos
    ↓
Inspección del mapping file y BIOM (inspect_data.py, inspect_missing_values.py)
    ↓
Normalización de valores ausentes + construcción de sample_table.csv (build_sample_table.py)
    ↓
Análisis dirigido y selección de 17 muestras (01_analyze_sample_table.ipynb)
    ↓
Diseño RDF v0 (docs/kg_design_v0.md)
    ↓
Exploración y validación del modelo RDF (notebooks/03_to_rdf.ipynb)
    ↓
Conversión reproducible CSV → RDF/Turtle (scripts/csv_to_rdf.py)
    ↓
Generación y validación de empkg_v0_test.ttl
    ↓
[siguiente] Carga en GraphDB y consultas SPARQL de validación
    ↓
[siguiente] Extracción de ASVs, taxonomía y abundancias
    ↓
[posterior] Diseño RDF v1 con nodos ASV/Taxon
    ↓
[posterior] Mapeo ambiental a ENVO, potencialmente asistido por LLM y validado.
            Mapeo geográfico a GAZ/Wikidata.
            Mapeo taxonómico a NCBITaxon mediante búsqueda controlada y validación.
```

---

## Registro de avances

| Fecha        | Avance                                                                                                                                            |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| *(sem. 1-3)* | Setup del entorno. Descarga de datos EMP iniciales. Creación de `inspect_data.py`.                                                                |
| *(sem. 4+)*  | Creación de `inspect_missing_values.py`. Desarrollo de `build_sample_table.py`. Exploración del BIOM en `notebooks/00_explore_biom.ipynb`.        |
| 2026-07-11   | Completado `notebooks/03_to_rdf.ipynb`: primer RDF/Turtle v0 generado y validado desde `kg_v0_test_samples.csv`.                                  |
| 2026-07-19   | Completado `scripts/csv_to_rdf.py`: pipeline reproducible CSV → RDF/Turtle. Hito RDF v0 cerrado. Prueba también exitosa sobre las 2.000 muestras. |

> Añadir filas con fecha concreta al ir avanzando.

---

## Hallazgos de la inspección

Resultado de ejecutar `inspect_data.py` sobre el subset_2k.

### Estructura HDF5 del BIOM

```
/observation/ids               (155002,)      — IDs de ASVs (= secuencias nucleotídicas Deblur)
/observation/metadata/taxonomy (155002, 7)    — 7 niveles taxonómicos por ASV
/observation/matrix/ — representación dispersa orientada a observaciones
/sample/matrix/      — representación dispersa orientada a muestras
/sample/ids                    (2000,)        — IDs de muestras
/sample/metadata/              — VACÍO        — metadatos en mapping file TSV
```

### Dimensiones del BIOM

| Métrica               | Valor   |
| --------------------- | ------- |
| ASVs (observaciones)  | 155.002 |
| Muestras              | 2.000   |
| Valores no nulos      | 858.173 |
| Densidad de la matriz | 0,28%   |

### Distribución ambiental (EMPO)

| Nivel  | Categorías principales                                                      |
| ------ | --------------------------------------------------------------------------- |
| empo_1 | Host-associated (1.019), Free-living (981)                                  |
| empo_2 | Animal (640), Non-saline (595), Saline (386), Plant (379)                   |
| empo_3 | 17 tipos; los más frecuentes: Animal surface (143), Soil (non-saline) (129) |

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

### Taxonomía de ASVs

Los metadatos de observación contienen un campo `taxonomy` con 7 niveles (reino → especie) en notación Greengenes (`k__`, `p__`, `c__`, `o__`, `f__`, `g__`, `s__`). El nivel de especie suele estar vacío.

### Validación de IDs

Todos los IDs de muestra coinciden exactamente entre BIOM y mapping file (2.000/2.000). No hay muestras huérfanas en ninguna de las dos fuentes.

---

## Scripts del proyecto

### `scripts/download_data.py`
Descarga los dos archivos iniciales del EMP si no existen localmente.

### `scripts/inspect_data.py`
Inspecciona mapping file, BIOM, estructura HDF5 y valida IDs. Exporta CSVs de diagnóstico.

### `scripts/inspect_missing_values.py`
Detecta marcadores no estándar de valores ausentes en el mapping file.

### `scripts/build_sample_table.py`
Pipeline reproducible. Construye `data/processed/sample_table.csv`.

### `scripts/csv_to_rdf.py` ✅
Pipeline reproducible. Transforma un CSV de muestras compatible en RDF/Turtle.
Entrada por defecto: `data/samples/kg_v0_test_samples.csv`.
Salida: `data/processed/empkg_v0_test.ttl`.
Probado también sobre `data/processed/sample_table.csv` (2.000 muestras).

### `notebooks/00_explore_biom.ipynb`
Notebook exploratorio del formato BIOM, HDF5 y `biom-format`. No es pipeline final.

### `notebooks/01_analyze_sample_table.ipynb`
Notebook de análisis dirigido sobre `sample_table.csv`. Valida cobertura, tipos de datos, consistencia EMPO y selección del subconjunto.

### `notebooks/03_to_rdf.ipynb`
Notebook de exploración y desarrollo del modelo RDF v0. Documenta el proceso de diseño de `csv_to_rdf.py`. No es el script de producción; sirve como evidencia didáctica.

**Uso del pipeline reproducible:**
```bash
conda activate empkg
python scripts/download_data.py
python scripts/build_sample_table.py
python scripts/csv_to_rdf.py
```

---

## Decisiones técnicas tomadas

| Decisión                                                    | Alternativas descartadas                      | Motivo                                                                                         |
| ----------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Usar ASVs de Deblur (no OTUs)                               | Greengenes 13.8, Silva 123                    | Los ASVs son el estándar actual; mayor resolución taxonómica                                   |
| Subconjunto 2k muestras para exploración                    | 5k, 10k, dataset completo                     | Manejable para Fase 0; escalar después                                                         |
| Python 3.11 como versión base                               | 3.12, 3.13                                    | Mayor estabilidad con `biom-format` y `h5py` en bioinformática                                 |
| Miniconda con solver libmamba                               | pip, poetry, venv                             | Mejor compatibilidad con paquetes bioinformáticos                                              |
| Usar Deblur 90bp, rarefaccionado a 5000                     | otros parámetros                              | Equilibrio entre resolución y manejabilidad                                                    |
| Separar exploración (notebook) de pipeline (scripts)        | hacer todo en notebook                        | El notebook sirve para aprender y validar; la lógica estable pasa a scripts                    |
| No convertir la matriz BIOM completa a denso                | `table.to_dataframe(dense=True)`              | Inviable en memoria (155.002 × 2.000); se usan operaciones dispersas                           |
| Usar `biom-format` como interfaz principal                  | Leer el HDF5 directamente con `h5py`          | `biom-format` abstrae la complejidad y ofrece métodos validados                                |
| Usar `h5py` solo para inspección estructural                | Reemplazar `biom-format` por `h5py` puro      | `h5py` es útil para depuración, `biom-format` es más seguro para el pipeline                   |
| Usar GraphDB + SPARQL en vez de Neo4j + Cypher              | Neo4j + Cypher (propuesta inicial)            | Indicación del tutor; las ontologías ENVO/NCBITaxon/GAZ son RDF/OWL nativo                     |
| Desarrollar primero RDF v0 en notebook, luego script        | Crear directamente un script cerrado          | El notebook permitió aprender RDF/RDFLib y depurar decisiones antes de consolidar              |
| Aplazar modularización (`src/empkg/`) al final de la Fase 1 | Modularizar inmediatamente                    | No tiene sentido modularizar antes de tener varios scripts estables con funciones reutilizadas |
| URIs de `Location` con hash SHA-256 abreviado               | Identificadores basados en coordenadas planas | El hash es determinista, compacto y evita problemas con caracteres especiales en URIs          |
| Fallback `sample_id` en URI de `Location` si faltan lat/lon | Generar nodo Location sin clave geográfica    | Evita fusionar muestras sin evidencia suficiente de que pertenecen al mismo lugar              |

---

## Dudas abiertas

- [ ] **`empo_v3.csv` inaccesible:** el servidor devuelve 404 para v3 y 403 para v2. ¿Dónde conseguir la ontología EMPO actualizada? Opciones: repositorio GitHub de EMP, Qiita, contactar con autores.
- [ ] **¿Es necesario EMPO ahora?** El fichero EMPO no es bloqueante para el KG v0. Será útil en fases
posteriores si se desea incorporar formalmente su jerarquía o aprovechar
sus correspondencias con ENVO.
- [ ] **Extensión del TFG:** ¿A/B/C? Decidir antes del mes 4 según el ritmo de avance.
- [x] **Motor de grafos: decidido GraphDB + SPARQL.** Indicación del tutor. Implica RDF/Turtle con `rdflib`, consultas SPARQL y compatibilidad nativa con ontologías ENVO/NCBITaxon/GAZ.
- [ ] **¿Cargar primero el RDF v0 de 17 muestras o la versión de 2.000 muestras?** El script ya funciona con ambas entradas; decidir antes de configurar GraphDB.
- [ ] **Cómo representar la relación muestra–ASV en el KG:** relación directa `Sample → ASV`, relación colapsada `Sample → Taxon`, o nodo intermedio `TaxonOccurrence`. Afecta directamente al tamaño del grafo (858.173 valores no nulos si se modela 1:1). Pendiente para `docs/kg_design_v1.md`.
- [ ] **¿Conviene filtrar ASVs por abundancia o prevalencia antes del KG?** Descartar singletons (38.892 ASVs) reduciría el ruido. Pendiente de decidir el umbral.
- [ ] **Qué partes modularizar en `src/empkg/`:** candidatas identificadas, pero estructura concreta aplazada al final de la Fase 1.
- [ ] **Pipeline LLM:** aplazado hasta tener KG v0 cargado en GraphDB y datos taxonómicos analizados. No se tocará hasta entonces.
- [ ] **`biom_total_reads` constante:** decidir si mantenerlo como propiedad de cada `Sample` o si pasarlo a metadato del dataset en la v1.

---

## Conceptos clave: muestra, lectura, ASV y abundancia

Es importante distinguir estos cuatro conceptos para el diseño del KG:

- **Muestra (`Sample`):** unidad ambiental o biológica recogida en el mundo real. Es la unidad fundamental del mapping file y de uno de los dos ejes del BIOM.
- **Lectura (`read`):** secuencia individual generada por el secuenciador. Unidad bruta antes de cualquier clasificación.
- **ASV (Amplicon Sequence Variant):** variante de secuencia exacta. En Deblur, el ID del ASV *es* la secuencia nucleotídica. **Un ASV no es un taxón**: es una secuencia a la que se le asigna una clasificación taxonómica. Esa distinción es clave para el diseño del KG v1.
- **Abundancia:** número de lecturas de una muestra asignadas a un ASV concreto. Es una propiedad de la *relación* muestra–ASV, no del ASV en sí.

**Aplicado al fichero `rare_5000`:**
- Todas las muestras tienen exactamente 5.000 lecturas (`biom_total_reads` constante = 5.000).
- El número de ASVs *distintos* observados varía mucho entre muestras (de 1 a 2.438).
- `biom_observed_asvs` refleja riqueza microbiana, no total de lecturas.

---

## Estrategia de tablas para el KG

| Tabla                 | Script                     | Qué contiene                                                                            | Estado    |
| --------------------- | -------------------------- | --------------------------------------------------------------------------------------- | --------- |
| `sample_table.csv`    | `build_sample_table.py`    | Una fila por muestra: metadatos, localización, mediciones, estadísticas BIOM            | ✅ Listo   |
| `asv_table.csv`       | `build_asv_table.py`       | Una fila por ASV: secuencia, taxonomía en 7 niveles, rango taxonómico más bajo conocido | Pendiente |
| `abundance_table.csv` | `build_abundance_table.py` | Una fila por par muestra–ASV: lecturas y abundancia relativa                            | Pendiente |

**Diseño del KG v0** (implementado): basado solo en `sample_table.csv`.
**Diseño del KG v1** (pendiente): incorporará `asv_table.csv` y `abundance_table.csv`, con nodos para ASVs y sus asignaciones taxonómicas.

---

## Notas sobre EMP y sus datos

### Resumen del proyecto EMP

El EMP Release 1 contiene ~25.000 muestras de 97 estudios (Thompson et al., *Nature* 2017, doi: `10.1038/nature24621`). Los datos están en el FTP: `https://ftp.microbio.me/emp/release1/`. El subset de 2k muestras es una submuestra estratificada representativa.

Repo oficial: https://github.com/biocore/emp

### Archivos descargados

| Archivo                                    | Ruta local                                 | Descripción                 |
| ------------------------------------------ | ------------------------------------------ | --------------------------- |
| `emp_qiime_mapping_subset_2k.tsv`          | `data/raw/emp/release1/mapping_files/`     | Metadatos de 2.000 muestras |
| `emp_deblur_90bp.subset_2k.rare_5000.biom` | `data/raw/emp/release1/otu_tables/deblur/` | Tabla de abundancias ASVs   |

---

## Notas sobre BIOM / HDF5

### HDF5
Hierarchical Data Format. Organiza grandes volúmenes de datos con **Datasets** (arrays multidimensionales) y **Grupos** (contenedores jerárquicos).

### BIOM 2.x
Almacena la tabla de abundancias como matriz dispersa dentro de un HDF5. La forma estándar de abrirlo en Python es `biom.load_table()`.

Especificación: https://biom-format.org/documentation/format_versions/biom-2.1.html

### OTUs vs ASVs
- **OTUs:** agrupan secuencias al 97% de similitud. Metodología más antigua.
- **ASVs:** representan secuencias exactas. Estándar actual. En Deblur, el ID es la propia secuencia nucleotídica.

### Rarefacción
Normalización que submuestrea todas las muestras al mismo número de lecturas (aquí: 5.000). El coste es que las muestras con pocas lecturas se eliminan.

---

## Notas sobre ontologías

### EMPO (EMP Ontology)
Clasificación jerárquica de tipos de entorno propia del EMP. Los campos `empo_3` del mapping file asignan cada muestra a un nodo EMPO. Archivo `empo_v3.csv` inaccesible actualmente.

### ENVO (Environment Ontology)
Ontología estándar de entornos ambientales. Se usará en fases posteriores para normalizar metadatos.

### Otras ontologías previstas

| Ontología | Dominio                 |
| --------- | ----------------------- |
| NCBITaxon | Taxonomía microbiana    |
| GAZ       | Geografía / ubicaciones |
| CHEBI     | Sustancias químicas     |

---

## Entorno y configuración

| Elemento             | Valor                                              |
| -------------------- | -------------------------------------------------- |
| Gestor de entornos   | Miniconda 25.11.1 con solver libmamba              |
| Entorno del proyecto | `empkg` (Python 3.11)                              |
| Canales conda        | conda-forge > bioconda > defaults                  |
| Dependencias base    | `biom-format`, `h5py`, `pandas`, `numpy`, `rdflib` |

```bash
# Reproducir entorno desde cero
conda env create -f environment.yml
conda activate empkg
```

## Estructura del repositorio

```text
empkg-lite/
├── data/
│   ├── raw/emp/release1/       # Datos originales (en .gitignore)
│   ├── inspection/             # CSVs de diagnóstico
│   ├── processed/              # Artefactos procesados (sample_table.csv, empkg_v0_test.ttl)
│   └── samples/                # Subconjuntos de prueba (kg_v0_test_samples.csv)
├── notebooks/                  # Exploración interactiva (no son el pipeline reproducible)
├── scripts/                    # Pipeline reproducible
├── docs/                       # Memoria y documentación
├── src/empkg/                  # Código modular (pendiente, al final de Fase 1)
└── tests/                      # Tests básicos
```

---

## Recursos útiles

### EMP y datos microbianos
- Repo oficial EMP: https://github.com/biocore/emp
- FTP EMP Release 1: `https://ftp.microbio.me/emp/release1/`
- Thompson et al. 2017: doi `10.1038/nature24621`

### BIOM / HDF5
- Documentación biom-format: https://biom-format.org/documentation/format_versions/biom-2.1.html
- Repo biom-format Python: https://github.com/biocore/biom-format

### Ontologías
- ENVO: https://obofoundry.org/ontology/envo.html
- NCBITaxon: https://obofoundry.org/ontology/ncbitaxon.html
- CHEBI: https://www.ebi.ac.uk/chebi/

### Documentación Python
- `help(biom)` en intérprete Python para API de biom-format.
