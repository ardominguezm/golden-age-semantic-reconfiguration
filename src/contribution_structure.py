# Contribution structure and meso-scale semantic neighborhoods
# This script consumes the analytical state created by main_analysis_mechanism.py
# in the same Python namespace.

import sys, subprocess, json, math
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

NETWORKX_VERSION = '3.5'
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', f'networkx=={NETWORKX_VERSION}'], check=True)
import networkx as nx
assert nx.__version__ == NETWORKX_VERSION, nx.__version__

REQUIRED_MAIN_GLOBALS = [
    'edge_contributors', 'mechanism_summary', 'STATS', 'primary', 'MC_DRAWS',
    'AUTHORS', 'left_members', 'right_members', 'close_edges', 'occurrences',
    'STAGE', 'MOVEMENT', 'pleft', 'pright', 'FULL_PIDS'
]
missing_globals = [x for x in REQUIRED_MAIN_GLOBALS if x not in globals()]
assert not missing_globals, f'Contribution analysis requires the completed main analysis; missing: {missing_globals}'

print('Contribution-structure environment ready | NetworkX', nx.__version__)

# -----------------------------------------------------------------------------
# 1. Contribution table and deterministic coverage slices
# -----------------------------------------------------------------------------
bal16 = edge_contributors[edge_contributors['mode'].eq('author_balanced')].copy()
bal16 = bal16.sort_values(
    ['expected_contribution', 'concept_u', 'concept_v'],
    ascending=[False, True, True],
).reset_index(drop=True)
bal16['phase16_rank'] = np.arange(1, len(bal16) + 1)

meanR16 = float(
    mechanism_summary.loc[
        mechanism_summary['mode'].eq('author_balanced'), 'mean_rewiring'
    ].iloc[0]
)
assert meanR16 > 0
assert abs(float(bal16['expected_contribution'].sum()) - meanR16) < 1e-8

positive_edges = bal16[bal16['expected_contribution'] > 0].copy()
positive_edges['share_of_mean_rewiring'] = (
    positive_edges['expected_contribution'] / meanR16
)
positive_edges['cumulative_share'] = positive_edges['share_of_mean_rewiring'].cumsum()

def coverage_prefix(df, target):
    vals = df['cumulative_share'].to_numpy(float)
    k = int(np.searchsorted(vals, target, side='left')) + 1
    k = min(k, len(df))
    out = df.iloc[:k].copy()
    actual = float(out['share_of_mean_rewiring'].sum())
    assert actual + 1e-12 >= target
    if k > 1:
        prev = float(df.iloc[:k-1]['share_of_mean_rewiring'].sum())
        assert prev < target + 1e-12
    return out

slice50 = coverage_prefix(positive_edges, 0.50)
slice80 = coverage_prefix(positive_edges, 0.80)

def build_contribution_graph(df):
    G = nx.Graph()
    nodes = sorted(set(df['concept_u']).union(set(df['concept_v'])))
    G.add_nodes_from(nodes)
    for r in df.sort_values(['phase16_rank', 'concept_u', 'concept_v']).itertuples(index=False):
        G.add_edge(
            r.concept_u,
            r.concept_v,
            edge_index=int(r.edge_index),
            rank=int(r.phase16_rank),
            expected_contribution=float(r.expected_contribution),
            share_of_mean_rewiring=float(r.share_of_mean_rewiring),
            eligibility_rate=float(r.eligibility_rate),
            dominant_direction=str(r.dominant_direction),
            direction_consistency=float(r.direction_consistency),
            expected_birth_contribution=float(r.expected_birth_contribution),
            expected_death_contribution=float(r.expected_death_contribution),
            expected_shared_reweight_contribution=float(r.expected_shared_reweight_contribution),
        )
    return G

G50 = build_contribution_graph(slice50)
G80 = build_contribution_graph(slice80)

