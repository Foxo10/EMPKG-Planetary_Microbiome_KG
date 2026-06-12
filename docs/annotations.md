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
- Gestor local: Miniconda 25.11.1 con solver libmamba
- Entorno del proyecto: `empkg` (Python 3.11)
- Canales conda: conda-forge > bioconda > defaults
- Dependencias base: biom-format, h5py, pandas, numpy
- Para activar: `conda activate empkg`
- Para reproducir: `conda env create -f environment.yml`
- No usar el entorno base para instalar paquetes del proyecto.
  
La documentación oficial de BIOM recomienda instalar `numpy`, `biom-format` y `h5py` para trabajar con BIOM 2.0+. Además, `biom-format` incluye tanto CLI como API de Python.

## Datos EMP y su descarga
EMP publica tablas de observaciones, metadatos y resultados en Zenodo, FTP y el portal EMP de Qiita; el FTP incluye README, mapping files, tablas OTU/BIOM, secuencias, árboles y resultados de diversidad. El repositorio oficial (`https://github.com/biocore/emp`) tiene instrucciones de acceso a los datos via FTP (`ftp://ftp.microbio.me/emp/release1/`). 

1. **Ficheros de metadatos (`mapping_files/`)**
Un 'mapping_file' es una tabla TSV donde cada fila es una muestra y cada columna es un campo de metadatos (pH, temperatura, bioma, coordenadas GPS, tipo de muestra, etc.). 
El fichero de metadatos principal para los análisis es `emp_qiime_mapping_qc_filtered.tsv`, la versión filtrada por calidad de todas las muestras del Release 1.
Además, contamos con submuestras de 2k, 5k y 10k muestras.
Estos ficheros TSV ya son legibles con `pandas` y no necesitamos `biom-format` ni `h5py` para empezar a explorar los metadatos.

2. **Ontología EMP (`emp_ontology/`)**
   * `empo_v3.csv`: La ontología EMPO (EMP Ontology) versión 3. Es una clasificación jerárquica de tipos de entorno usada por el EMP.
   * `envoEmpo_graph_v3.vue`: Un grafo que relaciona EMPO con ENVO.
EMPO es la ontoloǵia propia del EMP. En el mapping file, muchas muestras ya tienen un campo `empo_3` o similar que asigna cada muestra a un tipo de entorno según EMPO. Mientras que ENVO es la ontología estándar de entornos, EMPO es más gruesa y específica del EMP (por ejemplo: `Free-living aquatic`, `Animal corpus`, `Plant corpus`).
*Mirar el fichero empo_v3.csv con detalle*

3. **Tablas de OTUs/ASVs (`otu_tables/`)**
Tablas de abundancia microbiana: matrices donde las filas son taxa (OTUs o ASVs) y las columnas son muestras. Están en formatio BIOM (HDF5).
   * `closed_ref_greengenes/` — OTUs por referencia cerrada contra Greengenes 13.8
    La referencia Greengenes es la más antigua y ampliamente usada en estudios del EMP, pero está desactualizada
   * `closed_ref_silva/` — OTUs por referencia cerrada contra Silva 123
    Silva es más actualizada y tiene mejor cobertura de Archaea. Para un proyecto nuevo, esta o Deblur son mejores opciones que Greengenes.
   * `deblur/` — ASVs (Amplicon Sequence Variants) con Deblur
    Deblur genera ASVs en vez de OTUs. Los ASVs son más precisos: representan secuencias reales, no clusters al 97% de similitud. Son el estándar actual en microbiomía.
   * `open_ref_greengenes/` — OTUs por referencia abierta contra Greengenes 13.8
    La referencia abierta permite asignar también secuencias que no caen en la referencia (las pone en OTUs "nuevas"). Es la opción más completa pero también la que genera más ruido.

Los ficheros, dentro de cada una de estas carpetas, siguen una nomenclatura consistente:
```emp_<método>_<longitud_bp>.<tamaño>.<rarefacción>.biom```

4. **Información de referencia sobre OTUs/secuencias (`otu_info/`)**
Aquí viven los ficheros de referencia que se usaron para el OTU picking:

| Carpeta                   | Contenido                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------- |
| deblur/                   | Secuencias representativas (.fa) y árboles filogenéticos (.tre) para los ASVs de Deblur |
| greengenes_13_8/          | Secuencias, taxonomías y árbol filogenético de Greengenes 13.8                          |
| silva_123/                | Secuencias, taxonomías y árbol filogenético de Silva 123                                |
| open_ref/                 | Secuencias representativas del OTU picking de referencia abierta                        |
| greengenes_sepp_pipeline/ | Pipeline SEPP para inserción filogenética                                               |
5.  


