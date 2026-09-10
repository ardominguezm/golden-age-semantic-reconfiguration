# Representation robustness to POS and lemmatization choices
# This script consumes the analytical state created by main_analysis_mechanism.py
# in the same Python namespace.

import json, unicodedata, sys, subprocess
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.stats import spearmanr

NETWORKX_VERSION='3.5'
subprocess.run([sys.executable,'-m','pip','install','-q',f'networkx=={NETWORKX_VERSION}'],check=True)
import networkx as nx
assert nx.__version__==NETWORKX_VERSION

REQUIRED=[
    'primary','flat','docs','MAIN_POS','FULL_PIDS','author_lookup','sampled','MC_DRAWS',
    'ids_array','pidcol','WIN20','TRANS','memberships','traj_summary','mechanism_summary',
    'edge_contributors','STATS','MODES'
]
missing=[x for x in REQUIRED if x not in globals()]
assert not missing,f'Representation robustness requires the completed main analysis; missing: {missing}'
assert MC_DRAWS==1000
assert set(MODES)=={'author_balanced','raw'}

print('Representation-robustness environment ready | main-analysis namespace verified')

# -----------------------------------------------------------------------------
# 1. Frozen representation variants
# -----------------------------------------------------------------------------
VARIANTS={
    'lemma_only':'lemma',
    'surface_form':'surface',
}
MIN_ID_LEN=2

def norm_nfc_lower(s):
    return unicodedata.normalize('NFC',str(s)).strip().lower()

def make_units(kind):
    units={r.n_id:[set() for _ in r.lines] for r in primary.itertuples(index=False)}
    records=[]
    for (pid,line_no,_),doc in zip(flat,docs):
        cs=[]
        for tok in doc:
            if not tok.is_alpha or tok.pos_ not in MAIN_POS:
                continue
            if kind=='lemma': ident=norm_nfc_lower(tok.lemma_)
            elif kind=='surface': ident=norm_nfc_lower(tok.text)
            else: raise ValueError(kind)
            if len(ident)>=MIN_ID_LEN:
                cs.append(ident); records.append((pid,ident))
        units[pid][line_no-1]=set(cs)
    concept_poems=defaultdict(set)
    for pid,c in records: concept_poems[c].add(pid)
    vocab={c for c,pids in concept_poems.items() if len(pids)>=2}
    return units,vocab,records

variant_units={}; variant_vocab={}
for variant,kind in VARIANTS.items():
    units,vocab,_=make_units(kind)
    variant_units[variant]=units; variant_vocab[variant]=vocab
    print(variant,'DF>=2 vocabulary:',len(vocab))

# -----------------------------------------------------------------------------
# 2. Generic line-context PPMI representation
# -----------------------------------------------------------------------------
def prepare_variant_stats(pids,units_by_poem,vocab):
    concepts=sorted(vocab); cidx={c:i for i,c in enumerate(concepts)}; pair_keys=set()
    for pid in pids:
        for unit in units_by_poem[pid]:
            cs=sorted(c for c in unit if c in cidx)
            pair_keys.update(combinations(cs,2))
    pairs=sorted(pair_keys); pidx={p:i for i,p in enumerate(pairs)}
    M=np.zeros((len(pids),len(concepts)),dtype=np.float32); U=np.zeros(len(pids),dtype=np.float32)
    rr=[]; cc=[]; dd=[]
    for i,pid in enumerate(pids):
        units=units_by_poem[pid]; U[i]=len(units); mc=Counter(); pc=Counter()
        for unit in units:
            cs=sorted(c for c in unit if c in cidx)
            for c in cs: mc[c]+=1
            for pair in combinations(cs,2): pc[pair]+=1
        for c,v in mc.items(): M[i,cidx[c]]=v
        for pair,v in pc.items(): rr.append(i); cc.append(pidx[pair]); dd.append(v)
    P=csr_matrix((np.asarray(dd,dtype=np.float32),(rr,cc)),shape=(len(pids),len(pairs)),dtype=np.float32)
    ei=np.asarray([cidx[a] for a,b in pairs],dtype=np.int32)
    ej=np.asarray([cidx[b] for a,b in pairs],dtype=np.int32)
    return {
        'pids':list(pids),'pidrow':{p:i for i,p in enumerate(pids)},'concepts':concepts,'cidx':cidx,
        'pairs':pairs,'pidx':pidx,'M':M,'U':U,'P':P,'ei':ei,'ej':ej,
        'authors':np.asarray([author_lookup[p] for p in pids],dtype=object),
    }