def component_summary(G, df, target):
    comps = [set(c) for c in nx.connected_components(G)]
    comps.sort(key=lambda c: (-len(c), sorted(c)[0]))
    lcc = comps[0] if comps else set()
    lcc_df = df[
        df['concept_u'].isin(lcc) & df['concept_v'].isin(lcc)
    ].copy()
    total = float(df['expected_contribution'].sum())
    lcc_contrib = float(lcc_df['expected_contribution'].sum())
    birth = float(df['expected_birth_contribution'].sum())
    death = float(df['expected_death_contribution'].sum())
    shared = float(df['expected_shared_reweight_contribution'].sum())
    mech_total = birth + death + shared
    assert abs(mech_total - total) < 1e-8
    return {
        'coverage_target': target,
        'coverage_actual': total / meanR16,
        'n_edges': int(len(df)),
        'n_nodes': int(G.number_of_nodes()),
        'n_components': int(len(comps)),
        'largest_component_n_nodes': int(len(lcc)),
        'largest_component_node_share': (
            float(len(lcc) / G.number_of_nodes()) if G.number_of_nodes() else np.nan
        ),
        'largest_component_contribution': lcc_contrib,
        'largest_component_contribution_share_of_slice': (
            lcc_contrib / total if total > 0 else np.nan
        ),
        'birth_share_within_slice': birth / total if total > 0 else np.nan,
        'death_share_within_slice': death / total if total > 0 else np.nan,
        'shared_reweight_share_within_slice': shared / total if total > 0 else np.nan,
    }, lcc

cov50, lcc50 = component_summary(G50, slice50, 0.50)
cov80, lcc80 = component_summary(G80, slice80, 0.80)
coverage_summary = pd.DataFrame([cov50, cov80])

print(
    'Contribution coverage slices:',
    f"50% -> {len(slice50)} edges / {G50.number_of_nodes()} nodes;",
    f"80% -> {len(slice80)} edges / {G80.number_of_nodes()} nodes",
)

# -----------------------------------------------------------------------------
# 2. Deterministic community partition on the 80%-coverage LCC
# -----------------------------------------------------------------------------
G80_lcc = G80.subgraph(sorted(lcc80)).copy()
if G80_lcc.number_of_nodes() == 0:
    communities = []
elif G80_lcc.number_of_edges() == 0:
    communities = [frozenset(G80_lcc.nodes())]
else:
    communities = list(
        nx.community.greedy_modularity_communities(
            G80_lcc, weight='expected_contribution'
        )
    )

def internal_contribution(nodes):
    sg = G80_lcc.subgraph(nodes)
    return float(
        sum(
            float(d['expected_contribution'])
            for _, _, d in sg.edges(data=True)
        )
    )

communities = sorted(
    communities,
    key=lambda c: (-internal_contribution(c), -len(c), sorted(c)[0]),
)
node_to_comm = {}
for cid, comm in enumerate(communities, 1):
    for node in sorted(comm):
        node_to_comm[node] = cid

# Deterministic connected-component labels for all 80% nodes.
components80 = [set(c) for c in nx.connected_components(G80)]
components80.sort(key=lambda c: (-len(c), sorted(c)[0]))
node_to_component = {}
for component_id, comp in enumerate(components80, 1):
    for node in comp:
        node_to_component[node] = component_id

nodes50 = set(G50.nodes())
membership_rows = []
for node in sorted(G80.nodes()):
    membership_rows.append({
        'concept': node,
        'component_id': int(node_to_component[node]),
        'in_largest_component': bool(node in lcc80),
        'community_id': node_to_comm.get(node, pd.NA),
        'in_50pct_graph': bool(node in nodes50),
    })
community_membership = pd.DataFrame(membership_rows)

