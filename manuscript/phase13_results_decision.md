# Phase 13 — Results decision after counterfactual null models

## Execution state

The executed Phase-13 notebook was saved from Colab in commit `5f7bb4db91b930d8bc229dbaae5d6c90d67d1af5`. The canonical notebook remains `notebooks/paper1_analysis.ipynb`; no root-level duplicate exists. The run contains no notebook error output and the final checkpoint passed all frozen invariants:

- 97 primary-dated poems and 6 authors;
- main representation `B_line_support1` (poetic-line co-occurrence, support >=1, PPMI);
- 1,000 observed chronology realizations and 8 adjacent transitions;
- 2,000 N1 local counterfactuals per transition/mode;
- 2,000 N2 coherent global counterfactual trajectories;
- N2 max-statistic familywise calibration computed;
- no use of 1580/1605, historiographic labels, or change-point tuning.

## Primary result: N1 local overlap-preserving null

The strongest Phase-12 movement remains the transition centered at 1592. Its observed persistent-concept cosine rewiring is:

| mode | observed R | N1 median | N1 q90 | N1 q95 | excess | N1 percentile | empirical p |
|---|---:|---:|---:|---:|---:|---:|---:|
| author-balanced | 0.233746 | 0.213336 | 0.243669 | 0.255350 | +0.020410 | 0.8110 | 0.189405 |
| raw | 0.224870 | 0.209614 | 0.238483 | 0.246787 | +0.015256 | 0.7695 | 0.230885 |

The observed value is above the N1 median in both modes, but it remains below the N1 90th percentile. Across all 16 transition x mode cells, the smallest N1 empirical tail probability is approximately 0.172. Thus the preregistered **primary null does not provide evidence that the observed rewiring exceeds what can arise from the same local poem-turnover geometry and author composition**.

This is the governing Phase-13 inferential result. It cannot be replaced by a more favorable secondary null or by later sensitivity analysis.

## Secondary result: N2 global within-author chronology permutation

The same 1592 transition is much more unusual under the global within-author temporal permutation:

| mode | observed R | N2 median | N2 q90 | N2 q95 | excess | N2 percentile | empirical p | max-statistic p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| author-balanced | 0.233746 | 0.181492 | 0.218246 | 0.229168 | +0.052254 | 0.9640 | 0.036482 | 0.036482 |
| raw | 0.224870 | 0.182611 | 0.217273 | 0.226105 | +0.042259 | 0.9455 | 0.054973 | 0.054973 |

The author-balanced trajectory therefore places the 1592 movement above the N2 95th percentile and it also survives the N2 trajectory-level max-statistic calibration at the same empirical tail probability. The raw trajectory is close but weaker, lying between the N2 90th and 95th percentiles.

This N2 result is scientifically interesting because it shows that semantic content is not randomly arranged along each author's chronology. However, N2 is secondary and conditions less tightly on the exact local turnover geometry than N1. It therefore cannot by itself support the paper's intended structural-reconfiguration claim.

## Interpretation

Phase 13 yields **mixed but informative evidence**:

1. There is a temporally localized episode near the independently generated 1592 transition that is unusual under global within-author chronology permutation, especially after author balancing.
2. The same episode is not unusual enough under the stricter local author-overlap-preserving null.
3. Therefore the current data do not yet justify the sentence “persistent-concept rewiring exceeds what is expected from corpus turnover and author composition.”
4. The stronger defensible statement is that the observed trajectory contains a localized ordering signal, but much of its amplitude is compatible with which poems enter and leave adjacent windows under the observed sampling geometry.

This distinction is substantive, not a failed analysis. It identifies precisely what a naive semantic-drift study would conflate: global temporal ordering and local finite-corpus turnover are not the same counterfactual.

## Consequence for the paper

No Renaissance/Baroque, 1580/1605, or historical-breakpoint claim is authorized at this stage. Phase 14 must test the previously frozen representation, vocabulary, temporal-window, text-layer, and feasible author-ablation sensitivities. These analyses are robustness diagnostics and **may not be used to rescue or redefine the Phase-13 primary N1 result**.

If the global-N2/local-N1 contrast persists across robustness designs, the paper may need to frame its main contribution more carefully: not as a simple detection of a semantic phase transition, but as a decomposition of apparent literary-semantic reconfiguration into genuine temporal ordering versus turnover-induced network movement. If a robust N1 excess emerges only under a previously preregistered sensitivity, it must remain secondary to the main representation and be reported transparently as representation-dependent evidence.
