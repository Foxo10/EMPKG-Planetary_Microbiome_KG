# Diario técnico del TFG EMPKG-lite
> Documento vivo de seguimiento del TFG.

---

## Estado actual del proyecto

**Fase:** 1B completada a nivel de notebook → primer RDF/Turtle v0 generado y validado.

La exploración inicial de datos, la generación de `data/processed/sample_table.csv`, el análisis dirigido de ese artefacto y el diseño conceptual del KG v0 están completados. Además, se ha desarrollado `notebooks/03_to_rdf.ipynb`, que transforma el subconjunto `data/samples/kg_v0_test_samples.csv` en un primer grafo RDF/Turtle validable.

El siguiente paso inmediato es consolidar la lógica estable del notebook en `scripts/03_to_rdf.py`, para que la generación de RDF no dependa de la ejecución manual del notebook.

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
* Creado y ejecutado `notebooks/01_analyze_sample_table.ipynb`: valida `sample_id`,
  tipos de datos, cobertura, jerarquía EMPO, coordenadas duplicadas y campos
  fisicoquímicos sobre el artefacto final (no sobre el mapping crudo).
* Seleccionado `data/samples/kg_v0_test_samples.csv`: 17 muestras, una por cada categoría `empo_3`, elegidas de forma determinista por completitud de campos (no muestreo aleatorio).
* Redactado `docs/kg_design_v0.md` con el diseño v0: entidades `Sample`, `Study`, `Location`, `EMPOCategory`, `EnvironmentDescription`.
* Creado y ejecutado `notebooks/03_to_rdf.ipynb`: convierte `kg_v0_test_samples.csv` a RDF/Turtle usando `rdflib`.
* Generado `data/processed/empkg_v0_test.ttl` como primer Turtle de prueba del KG v0.
* Implementadas funciones de limpieza, sanitización de URIs, construcción de nodos RDF y generación de literales tipados.
* Validado el RDF generado: parseo correcto con `rdflib`, 17 `Sample`, 17 `EMPOCategory`, 17 `EnvironmentDescription`, 15 `Study`, 15 `Location`, 17 relaciones principales de cada tipo y 0 literales problemáticos.

**Lo que está en curso:**

* Preparar `scripts/03_to_rdf.py` a partir de la lógica ya estabilizada en `notebooks/03_to_rdf.ipynb`.
* Mantener el notebook como evidencia didáctica y de validación, pero pasar la generación final del RDF a un script reproducible.

**Decisiones de nomenclatura cerradas en esta fase:**

* Relación `Sample -> EMPOCategory`: se descarta `classifiedAs` y se fija
  `empkg:hasEMPOCategory`, por consistencia de patrón con `hasEnvironmentDescription`.
* Sección "Relaciones principales" añadida a `docs/kg_design_v0.md`, con las 4
  relaciones de v0 (`belongsToStudy`, `wasCollectedAt`, `hasEMPOCategory`,
  `hasEnvironmentDescription`), su dominio/rango y cardinalidad.
* Terminología residual `EnvironmentalFeature` eliminada de
  `01_analyze_sample_table.ipynb` (celdas de comprobación EMPO y de candidatos),
  sustituida por `EMPOCategory` en todo el notebook.

**Lo que NO está hecho aún:**

* No se ha creado todavía `scripts/03_to_rdf.py` como pipeline reproducible independiente del notebook.
* No se ha configurado todavía GraphDB.
* No se ha cargado todavía el Turtle generado en GraphDB.
* No se han escrito todavía consultas SPARQL sobre el KG v0.
* No se ha construido todavía `taxonomy_table.csv`.
* No se ha construido todavía `abundance_table.csv`.
* No se ha realizado todavía procesamiento LLM ni mapeo automático a ontologías.
* No se ha modularizado todavía código común en `src/empkg/`.


---

## Próximas tareas

### Fase 0 — Setup y exploración inicial

* [x] Crear entorno conda `empkg` con dependencias base.
* [x] Descargar `emp_qiime_mapping_subset_2k.tsv`.
* [x] Descargar `emp_deblur_90bp.subset_2k.rare_5000.biom`.
* [x] Crear y ejecutar `inspect_data.py`.
* [x] Crear y ejecutar `inspect_missing_values.py`.
* [x] Crear `notebooks/00_explore_biom.ipynb`.
* [x] Validar coincidencia exacta de IDs entre BIOM y mapping file.
* [x] Documentar diferencias entre muestra, lectura, ASV y abundancia.
* [ ] Intentar descargar `empo_v3.csv` o encontrar una fuente alternativa. No bloqueante.