# Internal/cross-community accounting for the 80% LCC.
slice80_lcc = slice80[
    slice80['concept_u'].isin(lcc80) & slice80['concept_v'].isin(lcc80)
].copy()
slice80_lcc['community_u'] = slice80_lcc['concept_u'].map(node_to_comm)
slice80_lcc['community_v'] = slice80_lcc['concept_v'].map(node_to_comm)
slice80_lcc['is_internal_community_edge'] = (
    slice80_lcc['community_u'].notna()
    & slice80_lcc['community_u'].eq(slice80_lcc['community_v'])
)
internal80 = slice80_lcc[slice80_lcc['is_internal_community_edge']].copy()
cross80 = slice80_lcc[~slice80_lcc['is_internal_community_edge']].copy()

community_summary_rows = []
top_concept_rows = []
top_edge_rows = []
community_edge_indices = defaultdict(list)

for cid, comm in enumerate(communities, 1):
    edf = internal80[internal80['community_u'].eq(cid)].copy()
    comm_contrib = float(edf['expected_contribution'].sum())
    community_edge_indices[cid] = edf['edge_index'].astype(int).tolist()

    birth = float(edf['expected_birth_contribution'].sum())
    death = float(edf['expected_death_contribution'].sum())
    shared = float(edf['expected_shared_reweight_contribution'].sum())
    if comm_contrib > 0:
        assert abs((birth + death + shared) - comm_contrib) < 1e-8

    strengthening = float(
        edf.loc[
            edf['dominant_direction'].eq('strengthening'), 'expected_contribution'
        ].sum()
    )
    weakening = float(
        edf.loc[
            edf['dominant_direction'].eq('weakening'), 'expected_contribution'
        ].sum()
    )
    neutral = float(
        edf.loc[
            edf['dominant_direction'].eq('neutral'), 'expected_contribution'
        ].sum()
    )

    community_summary_rows.append({
        'community_id': cid,
        'n_concepts': int(len(comm)),
        'n_internal_edges': int(len(edf)),
        'internal_expected_contribution': comm_contrib,
        'share_of_phase15_mean_rewiring': (
            comm_contrib / meanR16 if meanR16 > 0 else np.nan
        ),
        'share_of_80pct_slice': (
            comm_contrib / float(slice80['expected_contribution'].sum())
            if len(slice80) else np.nan
        ),
        'birth_share': birth / comm_contrib if comm_contrib > 0 else np.nan,
        'death_share': death / comm_contrib if comm_contrib > 0 else np.nan,
        'shared_reweight_share': (
            shared / comm_contrib if comm_contrib > 0 else np.nan
        ),
        'strengthening_contribution_share': (
            strengthening / comm_contrib if comm_contrib > 0 else np.nan
        ),
        'weakening_contribution_share': (
            weakening / comm_contrib if comm_contrib > 0 else np.nan
        ),
        'neutral_contribution_share': (
            neutral / comm_contrib if comm_contrib > 0 else np.nan
        ),
    })

    incident = Counter()
    for r in edf.itertuples(index=False):
        incident[r.concept_u] += float(r.expected_contribution)
        incident[r.concept_v] += float(r.expected_contribution)
    for rank, (concept, val) in enumerate(
        sorted(incident.items(), key=lambda kv: (-kv[1], kv[0]))[:10], 1
    ):
        top_concept_rows.append({
            'community_id': cid,
            'rank_within_community': rank,
            'concept': concept,
            'incident_internal_contribution': val,
            'share_of_community_internal_contribution': (
                val / comm_contrib if comm_contrib > 0 else np.nan
            ),
        })

    for rank, r in enumerate(
        edf.sort_values(
            ['expected_contribution', 'concept_u', 'concept_v'],
            ascending=[False, True, True],
        ).head(10).itertuples(index=False),
        1,
    ):
        top_edge_rows.append({
            'community_id': cid,
            'rank_within_community': rank,
            'edge_index': int(r.edge_index),
            'phase16_rank': int(r.phase16_rank),
            'concept_u': r.concept_u,
            'concept_v': r.concept_v,
            'expected_contribution': float(r.expected_contribution),
            'share_of_phase15_mean_rewiring': float(r.share_of_mean_rewiring),
            'dominant_direction': r.dominant_direction,
            'direction_consistency': float(r.direction_consistency),
        })