Primero descargar:
```bash
# El mapping file filtrado con las 2k muestras — solo TSV, abre con pandas
mkdir -p data/raw/emp/release1/mapping_files
wget -c \
  -O data/raw/emp/release1/mapping_files/emp_qiime_mapping_subset_2k.tsv \
  https://ftp.microbio.me/emp/release1/mapping_files/emp_qiime_mapping_subset_2k.tsv
```

Segundo:
```bash
# Tabla BIOM Deblur, 2k muestras, rarefaccionada — el fichero de datos más manejable
mkdir -p data/raw/emp/release1/otu_tables/deblur
wget -c \
  -O data/raw/emp/release1/otu_tables/deblur/emp_deblur_90bp.subset_2k.rare_5000.biom \
  https://ftp.microbio.me/emp/release1/otu_tables/deblur/emp_deblur_90bp.subset_2k.rare_5000.biom
```

**Por qué Deblur y no Greengenes o Silva:** Deblur genera ASVs de alta resolución, que son el estándar moderno, mientras que los métodos de referencia cerrada como Greengenes se usaron para compatibilidad con estudios previos. Para un proyecto nuevo y actual, Deblur es la opción más actualizada y con mejor resolución taxonómica.

**Por qué el subset_2k:** el Release 1 del EMP contiene alrededor de 25.000 muestras de 97 estudios, lo cual para una exploración inicial es demasiado. El subset de 2.000 muestras es suficiente para entender la estructura de los datos.

Intenté descargar `empo_v3.csv`, pero el servidor devolvía 404.
Después probé con `empo_v2.csv`, que aparece en el índice actual del FTP, pero devuelve 403 Forbidden al acceder directamente.

- El mapping file contiene los metadatos de las muestras.
- El archivo BIOM contiene la matriz de abundancias.
- EMPO será útil más adelante para interpretar/clasificar ambientes, pero no es necesario para abrir el BIOM ni validar la ingesta inicial.

## Archivos descargados
`emp_qiime_mapping_subset_2k.tsv` — el mapping file de 2.000 muestras. Es un TSV con una fila por muestra y una columna por campo de metadatos (pH, temperatura, bioma, coordenadas GPS, tipo de muestra, EMPO…). Lo puedes abrir directamente con pandas sin ninguna librería especial. Es el primer archivo que debes explorar porque te da el contexto ambiental de cada muestra.

`emp_deblur_90bp.subset_2k.rare_5000.biom` — la tabla de abundancias microbianas en formato BIOM/HDF5. El nombre lo dice todo: método Deblur, fragmentos de 90 pares de bases, subconjunto de 2k muestras, rarefaccionada a 5.000 lecturas por muestra. Es una matriz donde las filas son ASVs (taxones) y las columnas son muestras. Este es el archivo grande y el que requiere biom-format y h5py. El sufijo rare_5000 significa que todas las muestras tienen el mismo número de lecturas tras un proceso de submuestreo aleatorio (rarefacción), lo que permite comparar abundancias entre muestras de forma justa.

`empo_v3.csv` — la ontología EMPO versión 3. Es un CSV pequeño que define la clasificación jerárquica de tipos de entorno usada en el EMP (por ejemplo: "Animal corpus", "Free-living aquatic"). Lo necesitas para entender los valores del campo empo_3 del mapping file.

## Resumen EMP
El EMP Release 1 contiene ~25.000 muestras de 97 estudios publicadas en Thompson et al., Nature 2017  (doi: 10.1038/nature24621). Los datos están en el FTP `ftp://ftp.microbio.me/emp/release1/`. El subset 2k es una submuestra estratificada representativa usada en análisis exploratorios.

Los mapping files son archivos TSV donde cada fila es una muestra y cada columna es un campo de metadatos. La primera columna es `#SampleID`. Campos relevantes para el KG: `latitude_deg`, `longitude_deg`, `empo_3`, `ph`, `temperature_deg_c`. No todos los campos están rellenos en todas las muestras.

El formato **BIOM 2.x** almacena la tabla de abundancias como una matriz dispersa dentro de un HDF5. Usar `biom.load_table()` para abrirlo.

Los *OTUs* agrupan secuencias al 97% de similitud, lo que introduce ruido. Los *ASVs* (Amplicon Sequence Variants) representan secuencias exactar y son el estándar acutal. En Deblur, el ID de cada ASV es la propia secuencia nucleotídica.

*Rarefaccion*: normalización que submuestrea todas las muestras al mismo número de lecturas (aquí 5.000). Permite comparar diversidad microbiana de forma justa. El precio es que muestras con pocas lecturas se eliminan.


## Recursos
* Documentacion de biom y biom-format: ```help(biom)```
* Repo oficial de EMP: https://github.com/biocore/emp?tab=readme-ov-file


## Dudas varias
* Entorno y gestor de paquetes para scripts y programas que manejan datos biológicos.