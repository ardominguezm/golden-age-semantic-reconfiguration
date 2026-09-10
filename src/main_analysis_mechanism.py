# Main temporal analysis, historical overlay, and semantic mechanism
# Historical markers and literary-stage labels are introduced only after the semantic trajectory has been constructed.

import sys, subprocess, hashlib, urllib.request, re, shutil, unicodedata, math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from difflib import SequenceMatcher
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from scipy.sparse import csr_matrix
from scipy.stats import spearmanr

# -----------------------------------------------------------------------------
# 0. Frozen environment and pinned public sources
# -----------------------------------------------------------------------------
SPACY_VERSION='3.8.7'; MODEL_NAME='es_core_news_sm'; MODEL_VERSION='3.8.0'
MODEL_URL='https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.8.0/es_core_news_sm-3.8.0-py3-none-any.whl'
MODEL_SHA256='e451a83d6df79b87e9eed0cb553f03e99e36a3bab18a7b79f0dcfd1fdf875e12'
wheel=Path('/content/es_core_news_sm-3.8.0-py3-none-any.whl')
if not wheel.exists() or hashlib.sha256(wheel.read_bytes()).hexdigest()!=MODEL_SHA256:
    urllib.request.urlretrieve(MODEL_URL,wheel)
assert hashlib.sha256(wheel.read_bytes()).hexdigest()==MODEL_SHA256
subprocess.run([sys.executable,'-m','pip','install','-q',f'spacy=={SPACY_VERSION}',str(wheel)],check=True)
import spacy
assert spacy.__version__==SPACY_VERSION
nlp=spacy.load(MODEL_NAME,disable=['parser','ner'])
assert nlp.meta.get('version')==MODEL_VERSION

SOURCES={
 'navarro_tei':('https://github.com/bncolorado/CorpusSonetosSigloDeOro.git','092a5fe70a4065a4d84bfed288bffd3851348f9c'),
 'gongora_scholarly':('https://github.com/gongoradigital/gongoraobra.git','3beadeecc059a7cc48499dc2683bb378a2630978'),
}
ROOT=Path('/content/gasr_phase15_sources'); ROOT.mkdir(exist_ok=True)
def clone(name,url,commit):
    dst=ROOT/name
    if dst.exists(): shutil.rmtree(dst)
    subprocess.run(['git','clone','--quiet',url,str(dst)],check=True)
    subprocess.run(['git','-C',str(dst),'checkout','--quiet',commit],check=True)
    got=subprocess.check_output(['git','-C',str(dst),'rev-parse','HEAD'],text=True).strip()
    assert got==commit,(name,got,commit)
    return dst
paths={k:clone(k,*v) for k,v in SOURCES.items()}
N=paths['navarro_tei']; G=paths['gongora_scholarly']
XML_ID='{http://www.w3.org/XML/1998/namespace}id'
def local(tag): return tag.split('}')[-1] if '}' in tag else tag
def el_text(el): return '' if el is None else ' '.join(' '.join(el.itertext()).split())
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s.lower())
def years_1580_1626(s):
    return sorted(set(int(x) for x in re.findall(r'(?<!\d)(1[56]\d{2})(?!\d)',str(s)) if 1580<=int(x)<=1626))
print('Main analysis environment and pinned sources ready')

# -----------------------------------------------------------------------------
# 1. Reconstruct the 97-sonnet dated sample
# -----------------------------------------------------------------------------
rows=[]
for fp in sorted(N.rglob('*.xml')):
    root=ET.parse(fp).getroot(); lines=[el_text(x) for x in root.iter() if local(x.tag)=='l']; lines=[x for x in lines if x]
    if not lines: continue
    author=fp.parent.name; txt='\n'.join(lines)
    rows.append({'n_id':f'{author}::{fp.name}','author_dir':author,'n_lines':len(lines),'lines':lines,
                 'text_tei':txt,'signature':norm(txt),'first2_signature':norm('\n'.join(lines[:2]))})
n=pd.DataFrame(rows); assert len(n)==5078
primary_rows=[]
def add(pid,author,lo,hi,confidence,basis):
    primary_rows.append({'n_id':pid,'author_dir':author,'composition_min':int(lo),'composition_max':int(hi),
                         'temporal_confidence':confidence,'temporal_basis':basis})

groot=ET.parse(G/'gongora_obra-poetica.xml').getroot(); parent={child:par for par in groot.iter() for child in par}; grows=[]
for el in groot.iter():
    xid=el.attrib.get(XML_ID,'')
    if local(el.tag)!='div' or not xid.lower().startswith('poem'): continue
    lines=[el_text(x) for x in el.iter() if local(x.tag)=='l']; lines=[x for x in lines if x]
    if not lines: continue
    vals=[]; cur=el
    for _ in range(6):
        vals+=list(cur.attrib.values())
        if cur.text: vals.append(cur.text)
        for ch in list(cur):
            if local(ch.tag) in {'head','date','label'}: vals.append(el_text(ch))
            if ch.tail: vals.append(ch.tail)
        cur=parent.get(cur)
        if cur is None: break
    ys=sorted(set(y for v in vals for y in years_1580_1626(v))); txt='\n'.join(lines)
    grows.append({'g_id':xid,'n_lines':len(lines),'signature':norm(txt),'first2_signature':norm('\n'.join(lines[:2])),
                  'scholarly_year':ys[0] if len(ys)==1 else pd.NA,
                  'year_status':'unique' if len(ys)==1 else ('ambiguous' if len(ys)>1 else 'missing')})