community_summary = pd.DataFrame(community_summary_rows)
community_top_concepts = pd.DataFrame(top_concept_rows)
community_top_edges = pd.DataFrame(top_edge_rows)

# Diagnostic: how many primary 80%-graph communities are touched by the 50%-slice nodes?
fifty_community_ids = sorted(
    {
        node_to_comm[n]
        for n in nodes50
        if n in node_to_comm
    }
)

print(
    '80% LCC communities:',
    len(communities),
    '| internal contribution share of Phase-15 mean:',
    round(float(internal80['expected_contribution'].sum() / meanR16), 6),
    '| cross-community LCC share:',
    round(float(cross80['expected_contribution'].sum() / meanR16), 6),
)

# -----------------------------------------------------------------------------
# 3. Meso-scale author support using the main-analysis support definition
# -----------------------------------------------------------------------------
# We accumulate support once for the union of community-internal edges and the
# fixed close-reading edges. This avoids any post-hoc author-specific selection.
close_edge_indices = sorted(set(close_edges['edge_index'].astype(int)))
internal_edge_indices = sorted(set(internal80['edge_index'].astype(int)))
support_edge_indices = sorted(set(internal_edge_indices).union(close_edge_indices))
support_pos = {edge_index: j for j, edge_index in enumerate(support_edge_indices)}
support_acc = {
    (side, author): np.zeros(len(support_edge_indices), dtype=float)
    for side in ['left', 'right']
    for author in AUTHORS
}

for d in range(MC_DRAWS):
    for side, ids in [('left', left_members[d]), ('right', right_members[d])]:
        rows = np.asarray([STATS['pidrow'][p] for p in ids], dtype=int)
        U = STATS['U'][rows].astype(float)
        authors = STATS['authors'][rows]
        ac = Counter(authors.tolist())
        factors = np.asarray(
            [1.0 / (ac[a] * u) if u > 0 else 0.0 for a, u in zip(authors, U)],
            dtype=float,
        )
        if support_edge_indices:
            pm = STATS['P'][rows][:, support_edge_indices].toarray().astype(float)
            for author in AUTHORS:
                mask = authors == author
                if np.any(mask):
                    support_acc[(side, author)] += np.sum(
                        pm[mask] * factors[mask, None], axis=0
                    )

support_mean = {
    key: arr / MC_DRAWS
    for key, arr in support_acc.items()
}

community_author_rows = []
for cid in range(1, len(communities) + 1):
    edge_ids = community_edge_indices[cid]
    positions = [support_pos[e] for e in edge_ids if e in support_pos]
    for side in ['left', 'right']:
        author_values = {}
        for author in AUTHORS:
            vals = support_mean[(side, author)][positions] if positions else np.array([])
            author_values[author] = float(vals.sum()) if len(vals) else 0.0
        total = float(sum(author_values.values()))
        for author in AUTHORS:
            vals = support_mean[(side, author)][positions] if positions else np.array([])
            community_author_rows.append({
                'community_id': cid,
                'window_side': side,
                'author': author,
                'literary_stage': STAGE[author],
                'movement': MOVEMENT[author],
                'expected_weighted_pair_mass': author_values[author],
                'share_of_community_pair_mass': (
                    author_values[author] / total if total > 0 else np.nan
                ),
                'n_internal_edges_with_nonzero_expected_support': (
                    int(np.sum(vals > 0)) if len(vals) else 0
                ),
                'n_internal_edges': int(len(edge_ids)),
            })
community_author_support = pd.DataFrame(community_author_rows)

# -----------------------------------------------------------------------------
# 4. Fixed six-edge audit: meso-scale placement and author profile
# -----------------------------------------------------------------------------
edge_lookup16 = bal16.set_index('edge_index', drop=False)
slice80_edge_set = set(slice80['edge_index'].astype(int))
slice50_edge_set = set(slice50['edge_index'].astype(int))