variant_stats={
    v:prepare_variant_stats(FULL_PIDS,variant_units[v],variant_vocab[v])
    for v in VARIANTS
}

def build_state(stats,ids,mode):
    rows=np.asarray([stats['pidrow'][p] for p in ids],dtype=int)
    nv=len(stats['concepts']); ne=len(stats['pairs'])
    if len(rows)==0: return {'active':np.zeros(nv,bool),'w':np.zeros(ne,float)}
    U=stats['U'][rows].astype(float); authors=stats['authors'][rows]
    if mode=='raw': factors=np.ones(len(rows),float)
    elif mode=='author_balanced':
        ac=Counter(authors.tolist())
        factors=np.asarray([1.0/(ac[a]*u) if u>0 else 0.0 for a,u in zip(authors,U)],float)
    else: raise ValueError(mode)
    T=float(np.dot(factors,U)); assert T>0
    marg=(stats['M'][rows].astype(float)*factors[:,None]).sum(axis=0)
    pairmass=np.asarray(stats['P'][rows].multiply(factors[:,None]).sum(axis=0)).ravel().astype(float)
    support=np.asarray(stats['P'][rows].sum(axis=0)).ravel(); active=marg>0; w=np.zeros(ne,float)
    valid=(support>=1)&(pairmass>0)
    if np.any(valid):
        ii=np.flatnonzero(valid); ei=stats['ei'][valid]; ej=stats['ej'][valid]; pm=pairmass[valid]
        denom=(marg[ei]/T)*(marg[ej]/T); ratio=(pm/T)/denom
        w[ii]=np.maximum(0.0,np.log2(ratio))
    return {'active':active,'w':w}

def compare_states(stats,a,b):
    persistent=a['active']&b['active']; union=a['active']|b['active']
    nu=int(union.sum()); npers=int(persistent.sum())
    lexical=np.nan if nu==0 else 1.0-npers/nu
    keep=persistent[stats['ei']]&persistent[stats['ej']]
    w1=np.where(keep,a['w'],0.0); w2=np.where(keep,b['w'],0.0)
    n1=float(np.linalg.norm(w1)); n2=float(np.linalg.norm(w2))
    rewiring=np.nan if n1==0 or n2==0 else 1.0-float(np.dot(w1,w2)/(n1*n2))
    return lexical,rewiring,npers

# -----------------------------------------------------------------------------
# 3. Observed trajectories — exactly the frozen 20y memberships
# -----------------------------------------------------------------------------
obs_rows=[]; observed_summary=[]; obs_draw_tables={}
for variant,stats in variant_stats.items():
    unique_ids=sorted(set(x for row in memberships for x in row))
    cache={(ids,mode):build_state(stats,ids,mode) for ids in unique_ids for mode in MODES}
    rows=[]
    for d in range(MC_DRAWS):
        for li,ri,tc in TRANS:
            for mode in MODES:
                L,R,npers=compare_states(stats,cache[(memberships[d][li],mode)],cache[(memberships[d][ri],mode)])
                rows.append({'variant':variant,'draw':d,'transition_center':tc,'mode':mode,
                             'lexical_turnover':L,'rewiring_cosine':R,'n_persistent_concepts':npers})
    od=pd.DataFrame(rows); obs_draw_tables[variant]=od; obs_rows.append(od)
    for (tc,mode),q in od.groupby(['transition_center','mode'],sort=True):
        observed_summary.append({
            'variant':variant,'transition_center':float(tc),'mode':mode,
            'rewiring_median':float(np.median(q.rewiring_cosine)),
            'rewiring_q10':float(np.quantile(q.rewiring_cosine,.1)),
            'rewiring_q90':float(np.quantile(q.rewiring_cosine,.9)),
            'lexical_turnover_median':float(np.median(q.lexical_turnover)),
            'persistent_concepts_median':float(np.median(q.n_persistent_concepts)),
        })