g=pd.DataFrame(grows); g14=g[(g.n_lines==14)&g.signature.ne('')].copy(); g_by_id=g.set_index('g_id',drop=False)
ng=n[n.author_dir.eq('Gongora')].copy(); sig_to_gids=g14.groupby('signature').g_id.apply(list).to_dict(); links=[]
for r in ng.itertuples(index=False):
    exact_ids=sig_to_gids.get(r.signature,[])
    if len(exact_ids)==1: gid,score,method=exact_ids[0],1.0,'exact'
    else:
        best_gid,best_score=None,-1.0
        for gr in g14.itertuples(index=False):
            sc=SequenceMatcher(None,r.signature,gr.signature).ratio()
            if sc>best_score: best_gid,best_score=gr.g_id,sc
        gid,score,method=best_gid,best_score,'fuzzy'
    links.append({'n_id':r.n_id,'g_id':gid,'method':method,'score':float(score),'preaccept':method=='exact' or score>=0.98})
glink=pd.DataFrame(links); pre=glink[glink.preaccept].copy(); collisions=set(pre.g_id.value_counts()[lambda s:s>1].index)
glink['accept_phase4']=glink.preaccept&~glink.g_id.isin(collisions)
acc=glink[glink.accept_phase4].merge(g[['g_id','scholarly_year','year_status']],on='g_id',how='left')
acc=acc[acc.year_status.eq('unique')&acc.scholarly_year.notna()].copy()
for r in acc.itertuples(index=False):
    add(r.n_id,'Gongora',r.scholarly_year,r.scholarly_year,'A' if r.method=='exact' else 'B',
        'scholarly_chronology_year_exact_link' if r.method=='exact' else 'scholarly_chronology_year_fuzzy_link')
phase4_nids=set(acc.n_id); phase4_gids=set(acc.g_id); unmatched=ng[~ng.n_id.isin(phase4_nids)].copy()
first2_index=g14.groupby('first2_signature').g_id.apply(list).to_dict(); recovered=[]
for r in unmatched.itertuples(index=False):
    ids2=first2_index.get(r.first2_signature,[])
    if len(ids2)!=1: continue
    gid=ids2[0]
    if gid in phase4_gids: continue
    gr=g_by_id.loc[gid]; score=SequenceMatcher(None,r.signature,gr.signature).ratio()
    if score>=0.95 and gr.year_status=='unique' and pd.notna(gr.scholarly_year): recovered.append((r.n_id,gid,score,int(gr.scholarly_year)))
rec=pd.DataFrame(recovered,columns=['n_id','g_id','score','year']); dup=set(rec.g_id.value_counts()[lambda s:s>1].index) if len(rec) else set(); rec=rec[~rec.g_id.isin(dup)]
for r in rec.itertuples(index=False): add(r.n_id,'Gongora',r.year,r.year,'B','scholarly_chronology_year_variant_link')
assert sum(x['author_dir']=='Gongora' for x in primary_rows)==58

GAR={**{i:(1526,1532,'B','scholarly_phase_interval') for i in [1,2,3,4,6,26,27]},25:(1534,1535,'B','scholarly_interval'),
     33:(1535,1535,'A','historically_anchored_scholarly_year'),35:(1535,1535,'A','historically_anchored_scholarly_year'),
     **{i:(1533,1535,'B','revised_scholarly_interval') for i in [7,8,12,15,19,28,30,31]}}
for no,(lo,hi,conf,basis) in GAR.items(): add(f'GarcilasoDeLaVega::GarcilasoDeLaVega_{no:02d}.xml','GarcilasoDeLaVega',lo,hi,conf,basis)
for no,lo,hi,conf,basis in [(30,1596,1596,'B','Cadiz_1596'),(13,1598,1598,'A','FelipeII_tomb_1598'),(31,1597,1598,'B','Herrera_death_epitaph')]: add(f'Cervantes::Cervantes_{no}.xml','Cervantes',lo,hi,conf,basis)
for no,lo,hi,basis in [(224,1574,1574,'Alameda_CarlosV'),(279,1578,1579,'Barahona_Granada'),(276,1573,1574,'Bazan_Tunis'),(300,1580,1582,'Portugal_to_H'),(281,1578,1578,'DonJuan_de_Austria')]: add(f'FernandoDeHerrera::FernandoDeHerrera_{no}.xml','FernandoDeHerrera',lo,hi,'B',basis)
for no in [2,19,4,5]: add(f'PedroEspinosa::PedroEspinosa_{no}.xml','PedroEspinosa',1594,1596,'B','Espinosa_happiness_period_1594_1596')
for no,year,basis in [(131,1609,'Carrillo_sonnet_1609'),(69,1611,'Aminta_1611'),(70,1611,'Aminta_1611'),(72,1611,'Aminta_1611'),(76,1611,'Aminta_1611'),(42,1610,'HenryIV_1610'),(43,1610,'HenryIV_1610'),(45,1610,'HenryIV_1610'),(44,1624,'Osuna_1624')]: add(f'Quevedo::Quevedo_{no}.xml','Quevedo',year,year,'B',basis)
primary=pd.DataFrame(primary_rows).drop_duplicates('n_id').copy()
expected={'Gongora':58,'GarcilasoDeLaVega':18,'Quevedo':9,'FernandoDeHerrera':5,'PedroEspinosa':4,'Cervantes':3}
assert len(primary)==97 and primary.groupby('author_dir').size().to_dict()==expected
primary=primary.merge(n[['n_id','text_tei','lines','n_lines','signature']],on='n_id',how='left',validate='one_to_one'); assert primary.text_tei.notna().all()
print('FROZEN PRIMARY CHRONOLOGY REPRODUCED:',len(primary),'poems |',primary.author_dir.nunique(),'authors')

