# Temporal Reconstruction Protocol — Paper 1

## Objective

The diachronic analysis will not assign a single year to every poem unless that year is supported by explicit scholarly evidence. The temporal model will preserve uncertainty and distinguish composition, circulation/publication, witness/edition, and biographical evidence.

## Evidence hierarchy

1. **Composition year or bounded composition interval** from a scholarly critical source.
2. **First publication or collection/circulation date** when it can be tied to the poem or a defensible subset of poems.
3. **Witness or edition date** as bibliographic evidence only; never silently treated as composition.
4. **Author activity/career interval** as a fallback uncertainty interval.
5. **Birth/death dates** as biographical metadata only, never as poem dates.

## Corpus architecture

Navarro Colorado's TEI corpus is the poem-identity backbone. Hernández-Lorenzo supplies a standardized textual layer and source-exclusive material where appropriate. Automatic links are accepted only when exact normalized-text evidence is available; near-identical fuzzy links remain provisional until collision and variant checks are complete.

## Temporal audit before dynamic networks

Before choosing any historical window size, the project will quantify:

- poems with composition-level evidence;
- poems with publication/circulation evidence;
- poems with only witness/edition evidence;
- poems with only author-level fallback intervals;
- width of uncertainty intervals by author and period;
- concentration of poems by source/collection;
- potential temporal bias caused by large authors or retrospective editions.

Only after this audit will the project choose between fixed windows, adaptive windows, interval-weighted networks, or probabilistic temporal assignment.

## Historical markers

Dates such as 1580 and 1605 are external historiographic reference markers. They are not imposed change points. Any structural transition must be estimated from the corpus and compared with these markers post hoc.

## Current known limitations

The Hernández-Lorenzo metadata `Date` field encodes author lifespans, not poem dates. The Navarro TEI corpus contains very little explicit date markup; detected dates may refer to witnesses or editions. Therefore, a defensible dynamic analysis requires external scholarly temporal reconstruction rather than inference from author birth year.