observed_trajectory=pd.DataFrame(observed_summary)

# Add benchmark Phase-15 summary for a single comparison table.
benchmark_obs=traj_summary.copy(); benchmark_obs['variant']='benchmark_lemma_pos'
benchmark_obs=benchmark_obs[['variant','transition_center','mode','rewiring_median','rewiring_q10','rewiring_q90','lexical_turnover_median','persistent_concepts_median']]
observed_trajectory_all=pd.concat([benchmark_obs,observed_trajectory],ignore_index=True)

spec_rows=[
    {'variant':'benchmark_lemma_pos','identity':'normalized spaCy lemma::coarse POS','uses_spacy_lemma':True,'pos_in_node_identity':True,
     'retained_pos_gate':'NOUN|VERB|ADJ|ADV','df_threshold':2,'vocab_size':len(STATS['concepts']),'global_pair_count':len(STATS['pairs'])},
]
for v in VARIANTS:
    spec_rows.append({'variant':v,'identity':'normalized spaCy lemma' if v=='lemma_only' else 'lowercase NFC original token surface',
        'uses_spacy_lemma':v=='lemma_only','pos_in_node_identity':False,'retained_pos_gate':'NOUN|VERB|ADJ|ADV','df_threshold':2,
        'vocab_size':len(variant_stats[v]['concepts']),'global_pair_count':len(variant_stats[v]['pairs'])})
representation_specification=pd.DataFrame(spec_rows)

# Frozen benchmark ordering and variant comparisons.
comp_rows=[]
for mode in MODES:
    b=benchmark_obs[benchmark_obs['mode'].eq(mode)].sort_values('transition_center')
    bvals=b.rewiring_median.to_numpy(float)
    for v in VARIANTS:
        q=observed_trajectory[(observed_trajectory.variant.eq(v))&(observed_trajectory['mode'].eq(mode))].sort_values('transition_center')
        assert np.allclose(q.transition_center.to_numpy(float),b.transition_center.to_numpy(float))
        vals=q.rewiring_median.to_numpy(float)
        rho=float(spearmanr(bvals,vals).statistic)
        peak_row=q.sort_values(['rewiring_median','transition_center'],ascending=[False,True]).iloc[0]
        z=q[q.transition_center.eq(1592.0)].iloc[0]
        rank1592=int(q.rewiring_median.rank(method='min',ascending=False)[q.transition_center.eq(1592.0)].iloc[0])
        comp_rows.append({
            'variant':v,'mode':mode,'spearman_rho_vs_benchmark':rho,
            'peak_transition_center':float(peak_row.transition_center),'peak_rewiring':float(peak_row.rewiring_median),
            'rewiring_at_1592':float(z.rewiring_median),'rank_1592_among_8':rank1592,
            'lexical_turnover_at_1592':float(z.lexical_turnover_median),
            'persistent_concepts_at_1592':float(z.persistent_concepts_median),
        })
trajectory_comparison=pd.DataFrame(comp_rows)

# -----------------------------------------------------------------------------
# 4. Phase-13 N1 / N2 robustness, frozen 100 x 20 budget
# -----------------------------------------------------------------------------
NULL_SEED=20260826
NULL_DRAW_IDS=np.linspace(0,MC_DRAWS-1,100,dtype=int)
NULL_REPS=20
assert len(set(NULL_DRAW_IDS))==100 and len(NULL_DRAW_IDS)*NULL_REPS==2000