# -----------------------------------------------------------------------------
# 2. External literary labels — overlay only, never used in semantic construction
# -----------------------------------------------------------------------------
AUX_CLASSIFICATION_BLOB_SHA='b24456db2fc1925cef57f6b69df040d2217f1ba6'
STAGE={
 'GarcilasoDeLaVega':'Innovation',
 'FernandoDeHerrera':'Renovation',
 'Cervantes':'Transition',
 'PedroEspinosa':'Transition',
 'Gongora':'Culmination',
 'Quevedo':'Baroque',
}
MOVEMENT={
 'GarcilasoDeLaVega':'Renaissance','FernandoDeHerrera':'Renaissance',
 'Cervantes':'Baroque','PedroEspinosa':'Baroque','Gongora':'Baroque','Quevedo':'Baroque',
}
assert set(primary.author_dir.unique())==set(STAGE)==set(MOVEMENT)
primary['literary_stage']=primary.author_dir.map(STAGE); primary['movement']=primary.author_dir.map(MOVEMENT)
print('External literary overlay attached only after semantic design freeze | local classification blob:',AUX_CLASSIFICATION_BLOB_SHA)

# -----------------------------------------------------------------------------
# 3. Frozen NLP and line-context semantic network
# -----------------------------------------------------------------------------
MAIN_POS={'NOUN','VERB','ADJ','ADV'}; MIN_LEMMA_LEN=2
flat=[]
for r in primary.itertuples(index=False):
    for line_no,line in enumerate(r.lines,1): flat.append((r.n_id,line_no,line))
docs=list(nlp.pipe([x[2] for x in flat],batch_size=128))
line_units={r.n_id:[set() for _ in r.lines] for r in primary.itertuples(index=False)}; records=[]
for (pid,line_no,_),doc in zip(flat,docs):
    cs=[]
    for tok in doc:
        lemma=unicodedata.normalize('NFC',str(tok.lemma_)).strip().lower(); pos=tok.pos_
        if tok.is_alpha and pos in MAIN_POS and len(lemma)>=MIN_LEMMA_LEN:
            c=f'{lemma}::{pos}'; cs.append(c); records.append((pid,c))
    line_units[pid][line_no-1]=set(cs)
concept_poems=defaultdict(set)
for pid,c in records: concept_poems[c].add(pid)
VOCAB={c for c,pids in concept_poems.items() if len(pids)>=2}; assert len(VOCAB)==668,len(VOCAB)

author_lookup=dict(zip(primary.n_id,primary.author_dir)); FULL_PIDS=list(primary.n_id)
def prepare_stats(pids,units_by_poem,vocab):
    concepts=sorted(vocab); cidx={c:i for i,c in enumerate(concepts)}; pair_keys=set()
    for pid in pids:
        for unit in units_by_poem[pid]:
            cs=sorted(c for c in unit if c in cidx); pair_keys.update(combinations(cs,2))
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
    ei=np.asarray([cidx[a] for a,b in pairs],dtype=np.int32); ej=np.asarray([cidx[b] for a,b in pairs],dtype=np.int32)
    return {'pids':pids,'pidrow':{p:i for i,p in enumerate(pids)},'concepts':concepts,'cidx':cidx,'pairs':pairs,'pidx':pidx,
            'M':M,'U':U,'P':P,'ei':ei,'ej':ej,'authors':np.asarray([author_lookup[p] for p in pids],dtype=object)}
STATS=prepare_stats(FULL_PIDS,line_units,VOCAB)
print('Frozen semantic vocabulary/network representation reproduced:',len(STATS['concepts']),'concepts |',len(STATS['pairs']),'global observed line-pairs')

def build_state(ids,mode):
    rows=np.asarray([STATS['pidrow'][p] for p in ids],dtype=int); nv=len(STATS['concepts']); ne=len(STATS['pairs'])
    if len(rows)==0: return {'active':np.zeros(nv,bool),'w':np.zeros(ne,float)}
    U=STATS['U'][rows].astype(float); authors=STATS['authors'][rows]
    if mode=='raw': factors=np.ones(len(rows),float)
    else:
        ac=Counter(authors.tolist()); factors=np.asarray([1.0/(ac[a]*u) if u>0 else 0.0 for a,u in zip(authors,U)],float)
    T=float(np.dot(factors,U)); assert T>0
    marg=(STATS['M'][rows].astype(float)*factors[:,None]).sum(axis=0)
    pairmass=np.asarray(STATS['P'][rows].multiply(factors[:,None]).sum(axis=0)).ravel().astype(float)
    support=np.asarray(STATS['P'][rows].sum(axis=0)).ravel(); active=marg>0; w=np.zeros(ne,float)
    valid=(support>=1)&(pairmass>0)
    if np.any(valid):
        ei=STATS['ei'][valid]; ej=STATS['ej'][valid]; pm=pairmass[valid]
        denom=(marg[ei]/T)*(marg[ej]/T); ratio=(pm/T)/denom
        vals=np.maximum(0.0,np.log2(ratio)); w[np.flatnonzero(valid)]=vals
    return {'active':active,'w':w}