close_map_rows = []
for r in close_edges.sort_values('balanced_rank').itertuples(index=False):
    edge_index = int(r.edge_index)
    er = edge_lookup16.loc[edge_index]
    cid_u = node_to_comm.get(er.concept_u)
    cid_v = node_to_comm.get(er.concept_v)
    cid = cid_u if cid_u is not None and cid_u == cid_v else pd.NA

    mech_values = {
        'birth': float(er.expected_birth_contribution),
        'death': float(er.expected_death_contribution),
        'shared_reweight': float(er.expected_shared_reweight_contribution),
    }
    dominant_mechanism = max(
        sorted(mech_values),
        key=lambda k: mech_values[k],
    )

    row = {
        'edge_index': edge_index,
        'balanced_rank': int(r.balanced_rank),
        'concept_u': r.concept_u,
        'concept_v': r.concept_v,
        'direction': r.direction,
        'selection_basis': r.selection_basis,
        'expected_contribution': float(er.expected_contribution),
        'share_of_phase15_mean_rewiring': float(
            er.expected_contribution / meanR16
        ),
        'in_50pct_graph': bool(edge_index in slice50_edge_set),
        'in_80pct_graph': bool(edge_index in slice80_edge_set),
        'community_id': cid,
        'dominant_mechanism': dominant_mechanism,
        'expected_birth_contribution': float(er.expected_birth_contribution),
        'expected_death_contribution': float(er.expected_death_contribution),
        'expected_shared_reweight_contribution': float(
            er.expected_shared_reweight_contribution
        ),
    }

    pos = support_pos[edge_index]
    for side in ['left', 'right']:
        vals = {
            author: float(support_mean[(side, author)][pos])
            for author in AUTHORS
        }
        total = float(sum(vals.values()))
        if total > 0:
            top_author = sorted(vals, key=lambda a: (-vals[a], a))[0]
            top_share = vals[top_author] / total
            gongora_share = vals.get('Gongora', 0.0) / total
        else:
            top_author = pd.NA
            top_share = np.nan
            gongora_share = np.nan
        row[f'{side}_top_support_author'] = top_author
        row[f'{side}_top_support_share'] = top_share
        row[f'{side}_gongora_support_share'] = gongora_share

    close_map_rows.append(row)

close_edge_community_map = pd.DataFrame(close_map_rows)

# -----------------------------------------------------------------------------
# 5. Full poem contexts for every frozen Phase-15 close-reading occurrence
# -----------------------------------------------------------------------------
meta16 = primary.set_index('n_id')
context_rows = []
for r in occurrences.itertuples(index=False):
    rr = meta16.loc[r.n_id]
    context_rows.append({
        'edge_index': int(r.edge_index),
        'balanced_rank': int(r.balanced_rank),
        'direction': r.direction,
        'selection_basis': r.selection_basis,
        'concept_u': r.concept_u,
        'concept_v': r.concept_v,
        'n_id': r.n_id,
        'author': r.author,
        'literary_stage': r.literary_stage,
        'movement': r.movement,
        'composition_min': int(r.composition_min),
        'composition_max': int(r.composition_max),
        'p_left_window': float(r.p_left_window),
        'p_right_window': float(r.p_right_window),
        'matching_line_number': int(r.line_number),
        'matching_line_text': r.line_text,
        'poem_n_lines': int(rr.n_lines),
        'poem_text': '\n'.join(rr['lines']),
    })
close_reading_poem_contexts = pd.DataFrame(context_rows)
if len(close_reading_poem_contexts):
    close_reading_poem_contexts = close_reading_poem_contexts.sort_values(
        ['balanced_rank', 'n_id', 'matching_line_number']
    )

assert len(close_edges) == 6, len(close_edges)
assert len(close_reading_poem_contexts) == len(occurrences)

# -----------------------------------------------------------------------------
# 6. Exports and auditable checkpoint
# -----------------------------------------------------------------------------
OUT16 = Path('/content/gasr_phase16_outputs')
OUT16.mkdir(exist_ok=True)