def local_reassign(left,right,rng):
    L=set(left); R=set(right); pool=L|R; nl=set(); nr=set()
    for author in sorted(set(author_lookup[p] for p in pool)):
        pa=sorted(p for p in pool if author_lookup[p]==author)
        La=L&set(pa); Ra=R&set(pa); ns=len(La&Ra); nlo=len(La-Ra); nro=len(Ra-La)
        perm=np.asarray(pa,dtype=object)[rng.permutation(len(pa))].tolist()
        shared=set(perm[:ns]); onlyl=set(perm[ns:ns+nlo]); onlyr=set(perm[ns+nlo:ns+nlo+nro])
        nl|=shared|onlyl; nr|=shared|onlyr
    assert len(nl)==len(L) and len(nr)==len(R) and len(nl&nr)==len(L&R)
    return tuple(sorted(nl)),tuple(sorted(nr))

def ids_for_year_array(years,win):
    mask=(years>=win[0])&(years<=win[1])
    return tuple(sorted(ids_array[mask].tolist()))

def run_n1(variant,stats):
    rng=np.random.default_rng(np.random.SeedSequence([NULL_SEED,1]))
    rows=[]
    for d in NULL_DRAW_IDS:
        memb=memberships[int(d)]
        for rep in range(NULL_REPS):
            for li,ri,tc in TRANS:
                nl,nr=local_reassign(memb[li],memb[ri],rng)
                for mode in MODES:
                    a=build_state(stats,nl,mode); b=build_state(stats,nr,mode)
                    L,R,npers=compare_states(stats,a,b)
                    rows.append({'variant':variant,'draw':int(d),'rep':rep,'transition_center':tc,'mode':mode,
                                 'rewiring_cosine':R,'lexical_turnover':L,'n_persistent_concepts':npers})
    return pd.DataFrame(rows)

def run_n2(variant,stats):
    rng=np.random.default_rng(np.random.SeedSequence([NULL_SEED,2]))
    authors=sorted(set(author_lookup[p] for p in FULL_PIDS))
    apos={a:np.asarray([pidcol[p] for p in FULL_PIDS if author_lookup[p]==a],dtype=int) for a in authors}
    rows=[]; maxrows=[]
    for d in NULL_DRAW_IDS:
        base=sampled[int(d)].copy()
        for rep in range(NULL_REPS):
            perm=base.copy()
            for a,idx in apos.items():
                vals=base[idx].copy(); perm[idx]=vals[rng.permutation(len(vals))]
            memb=[ids_for_year_array(perm,w) for w in WIN20]
            for mode in MODES:
                states=[build_state(stats,ids,mode) for ids in memb]
                rvals=[]
                for li,ri,tc in TRANS:
                    L,R,npers=compare_states(stats,states[li],states[ri]); rvals.append(R)
                    rows.append({'variant':variant,'draw':int(d),'rep':rep,'transition_center':tc,'mode':mode,
                                 'rewiring_cosine':R,'lexical_turnover':L,'n_persistent_concepts':npers})
                maxrows.append({'variant':variant,'draw':int(d),'rep':rep,'mode':mode,'max_rewiring':float(np.nanmax(rvals))})
    return pd.DataFrame(rows),pd.DataFrame(maxrows)

n1_tables=[]; n2_tables=[]; n2max_tables=[]
for v,stats in variant_stats.items():
    print('Running Phase-18 N1:',v)
    n1_tables.append(run_n1(v,stats))
    print('Running Phase-18 N2:',v)
    n2,n2mx=run_n2(v,stats); n2_tables.append(n2); n2max_tables.append(n2mx)
n1_draws=pd.concat(n1_tables,ignore_index=True); n2_draws=pd.concat(n2_tables,ignore_index=True); n2_max=pd.concat(n2max_tables,ignore_index=True)

