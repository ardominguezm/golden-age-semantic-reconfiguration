# Chronology sources — Paper 1

This document records the scholarly provenance used to construct the composition-time axis. It is intentionally conservative: publication, witness, edition and author-lifespan dates are never substituted for composition dates.

## Góngora

Primary reproducible source for the current sprint: the Cátedra Góngora / `gongoradigital/gongoraobra` XML-TEI corpus, pinned at commit `3beadeecc059a7cc48499dc2683bb378a2630978`.

The Cátedra Góngora describes the poetry XML as a revised digital form of the Antonio Carreira / Biblioteca Castro corpus. It contains 477 poems (418 secure attributions and 59 probable attributions) organized chronologically by year from 1580 to 1626. The project documentation is available at:

- https://www.uco.es/catedragongora/?page_id=3483
- https://github.com/gongoradigital/gongoraobra

For Paper 1, a year extracted from this XML is recorded as `scholarly_chronology_year`. Confidence depends on linkage quality: an exact normalized full-text identity receives confidence A, whereas fuzzy or variant-based linkage receives confidence B. The scholarly chronology year is still not described as an exact documentary composition date unless independent evidence warrants that stronger claim. Collisions and low-similarity links remain excluded.

### Phase 5 linkage rule

Phase 4 accepts exact full-text matches or full-text similarity >= 0.98 when the scholarly target is one-to-one. Phase 5 may recover additional textual variants only when the normalized first two verse lines identify a unique 14-line scholarly poem, full-text similarity is >= 0.95, the target has a unique scholarly year, the target is unused by Phase 4, and no two Navarro poems compete for it. This is intended as an orthogonal identity check rather than a mechanical lowering of the Phase-4 threshold.

The corrected Phase-5 implementation is idempotent for repeated identical temporal assignments and raises an error only when a genuinely contradictory assignment is attempted. Under the pinned sources, the expected validated chronology totals are 58 primary-dated Góngora sonnets: 12 exact links (confidence A), 41 Phase-4 fuzzy links (confidence B), and 5 additional Phase-5 variant links (confidence B).

## Garcilaso de la Vega

The chronological seed follows Rafael Lapesa's diachronic reconstruction as summarized and discussed by Elias L. Rivers in the Centro Virtual Cervantes. Rivers explicitly notes that twelve sonnets cannot be dated and that the remaining chronology may be precise or approximate:

- https://cvc.cervantes.es/actcult/garcilaso/anotaciones/rivers.htm

Additional scholarly checks used for conservative interval construction include the AISO/CVC literature on Garcilaso's sonnet chronology and the limits of assigning all Naples-period poems to 1535:

- https://cvc.cervantes.es/literatura/aiso/pdf/02/aiso_2_2_046.pdf
- https://cvc.cervantes.es/literatura/aispi/pdf/19/i_27.pdf

The current notebook therefore encodes only a conservative subset. Historically anchored sonnets such as XXXIII and XXXV may receive year-level confidence A; broader scholarly groupings remain confidence B intervals. Undated sonnets remain undated and are exported as a poem-level worklist.

## Juan Boscán

The encounter with Andrea Navagero in Granada in 1526 is the conventional historical anchor for Boscán's systematic cultivation of Italianate forms. Boscán died in 1542 and the joint volume *Las obras de Boscán y algunas de Garcilasso de la Vega* appeared posthumously in 1543. Useful sources include:

- https://www.cervantesvirtual.com/obra-visor/sonetos--35/
- https://www.cervantesvirtual.com/portales/constituciones_hispanoamericanas/obras/autor/boscan-juan-ca1487-ca-1542-408
- https://cvc.cervantes.es/literatura/ajhi/02/06_fortunato.htm

Phase 5 therefore records `[1526, 1542]` only as a **sensitivity-only** interval for Boscán's sonnet corpus. It is not counted as primary poem-level chronology because individual composition ordering remains unresolved.

## Fernando de Herrera

The textual layers H (`Algunas obras`, 1582) and P/P2 (`Versos`, 1619) are treated as edition/circulation evidence, not composition dates. The companion corpus is pinned at commit `0de990eac908897b5e931aeb5c496170ccf35bab`:

- https://github.com/lamusadecima/Digital-Stylistics-Applied-to-Golden-Age

The Biblioteca Virtual Miguel de Cervantes chronology provides further historical attestation: Herrera has poems in preliminaries from 1561–1565, six poems in the 1577 *Flores de baria poesía* manuscript, a 1578 manuscript section with 130 poems, *Algunas obras* in 1582, and the posthumous *Versos* in 1619:

- https://www.cervantesvirtual.com/portales/fernando_de_herrera/autor_cronologia/

Consequently:

- 1582 is a circulation/edition year for H;
- 1619 is a posthumous circulation/edition year for P/P2;
- exact H/P2 textual matches may receive `circulation_year`, but neither value enters `composition_min` or `composition_max` without independent chronological evidence.

## Pedro Espinosa and *Flores de poetas ilustres*

The 1605 *Primera parte de las Flores de poetas ilustres de España* is a major attestation layer, not a universal composition date. The BNE record states that the anthology includes 19 poems by Espinosa himself:

- https://cervantes.bne.es/es/su-biblioteca/espinosa-pedro-primera-parte-flores-poetas-ilustres-espana-

A digitized 1605 copy is also available from the Universidad de Granada:

- https://digibug.ugr.es/handle/10481/12070

Poems linked individually to *Flores* may later receive a circulation/terminus-ante-quem record, but 1605 is not generalized to Espinosa's entire corpus.

## Juan de Arguijo

Arguijo is attested in the same 1605 *Flores* anthology. Menéndez Pelayo's bibliographical notice identifies five opening sonnets by incipit:

