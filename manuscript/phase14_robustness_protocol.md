# Phase 14 — Robustness of semantic reconfiguration and null contrast

## Purpose

Phase 13 produced a mixed result: the transition centered at 1592 is unusual under the secondary global within-author chronology permutation, particularly in author-balanced mode, but it does not exceed the preregistered primary local author-overlap-preserving null. Phase 14 therefore asks a narrower question before any historiographic validation:

> **Is the observed temporal pattern, and especially the contrast between N1 and N2, stable to the semantic representation, vocabulary threshold, temporal-window width, text layer, and author composition choices that were frozen before Phase-13 results?**

Phase 14 is a robustness phase, not a new search for a favorable specification. It may diagnose sensitivity or stability, but it may not replace the Phase-13 primary result. Historiographic dates, period labels, and change-point models remain excluded from construction and tuning.

## Frozen main benchmark

The benchmark remains:

- 97 primary-dated poems, 6 authors;
- 1,000 chronology realizations, seed `20260825`;
- Navarro TEI as the full-coverage main text layer;
- spaCy 3.8.7 + `es_core_news_sm` 3.8.0;
- concept identity `lemma::coarse_POS`, POS in NOUN/VERB/ADJ/ADV;
- global vocabulary poem-DF >=2 (668 concepts);
- 20-year rolling windows, 5-year step, 1565–1584 through 1605–1624;
- `B_line_support1`: within-line co-occurrence, minimum raw pair support 1, PPMI;
- rewiring measured as cosine distance on persistent-concept edge vectors;
- both raw and author-balanced modes;
- N1 local overlap-preserving null as the primary counterfactual and N2 global within-author chronology permutation as secondary.

The executed Phase-13 benchmark values are frozen in `manuscript/phase13_results_decision.md` and are not re-selected in Phase 14.

## Robustness axes

Only sensitivity designs already stated in Phases 9–13 are admissible.

### R1 — Alternative context representation

Use `C_token5_support1` from Phase 11B:

- sliding window of 5 retained content tokens;
- never cross poem boundaries;
- pair support >=1;
- same global DF>=2 vocabulary and PPMI weighting.

This tests whether the result depends on the poetic line as the local semantic context.

### R2 — Stricter global vocabulary

Keep the main `B_line_support1` representation but require poem document frequency >=3 instead of >=2. The vocabulary threshold was preregistered in Phase 10 as a sensitivity and is not chosen from Phase-13 outcomes.

### R3 — Temporal-window width

Keep the main semantic representation and use the exact stable calendar windows identified pre-semantically in Phase 9. This clarification is made before Phase-14 semantic robustness is executed and uses only Phase-9 support outputs.

For the 15-year design, stable windows are:

- 1570–1584 and 1575–1589 (an early two-window run);
- 1585–1599, 1590–1604, 1595–1609, 1600–1614, 1605–1619, and 1610–1624 (the longest six-window run).

The unstable 1580–1594 window is not inserted to bridge the two runs; transitions are computed only between consecutive stable windows separated by the frozen 5-year step.

For the 25-year design, the complete stable run is:

- 1560–1584, 1565–1589, 1570–1594, 1575–1599, 1580–1604, 1585–1609, 1590–1614, 1595–1619, and 1600–1624.

Neither 1580 nor 1605 defines these windows. Their locations are inherited from the Phase-9 calendar grid and support audit.

Because odd-width designs place adjacent-transition centers at half-integer years, exact-center Spearman concordance with the 20-year benchmark is undefined. For R3 the notebook therefore reports the complete sensitivity trajectory, its maximum, and the two sensitivity transition centers bracketing the benchmark 1592 episode where available. It does not interpolate or shift a sensitivity trajectory to manufacture common centers.

### R4 — Paired standardized-text sensitivity

The Hernández-Lorenzo standardized network corpus is used only for poem identities that were already reconciled to Navarro with the Phase-10 crosswalk rules. Because the standardized layer does not cover all 97 primary poems and Pedro Espinosa has no corresponding author file, this analysis is explicitly **paired and restricted**, not a replacement longitudinal corpus.

For every eligible poem, compare Navarro TEI with its matched standardized text under the same NLP and network specification. To avoid letting one text layer determine the other's vocabulary, each paired layer independently applies the already-frozen global poem-DF >=2 vocabulary-construction rule to the **same matched poem identities**. The resulting trajectory statistics, coverage, and vocabulary sizes are compared; no vocabulary is chosen from the outcome. This layer-specific application of the same frozen rule is specified before Phase-14 results.

