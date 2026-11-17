# Registro de decisiones de EMPKG-lite

Este documento recoge las decisiones técnicas vigentes y las que deben revisarse. No sustituye al roadmap ni a la documentación formal de la futura ontología. Cuando cambie una decisión, conservar su justificación y registrar la que la sustituye.

## Decisiones vigentes

| ID | Decisión | Justificación |
|---|---|---|
| D01 | RDF/OWL, GraphDB y SPARQL frente a Neo4j/Cypher | Representación semántica y reutilización de ontologías RDF/OWL, conforme a la orientación del tutor registrada en la documentación anterior. |
| D02 | EMP Release 1 `subset_2k`, Deblur 90 bp, rarefacción a 5.000 lecturas | Dataset inicial manejable y ambientalmente variado. Las ASVs y las OTUs son unidades distintas; las bases taxonómicas no son alternativas directas a Deblur. |
| D03 | Diseñar para el conjunto completo de 2.000 muestras y probar de forma incremental | Evitar ajustar el modelo a 17 muestras seleccionadas por completitud; las pruebas pequeñas reducen el coste de depuración. |
| D04 | Metodología Ontology First, iterativa | Definir requisitos, preguntas de competencia y modelo OWL antes del nuevo pipeline; las pruebas retroalimentarán el diseño. |
| D05 | Separar ontología, datos RDF y validación | Protégé/OWL para formalización y razonamiento; Python/RDFLib para población; GraphDB/SPARQL para explotación; SHACL para requisitos de calidad. |
| D06 | Python 3.11 y entorno Conda `empkg` | Mantener el entorno operativo y reproducible ya utilizado para la exploración. No se cambia la versión sin necesidad justificada. |
| D07 | Usar biom-format como interfaz principal y h5py para inspección | Aprovechar abstracciones del formato BIOM y conocer el almacenamiento sin implementar acceso disperso manualmente. |
| D08 | Evitar densificar la matriz BIOM completa | Solo 858.173 pares tienen recuento positivo de 310.004.000 posiciones posibles; las operaciones dispersas reducen costes de memoria. |
| D09 | Preservar datos originales e identificadores | Facilitar trazabilidad, reproducibilidad y uniones verificables; no truncar identificadores usados como claves. |
| D10 | Separar exploración de pipeline y pruebas automatizadas | El notebook ayuda a comprender los datos; las transformaciones estables pertenecen al pipeline y las comprobaciones reproducibles a las pruebas. |
| D11 | No versionar raw, processed ni inspection | Son datos descargados o artefactos generados; conservar localmente y documentar su reproducción. |
| D12 | Retirar RDF v0 y aplazar modularización | Evitar invertir trabajo en una arquitectura ligada a un modelo que se va a revisar; reutilizar código histórico cuando haya requisitos reales. |
| D13 | `main` estable, `develop` de integración y ramas temporales por tarea | Mantener hitos limpios y aislar el trabajo incremental. Preferir merges explícitos para conservar la estructura de ramas. |
| D14 | Preservar etiquetas originales y distinguir desconocimiento de cero | La ausencia de anotación o medición no constituye una afirmación negativa. No exigir completitud general para representar una muestra. |
| D15 | Distinguir ASV, taxón y asignación taxonómica | Una secuencia no equivale a una especie; la anotación depende del método y la referencia. Preservar su procedencia. |
| D16 | Tratar recuentos y métricas con su contexto | El recuento corresponde a un par ASV-muestra en un conjunto procesado; riqueza, prevalencia y abundancia relativa tienen denominadores y significado específicos. |
| D17 | LLM tras establecer un modelo y KG básicos | Evitar que propuestas de mapeo no verificadas determinen el esquema o introduzcan afirmaciones sin respaldo. Acordar con el tutor la contribución final. |

## Antecedente: RDF v0 (retirado)

El prototipo inicial se construyó a partir de `sample_table.csv`, generado desde el BIOM y el mapping file. Se seleccionaron 17 muestras, una por categoría `empo_3`, favoreciendo la completitud de metadatos. El modelo RDFS representaba `Sample`, `Study`, `Location`, `EMPOCategory` y `EnvironmentDescription`.

La documentación histórica registra 588 triples en el conjunto de prueba, 17 muestras, 15 estudios y 15 localizaciones. El script de generación también se probó sobre las 2.000 muestras en julio de 2026. No incluía ASVs, recuentos ni taxonomía como datos del grafo. Estos resultados son antecedentes documentados, no métricas de un KG v1 ni una ejecución reproducida durante la reorganización.

