## Objetivo

El objetivo de EMPKG-lite v0 es definir un primer modelo RDF pequeño, trazable y validable a partir de `sample_table.csv`. Esta versión no pretende representar todavía todo el Earth Microbiome Project ni incorporar todos los ASVs del fichero BIOM. Su finalidad es establecer una estructura inicial estable para representar muestras, estudios, localizaciones, categorías ambientales EMPO y descripciones ambientales originales.

Se considera una versión v0 porque prioriza simplicidad, validación y aprendizaje del modelo RDF. El mapeo a ontologías externas como ENVO, GAZ o NCBITaxon queda aplazado para fases posteriores.

## Fuentes de datos

El diseño se basa en `data/processed/sample_table.csv`, generado previamente a partir del mapping file de EMP y del fichero BIOM. Para el primer RDF de prueba se utilizará el subconjunto `data/samples/kg_v0_test_samples.csv`, que contiene 17 muestras seleccionadas en el notebook `notebooks/01_analyze_sample_table.ipynb`.

Este subconjunto incluye una muestra por cada una de las 17 categorías `empo_3`, por lo que permite probar que el modelo inicial cubre todos los tipos ambientales presentes en el subset de 2.000 muestras.

## Entidades principales

* `Sample`: entidad central del KG. Representa una muestra EMP.
* `Study`: representa el estudio al que pertenece una muestra.
* `Location`: representa el sitio de muestreo, descrito mediante país, coordenadas y variables espaciales.
* `EMPOCategory`: representa la categoría ambiental controlada del EMP, usando `empo_3` como nivel principal.
* `EnvironmentDescription`: conserva los metadatos ambientales originales de la muestra (`env_biome`, `env_feature`, `env_material` y `envo_biome_*`) sin normalizarlos todavía.

## Relaciones principales

Todo `Sample` se conecta a las otras cuatro entidades mediante exactamente cuatro relaciones. Ninguna de ellas es opcional: si `sample_table.csv` tiene el dato de origen, la relación se genera; si no lo tiene (caso de `Study`, `Location` o `EMPOCategory`, que en la práctica siempre están presentes, o de campos ambientales concretos dentro de `EnvironmentDescription`), no se genera el triple correspondiente, siguiendo el mismo criterio ya fijado para los literales.

| Relación                          | Dominio  | Rango                    | Cardinalidad (Sample →) | Nodo destino                                                                     |
| --------------------------------- | -------- | ------------------------ | ----------------------- | -------------------------------------------------------------------------------- |
| `empkg:belongsToStudy`            | `Sample` | `Study`                  | exactamente 1           | reutilizable (95 estudios para 2.000 muestras)                                   |
| `empkg:wasCollectedAt`            | `Sample` | `Location`               | exactamente 1           | reutilizable y deduplicado (~75% de las muestras comparten coordenadas con otra) |
| `empkg:hasEMPOCategory`           | `Sample` | `EMPOCategory`           | exactamente 1           | reutilizable (17 categorías `empo_3` para 2.000 muestras)                        |
| `empkg:hasEnvironmentDescription` | `Sample` | `EnvironmentDescription` | exactamente 1           | 1:1 con `Sample` en v0 (ver "Decisiones abiertas")                               |

```text
Sample ──belongsToStudy──────────────> Study
Sample ──wasCollectedAt──────────────> Location
Sample ──hasEMPOCategory─────────────> EMPOCategory
Sample ──hasEnvironmentDescription───> EnvironmentDescription
```

**Notas sobre cardinalidad:**

- `belongsToStudy`, `wasCollectedAt` y `hasEMPOCategory` apuntan a nodos **compartidos**: varias muestras del mismo estudio, del mismo punto de muestreo o de la misma categoría EMPO deben apuntar al *mismo* nodo destino, no a copias. Esto es lo que justifica que `Study`, `Location` y `EMPOCategory` sean nodos independientes en vez de propiedades planas de `Sample`.
- `hasEnvironmentDescription` es, de momento, 1:1 con `Sample` — cada muestra tiene su propia descripción ambiental sin deduplicar. Queda como decisión abierta si en una versión posterior conviene deduplicar por combinación exacta de `env_*`.
- `empkg:hasEMPOCategory` es el nombre definitivo elegido para esta relación (sustituye a `classifiedAs`, que aparecía como propuesta alternativa en las conclusiones de `01_analyze_sample_table.ipynb`).

## Literales y propiedades

### Propiedades de `Sample`

```text
sample_id
ph
temperature_deg_c
salinity_psu
oxygen_mg_per_l
biom_total_reads
biom_observed_asvs
```

Los campos fisicoquímicos se consideran opcionales. Si una muestra no tiene valor para una de estas variables, no se generará el triple RDF correspondiente.

