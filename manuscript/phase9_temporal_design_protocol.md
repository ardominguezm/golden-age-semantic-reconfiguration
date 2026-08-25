# Phase 9 temporal design protocol — pre-semantic feasibility

## Purpose

Phase 8 produced a validated **primary composition chronology of 97 sonnets** distributed across six authors: Góngora 58, Garcilaso 18, Quevedo 9, Herrera 5, Espinosa 4, and Cervantes 3. All five external López Bueno historiographic stages are represented, and the Phase-8 identifiability diagnostics passed.

Phase 9 freezes chronology acquisition for the main analysis and asks a different question: **how should uncertain poem dates be converted into a temporal design without looking at semantic results?** No semantic feature, network edge, community, distance, change-point statistic, or literary-historical label may be used to choose the main temporal windows.

The canonical notebook is `notebooks/paper1_analysis.ipynb`. The accidental root-level duplicate created by the Phase-8 Colab save was removed after its executed state had been preserved in Git history (commit `7387822b28415685ec36959f36d54eaa8cfc9252`).

## Frozen primary chronology

Phase 9 reconstructs only the primary composition-time layer needed for temporal design. Earlier circulation, terminus-ante-quem, and sensitivity-only evidence remains documented in Phases 5–8 and is not promoted to primary dating here.

The expected Phase-8 invariant is:

- 97 primary poems;
- 6 primary authors;
- Góngora 58;
- Garcilaso de la Vega 18;
- Quevedo 9;
- Fernando de Herrera 5;
- Pedro Espinosa 4;
- Cervantes 3.

Any failure of this invariant stops Phase 9.

## Date uncertainty model

For a poem with an admitted bounded composition interval `[a_i, b_i]`, Phase 9 draws an integer year from

`DiscreteUniform({a_i, ..., b_i})`.

Exact-year poems remain fixed. The uniform distribution is deliberately non-informative within the scholarly interval: the current evidence does not justify privileging one internal year over another.

The Monte Carlo design audit uses:

- random seed: `20260825`;
- 1,000 realizations.

These draws are used only to assess temporal support and author concentration. They do not yet enter a semantic model.

## Candidate fixed-calendar designs

The main-design candidates are rolling calendar windows with:

- widths: 10, 15, 20, and 25 years;
- step: 5 years;
- edges generated mechanically from the minimum and maximum primary composition chronology.

The traditional reference dates **1580** and **1605** do not define the windows. After the windows are generated, Phase 9 reports whether windows containing these dates have adequate support. The markers therefore remain external historiographic references rather than tuning parameters.

## Operational support diagnostics

For each Monte Carlo realization, a fixed window is labelled `usable` when all of the following hold:

- at least 10 poems;
- at least 2 represented authors;
- entropy-based effective number of authors `N_eff >= 1.5`;
- largest-author share `<= 0.85`.

A calendar window is labelled `stable_usable` when `P(usable) >= 0.80` across the Monte Carlo chronology realizations.

These values are engineering guardrails for network feasibility, not literary-theoretical thresholds and not inferential tests. They are frozen before semantic analysis.

For every candidate width the notebook exports:

- number and fraction of stable usable windows;
- longest consecutive run of stable usable windows;
- temporal extent of stable support;
- median effective authors;
- median largest-author share;
- per-window 10th/90th percentile support diagnostics.

## Equal-count sensitivity design

Equal-count windows are evaluated only as a robustness/sensitivity option, not as the default main design. Candidate sizes are:

- 20 poems;
- 25 poems;
- 30 poems;

with stride 5 poems after sorting the sampled composition years.

For each size the notebook reports the calendar-year span induced by equal-count windows, author diversity, effective authors, and author concentration. A very large or unstable year span would make an equal-count design historically difficult to interpret even if its sample size is numerically balanced.

## Leave-one-author-out feasibility

For each fixed-window width, Phase 9 repeats the support calculation after excluding each one of the six dated authors in turn. This is a pre-semantic fragility audit. In particular, the analysis records how much temporal support survives removal of Góngora, rather than discovering author dependence only after observing a semantic result.

Failure of a leave-one-author-out design does not automatically invalidate the paper; it determines which robustness claims will be feasible and which temporal regions cannot support author-ablated networks.

## Decision rule for Phase 10

Phase 9 does **not** automatically declare the temporal width that produces the most attractive literary result. Phase 10 will select the main temporal design using only the exported Phase-9 support tables, before semantic networks are built.

Preference will be given to the smallest fixed-calendar width that provides a sufficiently long and stable connected temporal run without excessive author dominance. Wider windows will be retained as sensitivity analyses. Equal-count windows will remain secondary unless fixed-calendar support is clearly inadequate.

Only after this choice is documented will the project proceed to semantic preprocessing and network construction.

## Outputs

The notebook writes the following runtime artifacts to `/content/gasr_phase9_outputs/`:

- `phase9_primary_chronology.csv`
- `phase9_interval_summary.csv`
- `phase9_fixed_window_design_summary.csv`
- `phase9_fixed_window_support.csv`
- `phase9_external_marker_support.csv`
- `phase9_equal_count_sensitivity_summary.csv`
- `phase9_leave_one_author_out_feasibility.csv`

The final checkpoint must explicitly state that **no semantic features or networks were computed**.