# Chronology sources — Paper 1

This document records the scholarly provenance used to construct the composition-time axis. It is intentionally conservative: publication, witness, edition and author-lifespan dates are never substituted for composition dates.

## Góngora

Primary reproducible source for the current sprint: the Cátedra Góngora / `gongoradigital/gongoraobra` XML-TEI corpus, pinned at commit `3beadeecc059a7cc48499dc2683bb378a2630978`.

The Cátedra Góngora describes the poetry XML as a revised digital form of the Antonio Carreira / Biblioteca Castro corpus. It contains 477 poems (418 secure attributions and 59 probable attributions) organized chronologically by year from 1580 to 1626. The project documentation is available at:

- https://www.uco.es/catedragongora/?page_id=3483
- https://github.com/gongoradigital/gongoraobra

For Paper 1, a year extracted from this XML is recorded as `scholarly_chronology_year` with confidence B. It is not automatically called an exact documentary composition date. Textual matching to the Navarro corpus must be verified poem by poem, with collisions and low-similarity links excluded.

## Garcilaso de la Vega

The chronological seed follows Rafael Lapesa's diachronic reconstruction as summarized and discussed by Elias L. Rivers in the Centro Virtual Cervantes. Rivers explicitly notes that twelve sonnets cannot be dated and that the remaining chronology may be precise or approximate:

- https://cvc.cervantes.es/actcult/garcilaso/anotaciones/rivers.htm

Additional scholarly checks used for conservative interval construction include the AISO/CVC literature on Garcilaso's sonnet chronology and the limits of assigning all Naples-period poems to 1535:

- https://cvc.cervantes.es/literatura/aiso/pdf/02/aiso_2_2_046.pdf
- https://cvc.cervantes.es/literatura/aispi/pdf/19/i_27.pdf

The current notebook therefore encodes only a conservative subset. Historically anchored sonnets such as XXXIII and XXXV may receive year-level confidence A; broader scholarly groupings remain confidence B intervals. Undated sonnets remain undated.

## Fernando de Herrera

The textual layers H (`Algunas obras`, 1582) and P/P2 (`Versos`, 1619) are treated as edition/circulation evidence, not composition dates. The empirical comparison in Phase 3 confirms that `Herrera_Sonetos` contains the H layer and that `AN_SonetosP2` is strongly P2-derived, while textual variation prevents naïve exact-identity assumptions.

Consequently:

- 1582 is a circulation/edition year for H;
- 1619 is a posthumous circulation/edition year for P/P2;
- neither value is assigned to `composition_min` or `composition_max` without independent chronological evidence.

## Lope de Vega and Quevedo

These authors require separate chronology work because large sonnet corpora are organized primarily through books, muses, editions and later editorial structures rather than uniformly documented poem-level composition dates. Publication chronology will be preserved as a secondary axis, but not used to manufacture composition years.

## General admissibility rule

A poem can enter the primary temporal analysis only through one of the following evidence classes:

1. documentary or historically anchored composition year;
2. scholarly chronology year;
3. bounded scholarly composition interval;
4. broad author-activity interval only as an explicitly labelled fallback in sensitivity analyses.

The following are never silently promoted to composition time: author birth/death years, author-lifespan midpoints, witness dates, modern edition dates, first-publication dates or posthumous collection dates.
