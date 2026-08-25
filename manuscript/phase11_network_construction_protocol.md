# Phase 11 — Semantic network construction and structural comparability

## Paper 1 objective retained

The paper asks whether the Renaissance-to-Baroque transition in Spanish Golden Age poetry is better described as gradual semantic drift or as a structural reorganization of the poetic semantic system.

Phase 11 does **not** redefine that question as an author-classification or stylometric problem. The empirical object is a dynamic **concept-to-concept semantic network** reconstructed from poems placed in composition time.

## Contribution / novelty to preserve

The contribution is designed around five linked elements rather than around methodological complexity for its own sake:

1. **Conceptual relations rather than author similarity.** Nodes are lexical-semantic concepts (`lemma::POS`) and edges represent within-line semantic co-presence. This is distinct from the author/text similarity networks used in the initial Hernández-Lorenzo reference framework.
2. **Historical time is reconstructed independently.** Composition dates/intervals were acquired and audited before semantic analysis. Historiographic markers (1580 and 1605) remain external references only.
3. **Rewiring is separable from vocabulary turnover.** Later phases will distinguish the appearance/disappearance of concepts from changes in relations among concepts that persist across adjacent windows. This decomposition is central to testing “drift” versus “structural reconfiguration.”
4. **Author dominance is treated explicitly.** Every main window is represented both by a raw network and by an author-balanced network in which each author contributes equal total line mass. This is essential because Góngora is structurally dominant in the dated corpus.
5. **Historiography is validation, not supervision.** Renaissance/Baroque or López Bueno labels cannot select edges, vocabulary, windows, or change points. They can only be compared with the independently estimated semantic trajectory later.

No claim of absolute priority (“first ever”) should be made until the final novelty-gap literature review is completed. The novelty claim should be stated relative to the combination above and to the initial Digital Humanities / Golden Age network literature reviewed for the paper.

## Inputs frozen before Phase 11

- Primary chronology: 97 poems, 6 authors.
- Main temporal design: 20-year rolling windows, 5-year step, from 1565–1584 through 1605–1624 (9 windows).
- Chronological uncertainty: 1,000 Monte Carlo draws, seed `20260825`.
- Main text: Navarro TEI (`text_tei`), complete 97/97.
- Secondary text robustness: Hernández standardized layer only on the exactly/fuzzily matched subset; comparisons must be paired on the same poem IDs.
- NLP: spaCy 3.8.7 + `es_core_news_sm` 3.8.0.
- Main concept POS: NOUN, VERB, ADJ, ADV.
- Concept identity: `lemma::coarse_POS`.
- Main global vocabulary: poem-document-frequency >= 2, frozen before network construction.
- Main co-occurrence context: unique concept presence within a poetic line.
- Main minimum pair support: 2 distinct poetic lines.
- Main edge weight: positive PMI (PPMI).

## Main network definition

For a temporal window W, let L_W be the set of poetic lines belonging to poems assigned to W in a given chronology realization. For concept i:

- c_i = number of lines containing i;
- c_ij = number of lines containing both i and j;
- N = total number of poetic lines in W.

For pairs with c_ij >= 2:

PPMI(i,j) = max(0, log2[(c_ij/N) / ((c_i/N)(c_j/N))]).

Only positive-PPMI pairs are edges. Active nodes are concepts from the globally frozen vocabulary that occur at least once in the window. Active isolates are retained in structural diagnostics.

## Author-balanced network

If poem p is by author a and has L_p poetic lines, while n_(a,W) poems by author a are present in W, each line of p receives weight

w_(line,p,a,W) = 1 / (n_(a,W) L_p).

Hence the total line mass contributed by every author present in W equals one. Weighted node and pair presences replace raw counts in the PMI probabilities, while the preregistered minimum raw pair support of two lines is retained. This creates a counterfactual network in which no prolific author has greater total mass merely because more of their poems are dated in the window.

## What Phase 11 may inspect

Phase 11 is a **network-feasibility and comparability audit**. It may inspect, across chronology draws and windows:

- number of poems and authors;
- effective number of authors and largest-author share;
- number of lines;
- active nodes and vocabulary coverage;
- positive-PPMI edge count;
- density;
- connected components and giant-component fraction;
- basic edge-support/PPMI distributions.

These quantities are used to detect degenerate or incomparable graphs, not to identify a Renaissance-Baroque break.

## What Phase 11 must not do

Phase 11 must not:

- choose a change point;
- rank 1580 or 1605 by fit;
- optimize window width using semantic outcomes;
- select a preferred support threshold because it produces a clearer transition;
- interpret a peak in density, clustering, centrality, modularity, or any other network statistic as the historical result;
- tune the vocabulary after seeing temporal network behavior.

## Reference networks

For reproducibility and visual QA only, Phase 11 may export one deterministic set of reference networks using the integer midpoint of each poem’s composition interval. These reference graphs are **not inferential estimates**. All historical claims in later phases must propagate chronological uncertainty.

## Phase 12 target

If the nine raw and nine author-balanced networks are structurally usable, Phase 12 will preregister and compute the actual historical reconfiguration statistics. The central analysis should explicitly decompose:

- **lexical turnover**: change in the active concept set;
- **relational rewiring**: change in edge structure/weights among concepts shared across adjacent windows.

That decomposition, together with author balancing and chronology uncertainty, is the direct operationalization of the paper’s drift-versus-reconfiguration question.