def summarize_null(null_df,observed_df,label):
    rows=[]
    for (v,tc,mode),q in null_df.groupby(['variant','transition_center','mode'],sort=True):
        obs=float(observed_df[(observed_df.variant.eq(v))&(observed_df.transition_center.eq(tc))&(observed_df['mode'].eq(mode))].rewiring_median.iloc[0])
        vals=q.rewiring_cosine.dropna().to_numpy(float); n=len(vals); assert n==2000,(label,v,tc,mode,n)
        rows.append({
            'null_model':label,'variant':v,'transition_center':float(tc),'mode':mode,'n_null':n,'observed_rewiring':obs,
            'null_median':float(np.median(vals)),'null_q90':float(np.quantile(vals,.90)),'null_q95':float(np.quantile(vals,.95)),'null_q99':float(np.quantile(vals,.99)),
            'observed_minus_null_median':obs-float(np.median(vals)),
            'observed_percentile':float(100*np.mean(vals<=obs)),
            'empirical_tail_p':float((1+np.sum(vals>=obs))/(1+n)),
        })
    return pd.DataFrame(rows)

n1_summary=summarize_null(n1_draws,observed_trajectory,'N1')
n2_summary=summarize_null(n2_draws,observed_trajectory,'N2')

n2max_rows=[]
for (v,mode),q in n2_max.groupby(['variant','mode'],sort=True):
    vals=q.max_rewiring.dropna().to_numpy(float); assert len(vals)==2000
    for tc in sorted(observed_trajectory[observed_trajectory.variant.eq(v)].transition_center.unique()):
        obs=float(observed_trajectory[(observed_trajectory.variant.eq(v))&(observed_trajectory.transition_center.eq(tc))&(observed_trajectory['mode'].eq(mode))].rewiring_median.iloc[0])
        n2max_rows.append({'variant':v,'mode':mode,'transition_center':float(tc),'n_null_trajectories':len(vals),'observed_rewiring':obs,
            'null_max_median':float(np.median(vals)),'null_max_q95':float(np.quantile(vals,.95)),
            'observed_max_percentile':float(100*np.mean(vals<=obs)),
            'max_stat_tail_p':float((1+np.sum(vals>=obs))/(1+len(vals)))})
n2_max_summary=pd.DataFrame(n2max_rows)