### Fase 1A — Tabla base de muestras

* [x] Cargar mapping file con normalización controlada de valores ausentes.
* [x] Convertir columnas numéricas relevantes.
* [x] Cargar el BIOM con `biom.load_table()`.
* [x] Construir `sample_stats`:

  * `biom_total_reads`
  * `biom_observed_asvs`
* [x] Validar IDs entre mapping file y BIOM.
* [x] Cruzar mapping file + estadísticas BIOM.
* [x] Seleccionar columnas relevantes para el KG inicial.
* [x] Validar la tabla final.
* [x] Exportar `data/processed/sample_table.csv`.

### Fase 1B-preliminar — Análisis dirigido de sample_table.csv
- [x] Crear y ejecutar notebooks/01_analyze_sample_table.ipynb
- [x] Validar sample_id, tipos de datos y cobertura sobre el artefacto final
- [x] Comprobar consistencia jerárquica empo_1/empo_2/empo_3
- [x] Analizar duplicidad de coordenadas → decidido: Location compartida y deduplicada
- [x] Seleccionar subconjunto representativo para el RDF de prueba
      (17 muestras, una por categoría empo_3 — cobertura completa en vez de 5-10 arbitrarias)
- [x] Redactar docs/kg_design_v0.md con las conclusiones del notebook,
      incluida la sección "Relaciones principales"

### Fase 1B — Diseño RDF mínimo desde `sample_table.csv`

* [x] Crear `docs/kg_design_v0.md` (ver Fase 1B-preliminar).
* [x] Definir prefijos iniciales:

  * `empkg:`
  * `sample:`
  * `study:`
  * `loc:`
  * `empo:`
  * `envdesc:`
  * `rdf:`
  * `rdfs:`
  * `xsd:`
  * `schema:`
* [x] Definir clases iniciales:

  * `empkg:Sample`
  * `empkg:Study`
  * `empkg:Location`
  * `empkg:EnvironmentDescription`
  * `empkg:EMPOCategory`
* [x] Definir relaciones iniciales:

  * `empkg:belongsToStudy`
  * `empkg:wasCollectedAt`
  * `empkg:hasEMPOCategory`
  * `empkg:hasEnvironmentDescription`
* [x] Crear y ejecutar `notebooks/03_to_rdf.ipynb`.
* [x] Generar RDF/Turtle de prueba con las 17 muestras de `kg_v0_test_samples.csv`.
* [x] Generar `data/processed/empkg_v0_test.ttl`.
* [x] Validar el Turtle con `rdflib` (parseo sin errores, 17 `Sample`, 17 `EMPOCategory`, relaciones completas, sin triples para valores ausentes).
* [ ] Crear `scripts/03_to_rdf.py` a partir del notebook.

### Fase 1C — Consolidación y modularización ligera

* [ ] Crear `scripts/03_to_rdf.py` con la lógica estable de `notebooks/03_to_rdf.ipynb`.
* [ ] Ejecutar el script desde cero y comprobar que genera el mismo `empkg_v0_test.ttl`.
* [ ] Identificar funciones repetidas entre scripts.
* [ ] Crear estructura inicial `src/empkg/` solo cuando haya funciones suficientemente estables.
* [ ] Mover funciones comunes sin romper la ejecución actual.
* [ ] Añadir imports desde scripts sin romper la ejecución actual.

### Fase 1D — Normalización con LLM

* [ ] Diseñar prompts para mapear campos ambientales a términos ontológicos.
* [ ] Empezar con un subconjunto pequeño de valores únicos, no con las 2.000 muestras completas.
* [ ] Mapear progresivamente:

  * `env_biome`
  * `env_feature`
  * `env_material`
  * `empo_3`
* [ ] Guardar resultados en una tabla intermedia revisable.
* [ ] No insertar resultados LLM directamente en el KG sin validación manual parcial.

### Fase 2 — GraphDB/SPARQL

