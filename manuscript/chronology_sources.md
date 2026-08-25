# Chronology sources — Paper 1

This document records the scholarly provenance used to construct the composition-time axis. It is intentionally conservative: publication, witness, edition and author-lifespan dates are never substituted for composition dates.

## Góngora

Primary reproducible source for the current sprint: the Cátedra Góngora / `gongoradigital/gongoraobra` XML-TEI corpus, pinned at commit `3beadeecc059a7cc48499dc2683bb378a2630978`.

The Cátedra Góngora describes the poetry XML as a revised digital form of the Antonio Carreira / Biblioteca Castro corpus. It contains 477 poems (418 secure attributions and 59 probable attributions) organized chronologically by year from 1580 to 1626. The project documentation is available at:

- https://www.uco.es/catedragongora/?page_id=3483
- https://github.com/gongoradigital/gongoraobra

For Paper 1, a year extracted from this XML is recorded as `scholarly_chronology_year` with confidence B. It is not automatically called an exact documentary composition date. Textual matching to the Navarro corpus must be verified poem by poem, with collisions and low-similarity links excluded.

### Phase 5 linkage rule

Phase 4 accepts exact full-text matches or full-text similarity >= 0.98 when the scholarly target is one-to-one. Phase 5 may recover additional textual variants only when the normalized first two verse lines identify a unique 14-line scholarly poem, full-text similarity is >= 0.95, the target has a unique scholarly year, the target is unused by Phase 4, and no two Navarro poems compete for it. This is intended as an orthogonal identity check rather than a mechanical lowering of the Phase-4 threshold.

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

Arguijo is attested in the same 1605 *Flores* anthology, where six compositions were included. Later manuscript transmission preserves a substantial sonnet corpus. Sources for the Phase-5 evidence inventory include:

- https://www.classicahispalensia.es/estudios/58-juan-de-arguijo-y-la-sevilla-del-siglo-de-oro-el-contexto-literario
- https://bibliotecavirtualmadrid.comunidad.madrid/bvmadrid_publicacion/es/consulta/registro.do?id=17302

These dates remain circulation/manuscript evidence until individual Navarro sonnets are linked to specific attestations.

## Juan de Jáuregui

The Biblioteca Virtual Miguel de Cervantes records *Rimas de Don Iuan de Iauregui* as published in Seville in 1618:

- https://www.cervantesvirtual.com/portales/portal_nacional_venezuela/obras/autor/jauregui-juan-de-38294

For Paper 1 this is circulation evidence only unless poem-specific composition evidence is established.

## Luis Carrillo y Sotomayor

Carrillo died in 1610 and his *Obras* appeared posthumously in Madrid in 1611. The 1611 date is therefore not promoted to composition time. Phase 5 records it only in the historical anchor inventory; poem-level reconstruction is still required.

## Cervantes

The sonnet corpus is heterogeneous and includes occasional, paratextual and context-dependent poems. No single collection date is allowed to stand in for composition chronology. Cervantes remains a poem-level reconstruction target.

## Lope de Vega and Quevedo

These authors require separate chronology work because large sonnet corpora are organized primarily through books, muses, editions and later editorial structures rather than uniformly documented poem-level composition dates. Publication chronology will be preserved as a secondary axis, but not used to manufacture composition years.

The 1605 *Flores* anthology attests a subset of Quevedo's early printed poems, but that date must not be generalized to the whole Quevedo corpus.

## General admissibility rule

A poem can enter the primary temporal analysis only through one of the following evidence classes:

1. documentary or historically anchored composition year;
2. scholarly chronology year;
3. bounded scholarly composition interval;
4. broad author-activity interval only as an explicitly labelled fallback in sensitivity analyses.

The following are never silently promoted to composition time: author birth/death years, author-lifespan midpoints, witness dates, modern edition dates, first-publication dates or posthumous collection dates.

Phase 5 operationalizes this by keeping three separate clocks in the notebook: `composition_min/max`, `circulation_year`, and `sensitivity_min/max`.
