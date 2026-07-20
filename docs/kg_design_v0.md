# Diseño del Knowledge Graph EMPKG-lite v0

> **Estado: IMPLEMENTADO Y CERRADO.**
> Este documento describe la especificación del modelo RDF v0 tal como fue diseñado e implementado.
> Para el diseño del modelo v1 (con ASVs, taxonomía y abundancias) véase `docs/kg_design_v1.md` (pendiente).

---

## Objetivo

El objetivo de EMPKG-lite v0 es definir un primer modelo RDF pequeño, trazable y validable a partir de `sample_table.csv`. Esta versión no pretende representar todavía todo el Earth Microbiome Project ni incorporar todos los ASVs del fichero BIOM. Su finalidad es establecer una estructura inicial estable para representar muestras, estudios, localizaciones, categorías ambientales EMPO y descripciones ambientales originales.

Se considera una versión v0 porque prioriza simplicidad, validación y aprendizaje del modelo RDF. El mapeo a ontologías externas como ENVO, GAZ o NCBITaxon queda aplazado para fases posteriores.

---

## Fuentes de datos

El diseño se basa en `data/processed/sample_table.csv`, generado a partir del mapping file de EMP y del fichero BIOM. Para el primer RDF de prueba se utilizó el subconjunto `data/samples/kg_v0_test_samples.csv`, que contiene 17 muestras seleccionadas en `notebooks/01_analyze_sample_table.ipynb`.

Este subconjunto incluye una muestra por cada una de las 17 categorías `empo_3`, cubriendo todos los tipos ambientales presentes en el subset de 2.000 muestras.

---

## Entidades principales

* `Sample`: entidad central del KG. Representa una muestra EMP.
* `Study`: representa el estudio al que pertenece una muestra.
* `Location`: representa el sitio de muestreo, descrito mediante país, coordenadas y variables espaciales.
* `EMPOCategory`: representa la categoría ambiental controlada del EMP, usando `empo_3` como nivel principal.
* `EnvironmentDescription`: conserva los metadatos ambientales originales de la muestra (`env_biome`, `env_feature`, `env_material` y `envo_biome_*`) sin normalizarlos todavía.

---

## Relaciones principales

Todo Sample se conecta mediante exactamente cuatro relaciones. El script
crea los nodos Study, Location, EMPOCategory y EnvironmentDescription para
cada muestra válida. Cuando falta un valor opcional, se omite únicamente
el triple de la propiedad literal correspondiente; no se elimina la
relación principal del Sample.

| Relación                          | Dominio  | Rango                    | Cardinalidad (Sample →) | Nodo destino                                                            |
| --------------------------------- | -------- | ------------------------ | ----------------------- | ----------------------------------------------------------------------- |
| `empkg:belongsToStudy`            | `Sample` | `Study`                  | exactamente 1           | reutilizable (95 estudios para 2.000 muestras)                          |
| `empkg:wasCollectedAt`            | `Sample` | `Location`               | exactamente 1           | reutilizable y deduplicado (~75% de las muestras comparten coordenadas) |
| `empkg:hasEMPOCategory`           | `Sample` | `EMPOCategory`           | exactamente 1           | reutilizable (17 categorías `empo_3`)                                   |
| `empkg:hasEnvironmentDescription` | `Sample` | `EnvironmentDescription` | exactamente 1           | 1:1 con `Sample` en v0                                                  |

```text
Sample ──belongsToStudy──────────────> Study
Sample ──wasCollectedAt──────────────> Location
Sample ──hasEMPOCategory─────────────> EMPOCategory
Sample ──hasEnvironmentDescription───> EnvironmentDescription
```

**Notas sobre cardinalidad:**

- `belongsToStudy`, `wasCollectedAt` y `hasEMPOCategory` apuntan a nodos **compartidos**: varias muestras del mismo estudio, del mismo punto de muestreo o de la misma categoría EMPO apuntan al *mismo* nodo destino.
- `hasEnvironmentDescription` es 1:1 con `Sample` en v0. Queda abierto si en v1 conviene deduplicar por combinación exacta de `env_*`.
- `empkg:hasEMPOCategory` es el nombre definitivo (sustituye a `classifiedAs`, propuesta descartada).

---

## Literales y propiedades

### Propiedades de `Sample`

```text
empkg:sampleId          (literal textual)
empkg:ph                (xsd:decimal, opcional)
empkg:temperatureDegC   (xsd:decimal, opcional)
empkg:salinityPsu       (xsd:decimal, opcional)
empkg:oxygenMgPerL      (xsd:decimal, opcional)
empkg:biomTotalReads    (xsd:integer)
empkg:biomObservedASVs  (xsd:integer)
```

Los campos fisicoquímicos son opcionales. Si una muestra no tiene valor, no se genera el triple.

### Propiedades de `Study`

```text
empkg:studyId  (literal textual)
rdfs:label     (literal textual)
```

### Propiedades de `Location`

```text
empkg:country    (literal textual)
schema:latitude  (xsd:decimal)
schema:longitude (xsd:decimal)
empkg:depthM     (xsd:decimal, opcional)
empkg:altitudeM  (xsd:decimal, opcional)
empkg:elevationM (xsd:decimal, opcional)
rdfs:label       (literal textual)
```

`Location` es un nodo reutilizable y deduplicado mediante hash de la clave geográfica (ver sección "Estrategia de URIs").

### Propiedades de `EMPOCategory`