* [ ] Decidir si se carga primero el RDF v0 de 17 muestras o una versión ampliada generada desde `sample_table.csv` completo.
* [ ] Instalar y configurar GraphDB.
* [ ] Crear repositorio local EMPKG-lite.
* [ ] Cargar RDF/Turtle inicial.
* [ ] Escribir consultas SPARQL básicas.
* [ ] Documentar resultados y limitaciones.


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

`study_id` se mantiene como columna normal y podrá convertirse en nodo `empkg:Study` o en propiedad de la muestra.

### Columnas principales

La tabla contiene:

* Identidad:

  * `study_id`
* Clasificación EMPO:

  * `empo_1`
  * `empo_2`
  * `empo_3`
* Descripción ambiental:

  * `env_biome`
  * `env_feature`
  * `env_material`
  * `envo_biome_0`
  * `envo_biome_1`
  * `envo_biome_2`
  * `envo_biome_3`
* Localización:

  * `country`
  * `latitude_deg`
  * `longitude_deg`
  * `depth_m`
  * `altitude_m`
  * `elevation_m`
* Mediciones físico-químicas:

  * `temperature_deg_c`
  * `ph`
  * `salinity_psu`
  * `oxygen_mg_per_l`
* Estadísticas derivadas del BIOM:

  * `biom_total_reads`
  * `biom_observed_asvs`

### Validaciones realizadas

El script valida que:

* El índice se llama `sample_id`.
* No hay `sample_id` duplicados.
* Los IDs coinciden entre mapping file y BIOM.
* Todas las muestras tienen `biom_total_reads = 5000`, coherente con el fichero `rare_5000`.
* `biom_observed_asvs` tiene valores positivos.
* Las columnas numéricas relevantes se han convertido correctamente.

### Interpretación

`sample_table.csv` permite construir un KG inicial sin introducir todavía toda la complejidad de las abundancias muestra-ASV.

El primer KG puede modelar:

```text
Sample → belongsToStudy → Study
Sample → wasCollectedAt → Location
Sample → hasEMPOCategory → EMPOCategory
Sample → hasEnvironmentDescription → EnvironmentDescription
```

Las relaciones con ASVs y taxones se dejarán para fases posteriores, a partir de `taxonomy_table.csv` y `abundance_table.csv`.


---

## Artefacto generado: `empkg_v0_test.ttl`

`data/processed/empkg_v0_test.ttl` es el primer artefacto RDF/Turtle del proyecto.

Fue generado por `notebooks/03_to_rdf.ipynb` a partir de:

* `data/samples/kg_v0_test_samples.csv`: subconjunto de 17 muestras, una por cada categoría `empo_3`.
* `docs/kg_design_v0.md`: diseño conceptual del KG v0.

### Propósito

El Turtle sirve como prueba controlada del modelo RDF v0. No pretende representar todavía el EMP completo ni incluir ASVs, taxones o abundancias. Su objetivo es validar que las entidades, relaciones, URIs, literales tipados y reglas de ausencia funcionan correctamente antes de escalar a más muestras.

### Contenido del grafo generado

Validación obtenida en el notebook:

| Métrica | Valor |
| ------- | ----- |
| Triples totales | 588 |
| `empkg:Sample` | 17 |
| `empkg:Study` | 15 |
| `empkg:Location` | 15 |
| `empkg:EMPOCategory` | 17 |
| `empkg:EnvironmentDescription` | 17 |
| `empkg:belongsToStudy` | 17 |
| `empkg:wasCollectedAt` | 17 |
| `empkg:hasEMPOCategory` | 17 |
| `empkg:hasEnvironmentDescription` | 17 |
| Literales problemáticos (`nan`, `None`, vacío, `unknown`) | 0 |

El número de estudios no coincide con 17 porque varias muestras pueden compartir `study_id`. El número de localizaciones tampoco tiene por qué coincidir con el número de muestras porque `Location` se deduplica mediante la clave geográfica.

### Validaciones realizadas

El notebook valida que:

* El CSV de entrada contiene 17 muestras y las columnas esperadas.
* No hay `sample_id` duplicados.
* Las 17 categorías `empo_3` están representadas.
* Las URIs generadas son deterministas y seguras para Turtle.
* Los campos ausentes no generan triples RDF.
* Los campos fisicoquímicos y geográficos se serializan como literales numéricos cuando existen.
* `biom_total_reads` y `biom_observed_asvs` se serializan como enteros.
* El Turtle generado puede parsearse de nuevo con `rdflib` sin errores.

