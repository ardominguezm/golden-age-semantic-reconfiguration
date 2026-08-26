# Phase 13 — Null models and counterfactual rewiring

## Scientific target

Paper 1 asks whether the Renaissance-to-Baroque transition in Spanish Golden Age poetry involved a structural reorganization of the poetic semantic system rather than only gradual semantic drift or vocabulary replacement. Phase 12 identified an uncertainty-aware trajectory of lexical turnover and persistent-concept relational rewiring, but it also showed that the largest observed movement coincides with substantial poem-set turnover. Phase 13 therefore asks the crucial counterfactual question: **is the observed persistent-concept rewiring larger than expected from finite sampling, poem turnover, and author composition when temporal semantic assignment is destroyed without changing the frozen representation?**

No historiographic date, period label, author-stage classification, or change-point model is used to construct or tune these nulls. In particular, 1580 and 1605 remain external reference markers for a later validation phase.

## Frozen observed design

- Primary chronology: 97 poems, 6 authors.
- Chronological uncertainty: 1,000 Monte Carlo realizations, seed `20260825`.
- Main temporal design: 20-year rolling windows, step 5 years, 9 windows and 8 adjacent transitions.
- Main text/NLP/vocabulary: Navarro TEI; spaCy 3.8.7 + `es_core_news_sm` 3.8.0; `lemma::POS`; NOUN/VERB/ADJ/ADV; global poem-DF >=2 vocabulary (668 concepts).
- Main representation: Phase-11B candidate B — within-line co-occurrence, support >=1, positive PMI (PPMI).
- Primary relational statistic: cosine distance between PPMI vectors after restricting both adjacent networks to their persistent concept set.
- Modes: raw and author-balanced.

Observed Phase-12 statistics continue to use all 1,000 chronology realizations. The null calibration uses a computationally fixed subset of chronology draws and does not alter the observed trajectory.

## Fixed null simulation budget

Before null results are inspected:

- `NULL_SEED = 20260826`.
- 100 chronology realizations are selected deterministically and evenly across the frozen 1,000 Phase-12 draws.
- 20 random counterfactual replicates are generated per selected chronology realization.
- Thus each null model provides 2,000 counterfactual realizations per transition and mode.

The minimum attainable one-sided empirical tail probability is therefore `1/2001` with the +1 correction. This budget is an engineering/computational choice, not a literary or inferential threshold.

## N1 — Local author-overlap-preserving reassignment null (primary)

For each selected chronology realization and each pair of adjacent observed windows, define the local union of poems in those two windows. Within each author separately, the counterfactual reassignment preserves exactly:

1. the number of that author's poems in the left window;
2. the number in the right window;
3. the number shared by both windows;
4. hence the author's left-only and right-only counts;
5. the total left/right poem counts, shared-poem count, entering/exiting counts, poem-set turnover, and author composition of the observed transition.

Only **which poems** occupy the shared, left-only, and right-only slots is randomized within that author's local pool. Networks are then rebuilt from the reassigned poems in raw and author-balanced modes.

This null conditions tightly on the local sampling geometry that can mechanically generate semantic distance. It asks whether the historical allocation of semantic content to the observed left/right positions produces more rewiring than arbitrary author-matched reallocations of the same local poems.

## N2 — Global within-author chronology permutation null (secondary)

For each selected chronology realization, the sampled year multiset is preserved exactly within every author, but the years are randomly permuted among that author's poems. The nine rolling windows and all eight transitions are then reconstructed coherently from this permuted chronology.

This preserves each author's complete sampled year distribution, the corpus-wide temporal support and author-specific temporal occupancy implied by the frozen chronology, and the poem texts/author identities, while destroying the association between a particular poem's semantic network and its temporal position within the author.

N2 therefore provides a stronger global counterfactual for the hypothesis that semantic content is temporally organized beyond author composition.

## Primary comparison and empirical tail probabilities

For each transition and mode, let `R_obs,t` be the median observed Phase-12 cosine rewiring over all 1,000 chronology draws. For each null model, report the null median, q10, q90, q95 and q99, observed-minus-null-median excess, the observed percentile in the null distribution, and one-sided empirical tail probability

`p = (1 + #{R_null >= R_obs,t}) / (1 + N_null)`.

No binary “significant/not significant” label is introduced in Phase 13. Effect size, percentile, and empirical tail probability are reported together.

## Familywise global max statistic

Because the main trajectory contains eight adjacent transitions, N2 additionally retains, for every full counterfactual trajectory and mode,

`M_null = max_t R_null,t`.

For each observed transition the max-statistic tail probability is

`p_max = (1 + #{M_null >= R_obs,t}) / (1 + N_null)`.

This is a conservative trajectory-level guard against highlighting the largest of eight observed transitions merely because eight opportunities were inspected.

## Lexical-turnover and composition diagnostics

The same null samples also retain lexical turnover. N1 should, by construction, preserve poem/author overlap geometry but need not reproduce the observed lexical overlap, because poem identities have been reassigned. N2 destroys semantic-time alignment more globally. These lexical-null quantities are diagnostics; the primary Phase-13 test remains persistent-concept PPMI cosine rewiring.

## Interpretation discipline

Phase 13 may say that an observed transition has more or less rewiring than its null expectation. It must not yet call that transition Renaissance, Baroque, a historical breakpoint, or evidence for 1580/1605. A historically meaningful claim requires successful null behavior plus the downstream robustness phase and only then external historiographic validation and close reading.

A strong eventual Paper-1 result would require evidence of the following form: observed persistent-concept rewiring exceeds the conditional null expectation, survives author balancing and representation/text/window sensitivities, and only afterward shows interpretable relation to historiographic periodization.

## Planned outputs

The notebook exports observed Phase-12-compatible draw-level trajectory and summary; draw-level N1 and N2 null metrics; transition-level null summaries; N2 max-statistic distributions; the observed-versus-null comparison table with empirical tail probabilities; and the frozen null specification.

If Phase 13 executes successfully, Phase 14 should run robustness analyses (alternative context C, vocabulary DF>=3, 15/25-year windows, paired Navarro/Hernandez standardized text where available, and feasible author-ablation checks) before any historiographic validation.