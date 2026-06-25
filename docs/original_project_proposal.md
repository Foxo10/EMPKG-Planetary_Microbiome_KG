
---

### **Theme 1: The EMP as a Foundational Knowledge Graph**
**Title:** **EMPKG: Building a Planetary-Scale Microbial Knowledge Graph from the Earth Microbiome Project with LLM-Enhanced Metadata Annotation**

**Core Idea:** Transform the EMP's massive, standardized dataset (thousands of samples across biomes) into a unified Knowledge Graph. The challenge is that sample **metadata** (environmental context like pH, temperature, biome type) is often in free-text or inconsistent formats. Use an LLM to normalize and structure this metadata, then link microbial abundances to environmental parameters and geographic locations in a queryable graph.

**Key Components:**
1.  **EMP Data Integration:** Download EMP samples (16S/18S rRNA amplicon data) with their environmental metadata.
2.  **LLM for Metadata Harmonization:** Design an LLM pipeline to parse heterogeneous metadata fields (e.g., "soil, forest, temperate" → standardized terms: `ENVO:00002258` (soil), `ENVO:01000174` (temperate broadleaf forest)).
3.  **Ontology Mapping:** Link all entities to ontologies: **ENVO** (environments), **NCBITaxon** (microbes), **GAZ** (geography), **CHEBI** (chemicals).
4.  **Graph Construction:** Build a KG where nodes are `Sample`, `Location`, `EnvironmentalFeature`, `Taxon`; edges represent `was_collected_at`, `has_feature`, `contains_taxon_with_abundance_X`.
5.  **Query System:** Enable powerful queries: *"Show all acidobacterial taxa whose abundance correlates with low pH in forest soils across North America."*

**Why it's Great with EMP:**
*   **Standardization Power:** EMP's standardized protocols make cross-study comparison feasible—a perfect KG use case.
*   **Global Scale:** Offers a "planetary" perspective few projects can match.
*   **Core CS Problem:** Massive data integration, entity resolution, and efficient graph querying on large-scale data.

---

### **Theme 2: LLM as an Ecological Pattern Discoverer**
**Title:** **EcoLLM: Discovering Latent Ecological Rules in the Earth Microbiome Project via LLM-Based Hypothesis Generation and Knowledge Graph Validation**

**Core Idea:** Use the EMP KG (from Theme 1 or a simplified version) not just for querying, but for **discovery**. Train or prompt an LLM on ecological principles and the EMP schema to generate testable hypotheses about microbial distributions (e.g., *"Thermophilic archaea should be absent from marine Arctic samples"*). Then, automatically **validate** these hypotheses by querying the KG, creating a closed-loop discovery system.