def compare_states(a,b):
    persistent=a['active']&b['active']; union=a['active']|b['active']; nu=int(union.sum()); npers=int(persistent.sum())
    L=np.nan if nu==0 else 1.0-npers/nu
    keep=persistent[STATS['ei']]&persistent[STATS['ej']]
    w1=np.where(keep,a['w'],0.0); w2=np.where(keep,b['w'],0.0)
    n1=float(np.linalg.norm(w1)); n2=float(np.linalg.norm(w2))
    R=np.nan if n1==0 or n2==0 else 1.0-float(np.dot(w1,w2)/(n1*n2))
    return L,R,npers

# -----------------------------------------------------------------------------
# 4. Frozen chronology draws and main 20-year trajectory
# -----------------------------------------------------------------------------
SEED=20260825; MC_DRAWS=1000; MODES=['author_balanced','raw']
ids_array=primary.n_id.to_numpy(object); pidcol={p:i for i,p in enumerate(ids_array)}
lo=primary.composition_min.to_numpy(int); hi=primary.composition_max.to_numpy(int)
rng_dates=np.random.default_rng(SEED); sampled=np.empty((MC_DRAWS,len(primary)),dtype=int)
for j,(a,b) in enumerate(zip(lo,hi)): sampled[:,j]=a if a==b else rng_dates.integers(a,b+1,size=MC_DRAWS)
WIN20=[(s,s+19) for s in range(1565,1606,5)]
def center(w): return (w[0]+w[1])/2.0
def trans_center(a,b): return (center(a)+center(b))/2.0
TRANS=[(i,i+1,trans_center(WIN20[i],WIN20[i+1])) for i in range(len(WIN20)-1)]
def window_ids(draw,win):
    mask=(sampled[draw]>=win[0])&(sampled[draw]<=win[1]); return tuple(sorted(ids_array[mask].tolist()))
memberships=[[window_ids(d,w) for w in WIN20] for d in range(MC_DRAWS)]
unique_ids=sorted(set(x for row in memberships for x in row)); state_cache={}
for ids in unique_ids:
    for mode in MODES: state_cache[(ids,mode)]=build_state(ids,mode)
traj_rows=[]
for d in range(MC_DRAWS):
    for li,ri,tc in TRANS:
        for mode in MODES:
            L,R,npers=compare_states(state_cache[(memberships[d][li],mode)],state_cache[(memberships[d][ri],mode)])
            traj_rows.append({'draw':d,'transition_center':tc,'mode':mode,'lexical_turnover':L,'rewiring_cosine':R,'n_persistent_concepts':npers})
trajectory=pd.DataFrame(traj_rows)
summary_rows=[]
for (tc,mode),q in trajectory.groupby(['transition_center','mode'],sort=True):
    summary_rows.append({'transition_center':tc,'mode':mode,
        'rewiring_median':float(np.median(q.rewiring_cosine)),'rewiring_q10':float(np.quantile(q.rewiring_cosine,.1)),'rewiring_q90':float(np.quantile(q.rewiring_cosine,.9)),
        'lexical_turnover_median':float(np.median(q.lexical_turnover)),'persistent_concepts_median':float(np.median(q.n_persistent_concepts))})
traj_summary=pd.DataFrame(summary_rows).sort_values(['mode','transition_center'])
for mode,expected_val in [('author_balanced',0.233746),('raw',0.224870)]:
    z=traj_summary[(traj_summary['mode']==mode)&(traj_summary.transition_center.eq(1592.0))].iloc[0]
    assert abs(z.rewiring_median-expected_val)<5e-6,(mode,z.rewiring_median)
print('Benchmark trajectory reproduced before historical overlay: TRUE')

# -----------------------------------------------------------------------------
# 5. External marker alignment — descriptive only
# -----------------------------------------------------------------------------
MARKERS=[1580.0,1605.0]; ENVELOPE=(1592.0,1604.5); WIDTH_PEAKS={'15y':1604.5,'20y':1592.0,'25y':1594.5}
def dist_to_interval(x,a,b): return a-x if x<a else (x-b if x>b else 0.0)
marker_rows=[]
for mode in MODES:
    q=traj_summary[traj_summary['mode'].eq(mode)].sort_values('transition_center'); xs=q.transition_center.to_numpy(float); ys=q.rewiring_median.to_numpy(float)
    for m in MARKERS:
        left_i=np.max(np.flatnonzero(xs<=m)); right_i=np.min(np.flatnonzero(xs>=m))
        if left_i==right_i:
            li=max(0,left_i-1); ri=min(len(xs)-1,right_i+1)
        else: li,ri=left_i,right_i
        interp=float(np.interp(m,xs,ys)); pct=float(100*np.mean(ys<=interp))
        marker_rows.append({'marker':m,'mode':mode,'left_center':xs[li],'left_rewiring':ys[li],'right_center':xs[ri],'right_rewiring':ys[ri],
                            'interpolated_rewiring':interp,'descriptive_percentile_among_8':pct,
                            'distance_to_phase14_envelope':dist_to_interval(m,*ENVELOPE),'envelope_start':ENVELOPE[0],'envelope_end':ENVELOPE[1]})