### Interpretación

Este artefacto cierra la primera prueba completa CSV → RDF/Turtle del proyecto. La lógica ya está validada en notebook, pero todavía debe consolidarse en un script reproducible (`scripts/03_to_rdf.py`) antes de pasar a GraphDB o a fases más complejas.

---

## Flujo de trabajo aplicado hasta ahora

Resumen del pipeline tal como existe hoy, repartido entre notebooks de exploración y scripts reproducibles:

1. Descarga/carga de los dos ficheros EMP iniciales (mapping TSV + BIOM), con comprobación de existencia previa.
2. Inspección de la estructura HDF5 del BIOM con `h5py` (grupos, datasets, atributos).
3. Carga del BIOM con `biom-format` (`biom.load_table()`).
4. Extracción de IDs de muestra (`axis="sample"`) y de observación/ASV (`axis="observation"`).
5. Validación de coincidencia exacta de IDs entre BIOM y mapping file (incluye comprobación de espacios invisibles).
6. Normalización preliminar de valores ausentes en el mapping file, usando una lista controlada de marcadores no estándar (`""`, `"unknown"`, `"Missing: Not provided"`, etc.).
7. Conversión de columnas numéricas del mapping file (coordenadas, métricas físico-químicas, índices de diversidad) en `build_sample_table.py`.
8. Construcción de `sample_stats` (lecturas totales y ASVs observados por muestra) a partir del BIOM.
9. Join entre mapping file y `sample_stats`, validado por número de filas resultante.
10. Selección de `kg_v0_test_samples.csv`: 17 muestras representativas, una por cada `empo_3`.
11. Diseño RDF v0 en `docs/kg_design_v0.md`.
12. Conversión de `kg_v0_test_samples.csv` a RDF/Turtle en `notebooks/03_to_rdf.ipynb`.
13. Generación y validación de `data/processed/empkg_v0_test.ttl`.

El flujo ya demuestra la cadena completa CSV → RDF/Turtle en un subconjunto controlado. El siguiente paso es convertir la lógica del notebook `03_to_rdf.ipynb` en un script reproducible.

---

## Registro de avances
| Fecha        | Avance |
| ------------ | ------ |
| *(sem. 1-3)* | Setup del entorno. Descarga de datos EMP iniciales. Creación de `inspect_data.py`. |
| *(sem. 4+)*  | Creación de `inspect_missing_values.py`. Inicio de `build_sample_table.py` (carga, limpieza y conversión numérica del mapping file). Exploración completa del BIOM en `notebooks/00_explore_biom.ipynb` (estadísticas por eje, taxonomía, estructura HDF5, join exploratorio con mapping file). |
| 2026-07-11 | Completado `notebooks/03_to_rdf.ipynb`: generación del primer RDF/Turtle v0 desde `kg_v0_test_samples.csv`, validación local con `rdflib` y exportación de `data/processed/empkg_v0_test.ttl`. |

> Añadir filas con fecha concreta al ir avanzando.


---

## Hallazgos de la inspección (inspection.txt)

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

El BIOM 2.x almacena la matriz de abundancias en formato disperso y mantiene dos orientaciones internas para permitir acceso eficiente tanto por observaciones/ASVs como por muestras.

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

### `scripts/download_data.py`
Descarga los dos archivos iniciales del EMP si no existen localmente.

### `scripts/inspect_missing_values.py`
Detecta marcadores no estándar de valores ausentes en el mapping file.

### `scripts/build_sample_table.py`
Pipeline finalizado que construye `sample_table.csv` en `data/processed/`.

### `notebooks/00_explore_biom.ipynb`
Notebook exploratorio; no es pipeline final.

### `notebooks/01_analyze_sample_table.ipynb`
Notebook de análisis dirigido sobre `sample_table.csv`. Valida cobertura, tipos de datos, consistencia EMPO y selección del subconjunto `kg_v0_test_samples.csv`.

### `notebooks/03_to_rdf.ipynb`
Notebook de generación RDF v0. Convierte `kg_v0_test_samples.csv` en `empkg_v0_test.ttl`, define namespaces, crea el modelo RDF mínimo, genera nodos y relaciones con `rdflib`, valida conteos y comprueba que no se generan triples para valores ausentes.

