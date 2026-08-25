# Phase 8 chronology decisions — Transition + Baroque acquisition

## Purpose

Phase 7 ended with 84 primary-dated sonnets distributed across four author groups: Góngora 58, Garcilaso 18, Herrera 5, and Cervantes 3. The primary chronology therefore still had two structural weaknesses for the Paper 1 question: `Transition` was represented by only one author (Cervantes), and `Baroque` had no primary composition chronology.

Phase 8 is a deliberately small, source-driven acquisition pass. It adds no new Góngora dates. Its purpose is to test whether a small number of poem-specific scholarly anchors can improve historical identifiability without sacrificing the conservative chronology protocol.

López Bueno / ADSO categories remain an **external validation layer only**. They are not used to assign dates, select poems, construct semantic networks, or train any model.

## 1. Pedro Espinosa: 1594–1596 bounded scholarly interval

Rafael Bonilla Cerezo, in “Góngora entre azahares: la Epístola I a Heliodoro de Pedro Espinosa,” *Analecta Malacitana* XXX.1 (2007), pp. 53–100, summarizes the evolution of Espinosa’s amorous poetry following Francisco López Estrada’s *Poesías completas* (Madrid: Espasa-Calpe, 1975). In note 4 Bonilla explicitly states that the **“período de felicidad” (1594–1596)** is manifested in four sonnets:

- `Llegó diciembre sobre el cierzo helado`
- `Levantaba, gigante en pensamiento`
- `El sol a noble furia se provoca`
- `Pues son vuestros pinceles, Mohedano`

Primary source used for the Phase-8 acquisition:

- Rafael Bonilla Cerezo, “Góngora entre azahares: la Epístola I a Heliodoro de Pedro Espinosa,” *Analecta Malacitana* XXX.1 (2007), 53–100. Universidad de Córdoba repository: https://helvia.uco.es/xmlui/handle/10396/9233
- Direct PDF: https://helvia.uco.es/bitstream/handle/10396/9233/bonilla5.pdf?isAllowed=y&sequence=1

The notebook treats `[1594, 1596]` as a confidence-B **bounded scholarly composition interval** only when an incipit resolves uniquely against the pinned Navarro `PedroEspinosa` corpus. No other Espinosa poem inherits this interval.

## 2. Quevedo: poem-specific Baroque anchors

### 2.1 Sonnet addressed to Luis Carrillo — 1609

Marcelino Menéndez Pelayo, writing to Francisco Rodríguez Marín on 6 July 1899, explicitly states that the sonnet beginning

`Así, sagrado mar, nunca te oprima...`

“se escribió en 1609.” The Navarro corpus may preserve `Así`/`Ansí` orthographic variation, so Phase 8 allows those variants but requires a unique target.

Source:

- Marcelino Menéndez Pelayo, *Epistolario*, vol. 15, carta 386, to Francisco Rodríguez Marín, Santander, 6 July 1899: https://www.cervantesvirtual.com/s3/BVMC_OBRAS/01d/be7/208/2b2/11d/fac/c70/021/85c/e60/64/mimes/01dbe720-82b2-11df-acc7-002185ce6064.pdf

Important correction to earlier work: this is a **Quevedo sonnet addressed to Carrillo**, not evidence for the composition chronology of Carrillo’s own sonnets. It must not be used to date the `LuisCarrilloySotomayor` corpus.

### 2.2 Aminta group — 1611

The same Menéndez Pelayo letter states that four Aminta sonnets “deben de ser también del año 1611,” on contextual and stylistic grounds:

- `Aminta, si a tu pecho y a tu cuello`
- `Lo que me quita en fuego, me da en nieve`
- `Aminta, para mí cualquiera día`
- `Ver relucir en llamas encendido`

These are encoded as confidence-B scholarly year assignments, not documentary autograph dates, and only if each incipit resolves uniquely in Navarro.

### 2.3 Henry IV memorial sonnets — 1610

The Biblioteca Virtual Miguel de Cervantes edition of Quevedo’s sonnets explicitly identifies poems associated with the death of Henry IV of France, including:

- `Su mano coronó su cuello ardiente` — “Inscripción al túmulo del Rey de Francia Enrique IV”
- `No pudo haber estrella que infamase` — memorial poem on the same king
- `No llegó a tanta envidia de los hados` — on the death of Henry IV

Henry IV was assassinated in 1610. Because the headings identify the death/memorial as the occasion of the poems, Phase 8 tests 1610 as confidence-B historical-event chronology, conditional on unique corpus linkage.

Source:

- Biblioteca Virtual Miguel de Cervantes, *Sonetos de Quevedo*: https://www.cervantesvirtual.com/obra-visor/sonetos-de-quevedo--0/html/ffd3e310-82b1-11df-acc7-002185ce6064_3.html

A historical event is not generally treated as a composition date. It is admissible here only because the critical heading explicitly identifies the event as the occasion of the poem.

### 2.4 Duke of Osuna memorial — 1624

The sonnet beginning

`Faltar pudo su patria al grande Osuna`

is explicitly a memorial poem for Pedro Téllez-Girón, Duke of Osuna, who died in prison in 1624. Phase 8 tests 1624 as confidence-B historical-event chronology, conditional on unique linkage.

The event-year rule is again poem-specific: the date is not generalized to nearby Quevedo poems or to the whole corpus.

## 3. Evidence deliberately not promoted in Phase 8

### Juan de Arguijo

The current evidence is useful for source history and termini ante quem, especially the *Flores* poems, but it does not yet provide a defensible lower bound for enough individual sonnets to turn the known source-level period into bounded primary composition chronology. Phase 8 therefore leaves the securely identified *Flores* sonnets as one-sided constraints rather than fabricating exact or bounded dates.

### Juan de Jáuregui

Scholarship contains dated poems outside the core Navarro subset, but dates are not transferred to the 23 Navarro sonnets without demonstrated text identity. Publication of *Rimas* (1618) remains circulation evidence only.

### Luis Carrillo y Sotomayor

The 1609 `Así/Ansí, sagrado mar...` evidence belongs to Quevedo. Carrillo’s death in 1610 remains a one-sided upper bound for his corpus, not a composition date. The failed Phase-6 Carrillo incipit search is therefore not pursued as if it were missing Carrillo evidence.

## 4. Revised readiness diagnostics

Phase 7 used a guardrail requiring at least four historiographic stages. That criterion was too weak because it could pass while `Baroque` remained completely absent. Phase 8 replaces it with the following operational diagnostics:

- at least 5 primary author groups;
- **all five** external historiographic stages represented;
- at least 2 independently represented `Transition` authors;
- at least 1 primary `Baroque` poem;
- effective number of primary authors `>= 3`;
- largest author share `< 0.65`.

These are engineering guardrails for deciding whether a temporal semantic analysis is identifiable enough to begin. They are not literary-theoretical thresholds and are not inferential tests.

If all six pass, the next phase can move from chronology acquisition to **temporal-design pre-registration / semantic representation design**. Passing the guardrails does not by itself validate any Renaissance–Baroque change point.

## 5. Reproducibility rule

Phase 8 does not hard-code an expected number of successful new dates. All candidates are resolved at runtime against the pinned Navarro corpus. Unresolved or ambiguous incipits remain excluded. The Phase-7 baseline of 84 primary poems must be reproduced before any Phase-8 assignment is added.
