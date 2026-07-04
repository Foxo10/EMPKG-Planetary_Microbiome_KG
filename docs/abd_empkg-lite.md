## Tema ABD 1 — NoSQL y grafos aplicados a EMPKG-lite

El modelo relacional representa los datos como tablas, filas y columnas. Es útil para la limpieza inicial del EMP, pero el objetivo del TFG requiere representar relaciones entre muestras, estudios, localizaciones, entornos, taxones y ontologías. Por eso el proyecto evoluciona desde `sample_table.csv` hacia un Knowledge Graph.

### Decisión para EMPKG-lite

La tabla `sample_table.csv` será el punto de partida limpio. A partir de ella se construirán nodos y relaciones:

- `Sample`
- `Study`
- `Location`
- `EnvironmentalFeature`
- `EnvironmentalMaterial`
- `Biome`
- `Taxon`
- `TaxonOccurrence`

Relaciones iniciales:

- `belongsToStudy`
- `wasCollectedAt`
- `hasEnvironment`
- `hasMaterial`
- `hasBiome`
- `hasObservation`
- `taxon`
- `relativeAbundance`

### Criterio de modelado

Un campo se convierte en nodo cuando representa una entidad reutilizable, enlazable o mapeable a una ontología. Un campo se deja como literal cuando es un valor simple, como `ph`, `temperature_deg_c`, `latitude_deg` o `longitude_deg`.

## Tema ABD 2 — Modelado inicial del grafo EMPKG-lite

### Objetivo

Diseñar el modelo conceptual del Knowledge Graph antes de generar RDF o cargar datos en GraphDB.

### Modelo mínimo

Nodos iniciales:

- `Sample`
- `Study`
- `Location`
- `Environment`
- `Taxon`
- `TaxonOccurrence`

Relaciones iniciales:

- `Sample -> Study` mediante `belongsToStudy`
- `Sample -> Location` mediante `wasCollectedAt`
- `Sample -> Environment` mediante `hasEnvironment`
- `Sample -> TaxonOccurrence` mediante `hasTaxonOccurrence`
- `TaxonOccurrence -> Taxon` mediante `observedTaxon`

### Decisiones

- Los campos `ph`, `temperature_deg_c`, `salinity_psu` y `oxygen_mg_per_l` se modelarán inicialmente como propiedades numéricas de `Sample`.
- Las coordenadas y datos espaciales se agruparán en un nodo `Location`.
- Los campos `env_biome`, `env_feature`, `env_material` y `empo_3` se conservarán inicialmente como texto original dentro de `Environment`.
- El mapeo a ENVO se hará después, para evitar crear nodos duplicados a partir de cadenas no normalizadas.
- Las abundancias microbianas se modelarán mediante un nodo intermedio `TaxonOccurrence`, porque la relación entre muestra y taxón tiene propiedades propias como `abundance` o `relative_abundance`.


## Tema ABD 3 — RDF aplicado a EMPKG-lite

### Idea principal

RDF representa conocimiento mediante triples `sujeto-predicado-objeto`. En EMPKG-lite, cada muestra, estudio, localización y entorno se representará como un recurso identificado mediante URI. Los valores simples, como pH, temperatura, latitud o longitud, se representarán como literales tipados.

### Decisión inicial

El primer RDF del proyecto no incluirá todavía todas las abundancias del BIOM. Se generará primero un RDF ligero con:

- `Sample`
- `Study`
- `Location`
- `Environment`

A partir de `sample_table.csv`.

### Mapeo inicial

- `sample_id` → URI de `Sample`
- `study_id` → URI de `Study`
- `country`, `latitude_deg`, `longitude_deg` → `Location`
- `env_biome`, `env_feature`, `env_material`, `empo_3` → `Environment`
- `ph`, `temperature_deg_c`, `salinity_psu`, `oxygen_mg_per_l` → literales numéricos de `Sample`

### Criterio de generación

No se generarán triples para valores ausentes (`NaN`, `None`, `not applicable`, `unknown`). Si falta un dato, simplemente no se afirma en el grafo.

### Siguiente paso técnico

Crear un primer script `to_rdf_samples.py` o `03_to_rdf.py` que lea `data/processed/sample_table.csv` y genere `data/processed/empkg_samples.ttl` usando `rdflib`.