marker_alignment=pd.DataFrame(marker_rows)
peakdist=[]
for m in MARKERS:
    for width,pk in WIDTH_PEAKS.items(): peakdist.append({'marker':m,'temporal_design':width,'frozen_peak_center':pk,'absolute_distance_years':abs(m-pk)})
marker_peak_distances=pd.DataFrame(peakdist)

# -----------------------------------------------------------------------------
# 6. External literary-stage mixture and transition TV
# -----------------------------------------------------------------------------
STAGES=['Innovation','Renovation','Transition','Culmination','Baroque']; MOVES=['Renaissance','Baroque']
def mixture(ids,labels,equal_author=False):
    if not ids: return {x:0.0 for x in labels}
    if equal_author:
        authors=sorted(set(author_lookup[p] for p in ids)); vals=[STAGE[a] if labels is STAGES else MOVEMENT[a] for a in authors]
    else:
        vals=[STAGE[author_lookup[p]] if labels is STAGES else MOVEMENT[author_lookup[p]] for p in ids]
    c=Counter(vals); den=sum(c.values()); return {x:c.get(x,0)/den for x in labels}
stage_rows=[]; tv_rows=[]
for d in range(MC_DRAWS):
    mix_cache={}
    for wi,w in enumerate(WIN20):
        ids=memberships[d][wi]
        for scheme,labels in [('lopez_stage',STAGES),('movement',MOVES)]:
            for weighting in ['raw_poem','equal_author']:
                mm=mixture(ids,labels,equal_author=(weighting=='equal_author')); mix_cache[(wi,scheme,weighting)]=mm
                for lab,val in mm.items(): stage_rows.append({'draw':d,'window_index':wi,'window_start':w[0],'window_end':w[1],'scheme':scheme,'weighting':weighting,'label':lab,'proportion':val})
    for li,ri,tc in TRANS:
        for scheme,labels in [('lopez_stage',STAGES),('movement',MOVES)]:
            for weighting in ['raw_poem','equal_author']:
                a=mix_cache[(li,scheme,weighting)]; b=mix_cache[(ri,scheme,weighting)]; tv=.5*sum(abs(a[x]-b[x]) for x in labels)
                tv_rows.append({'draw':d,'transition_center':tc,'scheme':scheme,'weighting':weighting,'stage_tv':tv})
stage_mix=pd.DataFrame(stage_rows); stage_tv=pd.DataFrame(tv_rows)
stage_mix_summary=(stage_mix.groupby(['window_index','window_start','window_end','scheme','weighting','label']).proportion
                   .agg(median='median',q10=lambda x:np.quantile(x,.1),q90=lambda x:np.quantile(x,.9)).reset_index())
stage_tv_summary=(stage_tv.groupby(['transition_center','scheme','weighting']).stage_tv
                  .agg(median='median',q10=lambda x:np.quantile(x,.1),q90=lambda x:np.quantile(x,.9)).reset_index())
assoc=[]
for scheme in ['lopez_stage','movement']:
    for mode,weighting in [('author_balanced','equal_author'),('raw','raw_poem')]:
        a=traj_summary[traj_summary['mode'].eq(mode)][['transition_center','rewiring_median']]
        b=stage_tv_summary[(stage_tv_summary.scheme.eq(scheme))&(stage_tv_summary.weighting.eq(weighting))][['transition_center','median']].rename(columns={'median':'stage_tv_median'})
        m=a.merge(b,on='transition_center'); rho=float(spearmanr(m.rewiring_median,m.stage_tv_median).statistic)
        assoc.append({'scheme':scheme,'semantic_mode':mode,'stage_weighting':weighting,'n_transitions':len(m),'spearman_rho_descriptive':rho,'inferential_p_used':False})
stage_assoc=pd.DataFrame(assoc)

