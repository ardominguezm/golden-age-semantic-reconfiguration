# Phase 11B — Structural representation calibration

## Purpose

Phase 11B is a blind structural-feasibility calibration inserted after Phase 11 showed that the conservative preregistered graph (within-line co-occurrence, raw pair support >=2) was too sparse for a defensible rewiring analysis. The paper's scientific objective remains unchanged: test whether the Renaissance-to-Baroque transition is better characterized as gradual semantic drift or as structural reorganization among poetic concepts.

This phase does **not** estimate semantic temporal distance, a change point, or the fit of 1580/1605. Historiographic labels are not used for representation selection.

## Candidates

Only alternatives already frozen in Phase 10 are admissible:

1. `A_line_support2`: unique concept presence within a poetic line; minimum raw pair support 2. This is the Phase-11 benchmark.
2. `B_line_support1`: same poetic-line context; minimum raw pair support 1. This was preregistered in Phase 10 as a support sensitivity.
3. `C_token5_support1`: sliding context of five retained content tokens, never crossing poem boundaries; minimum raw pair support 1. This was preregistered in Phase 10 as the alternative context sensitivity.

The main vocabulary remains the globally frozen 668 `lemma::POS` concepts with poem document frequency >=2. The primary chronology remains 97 poems, 6 authors, with 1,000 Monte Carlo chronology realizations and the 9 preregistered 20-year windows stepped by 5 years.

## Raw and author-balanced modes

Every candidate is evaluated in both raw and author-balanced mode. For any context system, if a poem by author `a` contributes `U_p` context units and there are `n_(a,W)` poems by the author in the temporal window, each context unit receives weight

`1 / (n_(a,W) U_p)`

in author-balanced mode. Hence each author present in a window contributes total context mass one. Raw mode assigns mass one per context unit.

## Frozen structural criteria

Candidate selection is based only on the following median structural quantities across chronology realizations for each window x mode cell:

- connected fraction >= 1/3: at least one third of active concepts participate in an edge;
- giant-component fraction among connected nodes >= 0.50;
- mean degree among connected nodes >= 2.0;
- effective edge fraction >= 0.25, where effective edge count is the exponential Shannon effective number of positive PPMI edge weights divided by the observed edge count.

A candidate passes only if **all 18 cells** (9 windows x 2 modes) satisfy all four criteria. These are engineering feasibility guardrails, not literary-theoretical thresholds.

## Selection rule

Candidates are ordered by minimal deviation from the frozen main representation:

`A_line_support2` -> `B_line_support1` -> `C_token5_support1`.

The selected representation is the first candidate in this order that passes all 18 cells. If none passes, Phase 11B returns `NO REPRESENTATION SELECTED`; thresholds are not relaxed after inspecting results.

## Why this preserves the novelty claim

The paper's contribution is not the choice of a graph threshold. The novelty is the combined design in which composition chronology is reconstructed independently; semantic relations are modeled at concept level rather than as author similarity; chronology uncertainty is propagated; author dominance is explicitly controlled; and the eventual historical statistic separates **lexical turnover** from **relational rewiring among persistent concepts**. Historiographic periodization is external validation rather than supervision.

Phase 11B exists only to ensure that the graph representation is rich enough for that later decomposition to be meaningful without tuning to a desired historical result.

## Phase 12 gate

Only if a candidate is selected may Phase 12 preregister the historical reconfiguration statistics. Phase 12 should then define, before viewing temporal peaks:

- lexical turnover between adjacent windows;
- edge-set and edge-weight rewiring restricted to concepts persistent across adjacent windows;
- raw versus author-balanced agreement;
- chronology uncertainty intervals;
- null models and change-point logic.

No historical interpretation is authorized in Phase 11B itself.
