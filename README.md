# Golden Age Semantic Reconfiguration

Companion repository for the manuscript **“Literary Change as Relational Reconfiguration: Temporal Semantic Networks of Spanish Golden Age Poetry.”** Submitted in *Digital Scholarship in the Humanities*, Oxford University Press, Sept. 2026.

This repository contains the reproducibility materials for a study of temporally organized change in semantic relations across a dated corpus of Spanish Golden Age sonnets. Poetic lines are represented as weighted semantic networks, chronological uncertainty is propagated through repeated chronology realizations, and adjacent temporal windows are evaluated with complementary counterfactual, mechanism, and robustness analyses.

## Repository structure

- `notebooks/paper1_analysis.ipynb` — canonical Google Colab entry point.
- `src/temporal_robustness.py` — reconstruction of the dated corpus and temporal-resolution robustness analyses.
- `src/main_analysis_mechanism.py` — primary 20-year trajectory, counterfactual analyses, historical overlay, and edge-level mechanism decomposition.
- `src/contribution_structure.py` — contribution-coverage and meso-scale structure analyses.
- `src/representation_robustness.py` — lemma-only and surface-form representation robustness analyses.
- `data/derived/publication/` — compact numerical data corresponding to the principal figures and tables.
- `data/derived/auxiliary_literary_classification_priorityA.csv` — auxiliary literary-stage reference used only for the descriptive historical overlay; it is not used to construct semantic networks or counterfactual null models.
- `tests/` — targeted regression checks for publication-facing analysis code.
- `requirements.txt` — Python dependency specification for the public workflow.
- `CITATION.cff` — repository citation metadata.

## Reproducing the analysis

The recommended route is to open:

`notebooks/paper1_analysis.ipynb`

in Google Colab and execute the notebook from top to bottom. The notebook clones the repository, installs the documented dependencies, and runs the analysis scripts in their required sequence. The later contribution-structure and representation-robustness analyses intentionally reuse the analytical state reconstructed by the main-analysis script.

The principal chronology analysis uses 1,000 chronology realizations. Counterfactual distributions use 2,000 realizations for each relevant comparison and weighting scheme. The main temporal design uses 20-year rolling windows with a 5-year step; 15- and 25-year windows are used to assess temporal-resolution sensitivity.

Key software components explicitly fixed in the analysis code include spaCy 3.8.7, `es_core_news_sm` 3.8.0, and NetworkX 3.5. External scholarly corpora are retrieved at pinned repository revisions where applicable.

## Analytical scope

The dated sample contains 97 sonnets by six authors. Semantic relations are constructed from line-level co-occurrence among alphabetic content-word tokens (NOUN, VERB, ADJ, and ADV) and weighted using positive pointwise mutual information (PPMI). The primary aggregation is author-balanced, with raw poem weighting used as a secondary specification.

The study evaluates temporal rewiring using cosine distance over persistent-concept edge vectors. The principal mechanism comparison contrasts the 1580–1599 and 1585–1604 windows. Edge-level contributions are used to distinguish relation births, deaths, and reweighting of relations present in both networks.

Two counterfactual models address different questions. N1 preserves local author composition and poem-overlap structure while reassigning poems within the adjacent comparison. N2 permutes chronology within author and evaluates the observed transition against the distribution of trajectory-level maxima.

## Derived publication data

`data/derived/publication/` provides compact CSV files underlying the principal quantitative figures and tables. These files are intended for direct inspection of reported values without requiring a complete rerun of the computational workflow.

Figures 1 and 6 are schematic or contextual and therefore do not have independent numerical plot-data files. Literary source texts are not redistributed in this repository.

## Interpretation and limitations

The results support temporally organized and representation-robust relational turnover under the main temporal design. They do not establish a discrete or composition-independent Renaissance-to-Baroque breakpoint. Interpretation is constrained by uneven author representation, chronological uncertainty, sensitivity to temporal resolution, and the use of a modern Spanish NLP model on historical verse.

The principal chronology also cannot be identified independently of Góngora because the available dated corpus becomes insufficient after his removal. The repository should therefore be read as supporting a reproducible analysis of temporal organization in relational turnover rather than as a claim of a formally detected literary-historical phase transition.

## Source texts and licensing

Literary texts are obtained from the external scholarly corpora referenced in the analysis code and remain subject to their original licensing conditions. This repository contains analysis code and derived analytical material rather than redistributed copies of those corpora.

No software license is asserted here beyond the rights provided by the repository host; source-text licensing remains entirely governed by the original corpus providers.

## Citation

Please cite the associated article once final bibliographic details are available. Until then, use the citation metadata provided in `CITATION.cff`.