# -----------------------------------------------------------------------------
# 7. Exact additive semantic-mechanism attribution at frozen 1592 episode
# -----------------------------------------------------------------------------
LEFT=(1580,1599); RIGHT=(1585,1604)
left_members=[window_ids(d,LEFT) for d in range(MC_DRAWS)]; right_members=[window_ids(d,RIGHT) for d in range(MC_DRAWS)]
ne=len(STATS['pairs']); nv=len(STATS['concepts'])
edge_long=[]; concept_long=[]; mechanism_rows=[]; lexical_left=np.zeros(nv,float); lexical_right=np.zeros(nv,float)
mode_edge_tables={}
for mode in MODES:
    contrib_sum=np.zeros(ne,float); elig_count=np.zeros(ne,float); delta_sum=np.zeros(ne,float); delta_elig_sum=np.zeros(ne,float)
    strengthen=np.zeros(ne,float); weaken=np.zeros(ne,float); birth_sum=np.zeros(ne,float); death_sum=np.zeros(ne,float); shared_sum=np.zeros(ne,float)
    concept_sum=np.zeros(nv,float); Rs=[]
    for d in range(MC_DRAWS):
        a=state_cache.get((left_members[d],mode)) or build_state(left_members[d],mode)
        b=state_cache.get((right_members[d],mode)) or build_state(right_members[d],mode)
        persistent=a['active']&b['active']; keep=persistent[STATS['ei']]&persistent[STATS['ej']]
        wl=np.where(keep,a['w'],0.0); wr=np.where(keep,b['w'],0.0); nl=float(np.linalg.norm(wl)); nr=float(np.linalg.norm(wr)); assert nl>0 and nr>0
        x=wl/nl; y=wr/nr; c=.5*(x-y)**2; delta=y-x; R=float(c.sum()); direct=1.0-float(np.dot(x,y)); assert abs(R-direct)<1e-10
        Rs.append(R); contrib_sum+=c; elig_count+=keep; delta_sum+=delta; delta_elig_sum+=np.where(keep,delta,0.0)
        strengthen+=keep&(delta>0); weaken+=keep&(delta<0)
        birth=(keep&(x==0)&(y>0)); death=(keep&(x>0)&(y==0)); shared=(keep&(x>0)&(y>0))
        birth_sum+=np.where(birth,c,0.0); death_sum+=np.where(death,c,0.0); shared_sum+=np.where(shared,c,0.0)
        np.add.at(concept_sum,STATS['ei'],.5*c); np.add.at(concept_sum,STATS['ej'],.5*c)
        if mode=='author_balanced': lexical_left+=a['active']; lexical_right+=b['active']
    exp=contrib_sum/MC_DRAWS; elig=elig_count/MC_DRAWS; meanR=float(np.mean(Rs)); medR=float(np.median(Rs))
    edir=np.divide(delta_elig_sum,elig_count,out=np.zeros_like(delta_elig_sum),where=elig_count>0)
    sr=np.divide(strengthen,elig_count,out=np.zeros_like(strengthen),where=elig_count>0); wrate=np.divide(weaken,elig_count,out=np.zeros_like(weaken),where=elig_count>0)
    rows=[]
    for i,(u,v) in enumerate(STATS['pairs']):
        rows.append({'mode':mode,'edge_index':i,'concept_u':u,'concept_v':v,'expected_contribution':exp[i],
                     'share_of_mean_rewiring':exp[i]/meanR if meanR>0 else np.nan,'eligibility_rate':elig[i],
                     'mean_delta_all_draws':delta_sum[i]/MC_DRAWS,'mean_delta_eligible':edir[i],
                     'strengthening_rate_eligible':sr[i],'weakening_rate_eligible':wrate[i],
                     'expected_birth_contribution':birth_sum[i]/MC_DRAWS,'expected_death_contribution':death_sum[i]/MC_DRAWS,
                     'expected_shared_reweight_contribution':shared_sum[i]/MC_DRAWS})
    edf=pd.DataFrame(rows).sort_values('expected_contribution',ascending=False).reset_index(drop=True); edf['rank']=np.arange(1,len(edf)+1)
    edf['dominant_direction']=np.where(edf.mean_delta_eligible>0,'strengthening',np.where(edf.mean_delta_eligible<0,'weakening','neutral'))
    edf['direction_consistency']=edf[['strengthening_rate_eligible','weakening_rate_eligible']].max(axis=1)
    mode_edge_tables[mode]=edf; edge_long.append(edf)
    cexp=concept_sum/MC_DRAWS; cdf=pd.DataFrame({'mode':mode,'concept':STATS['concepts'],'expected_contribution':cexp})
    cdf=cdf.sort_values('expected_contribution',ascending=False).reset_index(drop=True); cdf['rank']=np.arange(1,len(cdf)+1); cdf['share_of_mean_rewiring']=cdf.expected_contribution/meanR
    concept_long.append(cdf)
    vals=edf.expected_contribution.to_numpy(float)
    mechanism_rows.append({'mode':mode,'mean_rewiring':meanR,'median_rewiring':medR,
        'birth_share':float(birth_sum.sum()/MC_DRAWS/meanR),'death_share':float(death_sum.sum()/MC_DRAWS/meanR),'shared_reweight_share':float(shared_sum.sum()/MC_DRAWS/meanR),
        'top1_edge_share':float(vals[:1].sum()/meanR),'top5_edge_share':float(vals[:5].sum()/meanR),'top10_edge_share':float(vals[:10].sum()/meanR),'top20_edge_share':float(vals[:20].sum()/meanR)})
edge_contributors=pd.concat(edge_long,ignore_index=True); concept_contributors=pd.concat(concept_long,ignore_index=True); mechanism_summary=pd.DataFrame(mechanism_rows)

# Lexical-presence shifts, kept separate from rewiring.
pl=lexical_left/MC_DRAWS; pr=lexical_right/MC_DRAWS; da=pr-pl
lexical=pd.DataFrame({'concept':STATS['concepts'],'p_active_left':pl,'p_active_right':pr,'activity_delta':da})
lexical['direction']=np.where(lexical.activity_delta>0,'entering',np.where(lexical.activity_delta<0,'leaving','stable'))
lexical['abs_activity_delta']=lexical.activity_delta.abs(); lexical=lexical.sort_values('abs_activity_delta',ascending=False).reset_index(drop=True)
lexical['rank_abs']=np.arange(1,len(lexical)+1)