### Propiedades de `Study`

```text
study_id
```

### Propiedades de `Location`

```text
country
latitude_deg
longitude_deg
depth_m
elevation_m
altitude_m
```

`Location` se modelará como un nodo reutilizable y deduplicado. La clave de deduplicación inicial combinará país, latitud, longitud, profundidad y elevación cuando estén disponibles.

### Propiedades de `EMPOCategory`

```text
empo_1
empo_2
empo_3
label
```

`empo_3` será el identificador principal de la categoría. `empo_1` y `empo_2` se conservarán como contexto jerárquico.

### Propiedades de `EnvironmentDescription`

```text
env_biome
env_feature
env_material
envo_biome_0
envo_biome_1
envo_biome_2
envo_biome_3
```

Estos campos se conservarán como literales originales. No se mapearán todavía a URIs ENVO en v0.

## Estrategia de URIs

Se usará un namespace propio para los recursos del proyecto:

```text
https://w3id.org/empkg/resource/
```

Y otro para el vocabulario propio del proyecto:

```text
https://w3id.org/empkg/ontology/
```

Las URIs de recursos seguirán patrones estables y legibles. En la implementación v0
se usan sub-namespaces con prefijos `sample:`, `study:`, `loc:`, `empo:` y `envdesc:`:

```text
sample:{sample_id_sanitized}
study:{study_id_sanitized}
loc:{country}_lat{lat}_lon{lon}_depth{depth}_alt{alt}_elev{elev}
empo:{empo_3_sanitized}
envdesc:{sample_id_sanitized}
```

Los valores usados en URIs deberán sanitizarse para evitar espacios, paréntesis, puntos u otros caracteres problemáticos. La sanitización deberá ser determinista, es decir, el mismo valor original siempre debe producir la misma URI.

Ejemplos:

```text
sample_id original:
550.L1S116.s.1.sequence

URI:
empkg:sample/550_L1S116_s_1_sequence
```

```text
empo_3 original:
Soil (non-saline)

URI:
empkg:empo-category/soil_non_saline
```

Para `Location`, se recomienda generar una clave a partir de los campos normalizados:

```text
country + latitude_deg + longitude_deg + depth_m + elevation_m
```

y convertir esa clave en un hash corto o en un identificador sanitizado. Esto permite reutilizar el mismo nodo `Location` cuando varias muestras comparten exactamente el mismo sitio de muestreo.

## Qué queda fuera de v0

Quedan fuera de EMPKG-lite v0:

* La carga completa de los 155.002 ASVs del fichero BIOM.
* Las ocurrencias muestra-taxón y sus abundancias.
* El mapeo automático de `env_biome`, `env_feature` y `env_material` a ENVO.
* El mapeo de `country` a URIs GAZ reales.
* El mapeo de taxonomía microbiana a NCBITaxon.
* El uso de LLM para armonización de metadatos.
* La validación SHACL.
* La carga en GraphDB.
* Consultas SPARQL avanzadas.

Estos elementos se aplazan para fases posteriores. La prioridad de v0 es generar un RDF mínimo, correcto y fácil de inspeccionar.

## Decisiones abiertas

- Decidir si `EnvironmentDescription` será siempre 1:1 con `Sample` o si en futuras versiones se deduplicará por combinación exacta de `env_*`.
- Decidir si `country`, que aparece con formato tipo `GAZ:United States of America`, se conservará como literal o se mapeará a una URI GAZ/Wikidata.
- Decidir si `altitude_m` y `elevation_m` deben conservarse ambas en v0 o si una de ellas es redundante.
- Decidir si `biom_total_reads`, al ser constante, se mantiene como propiedad de cada `Sample` o se mueve más adelante a metadato del dataset.
- Decidir en qué fase se incorporarán los ASVs y abundancias mediante nodos `TaxonOccurrence`.

## Próximo paso: RDF mínimo

El siguiente paso será implementar un primer generador RDF que lea `data/samples/kg_v0_test_samples.csv` y produzca un archivo Turtle pequeño, por ejemplo:

`data/processed/empkg_v0_test.ttl`

Este RDF incluirá únicamente:

- `Sample`
- `Study`
- `Location`
- `EMPOCategory`
- `EnvironmentDescription`

No incluirá todavía taxones, ASVs ni abundancias.

Después de generar el Turtle, se validará localmente con `rdflib` comprobando:

- que el archivo se puede parsear sin errores;
- que contiene 17 nodos `Sample`;
- que contiene 17 categorías `EMPOCategory`;
- que cada `Sample` tiene exactamente una relación con `Study`, `Location`, `EMPOCategory` y `EnvironmentDescription`;
- que no se generan triples para valores ausentes.