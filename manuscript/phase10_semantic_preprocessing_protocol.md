# Phase 10 semantic representation and preprocessing protocol

## Purpose

Phase 9 froze the temporal design before any semantic analysis. Phase 10 freezes the textual and linguistic representation before any semantic network, network distance, historical comparison, or change-point statistic is computed. The canonical notebook is `notebooks/paper1_analysis.ipynb`.

## Frozen temporal design

The main trajectory uses 20-year rolling windows with a 5-year step, producing nine supported windows from 1565–1584 through 1605–1624. Widths of 25 and 15 years are sensitivity designs. The dates 1580 and 1605 remain external historiographic reference markers only.

## Text layers

Navarro-Colorado TEI at commit `092a5fe70a4065a4d84bfed288bffd3851348f9c` remains the canonical poem-identity backbone and supplies `text_tei` for all 97 primary-dated sonnets.

The Hernández-Lorenzo network corpus is pinned at commit `ef6b7b691f67abe60d9cfa85c274f0be8095dd9a`. Its repository has no declared GitHub license field, so Phase 10 downloads it at runtime and does not redistribute the raw corpus. Relevant author files are reconciled to the 97 primary poems by author-restricted exact normalized full-text identity followed by unique fuzzy matching at similarity >=0.98, with source collisions excluded. Pedro Espinosa has no corresponding author file in the pinned network corpus.

A main longitudinal text layer must cover all 97 canonical primary poems. Therefore no partial Hernández layer is silently mixed with Navarro author-by-author. If the Hernández layer is incomplete, `text_tei` is the main layer and the matched Hernández text is a secondary robustness/audit layer. This rule is structural and is fixed before semantic outcomes exist.

## NLP

The pipeline is spaCy `3.8.7` with `es_core_news_sm` `3.8.0`. The model wheel is pinned to SHA256 `e451a83d6df79b87e9eed0cb553f03e99e36a3bab18a7b79f0dcfd1fdf875e12`. The model is trained on modern Spanish, so its use on Early Modern Spanish is treated as a documented measurement limitation. Phase 10 exports aggregate `X`-POS/empty-lemma diagnostics and a deterministic quality sample; these diagnostics cannot be used to tune the pipeline after observing historical semantic results.

## Concept definition

Main nodes are `lemma::coarse_POS` for tokens tagged `NOUN`, `VERB`, `ADJ`, or `ADV`. `PROPN` is excluded from the main representation and included only in a named-entity sensitivity analysis. No external modern stopword list is used in the main pipeline; function words are excluded by POS. Nonalphabetic tokens, empty lemmas, and one-character lemmas are technical exclusions.

The vocabulary is frozen globally across the 97 primary-dated poems before temporal networks are constructed. Main vocabulary requires presence in at least 2 distinct poems; document frequency >=3 is a sensitivity threshold. Global filtering avoids choosing a different vocabulary after inspecting individual historical windows.

## Co-occurrence network specification for Phase 11

The main co-occurrence unit is the poetic line. Within each line, repeated occurrences of the same concept are collapsed, and each unordered pair of distinct retained concepts contributes at most one raw co-occurrence event. For a temporal window, edge strength will be positive pointwise mutual information (PPMI) computed from line-presence probabilities. The main network requires raw pair support in at least 2 lines; support thresholds 1 and 3 are sensitivity analyses. A sliding window of 5 retained content tokens is an alternative-context sensitivity analysis.

No PPMI network is instantiated in Phase 10.

## Author composition control

The raw poem-pooled network is the historical-corpus estimand. Because Phase 9 showed strong Góngora concentration, Phase 11 must also construct an author-balanced robustness network. For author `a`, poem `p`, line `l`, and temporal window `W`, the line weight is `1 / (n_{a,W} L_p)`, making each represented author's total line mass equal within the window. Leave-one-author-out is used only where Phase 9 showed temporal feasibility; full Góngora ablation is not claimed where the dated corpus cannot support it.

## Anti-circularity safeguards

Historiographic classifications may be used only after network construction for external interpretation/validation. They cannot choose text matches, NLP parameters, vocabulary thresholds, co-occurrence context, PPMI support, temporal windows, or change points. Semantic results cannot retrospectively alter the Phase-10 configuration.

## Runtime outputs

Phase 10 writes to `/content/gasr_phase10_outputs/`: primary chronology/text layers, Hernández crosswalk, text-layer coverage by author and main window, NLP audits, deterministic quality sample, global vocabulary, and a machine-readable preprocessing configuration.