### `scripts/03_to_rdf.py`
Pendiente. Debe consolidar la lógica estable de `notebooks/03_to_rdf.ipynb` en un script reproducible.

**Uso:**
```bash
conda activate empkg
python scripts/[nombre_del_script].py
```

---

## Decisiones técnicas tomadas
| Decisión                                             | Alternativas descartadas                             | Motivo                                                                                                                                                                                                                  |
| ---------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usar ASVs de Deblur (no OTUs)                        | Greengenes 13.8, Silva 123                           | Los ASVs son el estándar actual; mayor resolución taxonómica                                                                                                                                                            |
| Subconjunto 2k muestras para exploración             | 5k, 10k, dataset completo                            | Manejable para Fase 0; escalar después                                                                                                                                                                                  |
| Python 3.11 como versión base                        | 3.12, 3.13                                           | Mayor estabilidad con `biom-format` y `h5py` en bioinformática                                                                                                                                                          |
| Miniconda con solver libmamba                        | pip, poetry, venv                                    | Mejor compatibilidad con paquetes bioinformáticos (canales conda-forge, bioconda)                                                                                                                                       |
| Usar Deblur 90bp, rarefaccionado a 5000              | otros parámetros                                     | Equilibrio entre resolución y manejabilidad; rarefacción permite comparar muestras de forma justa                                                                                                                       |
| Separar exploración (notebook) de pipeline (scripts) | hacer todo en notebook                               | El notebook sirve para aprender y validar; solo la lógica estable y reproducible pasa a `build_sample_table.py` y futuros módulos en `src/empkg/`                                                                       |
| No convertir la matriz BIOM completa a denso         | `table.to_dataframe(dense=True)` sobre toda la tabla | Inviable en memoria (155.002 × 2.000); se usan operaciones dispersas (`sum`, `nonzero_counts`) o se extrae fila/columna individual cuando hace falta                                                                    |
| Usar `biom-format` como interfaz principal           | Leer el HDF5 directamente con `h5py` para todo       | `biom-format` abstrae la complejidad de la matriz dispersa (CSC/CSR) y ofrece métodos validados (`sum`, `nonzero_counts`, `metadata`)                                                                                   |
| Usar `h5py` solo para inspección estructural         | Reemplazar `biom-format` por `h5py` puro             | `h5py` es útil para entender/depurar la estructura interna, pero `biom-format` es más seguro y mantenible para el pipeline real                                                                                         |
| Usar GraphDB + SPARQL en vez de Neo4j + Cypher       | Neo4j + Cypher (propuesta inicial)                   | Indicación del tutor; las ontologías ENVO/NCBITaxon/GAZ ya son RDF/OWL nativo, lo que encaja directamente con GraphDB y permite inferencia; evita reimplementar jerarquías ontológicas a mano como en un property graph |
| Desarrollar primero RDF v0 en notebook antes de script | Crear directamente un script cerrado                  | El notebook ha permitido aprender RDF/RDFLib, validar cada bloque y depurar decisiones de modelado antes de consolidar código reproducible. |

---

