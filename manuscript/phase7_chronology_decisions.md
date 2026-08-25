# Phase 7 chronology decisions — focused scholarly acquisition

## Purpose

Phase 6 established that the primary chronology is still dominated by Góngora and Garcilaso. Phase 7 therefore does not maximize the number of nominally dated poems. It targets evidence that improves author and historiographic-stage identifiability, especially Fernando de Herrera (`Renovation`) and the transitional layer.

No literary-historical label is used to assign a date or to construct a semantic representation. López Bueno / ADSO classifications remain external validation only.

## 1. *Flores de poetas ilustres*: separate terminus ante quem from publication

The Phase-6 implementation used 1605, the publication year of Pedro Espinosa's *Primera parte de las Flores de poetas ilustres de España*, as a terminus ante quem for securely identified poems. Phase 7 tightens that constraint to **1603** without converting it into an exact composition date.

Evidence:

- the dedication is dated Valladolid, **20 September 1603**;
- the approval is dated Valladolid, **24 November 1603**;
- publication/circulation remains **1605**.

Accordingly, a poem securely linked to *Flores* receives:

- `composition_not_after = 1603`;
- `circulation_year = 1605`;
- no `composition_min/max` merely from inclusion in the anthology.

Key references:

- María José Alonso Veloso and Manuel Ángel Candelas Colodrón, “Los poemas de Quevedo incluidos en la Primera parte de Flores de poetas ilustres (1605) de Pedro de Espinosa,” *Calíope* 13.2 (2007): 63–80. The study notes the dedication of 20 September 1603.
- The historical approval reproduced with the anthology is dated 24 November 1603.

Phase 7 also adds the sixth Arguijo sonnet reported for *Flores*, beginning `La tirana codicia del hermano`, to the incipit-resolution audit. In the pinned Navarro corpus this incipit is present in `JuanDeArguijo/JuanDeArguijo_70.xml`; the notebook still requires unique runtime resolution before adding the 1603 upper bound.

## 2. Fernando de Herrera: curated poem-level chronology

Primary source for the current acquisition seed:

Fernando de Herrera, *Algunas obras*, ed. Begoña López Bueno. Sevilla: Diputación de Sevilla, Área de Cultura, 1998. Digital edition: Alicante, Biblioteca Virtual Miguel de Cervantes, 2011.

Bibliographic record:

https://www.cervantesvirtual.com/obra/fernando-de-herrera-algunas-obras/

Digital text:

https://www.cervantesvirtual.com/obra-visor/algunas-obras-de-fernando-de-herrera--0/html/

The notebook tests only the following small set of poem-specific chronological arguments. All receive confidence **B**, because they are scholarly/historical reconstructions rather than documentary autograph composition dates.

| Critical-edition sonnet | Incipit used for linkage | Phase-7 interval | Basis |
|---|---|---:|---|
| LVI | `Temiendo tu valor, tu ardiente espada` | 1574 | Coster/López Bueno chronology associates the poem with the monuments to Charles V erected in the Alameda of Seville in 1574. |
| LIX | `Vos, celebrando al son de noble lira` | 1578–1579 | López Bueno's note identifies Luis Barahona de Soto and relates the poem to his residence in Granada in 1578–1579. |
| LX | `Esconde/Asconde tardo Bágrada` | 1573–1574 | The poem addresses Álvaro de Bazán; scholarship connects its occasion to the Tunis campaign. The interval is deliberately wider than a single event-year. |
| LXIV | `Ya que el sujeto reino Lusitano` | 1580–1582 | The poem presupposes the Portuguese annexation of 1580 and belongs to the H collection published in 1582; the two facts define a bounded interval rather than a single year. |
| LXIX | `Pongan en tu sepulcro` | 1578 | Scholarship identifies it as composed on the death of Don Juan de Austria in 1578. |

The Navarro corpus contains multiple Herrera textual variants in some cases. Therefore no date is assigned by title/sonnet number alone: Phase 7 requires a unique normalized incipit match to a Navarro record. Any unresolved or ambiguous candidate remains excluded.

Important negative rule: historical events mentioned by a poem do **not** automatically date its composition. For example, a poem about a much earlier battle is not assigned that battle's year unless the critical scholarship specifically uses the event as a composition anchor.

## 3. Readiness diagnostics

After the Phase-7 additions, the notebook recomputes:

- number of primary-dated poems;
- primary author groups;
- primary López Bueno stages;
- entropy-based effective number of primary authors;
- top-author and Góngora shares.

It also reports conservative operational guardrails (`>=4` primary authors, `>=4` primary historiographic stages, effective authors `>=3`, top-author share `<0.65`). These are **diagnostic engineering guardrails**, not literary-theoretical thresholds and not inferential tests. Their purpose is to prevent starting a temporal semantic-network analysis while one author still dominates the dated evidence.

If these guardrails are not jointly satisfied, the next step is another focused acquisition pass, prioritizing additional `Transition` authors and an early Quevedo/`Baroque` anchor rather than adding more Góngora.
