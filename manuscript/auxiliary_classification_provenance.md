# Auxiliary literary classification table — provenance note

Source file supplied by the project author: `ADSO_processing.xlsx`.

The workbook contains an author-level network-processing table with 41 rows and columns including `Movimiento Literario`, `Lopez Bueno 2006`, `Pedraza`, network centralities, modularity classes, and several date-like fields. The project author reports that the file was assembled previously from a Hernández-Lorenzo publication / repository workflow and another GitHub source and had already been validated in that earlier work, but the exact upstream repository path is not currently remembered.

## Admissible use in Paper 1

Until the exact upstream provenance is recovered, this workbook is **not** used to construct poem-level chronology and its date-like columns (`Time`, `Time II`, `Birth`, `Death`, `timeset`) are not imported into `composition_min/max` or temporal constraints. The sheet contains some internal date inconsistencies, which reinforces this decision.

The currently useful content is the literary-historical classification layer for Priority-A authors:

- `Movimiento Literario`: broad Renaissance / Baroque label;
- `Lopez Bueno 2006`: Innovation / Renovation / Transition / Culmination / Baroque-type historical grouping;
- `Pedraza`: independent Renaissance / Baroque classification where available;
- `modularity2`: legacy network-community label, retained only as a diagnostic comparison and never as a historical ground truth.

A minimal crosswalk is stored in `data/derived/auxiliary_literary_classification_priorityA.csv`.

## Methodological role

This table should be treated as an **external validation / stratification layer**, not as training labels and not as a chronology source. In Phase 6 and later analyses it can be used to ask whether semantic-network trajectories recover historically meaningful distinctions independently of the computational model. In particular, the López Bueno categories are useful because the Priority-A authors span:

- Innovation: Garcilaso, Boscán;
- Renovation: Herrera;
- Transition: Arguijo, Jáuregui, Cervantes, Espinosa, Carrillo;
- Culmination: Góngora, Lope;
- Baroque: Quevedo.

This is especially valuable for the identifiability problem: it provides a historiographic ordering/stratification that is richer than a binary Renaissance–Baroque split and can later be compared with semantic reconfiguration results.

## Provenance task

Before publication, recover and cite the exact upstream source(s) for the ADSO processing table. Until then, manuscript claims should cite the underlying literary scholarship (e.g. López Bueno 2006 / Pedraza) directly rather than citing this local spreadsheet.
