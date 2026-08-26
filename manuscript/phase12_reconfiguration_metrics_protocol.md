# Phase 12 — Lexical turnover versus persistent-concept rewiring

## Paper 1 target

Paper 1 tests whether the Renaissance-to-Baroque transition in Spanish Golden Age poetry is better described as gradual semantic drift or as a structural reorganization of the poetic semantic system. The central empirical distinction is therefore not simply whether vocabulary changes through time, but whether **relations among concepts that persist across time are themselves rewired**.

Phase 12 is the first phase that measures temporal semantic change. It does **not** test 1580 or 1605, use historiographic period labels, estimate a change point, or claim a Renaissance/Baroque transition. Those comparisons remain downstream and external to the construction of the trajectory.

## Frozen inputs

- Primary chronology: 97 poems, 6 authors.
- Chronological uncertainty: 1,000 Monte Carlo realizations, seed `20260825`.
- Main temporal design: 20-year rolling windows with 5-year step, from 1565–1584 through 1605–1624 (9 windows; 8 adjacent transitions).
- Main text: Navarro TEI.
- NLP: spaCy 3.8.7 + `es_core_news_sm` 3.8.0.
- Concept identity: `lemma::coarse_POS`, POS in NOUN/VERB/ADJ/ADV.
- Global vocabulary: poem document frequency >=2 (668 concepts), frozen before temporal analysis.
- Network representation selected blindly in Phase 11B: **B — within-line concept co-occurrence, minimum raw support 1, positive PMI (PPMI)**.
- Network modes: `raw` and `author_balanced`.

Phase 11B selected B because it was the first preregistered representation, in increasing order of relaxation, to satisfy all 18 structural feasibility cells. Candidate C remains a later context sensitivity and is not used to redefine the main Phase-12 trajectory.

## 1. Active lexical set and lexical turnover

For adjacent temporal windows t and t+1, let V_t and V_(t+1) be the sets of active concepts from the globally frozen vocabulary.

The primary lexical-turnover statistic is Jaccard distance:

L_t = 1 - |V_t ∩ V_(t+1)| / |V_t ∪ V_(t+1)|.

L_t is independent of edge weights and, for a fixed chronology realization, is identical in raw and author-balanced modes. We also retain:

- number of active concepts in each window;
- number of persistent concepts |V_t ∩ V_(t+1)|;
- persistent-concept fraction |V_t ∩ V_(t+1)| / |V_t ∪ V_(t+1)|.

## 2. Persistent-concept relational rewiring

Define the persistent concept set

P_t = V_t ∩ V_(t+1).

Both networks are first restricted to P_t. This is essential: the rewiring statistic is not allowed to gain signal merely because nodes appear or disappear.

Let E*_t be the positive-PPMI edges whose two endpoints lie in P_t, and likewise E*_(t+1). Let U_t = E*_t ∪ E*_(t+1). Over the common edge universe U_t, construct vectors w_t and w_(t+1), assigning weight zero when an edge is absent from one network.

### Primary rewiring statistic: cosine distance

R_t = 1 - <w_t,w_(t+1)> / (||w_t||_2 ||w_(t+1)||_2).

This statistic is scale-invariant. It therefore targets changes in the **pattern of relations among persistent concepts** rather than a global increase or decrease in PPMI magnitude.

### Secondary rewiring diagnostics

Two complementary quantities are frozen before results are inspected:

1. **Binary persistent-edge turnover**

   J^E_t = 1 - |E*_t ∩ E*_(t+1)| / |E*_t ∪ E*_(t+1)|.

2. **Jensen–Shannon divergence of normalized persistent-edge PPMI mass**

   Edge-weight vectors are normalized to probability mass on U_t and their base-2 Jensen–Shannon divergence is computed. This lies in [0,1] when defined.

These are robustness diagnostics. Cosine distance remains the primary Phase-12 relational statistic.

## 3. Sampling-composition diagnostics

Because rolling windows share 15 of 20 calendar years, adjacent networks are deliberately overlapping. For every chronology realization and adjacent-window transition we therefore record, without using them to tune the semantic metric:

- poem-set Jaccard turnover;
- number of entering, exiting, and shared poems;
- author-set Jaccard turnover;
- total-variation distance between raw author-share distributions.

These quantities diagnose whether a large semantic movement coincides with unusually large corpus-composition movement. They are not subtracted from the semantic statistic in Phase 12.

## 4. Chronological uncertainty

For every Monte Carlo realization, exact dates remain fixed and bounded composition intervals are sampled with the same discrete-uniform operational rule frozen in Phase 9. Networks are rebuilt for all nine windows. The eight adjacent transitions are then measured in both raw and author-balanced modes.

For every transition and statistic, Phase 12 reports the median, 10th percentile, and 90th percentile over the 1,000 chronology realizations.

The temporal coordinate used for display is the midpoint between the midpoints of the two adjacent rolling windows. This produces an independently determined sequence (1577, 1582, ..., 1612) and is not aligned to historiographic dates.

## 5. Raw versus author-balanced concordance

The same chronology realization is evaluated in both network modes. Phase 12 reports the absolute raw-versus-balanced difference in the primary rewiring statistic for each transition and realization. This is a robustness diagnostic for author dominance, especially Góngora.

No representation is chosen on the basis of raw/balanced agreement. Representation B was already selected in Phase 11B by structure alone.

## 6. Interpretation discipline

Phase 12 may describe the independently estimated trajectories L_t and R_t, but it must **not** yet label any peak as Renaissance, Baroque, transition, culmination, 1580, or 1605 evidence.

The conceptual interpretation to preserve is:

- low L_t, low R_t: semantic continuity;
- high L_t, low R_t: primarily lexical replacement;
- low L_t, high R_t: relational reorganization within a persistent vocabulary;
- high L_t, high R_t: broad semantic transformation.

No hard thresholds for “high” or “low” are introduced in Phase 12.

## 7. No change-point claim yet

There are only eight adjacent transitions in the main rolling trajectory. Phase 12 therefore does not promote a classical change-point algorithm as the main result. It first establishes an uncertainty-aware **semantic reconfiguration trajectory**.

A later phase must introduce null models / counterfactual temporal baselines and robustness analyses before the paper can claim that an observed rewiring episode exceeds what is expected from corpus turnover, author composition, or finite-sample variation.

## Phase 12 outputs

The notebook will export:

- draw-level lexical and rewiring metrics;
- transition-level uncertainty summaries;
- raw-versus-author-balanced rewiring concordance diagnostics;
- a deterministic midpoint reference trajectory for QA only;
- the frozen metric specification.

The next phase, conditional on successful execution, should construct null and robustness baselines before any historiographic validation or historical claim is made.