# -----------------------------------------------------------------------------
# 5. Exact Phase-15 mechanism under the two fixed identities
# -----------------------------------------------------------------------------
LEFT=(1580,1599); RIGHT=(1585,1604)
left_members=[tuple(sorted(ids_array[((sampled[d]>=LEFT[0])&(sampled[d]<=LEFT[1]))].tolist())) for d in range(MC_DRAWS)]
right_members=[tuple(sorted(ids_array[((sampled[d]>=RIGHT[0])&(sampled[d]<=RIGHT[1]))].tolist())) for d in range(MC_DRAWS)]
mechanism_rows=[]; contribution_tables={}
for variant,stats in variant_stats.items():
    for mode in MODES:
        ne=len(stats['pairs']); contrib=np.zeros(ne,float); birth=np.zeros(ne,float); death=np.zeros(ne,float); shared=np.zeros(ne,float); Rs=[]
        for d in range(MC_DRAWS):
            a=build_state(stats,left_members[d],mode); b=build_state(stats,right_members[d],mode)
            persistent=a['active']&b['active']; keep=persistent[stats['ei']]&persistent[stats['ej']]
            wl=np.where(keep,a['w'],0.0); wr=np.where(keep,b['w'],0.0)
            nl=float(np.linalg.norm(wl)); nr=float(np.linalg.norm(wr)); assert nl>0 and nr>0
            x=wl/nl; y=wr/nr; c=.5*(x-y)**2; R=float(c.sum())
            assert abs(R-(1.0-float(np.dot(x,y))))<1e-10
            Rs.append(R); contrib+=c
            birth+=np.where(keep&(x==0)&(y>0),c,0.0)
            death+=np.where(keep&(x>0)&(y==0),c,0.0)
            shared+=np.where(keep&(x>0)&(y>0),c,0.0)
        exp=contrib/MC_DRAWS; meanR=float(np.mean(Rs)); vals=np.sort(exp)[::-1]
        assert abs(float(exp.sum())-meanR)<1e-8
        mechanism_rows.append({
            'variant':variant,'mode':mode,'mean_rewiring':meanR,'median_rewiring':float(np.median(Rs)),
            'birth_share':float(birth.sum()/MC_DRAWS/meanR),'death_share':float(death.sum()/MC_DRAWS/meanR),
            'shared_reweight_share':float(shared.sum()/MC_DRAWS/meanR),
            'top1_edge_share':float(vals[:1].sum()/meanR),'top5_edge_share':float(vals[:5].sum()/meanR),
            'top10_edge_share':float(vals[:10].sum()/meanR),'top20_edge_share':float(vals[:20].sum()/meanR),
        })
        if mode=='author_balanced':
            contribution_tables[variant]=pd.DataFrame({
                'edge_index':np.arange(ne,dtype=int),
                'concept_u':[p[0] for p in stats['pairs']],
                'concept_v':[p[1] for p in stats['pairs']],
                'expected_contribution':exp,
                'expected_birth_contribution':birth/MC_DRAWS,
                'expected_death_contribution':death/MC_DRAWS,
                'expected_shared_reweight_contribution':shared/MC_DRAWS,
            }).sort_values(['expected_contribution','concept_u','concept_v'],ascending=[False,True,True]).reset_index(drop=True)
mechanism_summary18=pd.DataFrame(mechanism_rows)

# -----------------------------------------------------------------------------
# 6. Diffuseness: fixed 50% / 80% expected-contribution slices
# -----------------------------------------------------------------------------
def coverage_prefix(df,target,total):
    q=df[df.expected_contribution>0].copy(); q['share']=q.expected_contribution/total; q['cum']=q.share.cumsum()
    k=int(np.searchsorted(q['cum'].to_numpy(float),target,side='left'))+1; k=min(k,len(q)); return q.iloc[:k].copy()

def coverage_row(variant,df,target,total):
    q=coverage_prefix(df,target,total); G=nx.Graph()
    for r in q.itertuples(index=False): G.add_edge(r.concept_u,r.concept_v,weight=float(r.expected_contribution))
    comps=[set(c) for c in nx.connected_components(G)] if G.number_of_nodes() else []
    comps.sort(key=lambda c:(-len(c),sorted(c)[0]))
    lcc=comps[0] if comps else set(); lcc_contrib=0.0
    if lcc:
        lcc_contrib=float(q[q.concept_u.isin(lcc)&q.concept_v.isin(lcc)].expected_contribution.sum())
    slice_total=float(q.expected_contribution.sum())
    return {
        'variant':variant,'coverage_target':target,'coverage_actual':slice_total/total,'n_edges':int(len(q)),'n_concepts':int(G.number_of_nodes()),
        'n_components':int(len(comps)),'largest_component_n_concepts':int(len(lcc)),
        'largest_component_node_share':float(len(lcc)/G.number_of_nodes()) if G.number_of_nodes() else np.nan,
        'largest_component_contribution_share_of_slice':float(lcc_contrib/slice_total) if slice_total>0 else np.nan,
    }

coverage_rows=[]
for v,edf in contribution_tables.items():
    total=float(mechanism_summary18[(mechanism_summary18.variant.eq(v))&(mechanism_summary18['mode'].eq('author_balanced'))].mean_rewiring.iloc[0])
    for target in [.50,.80]: coverage_rows.append(coverage_row(v,edf,target,total))
coverage_summary18=pd.DataFrame(coverage_rows)