## Dudas abiertas
- [ ] **`empo_v3.csv` inaccesible:** el servidor devuelve 404 para v3 y 403 para v2. ¿Dónde conseguir la ontología EMPO actualizada? Opciones a investigar: repositorio GitHub de EMP, Qiita, contactar con autores.
- [ ] **¿Es necesario EMPO ahora?** Para la Fase 0 no es bloqueante. Los campos `empo_3` del mapping file ya están codificados como cadenas de texto. EMPO será necesario cuando se mapee a ENVO.
- [ ] **Extensión del TFG:** ¿A/B/C? Decidir antes del mes 4 según el ritmo de avance. No es urgente ahora.
- [x] **Motor de grafos: decidido GraphDB + SPARQL.** Indicación explícita del tutor del TFG: sustituir Neo4j/Cypher por GraphDB/SPARQL en todo el proyecto. Implica trabajar en RDF (tripletas) en lugar de property graph, generar el grafo como Turtle (`.ttl`) con `rdflib`, y consultar con SPARQL (vía interfaz web de GraphDB o `SPARQLWrapper` desde Python). Ventaja clave: las ontologías objetivo (ENVO, NCBITaxon, GAZ) ya están publicadas en RDF/OWL, por lo que se integran de forma nativa y permiten razonamiento (RDFS/OWL-Horst), algo que no es nativo en Neo4j.
- [ ] **Cómo representar la relación muestra–ASV en el KG:** ¿relación directa `Sample -> contains -> ASV`, relación agregada `Sample -> contains -> Taxon` (colapsando por nivel taxonómico), o un nodo intermedio de tipo "observación" que cuelgue la abundancia como propiedad? Afecta directamente al tamaño del grafo (858.173 valores no nulos si se modela 1:1).
- [ ] **¿Conviene guardar todos los valores no cero del BIOM como relaciones del KG?** Con 858.173 valores no nulos y una distribución de cola larga (42,8% de ASVs en una sola muestra), modelar todo podría generar un grafo poco manejable para un TFG.
- [ ] **¿Conviene filtrar ASVs por abundancia o prevalencia antes de construir el grafo?** Por ejemplo, descartar singletons (38.892 ASVs con abundancia total = 1) podría reducir el ruido sin perder señal ecológica relevante. Pendiente de decidir el umbral.
- [ ] **Qué partes modularizar en `src/empkg/`:** candidatas identificadas en el notebook (`load_biom_table`, `build_biom_sample_stats`, `extract_taxonomy_preview`, `extract_abundance_for_sample`), pero la estructura concreta del paquete (`src/empkg/io/`, `src/empkg/cleaning/`, etc.) todavía no está decidida.
- [ ] Pipeline LLM queda formalmente aplazado hasta consolidar primero `scripts/03_to_rdf.py` y validar la carga básica del Turtle en GraphDB. No se tocará `scripts/02_llm_harmonize.py` hasta tener un flujo RDF reproducible.

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

## Notebook `00_explore_biom.ipynb`

Notebook exploratorio creado para familiarizarse con el formato BIOM, la librería `biom-format` y la estructura HDF5 subyacente, antes de consolidar la lógica estable en scripts. No es un pipeline final: es un espacio de aprendizaje y validación de conceptos.

**Qué hace el notebook, en orden:**

1. **Setup y rutas:** importa `biom`, `h5py`, `pandas`, `numpy`; detecta automáticamente la raíz del proyecto (funciona tanto desde `notebooks/` como desde la raíz).
2. **Descarga automática:** si `emp_qiime_mapping_subset_2k.tsv` o el `.biom` no existen localmente, los descarga del FTP del EMP con barra de progreso (`download_if_missing()`).
3. **Carga del BIOM:** `biom.load_table()` sobre el `.biom`. Resultado: tabla de 155.002 observaciones (ASVs) × 2.000 muestras, con 858.173 valores no nulos (densidad ≈ 0,28%).
4. **Ejes `sample` vs `observation`:** aclara que `axis="sample"` corresponde a las 2.000 muestras ambientales y `axis="observation"` a los 155.002 ASVs detectados por Deblur. En Deblur, el ID de cada ASV es la propia secuencia nucleotídica (90 pb), no un nombre legible.
5. **Metadatos de muestra vs. observación:** confirma que el BIOM **no** trae metadatos de muestra embebidos (están en el mapping file TSV, como es habitual en EMP), pero sí trae taxonomía por ASV en 7 niveles (`kingdom` → `species`, notación Greengenes con prefijos `k__`, `p__`, etc.).
6. **Estadísticas básicas por eje:**
   - `sample_sums` (`table.sum(axis="sample")`): lecturas totales por muestra. Confirmado: las 2.000 muestras tienen exactamente 5.000 lecturas, coherente con el sufijo `rare_5000` del fichero.
   - `observation_sums` (`table.sum(axis="observation")`): abundancia total por ASV. Distribución de cola larga: 38.892 ASVs son singletons (abundancia total = 1).
   - `observed_asvs_per_sample` (`table.nonzero_counts(axis="sample")`): nº de ASVs distintos por muestra. Mediana ≈ 246, rango 1–2.438.
   - `prevalence_per_asv` (`table.nonzero_counts(axis="observation")`): nº de muestras donde aparece cada ASV. El 42,8% de los ASVs aparece en una sola muestra.