# -----------------------------------------------------------------------------
# 8. Deterministic close-reading edge selection
# -----------------------------------------------------------------------------
bal=mode_edge_tables['author_balanced'].copy(); bal['stable_direction']=(bal.eligibility_rate>=.80)&(bal.direction_consistency>=.80)
selected=[]
for direction in ['strengthening','weakening']:
    pool=bal[bal.dominant_direction.eq(direction)].sort_values('expected_contribution',ascending=False)
    stable=pool[pool.stable_direction].head(3)
    for r in stable.itertuples(index=False): selected.append((int(r.edge_index),direction,'stable_preregistered'))
    need=3-len(stable)
    if need>0:
        used={x[0] for x in selected}; fallback=pool[~pool.edge_index.isin(used)].head(need)
        for r in fallback.itertuples(index=False): selected.append((int(r.edge_index),direction,'fallback_insufficient_stable'))
close_rows=[]
for idx,direction,basis in selected:
    r=bal[bal.edge_index.eq(idx)].iloc[0]
    close_rows.append({'edge_index':idx,'balanced_rank':int(r['rank']),'concept_u':r.concept_u,'concept_v':r.concept_v,'direction':direction,'selection_basis':basis,
                       'expected_contribution':r.expected_contribution,'eligibility_rate':r.eligibility_rate,'direction_consistency':r.direction_consistency,'mean_delta_eligible':r.mean_delta_eligible})
close_edges=pd.DataFrame(close_rows).sort_values(['direction','expected_contribution'],ascending=[True,False]).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 9. Expected author support for top-20 balanced edges
# -----------------------------------------------------------------------------
top20=bal.head(20).copy(); top_idx=top20.edge_index.astype(int).to_numpy(); AUTHORS=sorted(primary.author_dir.unique())
support_acc={(side,a):np.zeros(len(top_idx),float) for side in ['left','right'] for a in AUTHORS}
for d in range(MC_DRAWS):
    for side,ids in [('left',left_members[d]),('right',right_members[d])]:
        rows=np.asarray([STATS['pidrow'][p] for p in ids],dtype=int); U=STATS['U'][rows].astype(float); authors=STATS['authors'][rows]; ac=Counter(authors.tolist())
        factors=np.asarray([1.0/(ac[a]*u) if u>0 else 0.0 for a,u in zip(authors,U)],float)
        pm=STATS['P'][rows][:,top_idx].toarray().astype(float)
        for a in AUTHORS:
            mask=(authors==a)
            if np.any(mask): support_acc[(side,a)]+=np.sum(pm[mask]*factors[mask,None],axis=0)
author_support_rows=[]
for side in ['left','right']:
    totals=np.zeros(len(top_idx),float)
    means={}
    for a in AUTHORS:
        means[a]=support_acc[(side,a)]/MC_DRAWS; totals+=means[a]
    for j,idx in enumerate(top_idx):
        er=top20.iloc[j]
        for a in AUTHORS:
            val=means[a][j]; author_support_rows.append({'edge_index':int(idx),'balanced_rank':int(er['rank']),'concept_u':er.concept_u,'concept_v':er.concept_v,
                'window_side':side,'author':a,'literary_stage':STAGE[a],'movement':MOVEMENT[a],'expected_balanced_pair_mass':val,'share_of_edge_pair_mass':val/totals[j] if totals[j]>0 else np.nan})
author_support=pd.DataFrame(author_support_rows)

# -----------------------------------------------------------------------------
# 10. Trace selected edges to every supporting verse in the primary corpus
# -----------------------------------------------------------------------------
pleft={p:float(np.mean((sampled[:,pidcol[p]]>=LEFT[0])&(sampled[:,pidcol[p]]<=LEFT[1]))) for p in FULL_PIDS}
pright={p:float(np.mean((sampled[:,pidcol[p]]>=RIGHT[0])&(sampled[:,pidcol[p]]<=RIGHT[1]))) for p in FULL_PIDS}
meta=primary.set_index('n_id')
occ=[]
for er in close_edges.itertuples(index=False):
    u,v=er.concept_u,er.concept_v
    for pid in FULL_PIDS:
        rr=meta.loc[pid]
        for line_no,(line_text,unit) in enumerate(zip(rr['lines'],line_units[pid]),1):
            if u in unit and v in unit:
                occ.append({'edge_index':er.edge_index,'balanced_rank':er.balanced_rank,'direction':er.direction,'selection_basis':er.selection_basis,
                    'concept_u':u,'concept_v':v,'n_id':pid,'author':rr.author_dir,'literary_stage':STAGE[rr.author_dir],'movement':MOVEMENT[rr.author_dir],
                    'composition_min':int(rr.composition_min),'composition_max':int(rr.composition_max),'p_left_window':pleft[pid],'p_right_window':pright[pid],
                    'line_number':line_no,'line_text':line_text})
occurrences=pd.DataFrame(occ)
if len(occurrences): occurrences=occurrences.sort_values(['balanced_rank','author','n_id','line_number'])