# -----------------------------------------------------------------------------
# 7. Pre-specified A/B/C classification and contradiction flags
# -----------------------------------------------------------------------------
criteria_rows=[]; envelope=(1592.0,1604.5)
for v in VARIANTS:
    tr=trajectory_comparison[(trajectory_comparison.variant.eq(v))&(trajectory_comparison['mode'].eq('author_balanced'))].iloc[0]
    mech=mechanism_summary18[(mechanism_summary18.variant.eq(v))&(mechanism_summary18['mode'].eq('author_balanced'))].iloc[0]
    cov=coverage_summary18[(coverage_summary18.variant.eq(v))&(coverage_summary18.coverage_target.eq(.80))].iloc[0]
    c1=bool(tr.spearman_rho_vs_benchmark>=.70)
    c2=bool(envelope[0]<=tr.peak_transition_center<=envelope[1])
    c3=bool(tr.rank_1592_among_8<=3)
    c4=bool(mech.birth_share+mech.death_share>=.80)
    c5=bool((cov.n_components>1)&(cov.largest_component_contribution_share_of_slice<.80))
    ncrit=int(sum([c1,c2,c3,c4,c5])); all5=ncrit==5
    n1z=n1_summary[(n1_summary.variant.eq(v))&(n1_summary['mode'].eq('author_balanced'))&(n1_summary.transition_center.eq(1592.0))].iloc[0]
    n2z=n2_max_summary[(n2_max_summary.variant.eq(v))&(n2_max_summary['mode'].eq('author_balanced'))&(n2_max_summary.transition_center.eq(1592.0))].iloc[0]
    flags=[]
    if n1z.observed_percentile>=95: flags.append('N1_percentile_ge_95')
    if n2z.observed_max_percentile>=95: flags.append('N2_max_percentile_ge_95')
    if mech.shared_reweight_share>max(mech.birth_share,mech.death_share): flags.append('shared_reweight_dominant')
    if cov.n_components==1 and cov.largest_component_contribution_share_of_slice>=.80: flags.append('coverage80_collapsed')
    if not c2: flags.append('peak_outside_phase14_envelope')
    criteria_rows.append({'variant':v,'rho_ge_0_70':c1,'peak_in_envelope':c2,'rank1592_top3':c3,'birth_plus_death_ge_0_80':c4,
                          'coverage80_diffuse':c5,'n_criteria_met':ncrit,'meets_all_five':all5,'contradiction_flags':'|'.join(flags) if flags else ''})
criteria=pd.DataFrame(criteria_rows)
all_count=int(criteria.meets_all_five.sum())
if all_count==2: robustness_class='A_strong_representation_robustness'
elif all_count==1 or bool((criteria.n_criteria_met>=3).all()): robustness_class='B_partial_representation_robustness'
else: robustness_class='C_representation_fragility'

# -----------------------------------------------------------------------------
# 8. Serialize
# -----------------------------------------------------------------------------
OUT=Path('/content/gasr_phase18_outputs'); OUT.mkdir(exist_ok=True)
representation_specification.to_csv(OUT/'phase18_representation_specification.csv',index=False)
observed_trajectory_all.to_csv(OUT/'phase18_observed_trajectory.csv',index=False)
trajectory_comparison.to_csv(OUT/'phase18_trajectory_comparison.csv',index=False)
n1_summary.to_csv(OUT/'phase18_n1_summary.csv',index=False)
n2_summary.to_csv(OUT/'phase18_n2_summary.csv',index=False)
n2_max_summary.to_csv(OUT/'phase18_n2_max_summary.csv',index=False)
mechanism_summary18.to_csv(OUT/'phase18_mechanism_summary.csv',index=False)
coverage_summary18.to_csv(OUT/'phase18_coverage_summary.csv',index=False)
criteria.to_csv(OUT/'phase18_preregistered_criteria.csv',index=False)