7. **Tabla `sample_stats`:** construida con `sample_id`, `biom_total_reads`, `biom_observed_asvs`. Es el "puente" entre BIOM y mapping file.
8. **Taxonomía:** extrae taxonomía de observaciones vía `table.metadata(id=..., axis="observation")`; calcula cobertura por nivel taxonómico sobre una muestra aleatoria de 5.000 ASVs (kingdom 100%, phylum ≈ 88%, hasta species ≈ 1,7%); calcula distribución por filo ponderada por abundancia (Firmicutes y Proteobacteria dominan).
9. **Inspección HDF5 con `h5py`:** recorre la estructura interna del fichero (`/observation/...`, `/sample/...`), confirma que la matriz se almacena en formato CSC/CSR comprimido (Compressed Sparse Column/Row) y que ambas orientaciones (`observation/matrix` y `sample/matrix`) contienen los mismos valores no nulos organizados de forma distinta.
10. **Carga del mapping file:** con `dtype=str`, `keep_default_na=False`, `na_filter=False` para controlar manualmente qué se trata como valor ausente (mismo criterio que en `inspect_missing_values.py`).
11. **Distribución EMPO:** `empo_0` (100% "EMP sample"), `empo_1` (Host-associated 50,9% / Free-living 49,0%), `empo_2` (4 categorías), `empo_3` (17 categorías, de "Animal surface" a "Hypersaline").
12. **Cobertura de campos clave:** calculada explícitamente para 21 campos relevantes para el KG. Coordenadas GPS ≈ 99,9%, `empo_3`/`env_biome` 100%, pero `ph` solo 14,2%, `temperature_deg_c` 20,5%, `oxygen_mg_per_l` apenas 1,3%.
13. **Validación formal de IDs:** mediante `assert`, confirma que los 2.000 IDs de muestra coinciden exactamente entre mapping y BIOM, sin IDs exclusivos de un lado ni espacios invisibles.
14. **Join exploratorio:** `mapping_indexed.join(sample_stats, how="inner")` → prototipo de `sample_table` (2.000 × 77 columnas). Selecciona y previsualiza el subconjunto de 23 columnas relevantes para el KG.
15. **Cobertura combinada por componente del KG:** estima cuántas muestras servirían para construir cada tipo de nodo/propiedad (p. ej., nodo `Location` con coordenadas: 99,9%; propiedad pH: solo 14,2%).
16. **Exploración ecológica básica:** compara diversidad observada (`biom_observed_asvs`) entre categorías `empo_3` (p. ej., `Plant rhizosphere` tiene mediana ≈ 1.417 ASVs frente a `Plant corpus` ≈ 12); identifica los ASVs más abundantes de la muestra con mayor riqueza y los asocia a su taxonomía (dominan Proteobacteria/Betaproteobacteria).

**Qué lógica debería pasar a scripts:**
- A `build_sample_table.py`: carga del mapping, normalización de NA, conversión numérica, carga del BIOM, validación de IDs, construcción de `sample_stats`, join, exportación de `sample_table.csv`.
- A un futuro `src/empkg/io/biom.py`: `load_biom_table`, `build_biom_sample_stats`, `extract_taxonomy_preview`, `extract_abundance_for_sample`.
- Se queda solo en el notebook: impresiones didácticas, exploración HDF5 detallada paso a paso, tablas descriptivas extensas, explicaciones largas de conceptos.

---

## Conceptos clave: muestra, lectura, ASV y abundancia

Conviene tener estos cuatro conceptos claros antes de diseñar el esquema del KG, porque se mapean directamente a los futuros nodos `Sample` y `Taxon`, y a la relación `contains_taxon_with_abundance_X`:

- **Muestra (`Sample`):** una unidad ambiental o biológica recogida en el mundo real (un puñado de suelo, un hisopado animal, un volumen de agua). Es la unidad fundamental del mapping file y de uno de los dos ejes del BIOM.
- **Lectura (`read`):** una secuencia individual generada por el secuenciador a partir del material genético de una muestra. Es la unidad bruta de salida de la secuenciación, antes de cualquier agrupación o clasificación.
- **ASV (Amplicon Sequence Variant):** una variante de secuencia exacta a la que se asignan lecturas. A diferencia de los OTUs (que agrupan al 97% de similitud), un ASV no agrupa nada: cada secuencia única detectada por Deblur es su propio ASV, y su ID *es* la secuencia nucleotídica.
- **Abundancia:** el valor numérico en cada celda de la matriz BIOM. Indica cuántas lecturas de una muestra concreta fueron asignadas a un ASV concreto. Es la magnitud que terminará como propiedad numérica de la relación `contains_taxon_with_abundance_X` en el KG.