El código utilizaba un hash SHA-256 abreviado sobre una clave geográfica para reutilizar localizaciones y añadía el identificador de muestra cuando faltaban coordenadas. Esa solución, las cuatro relaciones obligatorias por muestra, las IRIs del prototipo y las decisiones de selección de columnas no se consideran requisitos vigentes. Deberán evaluarse de nuevo a partir de las preguntas de competencia.

### Trazabilidad histórica

La versión anterior a la reorganización se conserva en el commit [`aa5ad78`](https://github.com/Foxo10/EMPKG-Planetary_Microbiome_KG/tree/aa5ad784785655cb6535b4c9192671f44e411a3f). Allí se pueden consultar:

- [Diseño RDF v0](https://github.com/Foxo10/EMPKG-Planetary_Microbiome_KG/blob/aa5ad784785655cb6535b4c9192671f44e411a3f/docs/kg_design_v0.md).
- [Diario técnico anterior](https://github.com/Foxo10/EMPKG-Planetary_Microbiome_KG/blob/aa5ad784785655cb6535b4c9192671f44e411a3f/docs/annotations.md).
- [Roadmap anterior](https://github.com/Foxo10/EMPKG-Planetary_Microbiome_KG/blob/aa5ad784785655cb6535b4c9192671f44e411a3f/docs/workflow_v2.md).
- [Código Python de conversión RDF](https://github.com/Foxo10/EMPKG-Planetary_Microbiome_KG/blob/aa5ad784785655cb6535b4c9192671f44e411a3f/scripts/csv_to_rdf.py) y notebooks del prototipo.

Ejemplo de recuperación sin alterar el repositorio:

```bash
git show aa5ad78:scripts/csv_to_rdf.py
```

## Decisiones pendientes de ingeniería ontológica

| Tema | Pregunta abierta |
|---|---|
| Requisitos | ¿Qué preguntas de competencia definen el núcleo del TFG? |
| Reutilización | ¿Qué versiones y conceptos de EMPO, ENVO, NCBITaxon, MIxS y otros recursos necesitamos? |
| Identidad | ¿Cómo identificar muestras, observaciones de secuencia, lugares y eventos sin fusionar entidades indebidamente? |
| Recuentos | ¿Qué patrón representa cada combinación muestra–ASV y su contexto de procesamiento? |
| Taxonomía | ¿Cómo representar linajes parciales, referencias/versiones y asignaciones alternativas? |
| Ambiente | ¿Cómo diferenciar clasificación, contexto, material, lugar y mediciones con unidades? |
| Procedencia | ¿Qué nivel de detalle sobre estudios, dataset y procesamiento exige el modelo? |
| Métricas | ¿Cuáles se almacenan justificadamente y cuáles se calculan mediante consultas? |
| Validación | ¿Qué requisitos son axiomas OWL y cuáles son constraints SHACL? |
| Escalabilidad | ¿Qué volumen y estrategias de carga resultan adecuados tras medir el grafo? |
| Armonización | ¿Qué papel tendrá el LLM en el alcance final y cómo se evaluará? |

No se fijan todavía nombres de clases, IRIs definitivas, cardinalidades, filtros de ASVs ni un esquema de tablas intermedias. Tampoco se da por supuesto que las etiquetas actuales de EMPO/ENVO sean identificadores ontológicos verificados.

## Hitos históricos

| Fecha o periodo | Hito |
|---|---|
| Etapa inicial | Configuración del entorno, adquisición de fuentes EMP y primeros análisis. |
| 2026-07-11 | Notebook de generación RDF v0 completado (según el diario anterior). |
| 2026-07-19 | Script `csv_to_rdf.py` completado y probado sobre ambos conjuntos (según el diario anterior). |
| Noviembre de 2026 | Revisión de la exploración, apuntes bioinformáticos, limpieza de artefactos y retirada del código RDF v0. |
| Noviembre de 2026 | Reorientación acordada hacia ingeniería ontológica y preparación del nuevo roadmap. |

## Cómo mantener este registro

Para decisiones nuevas, incluir fecha, estado (propuesta, aceptada o sustituida), contexto, alternativas, elección, justificación, consecuencias y referencias a pruebas o documentación. Registrar decisiones que afecten al diseño o a la reproducibilidad, no cada cambio de código.