# -----------------------------------------------------------------------------
# 11. Exports and compact auditable checkpoint
# -----------------------------------------------------------------------------
OUT=Path('/content/gasr_phase15_outputs'); OUT.mkdir(exist_ok=True)
traj_summary.to_csv(OUT/'phase15_main_trajectory.csv',index=False)
marker_alignment.to_csv(OUT/'phase15_marker_alignment.csv',index=False); marker_peak_distances.to_csv(OUT/'phase15_marker_peak_distances.csv',index=False)
stage_mix_summary.to_csv(OUT/'phase15_stage_mix_summary.csv',index=False); stage_tv_summary.to_csv(OUT/'phase15_stage_tv_summary.csv',index=False); stage_assoc.to_csv(OUT/'phase15_stage_rewiring_association.csv',index=False)
edge_contributors.to_csv(OUT/'phase15_edge_contributors.csv',index=False); concept_contributors.to_csv(OUT/'phase15_concept_contributors.csv',index=False); mechanism_summary.to_csv(OUT/'phase15_edge_mechanism_summary.csv',index=False)
lexical.to_csv(OUT/'phase15_lexical_activity_shifts.csv',index=False); author_support.to_csv(OUT/'phase15_top_edge_author_support.csv',index=False)
close_edges.to_csv(OUT/'phase15_close_reading_edges.csv',index=False); occurrences.to_csv(OUT/'phase15_close_reading_occurrences.csv',index=False)

print('\nMAIN ANALYSIS CHECKPOINT')
print('-------------------')
print('Primary chronology:',len(primary),'poems |',primary.author_dir.nunique(),'authors')
print('Frozen 20y trajectory reproduced: TRUE')
print('1580/1605 used before the historical overlay: FALSE')
print('External literary labels used in semantic construction: FALSE')
print('Classical change point computed: FALSE')
print('Edge attribution identity sum(C_e)=R verified per draw: TRUE')
print('Close-reading edges selected without thematic/manual filtering: TRUE')
print('Historical phase-transition claim made: FALSE')
print('Outputs:',OUT)

print('\nMAIN 20Y TRAJECTORY')
print(traj_summary.sort_values(['transition_center','mode']).to_string(index=False))
print('\nEXTERNAL MARKER ALIGNMENT')
print(marker_alignment.to_string(index=False))
print('\nMARKER DISTANCE TO FROZEN WIDTH-SPECIFIC PEAKS')
print(marker_peak_distances.to_string(index=False))
print('\nSTAGE-MIX / REWIRING ASSOCIATION — DESCRIPTIVE ONLY')
print(stage_assoc.to_string(index=False))
print('\nSTAGE TV SUMMARY')
print(stage_tv_summary.sort_values(['scheme','weighting','transition_center']).to_string(index=False))
print('\nEDGE MECHANISM SUMMARY')
print(mechanism_summary.to_string(index=False))
print('\nTOP 20 AUTHOR-BALANCED EDGE CONTRIBUTORS')
print(bal.head(20)[['rank','concept_u','concept_v','expected_contribution','share_of_mean_rewiring','eligibility_rate','dominant_direction','direction_consistency','mean_delta_eligible','expected_birth_contribution','expected_death_contribution','expected_shared_reweight_contribution']].to_string(index=False))
print('\nTOP 15 AUTHOR-BALANCED CONCEPT CONTRIBUTORS')
print(concept_contributors[concept_contributors['mode'].eq('author_balanced')].head(15)[['rank','concept','expected_contribution','share_of_mean_rewiring']].to_string(index=False))
print('\nTOP 15 LEXICAL ENTERING CONCEPTS')
print(lexical[lexical.direction.eq('entering')].sort_values('activity_delta',ascending=False).head(15)[['concept','p_active_left','p_active_right','activity_delta']].to_string(index=False))
print('\nTOP 15 LEXICAL LEAVING CONCEPTS')
print(lexical[lexical.direction.eq('leaving')].sort_values('activity_delta').head(15)[['concept','p_active_left','p_active_right','activity_delta']].to_string(index=False))
print('\nPREREGISTERED CLOSE-READING EDGES')
print(close_edges.to_string(index=False))
print('\nCLOSE-READING OCCURRENCE COUNTS')
if len(occurrences):
    print(occurrences.groupby(['balanced_rank','concept_u','concept_v','direction']).size().rename('n_verse_occurrences').reset_index().to_string(index=False))
    print('\nALL CLOSE-READING VERSE OCCURRENCES')
    print(occurrences.to_string(index=False))
else:
    print('No verse occurrences found — unexpected diagnostic state')
def select_top_author_support(author_support):
    """Return the top defined author-support row per edge/window; skip all-NaN groups."""
    if author_support.empty:
        return author_support.copy()
    usable=author_support.dropna(subset=['share_of_edge_pair_mass']).copy()
    if usable.empty:
        return usable
    idx=(usable.groupby(['edge_index','window_side'],sort=False)['share_of_edge_pair_mass']
         .idxmax().dropna().astype(int))
    return usable.loc[idx].sort_values(['balanced_rank','window_side'])

print('\nTOP-EDGE AUTHOR SUPPORT — TOP AUTHOR PER EDGE/WINDOW')
zz=select_top_author_support(author_support)
if len(zz):
    print(zz[['balanced_rank','concept_u','concept_v','window_side','author','literary_stage','expected_balanced_pair_mass','share_of_edge_pair_mass']].to_string(index=False))
else:
    print('No edge/window group has a defined author-support share.')
print('\nPHASE 15 SCIENTIFIC OUTPUTS SERIALIZED: TRUE')