**Aplicado al fichero `rare_5000` usado en este proyecto:**
- Todas las muestras tienen exactamente 5.000 lecturas totales (por la rarefacción), pero el número de ASVs *distintos* observados varía mucho entre muestras (de 1 a 2.438).
- `biom_total_reads` = suma de todas las lecturas de una muestra (constante = 5.000 en este dataset).
- `biom_observed_asvs` = número de ASVs distintos con al menos una lectura en esa muestra (variable, refleja riqueza/diversidad).

Esta distinción explica por qué dos muestras con el mismo `biom_total_reads` pueden tener una diversidad microbiana muy distinta.

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

## Diseño inicial del Knowledge Graph (Fase 2)

### Estrategia por tablas

El pipeline de ingestión se divide en tres tablas que se construyen
de forma incremental y corresponden a los tres tipos principales de
entidades del KG:

| Tabla                 | Script                     | Qué contiene                                                                 | Estado    |
| --------------------- | -------------------------- | ---------------------------------------------------------------------------- | --------- |
| `sample_table.csv`    | `build_sample_table.py`    | Una fila por muestra: metadatos, localización, mediciones, estadísticas BIOM | ✅ Listo   |
| `taxonomy_table.csv`  | `build_taxonomy_table.py`  | Una fila por ASV: taxonomía en 7 niveles (kingdom → species)                 | Pendiente |
| `abundance_table.csv` | `build_abundance_table.py` | Una fila por par muestra-ASV: lecturas y abundancia relativa                 | Pendiente |

### Mapeo conceptual: tabla → KG

```text
sample_id          → nodo empkg:Sample
study_id           → nodo empkg:Study
country/lat/lon/…  → nodo empkg:Location
empo_*             → nodo empkg:EMPOCategory
env_*/envo_*       → nodo empkg:EnvironmentDescription
ph/temperature/…   → propiedades numéricas de empkg:Sample
biom_total_reads   → empkg:biomTotalReads (xsd:integer)
biom_observed_asvs → empkg:biomObservedASVs (xsd:integer)
```

### Relaciones iniciales (solo con `sample_table.csv`)

```text
Sample  → empkg:belongsToStudy            → Study
Sample  → empkg:wasCollectedAt            → Location
Sample  → empkg:hasEMPOCategory           → EMPOCategory
Sample  → empkg:hasEnvironmentDescription → EnvironmentDescription
```

## Diseño del Knowledge Graph v0

El diseño detallado del KG vive en `docs/kg_design_v0.md` (entidades, propiedades,
relaciones, estrategia de URIs y decisiones abiertas). Este documento es la fuente
de verdad; no se duplica aquí para evitar que ambos textos diverjan.


## Siguiente paso recomendado

El siguiente paso no debería ser todavía el procesamiento LLM ni las abundancias ASV. La prioridad inmediata es convertir la lógica validada en `notebooks/03_to_rdf.ipynb` en un script reproducible:

```text
notebooks/03_to_rdf.ipynb  →  scripts/03_to_rdf.py
```

Objetivos del script:

* Leer `data/samples/kg_v0_test_samples.csv` o, más adelante, `data/processed/sample_table.csv`.
* Generar `data/processed/empkg_v0_test.ttl` de forma reproducible.
* Incluir validaciones críticas: conteo de clases, conteo de relaciones principales, parseo Turtle y ausencia de literales problemáticos.
* Separar progresivamente funciones comunes si empiezan a repetirse (`src/empkg/rdf/`, `src/empkg/cleaning/`, etc.).

Después de tener `scripts/03_to_rdf.py`, el siguiente hito lógico será cargar el Turtle en GraphDB y escribir consultas SPARQL básicas sobre el KG v0. Solo después tiene sentido decidir si avanzar hacia mapeo LLM/ENVO o hacia taxonomía/abundancias.

---

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