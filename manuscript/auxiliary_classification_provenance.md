# Auxiliary literary classification table — provenance note

Source file supplied by the project author: `ADSO_processing.xlsx`.

Direct inspection of the workbook shows one sheet (`Hoja1`) spanning `A1:T41`: **20 columns and 40 author records plus the header row**. Columns include `Movimiento Literario`, `Lopez Bueno 2006`, `Pedraza`, network centralities, modularity classes, and several date-like fields. The project author reports that the file was assembled previously from a Hernández-Lorenzo publication/repository workflow and another GitHub source and had already been validated in that earlier work, but the exact upstream repository path is not currently remembered.

## Admissible use in Paper 1

Until the exact upstream provenance is recovered, this workbook is **not** used to construct poem-level chronology and its date-like columns (`Time`, `Time II`, `Birth`, `Death`, `timeset`) are not imported into `composition_min/max` or temporal constraints. Some author-level date fields are not internally suitable as poem chronology, which reinforces this decision.

The currently useful content is the literary-historical classification layer:

- `Movimiento Literario`: broad Renaissance / Baroque label;
- `Lopez Bueno 2006`: Innovation / Renovation / Transition / Culmination / Baroque / Continuity and Dispersion grouping;
- `Pedraza`: independent Renaissance / Baroque classification where available;
- `modularity2`: legacy network-community label, retained only as a diagnostic comparison and never as historical ground truth.

Two derived, non-raw tables are stored in the repository:

- `data/derived/auxiliary_literary_classification_all.csv`: classification-only extraction for all 40 author records;
- `data/derived/auxiliary_literary_classification_priorityA.csv`: crosswalk to the current Priority-A Navarro author folders. The single Lope de Vega author-level row is duplicated only at the crosswalk stage for `LopeDeVega_1` and `LopeDeVega_2`; this does not create two independent historiographic observations.

## Methodological role

This table is treated as an **external validation / stratification layer**, not as training labels and not as a chronology source. Phase 6 uses it only after the temporal evidence has been reconstructed independently.

For the current Priority-A authors, the López Bueno sequence is:

- Innovation: Garcilaso, Boscán;
- Renovation: Herrera;
- Transition: Arguijo, Jáuregui, Cervantes, Espinosa, Carrillo;
- Culmination: Góngora, Lope;
- Baroque: Quevedo.

This ordering is useful for the identifiability problem because it is richer than a binary Renaissance–Baroque split. The paper can therefore test whether independently constructed semantic trajectories recover or challenge these literary-historical distinctions.

## Safeguard against circularity

The auxiliary classifications must not be used to select semantic edges, tune NLP parameters, determine change points, or assign poem dates. They may be used only for post hoc comparison, stratified diagnostics, robustness checks, and interpretation. This separation is necessary if the eventual comparison between historiography and semantic-network structure is to count as external validation rather than circular confirmation.

## Provenance task

Before publication, recover and cite the exact upstream source(s) for the ADSO processing table. Until then, manuscript claims should cite the underlying literary scholarship (e.g. López Bueno 2006 / Pedraza) directly rather than citing this local spreadsheet.