Coverage by author/window is reported before semantic comparison. No unmatched standardized poem is substituted for a canonical poem. This sensitivity is descriptive unless temporal support satisfies the same engineering support requirements as the benchmark after restricting to paired poems.

### R5 — Feasible leave-one-author-out analyses

Author ablation eligibility is determined only from the pre-semantic Phase-9 feasibility logic:

- at least 10 poems per tested window;
- at least 2 authors;
- effective authors >=1.5;
- largest-author share <=0.85;
- stable usability probability >=0.80 over chronology realizations.

An author is tested only for transitions whose two adjacent windows satisfy these gates after exclusion. No semantic result may change ablation eligibility. In particular, no claim is made for a Góngora-removed region that fails the frozen temporal support gate.

## Observed robustness trajectories

For R1–R3 and any R4/R5 design that passes its support gate, rebuild the trajectory over 1,000 chronology realizations and report for every eligible transition and mode:

- median, q10 and q90 lexical turnover;
- median, q10 and q90 persistent-concept cosine rewiring;
- rank of each transition by median rewiring;
- raw-versus-author-balanced difference;
- number of persistent concepts.

The Phase-13 1592 transition remains the benchmark episode because it was identified before Phase 14. Sensitivity trajectories may show a different maximum, but a new maximum is reported as a robustness outcome and is not promoted retroactively as a replacement primary event.

## Null robustness

### N1 robustness — primary

For each admissible robustness design, apply the same local author-overlap-preserving reassignment logic as Phase 13. To keep computational scale fixed before results, use:

- `ROBUST_NULL_SEED = 20260827`;
- 50 chronology realizations selected evenly from the 1,000 benchmark chronology draws;
- 20 counterfactual replicates per selected realization;
- 1,000 N1 counterfactual realizations per eligible transition and mode.

Report null median, q90, q95, observed-minus-null excess, observed percentile and one-sided empirical tail probability. These robustness tail probabilities are descriptive stability diagnostics and do not supersede the 2,000-draw Phase-13 N1 result.

### N2 robustness — secondary

For R1–R3, generate 1,000 coherent within-author chronology-permutation trajectories using the same 50 x 20 budget and compute both transition-specific tails and the trajectory-level max statistic. R4 and R5 use N2 only when the paired/ablated corpus passes the frozen temporal support gates over the full tested region; otherwise they remain descriptive robustness checks.

## Concordance summaries

For each robustness design, report without defining a post-hoc binary success threshold:

1. whether the benchmark episode remains among the largest rewiring movements, or for R3 the behavior of the pre-specified neighborhood bracketing 1592;
2. sign and magnitude of observed-minus-N1-median excess;
3. N1 percentile and empirical tail probability in raw and author-balanced modes;
4. N2 percentile and max-statistic tail probability when applicable;
5. Spearman rank correlation between benchmark and sensitivity trajectories only when exact transition centers are shared; otherwise `NA` with the reason recorded;
6. the absolute raw-versus-author-balanced difference.

The analysis emphasizes the pattern across sensitivity designs, not a count of p-values below an arbitrary cutoff.

## Interpretation rules

Phase 14 cannot state that the main Phase-13 N1 null was rejected. Three outcomes are possible:

- **Stable mixed evidence:** the 1592 episode and N2 unusualness persist, but N1 continues to overlap strongly. This supports a nuanced interpretation in which temporal ordering exists but local finite-corpus turnover explains much of the apparent structural movement.
- **Robust conditional excess:** multiple previously frozen sensitivities show a clearly larger N1 excess while the benchmark remains weaker. This is secondary, representation-dependent evidence and must be reported as such rather than replacing the main analysis.
- **Fragility:** the peak rank, sign of excess, or author-balanced behavior changes substantially across the frozen sensitivities. The paper should then emphasize methodological decomposition and corpus-identifiability limits rather than a strong historical reconfiguration claim.

No historiographic label is used to decide among these outcomes.

## External historical validation remains downstream

Only after Phase 14 is complete may the project compare the independently estimated temporal pattern with external historiographic markers such as 1580 and 1605, literary-period classifications, and close readings of poems/concept relations contributing to any robust episode. Those external sources may interpret a signal but cannot create or tune it.

## Planned runtime outputs

The Phase-14 notebook should export:

- `phase14_robustness_specification.csv`;
- observed sensitivity trajectories and summaries;
- N1 robustness null summaries;
- N2 robustness summaries and max-statistic tables where admissible;
- trajectory concordance table;
- paired Navarro/Hernandez coverage and semantic comparison tables;
- leave-one-author-out feasibility and result tables;
- a final robustness decision table that records stability/fragility descriptively without redefining the Phase-13 primary inference.