**Key Components:**
1.  **Hypothesis Generation Module:** Fine-tune a small LLM (like Mistral-7B) on ecological text, or use advanced prompting with a large LLM, to output structured hypotheses in a format like: `(Taxon, Relation, Environment, Expected_Result)`.
2.  **Hypothesis-to-Query Compiler:** Translate the structured hypothesis into a Cypher (Neo4j) or SPARQL query against the EMP KG.
3.  **Validation & Feedback Loop:** Execute the query, compare results to the expectation, and score the hypothesis. Use results to provide few-shot examples back to the LLM.
4.  **Discovery Dashboard:** Visualize generated hypotheses, their validation status, and surprising findings (where the KG contradicted the LLM's expectation).

**Why it's Groundbreaking with EMP:**
*   **Moves Beyond Retrieval to Discovery:** This is a next-generation application of AI in science.
*   **EMP is Uniquely Suited:** Its global coverage allows testing of broad biogeographic rules.
*   **Truly Interdisciplinary:** Blends ecology, knowledge representation, and generative AI in a novel way.

---

### **Theme 3: Predictive Modeling of Microbial Dark Matter**
**Title:** **Predicting the Ecological Niche of Uncultured Microbial Clades (Microbial Dark Matter) in the EMP using Knowledge Graph Embeddings and LLM-Derived Functional Profiles**

**Core Idea:** A large fraction of EMP sequences belong to **"microbial dark matter"**—taxa with no cultured representatives and unknown functional traits. This project predicts their ecological role by:
1.  Using **KG embeddings** of their *co-occurrence network* with known taxa in the EMP graph.
2.  Using an **LLM** trained on genomic literature to infer potential functions from their taxonomic name/closest relatives (e.g., a clade named "JTB255" within *Gammaproteobacteria* might be predicted to be "sulfur-oxidizing" based on contextual papers).
3.  Fusing these signals to predict the environmental conditions where they thrive.

**Key Components:**
1.  **Identify Dark Matter:** Filter EMP taxa without functional annotations or cultured representatives.
2.  **Build Co-occurrence KG:** Create a graph linking taxa that frequently appear together in samples.
3.  **LLM for Functional Imputation:** Use a biomedical LLM (BioBERT, PubMedBERT) to generate textual functional profiles for clades based on their lineage and abstracts mentioning related taxa.
4.  **Multi-Modal Node Embedding:** Combine structural embeddings (from the co-occurrence graph) and semantic embeddings (from LLM text) for each taxon.
5.  **Niche Prediction Model:** Train a classifier to predict biome/habitat labels for dark matter nodes using the embeddings of their well-characterized neighbors.

**Why EMP is Critical Here:**
*   **Dark Matter is Pervasive:** EMP's scale ensures you'll have vast amounts of these uncharacterized sequences.
*   **Context is Key:** The global environmental metadata is essential for defining the "niche" to predict.

---

### **Theme 4: Temporal/Spatial Dynamics in the EMP**
**Title:** **ChronoBiome: Modeling Microbial Succession and Biogeography through Dynamic Knowledge Graphs from Longitudinal EMP Data**

**Core Idea:** While EMP is largely cross-sectional, some datasets have temporal or spatial series. Build a **temporal knowledge graph** where relationships have timestamps or spatial coordinates. Use **Graph Neural Networks (GNNs)** or **temporal KG embedding** methods to model how microbial communities change over time (e.g., after a perturbation) or across environmental gradients.

**Key Components:**
1.  **Temporal/Spatial EMP Data:** Curate EMP studies with time-series (e.g., soil after a fire) or clear transects (ocean depth, salinity gradient).
2.  **Dynamic KG Schema:** Extend the KG to support `(subject, relation, object, time, location)`.
3.  **Temporal Reasoning:** Apply models like **RE-NET** or **T-GAP** to learn evolutionary patterns of the graph.
4.  **Forecasting Application:** Predict future community states or fill in missing spatial samples. *"Given a grassland microbiome in summer, predict its state in winter."*
5.  **LLM for Explaining Shifts:** Use an LLM to generate natural language explanations of predicted shifts based on the learned graph dynamics and literature.

**Why EMP Enables This:**
*   **Standardized Time-Series:** EMP's harmonized data allows for comparing dynamics across different studies and biomes.
*   **Spatial Explicit:** Many EMP samples have precise GPS coordinates, enabling true spatial graph analysis.

---

### **Recommended Project Pathway:**

For a final degree project, I recommend a **phased approach focusing on Theme 1 with a clear extension**:

**Phase 1 (Core - 3-4 months):** Build **EMPKG-lite**. Ingest a subset of EMP data (e.g., 10,000 samples from 3 biomes). Use an LLM (via careful prompting) to clean and map metadata to ontologies. Build the graph in Neo4j and demonstrate insightful cross-biome queries.

**Phase 2 (Extension - 1-2 months):** Choose ONE compelling extension to demonstrate depth:
*   **Extension A (Discovery):** Implement a simple version of **EcoLLM's hypothesis generator** (just prompting a large LLM) and validate 5-10 hypotheses against your KG.
*   **Extension B (Prediction):** Add a **co-occurrence network** to your KG and use simple node embeddings (Node2Vec) to predict the biome of a held-out set of samples.
*   **Extension C (Visualization):** Build an interactive web dashboard (with Kepler.gl for maps, Plotly for graphs) to explore your planetary microbiome KG.

**Skills Demonstrated:** Big Data Processing, NLP/LLMs, Ontology Engineering, Graph Databases, Spatial Data, Scientific Visualization, and Systems Design.

**Final Title Suggestion:** *"A Scalable Framework for Constructing and Querying a Planetary Microbiome Knowledge Graph from the Earth Microbiome Project"*

This approach is ambitious but manageable, directly tackles your interest areas, and results in an impressive, demonstrable system with clear scientific relevance.
