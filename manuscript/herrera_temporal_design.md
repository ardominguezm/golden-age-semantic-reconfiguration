# Herrera edition identity and temporal design

## Phase-2 findings

The Navarro TEI corpus provides 5,078 poem-level records across 53 author folders, but essentially no composition chronology: only one TEI file contains witness/edition dates and none supplies a usable poem-level composition date. The corpus collapses to 57 author + source-description groups, making source/collection-level scholarly dating feasible.

The Hernández-Lorenzo network corpus contains two Herrera-related layers, `Herrera_Sonetos.txt` and `AN_SonetosP2.txt`. Their normalized poem sets overlap in only one poem, so they must not be treated as duplicate copies of the same set. Pacheco contributes 22 sonnets absent from Navarro and must be retained as source-exclusive material.

## External identification of H and P2

Hernández-Lorenzo's companion study distinguishes:

- **H**: sonnets from *Algunas obras* (1582), the edition published by Herrera during his lifetime.
- **P2**: sonnets unique to the posthumous *Versos de Fernando de Herrera* (1619), excluding poems already published in H.

The companion repository `lamusadecima/Digital-Stylistics-Applied-to-Golden-Age` exposes these layers explicitly as `H.txt` and `P2.txt`. Phase 3 pins that repository and compares those files directly with `Herrera_Sonetos.txt` and `AN_SonetosP2.txt`.

## Temporal design decision

Paper 1 will keep two temporal axes distinct.

**Composition axis (primary):** scholarly composition year or bounded composition interval. This axis addresses when semantic reconfiguration was occurring in poetic production.

**Publication/circulation axis (secondary sensitivity analysis):** first publication or collection date. For Herrera, 1582 (H) and 1619 (P2) are circulation evidence, not automatically composition dates.

Assigning P2 a composition year of 1619 would be historically invalid because Herrera died in 1597. The contrast between composition-time and circulation-time trajectories is therefore treated as a robustness and interpretation problem rather than collapsed into a single date.

No temporal windows will be selected until scholarly dating coverage for priority-A authors and source groups has been audited.
