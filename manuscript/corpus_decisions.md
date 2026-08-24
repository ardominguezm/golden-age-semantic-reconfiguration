# Paper 1 — Corpus decisions log

## Decision C1 — Canonical poem identity

**Status:** adopted after reconciliation run saved from Colab on 2026-08-24.

Use **Navarro Colorado's `CorpusSonetosSigloDeOro` TEI/XML corpus as the canonical poem-identity backbone**. It provides 5,078 individually encoded sonnets and stable poem-level identifiers.

Use the Hernández-Lorenzo derivative corpus as a **standardized textual layer and comparison source**, not as an independent second corpus to be concatenated naively.

### Empirical basis

- Hernández TXT segmentation recovered 4,381 poem blocks; 4,360 have 14 lines.
- 4,065 / 4,381 Hernández blocks (92.8%) have a unique exact normalized-text match in Navarro.
- Among the 316 non-exact blocks, 194 are near-identical (fuzzy score >= 98), 5 are in 95–98, 8 in 90–95, 87 are below 90, and 22 have no Navarro author candidate.
- The 22 no-candidate records are Pacheco, who is absent from Navarro and should be retained as source-exclusive material.
- The preliminary high-confidence linkage contains 4,065 exact links plus 194 provisional >=98 links. Seven TEI targets receive multiple Hernández links and must be resolved before final linkage.
- After excluding collision targets, 4,245 Navarro records can currently be enriched with Hernández standardized text.

## Decision C2 — Source-exclusive material

**Pacheco:** retain the 22 Hernández poems as legitimate source-exclusive records. They must receive project-level poem identifiers and explicit provenance rather than being forced into the Navarro backbone.

**Other unresolved Hernández blocks:** do not append automatically. First classify them as segmentation artefacts, textual variants, source-exclusive poems, or genuinely unmatched records.

## Decision C3 — Herrera requires a textual-variant layer

The Hernández files labelled `AN` and `Herrera` both map empirically to `FernandoDeHerrera` in Navarro. They must not be treated automatically as two independent sets of poems, because that can duplicate poem identities and over-weight Herrera in the semantic network.

Before final corpus construction:

1. inspect linkage collisions involving Herrera;
2. determine whether `AN` and `Herrera` encode distinct editions/witnesses/versions or partly overlapping selections;
3. represent alternative versions as textual witnesses of the same poem whenever identity can be established;
4. preserve genuinely distinct poems as separate records.

## Decision C4 — Text used for semantic analysis

For poems with a high-confidence Hernández ↔ Navarro link, preserve at least two text fields:

- `text_tei`: Navarro/TEI textual representation;
- `text_standardized`: Hernández-Lorenzo standardized orthography.

The primary semantic analysis will likely use the standardized representation for comparability, while the TEI text remains available for philological sensitivity checks. This decision will be re-evaluated after preprocessing tests.

## Decision C5 — Chronology is still unresolved

Do **not** use Hernández `Date` as poem chronology. All 41 values are author lifespan intervals.

The TEI corpus contains essentially no poem-level composition dates: the two explicit date records found in the current audit occur in one Garcilaso TEI file and are witness/edition dates (1580 and 1612), not composition dates.

Therefore the next research stage is a **temporal-source reconstruction audit**, not semantic-network construction.

## Diagnostic note

The first author-specific diagnostic table incorrectly counted exact matches as unresolved because `fuzzy_score` is null for records already matched exactly. This affects only that diagnostic column, not the exact-match totals, fuzzy-band totals, or linkage table. The diagnostic must be corrected in the next notebook revision.