```text
empkg:empo1  (literal textual)
empkg:empo2  (literal textual)
empkg:empo3  (literal textual)
rdfs:label   (literal textual)
```

`empo_3` es el identificador principal. `empo_1` y `empo_2` se conservan como contexto jerárquico.

### Propiedades de `EnvironmentDescription`

```text
empkg:envBiome    (literal textual, opcional)
empkg:envFeature  (literal textual, opcional)
empkg:envMaterial (literal textual, opcional)
empkg:envoBiome0  (literal textual, opcional)
empkg:envoBiome1  (literal textual, opcional)
empkg:envoBiome2  (literal textual, opcional)
empkg:envoBiome3  (literal textual, opcional)
```

Estos campos se conservan como literales originales. No se mapean todavía a URIs ENVO.

---

## Estrategia de URIs

### Namespaces

```text
https://w3id.org/empkg/ontology/   → prefijo empkg: (clases y propiedades)
https://w3id.org/empkg/resource/sample/       → prefijo sample:
https://w3id.org/empkg/resource/study/        → prefijo study:
https://w3id.org/empkg/resource/location/     → prefijo loc:
https://w3id.org/empkg/resource/empo-category/ → prefijo empo:
https://w3id.org/empkg/resource/environment-description/ → prefijo envdesc:
```

### Patrones de URI por entidad

```text
sample:   {sample_id_sanitized}
study:    {study_id_sanitized}
empo:     {empo_3_sanitized}
envdesc:  {sample_id_sanitized}
loc:      {hash_sha256_abreviado}
```

### Sanitización

Los valores usados en URIs se sanitizan de forma **determinista**:

- Para IDs técnicos (`sample_id`, `study_id`): se preservan mayúsculas/minúsculas, se reemplazan caracteres no alfanuméricos por `_`.
- Para etiquetas controladas (`empo_3`): se convierten a minúsculas, se expanden `(non-saline)` → `non_saline`, `(saline)` → `saline`.
- ~~Para números en URIs de `Location`: los negativos llevan prefijo `m`, el punto decimal se convierte en `_`.~~
- Para números en URIs de `Location`: loc:{hash_sha256_abreviado}

Ejemplos:

```text
sample_id: 550.L1S116.s.1.sequence → sample:550_L1S116_s_1_sequence
empo_3:    Soil (non-saline)        → empo:soil_non_saline
```

### Deduplicación de `Location`

Las URIs de `Location` se generan mediante un **hash SHA-256 abreviado** calculado sobre una clave canónica que incluye:

```text
country + latitude_deg + longitude_deg + depth_m + altitude_m + elevation_m
```

Los valores ausentes se mantienen como valores nulos dentro de la
representación JSON canónica usada para calcular el hash.

**Fallback:** si faltan latitud o longitud, se añade `sample_id` a la clave para evitar fusionar muestras sin evidencia geográfica suficiente de que pertenecen al mismo lugar.

---

## Qué queda fuera de v0

- Los 155.002 ASVs del fichero BIOM y sus abundancias.
- Los nodos `Taxon` y `TaxonOccurrence`.
- El mapeo automático de `env_biome`, `env_feature` y `env_material` a ENVO.
- El mapeo de `country` a URIs GAZ reales.
- El mapeo de taxonomía microbiana a NCBITaxon.
- El uso de LLM para armonización de metadatos.
- La validación SHACL.
- Consultas SPARQL avanzadas.

La incorporación de ASVs, taxonomía y abundancias se diseñará en `docs/kg_design_v1.md`.

---

## Estado de implementación

### Script

```text
scripts/csv_to_rdf.py
```

Transforma `data/samples/kg_v0_test_samples.csv` en `data/processed/empkg_v0_test.ttl`.
Probado también sobre las 2.000 muestras de `data/processed/sample_table.csv`.

### Métricas del grafo generado (subconjunto de 17 muestras)

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

El número de `Study` (15) es menor que el de `Sample` (17) porque varias muestras comparten `study_id`. El número de `Location` (15) es menor porque `Location` se deduplica.

### Validaciones realizadas

* El Turtle puede parsearse de nuevo con `rdflib` sin errores.
* Cada `Sample` tiene exactamente las 4 relaciones principales.
* No se generan triples para valores ausentes (`NaN`, cadenas vacías, `unknown`, etc.).
* Las URIs de `Location` son deterministas mediante hash SHA-256.
* Las 17 categorías `empo_3` están representadas como nodos `EMPOCategory`.
* Los literales numéricos usan los datatypes correctos (`xsd:decimal`, `xsd:integer`).

### Limitaciones conocidas

* `EnvironmentDescription` es 1:1 con `Sample`: no hay deduplicación aunque dos muestras compartan los mismos campos `env_*`.
* `country` se conserva como literal con formato `GAZ:United States of America`, sin mapear a URIs GAZ reales.
* La taxonomía asignada a cada ASV no está todavía en el grafo.
* El grafo no está cargado todavía en GraphDB.

---

## Decisiones abiertas (para v1)

- ¿`EnvironmentDescription` se deduplicará por combinación exacta de `env_*` en v1?
- ¿`country` se mapeará a una URI GAZ/Wikidata?
- ¿`altitude_m` y `elevation_m` son ambos necesarios, o uno es redundante?
- ¿`biom_total_reads` (constante = 5000) se mantiene por muestra o pasa a metadato del dataset?
- ¿La relación muestra–ASV se modela como `Sample → hasOccurrence → TaxonOccurrence → observedASV → ASV`?