- `Castiga el cielo a Tántalo inhumano`
- `A quién me quejaré del crudo engaño`
- `La horrible sima con espanto mira`
- `Si pudo de Anfión el dulce canto`
- `Ya el joven fuerte que con muestra hermosa`

Phase 6 resolves these incipits against Navarro where possible and records 1605 only as circulation / terminus ante quem, never as an exact composition year.

## Juan de Jáuregui

The Biblioteca Virtual Miguel de Cervantes records *Rimas de Don Iuan de Iauregui* as published in Seville in 1618:

- https://www.cervantesvirtual.com/portales/portal_nacional_venezuela/obras/autor/jauregui-juan-de-38294

For Paper 1 this is circulation evidence only unless poem-specific composition evidence is established.

## Luis Carrillo y Sotomayor

Carrillo died in 1610. His collected *Obras* appeared posthumously in Madrid in 1611 (Juan de la Cuesta), with a corrected second impression in 1613 (Luis Sánchez). These publication dates are not promoted to composition time.

For Phase 6 one stronger poem-level anchor is tested by incipit: Menéndez Pelayo wrote to Francisco Rodríguez Marín on 6 July 1899 that the sonnet beginning `Así, sagrado mar, nunca te oprima...` was written in 1609. If the Navarro incipit resolves uniquely, it receives a confidence-B primary year 1609. The 1610 death date remains a one-sided upper-bound constraint for the remaining Carrillo corpus.

## Cervantes

The sonnet corpus is heterogeneous and includes occasional, paratextual and context-dependent poems. No single collection date is allowed to stand in for composition chronology.

Phase 6 tests three historically anchored incipits, only if each resolves uniquely in Navarro:

- `Vimos en julio otra semana santa` — linked to the Cádiz episode of 1596; confidence B because the textual tradition includes attribution cautions;
- `Voto a Dios que me espanta esta grandeza` — sonnet on the tomb of Philip II in Seville, 1598; confidence A;
- `El que subió por sendas nunca usadas` — identified by Cervantes as written on the death of Fernando de Herrera; encoded conservatively as `[1597,1598]`, confidence B.

Relevant documentary / scholarly portals include the Biblioteca Nacional de España Cervantes exhibition and Biblioteca Virtual Miguel de Cervantes editions of the loose poems.

## Quevedo and *Flores* (1605)

Alonso Veloso and Candelas Colodrón, “Los poemas de Quevedo incluidos en la Primera parte de Flores de poetas ilustres (1605) de Pedro de Espinosa,” *Calíope* 13(2), 2007, pp. 63–80, identify eighteen Quevedo poems in the anthology, his first printed poems there. Phase 6 uses the seven sonnet incipits from that study as candidate text links:

- `Estábase la efesia cazadora`
- `Si con los mismos ojos que leyeres`
- `La voluntad de Dios por grillos tienes`
- `Escondido debajo de tu armada`
- `Mi madre tuve en ásperas montañas`
- `Sola en ti, Lesbia, vemos ha perdido`
- `Llegó a los pies de Cristo Madalena`

A unique Navarro match receives `composition_not_after = 1605` and `circulation_year = 1605`, not an exact composition date. The date is not generalized to the 517-poem Quevedo corpus.

## Lope de Vega

The two large Navarro Lope groups require book-level source reconstruction before chronology can be promoted. Publication chronology remains secondary evidence; no book date is generalized to all poems in a group.

## General admissibility rule

A poem can enter the primary temporal analysis only through one of the following evidence classes:

1. documentary or historically anchored composition year;
2. scholarly chronology year;
3. bounded scholarly composition interval;
4. broad author-activity interval only as an explicitly labelled fallback in sensitivity analyses.

The following are never silently promoted to composition time: author birth/death years, author-lifespan midpoints, witness dates, modern edition dates, first-publication dates or posthumous collection dates.

## Phase 6: four temporal evidence channels

Phase 6 extends the schema so that uncertainty is not forced into false intervals. The notebook now keeps four distinct evidence channels:

- `composition_min/max`: primary composition chronology;
- `circulation_year`: publication, manuscript or edition attestation;
- `sensitivity_min/max`: broad fallback envelopes used only in robustness analyses;
- `composition_not_before` / `composition_not_after`: one-sided chronological constraints.

Examples: an author death date can supply a hard `not_after` bound without becoming a poem date; an exact match to Herrera's 1582 H layer can supply `not_after = 1582`; a poem printed in *Flores* can supply `not_after = 1605` and circulation 1605.

The one-sided constraints are collapsed to the tightest compatible bound and checked against any primary interval. A contradiction between a primary date and a constraint is treated as an error requiring scholarly review.

## Phase 5 corrected validation target

With the currently pinned sources, the Phase-5 baseline must remain invariant before Phase-6 additions:

- 76 primary-dated poems in total;
- confidence A = 14;
- confidence B = 62;
- 100 Boscán poems in the sensitivity-only layer;
- 89 Herrera circulation/attestation records;
- zero H/P2 dates promoted to Herrera composition time.

Any future change to these totals must be explained by a documented source update or explicit methodological revision rather than by a silent code change.

## Phase 6 identifiability objective

The purpose of Phase 6 is not to maximize the number of nominally dated poems. It is to test whether the corpus has enough **author diversity across historical time** to distinguish a Renaissance–Baroque semantic reconfiguration from a two-author contrast. The notebook therefore exports author-level counts for `primary_interval`, `bounded_constraint`, `one_sided_constraint`, `circulation_only`, `sensitivity_only`, and `unconstrained`, together with a priority worklist for the next scholarly acquisition pass.