checkpoint={
    'phase':18,'status':'nlp_representation_robustness','robustness_class':robustness_class,
    'chronology_draws':MC_DRAWS,'null_draws':len(NULL_DRAW_IDS),'null_reps':NULL_REPS,'null_realizations_per_transition':len(NULL_DRAW_IDS)*NULL_REPS,
    'historical_markers_used_in_computation':False,'manual_lemma_corrections_used':False,'representation_search_after_results':False,
    'phase13_16_inference_reopened':False,'variants':{}
}
for v in VARIANTS:
    tr=trajectory_comparison[(trajectory_comparison.variant.eq(v))&(trajectory_comparison['mode'].eq('author_balanced'))].iloc[0]
    mech=mechanism_summary18[(mechanism_summary18.variant.eq(v))&(mechanism_summary18['mode'].eq('author_balanced'))].iloc[0]
    cov=coverage_summary18[(coverage_summary18.variant.eq(v))&(coverage_summary18.coverage_target.eq(.80))].iloc[0]
    n1z=n1_summary[(n1_summary.variant.eq(v))&(n1_summary['mode'].eq('author_balanced'))&(n1_summary.transition_center.eq(1592.0))].iloc[0]
    n2z=n2_max_summary[(n2_max_summary.variant.eq(v))&(n2_max_summary['mode'].eq('author_balanced'))&(n2_max_summary.transition_center.eq(1592.0))].iloc[0]
    cr=criteria[criteria.variant.eq(v)].iloc[0]
    checkpoint['variants'][v]={
        'vocab_size':int(representation_specification[representation_specification.variant.eq(v)].vocab_size.iloc[0]),
        'rho_vs_benchmark':float(tr.spearman_rho_vs_benchmark),'peak_center':float(tr.peak_transition_center),'rank_1592':int(tr.rank_1592_among_8),
        'rewiring_1592':float(tr.rewiring_at_1592),'birth_share':float(mech.birth_share),'death_share':float(mech.death_share),'shared_reweight_share':float(mech.shared_reweight_share),
        'coverage80_components':int(cov.n_components),'coverage80_lcc_contribution_share':float(cov.largest_component_contribution_share_of_slice),
        'n1_1592_percentile':float(n1z.observed_percentile),'n1_1592_tail_p':float(n1z.empirical_tail_p),
        'n2max_1592_percentile':float(n2z.observed_max_percentile),'n2max_1592_tail_p':float(n2z.max_stat_tail_p),
        'criteria_met':int(cr.n_criteria_met),'contradiction_flags':str(cr.contradiction_flags),
    }
(OUT/'phase18_checkpoint.json').write_text(json.dumps(checkpoint,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

print('\nREPRESENTATION ROBUSTNESS CHECKPOINT')
print('-------------------')
print(json.dumps(checkpoint,indent=2,ensure_ascii=False))
print('\nREPRESENTATION SPECIFICATION')
print(representation_specification.to_string(index=False))
print('\nTRAJECTORY COMPARISON')
print(trajectory_comparison.to_string(index=False))
print('\nN1 AT FROZEN 1592')
print(n1_summary[n1_summary.transition_center.eq(1592.0)].to_string(index=False))
print('\nN2 / MAX AT FROZEN 1592')
print(n2_summary[n2_summary.transition_center.eq(1592.0)].to_string(index=False))
print(n2_max_summary[n2_max_summary.transition_center.eq(1592.0)].to_string(index=False))
print('\nMECHANISM SUMMARY')
print(mechanism_summary18.to_string(index=False))
print('\nCOVERAGE SUMMARY')
print(coverage_summary18.to_string(index=False))
print('\nPREREGISTERED CRITERIA')
print(criteria.to_string(index=False))
print('\nPHASE 18 ROBUSTNESS CLASS:',robustness_class)
print('PHASE 18 OUTPUTS SERIALIZED:',OUT)
print('PHASE 18 COMPUTATION COMPLETE: TRUE')
