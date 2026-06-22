# El EMP como Grafo de Conocimiento fundamental
## **EMPKG**: Creación de un Knowledge Graph Microbiano a Escala Planetaria a partir del Earth Microbiome Project con anotacion de metadatos mejorada por LLM

**Idea principal:** Transformar el conjunto de datos masivo y estandarizado de EMP (miles de muestras en biomas) en un grafo de conocimiento unificado. El mayor obstáculo está en los **metadatos** de muestra (el contexto ambiental como el pH, la temperatura o el tipo de bioma) que a menudo se encuentran en formatos de texto libre o inconsistentes. Utilizaremos una LLM para estructurar y normalizar estos metadatos con el fin de vincular la abundancia microbiana con los parámetros ambientales y las ubicaciones geográficas en un grafo consultable.

### Componentes clave del proyecto

1. **Integración de datos EMP:** Descargar muestras EMP (datos de amplicones  de ARNr 16S/18S) con sus metadatos ambientales.
2. **LLM para la armonización de datos:** Diseñar una secuencia de LLM para analizar campos de metadatos heterogéneos. (p. ej., "suelo, bosque, templado" → términos estandarizados: `ENVO:00002258` (suelo), `ENVO:01000174` (bosque templado latifolio)).
3. **Mapeo de ontologías:** Vincular todas las entidades a las ontologías: **ENVO** (entornos), **NCBITaxon** (microbios), **GAZ** (geografía), **CHEBI** (sustancias químicas).
4. **Construcción de grafos:** Construir un KG donde los nodos sean `Muestra`, `Ubicación`, `Característica ambiental`, `Taxón`; y los bordes representen `recolectado_en`, `tiene_característica`, `contiene_taxon_con_abundancia_X`.
5. **Sistema de consultas:** Permite realizar consultas potentes: *"Mostrar todos los taxones de acidobacterias cuya abundancia se correlaciona con un pH bajo en suelos forestales de Norteamérica."*

**Ventajas con EMP:**


### Itinerario del Proyecto

Enfoque por fases centrado en 
EMPKG con una o varias de las extensiones planteadas.
* **Fase 1 (Core - 3/4 meses)**: Construir **EMPKG-lite**.
Ingestar un subconjunto de datos EMP (por ejemplo, 10.000 muestras de 3 biomas). Utilizar una LLM para limpiar y mapear los metadatos a ontologías. Crear el grafo en Neo4j que demuestra consultas interesantes entre biomas.
* **Fase 2 (Ampliación - 1/2 meses)** Escoger una extensión asequible y desarrollar en profundidad:
  * **Extension A (Descubrimiento):** Implementar una versión sencilla del "generador de hipótesis de EcoLLM" y validar entre 5-10 hipótesis del KG.
  * **Extension B (Predicción):** Añadir una "red de concurrencia" al KG y utilizr embeddings de nodos simples (Node2Vec) para predecir el bioma de un conjunto de muestras.
  * **Extension C (Visualización):** Crear un dashboard web interactivo (Kepler.gl --> mapas, Plotly --> gráficos) para explorar el KG del microbioma planetario.

**Habilidades desarrolladas:** Procesamiento de Big Data, NLP/LLM, ingeniería ontológica, GDB, datos espaciales, visualización científica y diseño de sistemas.