positive_edges.to_csv(OUT16 / 'phase16_contribution_edges.csv', index=False)
coverage_summary.to_csv(OUT16 / 'phase16_coverage_summary.csv', index=False)
community_membership.to_csv(OUT16 / 'phase16_community_membership.csv', index=False)
community_summary.to_csv(OUT16 / 'phase16_community_summary.csv', index=False)
community_top_concepts.to_csv(OUT16 / 'phase16_community_top_concepts.csv', index=False)
community_top_edges.to_csv(OUT16 / 'phase16_community_top_edges.csv', index=False)
community_author_support.to_csv(OUT16 / 'phase16_community_author_support.csv', index=False)
close_edge_community_map.to_csv(OUT16 / 'phase16_close_edge_community_map.csv', index=False)
close_reading_poem_contexts.to_csv(
    OUT16 / 'phase16_close_reading_poem_contexts.csv', index=False
)

checkpoint16 = {
    'phase': 16,
    'status': 'explanatory_meso_scale_followup',
    'networkx_version': NETWORKX_VERSION,
    'phase15_author_balanced_mean_rewiring': meanR16,
    'n_positive_contribution_edges': int(len(positive_edges)),
    'coverage_50_actual': float(cov50['coverage_actual']),
    'coverage_50_n_edges': int(cov50['n_edges']),
    'coverage_50_n_nodes': int(cov50['n_nodes']),
    'coverage_80_actual': float(cov80['coverage_actual']),
    'coverage_80_n_edges': int(cov80['n_edges']),
    'coverage_80_n_nodes': int(cov80['n_nodes']),
    'coverage_80_lcc_n_nodes': int(cov80['largest_component_n_nodes']),
    'coverage_80_lcc_contribution_share_of_slice': float(
        cov80['largest_component_contribution_share_of_slice']
    ),
    'n_communities_80_lcc': int(len(communities)),
    'n_communities_touched_by_50pct_nodes': int(len(fifty_community_ids)),
    'internal_community_share_of_phase15_mean': float(
        internal80['expected_contribution'].sum() / meanR16
    ),
    'cross_community_lcc_share_of_phase15_mean': float(
        cross80['expected_contribution'].sum() / meanR16
    ),
    'n_frozen_close_reading_edges': int(len(close_edges)),
    'n_close_edges_in_80pct_graph': int(
        close_edge_community_map['in_80pct_graph'].sum()
    ),
    'n_close_reading_occurrences': int(len(occurrences)),
    'n_close_reading_poem_context_rows': int(len(close_reading_poem_contexts)),
    'historical_break_reestimated': False,
    'new_significance_test_used': False,
    'community_labels_assigned_computationally': False,
    'close_reading_edges_reselected': False,
    'phase13_14_inference_reopened': False,
}
(OUT16 / 'phase16_checkpoint.json').write_text(
    json.dumps(checkpoint16, indent=2, ensure_ascii=False) + '\n',
    encoding='utf-8',
)

print('\nPHASE 16 CHECKPOINT')
print('-------------------')
for k, v in checkpoint16.items():
    print(f'{k}: {v}')

print('\nCOVERAGE SUMMARY')
print(coverage_summary.to_string(index=False))

print('\nCOMMUNITY SUMMARY')
if len(community_summary):
    print(
        community_summary.sort_values(
            'internal_expected_contribution', ascending=False
        ).to_string(index=False)
    )
else:
    print('No communities found.')

print('\nTOP CONCEPTS BY COMMUNITY')
if len(community_top_concepts):
    print(community_top_concepts.to_string(index=False))
else:
    print('No community concepts found.')

print('\nFIXED CLOSE-READING EDGE PLACEMENT')
print(close_edge_community_map.to_string(index=False))

print('\nPHASE 16 OUTPUTS SERIALIZED:', OUT16)
print('PHASE 16 COMPUTATION COMPLETE: TRUE')
