# Phase 14 — Robustness of semantic reconfiguration and null contrast
# Generated for the canonical Colab workflow. Historiographic markers/labels are intentionally absent.

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
# 0. Frozen environment and sources
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
 'hernandez_network':('https://github.com/lamusadecima/Network_for_Golden_Age_Spanish_Poetry.git','ef6b7b691f67abe60d9cfa85c274f0be8095dd9a'),
}
ROOT=Path('/content/gasr_phase14_sources'); ROOT.mkdir(exist_ok=True)
def clone(name,url,commit):
    dst=ROOT/name
    if dst.exists(): shutil.rmtree(dst)
    subprocess.run(['git','clone','--quiet',url,str(dst)],check=True)
    subprocess.run(['git','-C',str(dst),'checkout','--quiet',commit],check=True)
    got=subprocess.check_output(['git','-C',str(dst),'rev-parse','HEAD'],text=True).strip()
    assert got==commit,(name,got,commit)
    return dst
paths={k:clone(k,*v) for k,v in SOURCES.items()}
N=paths['navarro_tei']; G=paths['gongora_scholarly']; HNET=paths['hernandez_network']
XML_ID='{http://www.w3.org/XML/1998/namespace}id'
def local(tag): return tag.split('}')[-1] if '}' in tag else tag
def el_text(el): return '' if el is None else ' '.join(' '.join(el.itertext()).split())
def norm(s):
    s=unicodedata.normalize('NFKD',str(s)); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]','',s.lower())
def years_1580_1626(s):
    return sorted(set(int(x) for x in re.findall(r'(?<!\d)(1[56]\d{2})(?!\d)',str(s)) if 1580<=int(x)<=1626))
print('Environment and pinned sources ready')

# -----------------------------------------------------------------------------
# 1. Reproduce frozen 97-poem primary chronology exactly as Phase 13
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
# 2. NLP, frozen vocabularies, line and token-5 context units
# -----------------------------------------------------------------------------
MAIN_POS={'NOUN','VERB','ADJ','ADV'}; MIN_LEMMA_LEN=2

def process_poem_lines(poem_lines):
    records=[]; flat=[]
    for pid,lines in poem_lines.items():
        for line_no,line in enumerate(lines,1): flat.append((pid,line_no,line))
    docs=list(nlp.pipe([x[2] for x in flat],batch_size=128))
    line_units={pid:[set() for _ in lines] for pid,lines in poem_lines.items()}; seqs={pid:[] for pid in poem_lines}
    for (pid,line_no,_),doc in zip(flat,docs):
        cs=[]
        for tok in doc:
            lemma=unicodedata.normalize('NFC',str(tok.lemma_)).strip().lower(); pos=tok.pos_
            if tok.is_alpha and pos in MAIN_POS and len(lemma)>=MIN_LEMMA_LEN:
                c=f'{lemma}::{pos}'; cs.append(c); records.append((pid,c))
        line_units[pid][line_no-1]=set(cs); seqs[pid].extend(cs)
    token5={}
    for pid,seq in seqs.items(): token5[pid]=[set(seq[i:i+5]) for i in range(max(0,len(seq)-4))]
    concept_poems=defaultdict(set)
    for pid,c in records: concept_poems[c].add(pid)
    return line_units,token5,concept_poems

tei_lines={r.n_id:r.lines for r in primary.itertuples(index=False)}
line_units,token5_units,concept_poems=process_poem_lines(tei_lines)
VOCAB_DF2={c for c,pids in concept_poems.items() if len(pids)>=2}; VOCAB_DF3={c for c,pids in concept_poems.items() if len(pids)>=3}
assert len(VOCAB_DF2)==668,len(VOCAB_DF2); assert len(VOCAB_DF3)==349,len(VOCAB_DF3)
print('Frozen vocabularies reproduced: DF>=2',len(VOCAB_DF2),'| DF>=3',len(VOCAB_DF3))

# Efficient poem-by-feature representation. PPMI is reconstructed for every selected poem set.
def prepare_stats(name,pids,units_by_poem,vocab,author_lookup):
    pids=[p for p in pids if p in units_by_poem]; concepts=sorted(vocab); cidx={c:i for i,c in enumerate(concepts)}
    pair_keys=set()
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
    ei=np.asarray([cidx[a] for a,b in pairs],dtype=np.int32); ej=np.asarray([cidx[b] for a,b in pairs],dtype=np.int32)
    return {'name':name,'pids':pids,'pidrow':{p:i for i,p in enumerate(pids)},'concepts':concepts,'M':M,'U':U,'P':P,
            'ei':ei,'ej':ej,'authors':np.asarray([author_lookup[p] for p in pids],dtype=object)}

def build_state(stats,ids,mode):
    rows=np.asarray([stats['pidrow'][p] for p in ids if p in stats['pidrow']],dtype=int)
    nv=len(stats['concepts']); ne=stats['P'].shape[1]
    if len(rows)==0: return {'active':np.zeros(nv,bool),'w':np.zeros(ne,float)}
    U=stats['U'][rows].astype(float); authors=stats['authors'][rows]
    if mode=='raw': factors=np.ones(len(rows),float)
    else:
        ac=Counter(authors.tolist()); factors=np.asarray([1.0/(ac[a]*u) if u>0 else 0.0 for a,u in zip(authors,U)],float)
    T=float(np.dot(factors,U)); assert T>0
    marg=(stats['M'][rows].astype(float)*factors[:,None]).sum(axis=0)
    pairmass=np.asarray(stats['P'][rows].multiply(factors[:,None]).sum(axis=0)).ravel().astype(float)
    support=np.asarray(stats['P'][rows].sum(axis=0)).ravel()
    active=marg>0; w=np.zeros(ne,float); valid=(support>=1)&(pairmass>0)
    if np.any(valid):
        ei=stats['ei'][valid]; ej=stats['ej'][valid]; pm=pairmass[valid]
        denom=(marg[ei]/T)*(marg[ej]/T); ratio=(pm/T)/denom
        vals=np.maximum(0.0,np.log2(ratio)); idx=np.flatnonzero(valid); w[idx]=vals
    return {'active':active,'w':w}

def compare_states(stats,a,b):
    persistent=a['active']&b['active']; union=a['active']|b['active']; nu=int(union.sum()); npers=int(persistent.sum())
    L=np.nan if nu==0 else 1.0-npers/nu
    keep=persistent[stats['ei']]&persistent[stats['ej']]
    w1=np.where(keep,a['w'],0.0); w2=np.where(keep,b['w'],0.0)
    n1=float(np.linalg.norm(w1)); n2=float(np.linalg.norm(w2))
    R=np.nan if n1==0 or n2==0 else 1.0-float(np.dot(w1,w2)/(n1*n2))
    return L,R,npers

author_lookup=dict(zip(primary.n_id,primary.author_dir)); FULL_PIDS=list(primary.n_id)
STATS_B=prepare_stats('B_line_df2',FULL_PIDS,line_units,VOCAB_DF2,author_lookup)
STATS_C=prepare_stats('C_token5_df2',FULL_PIDS,token5_units,VOCAB_DF2,author_lookup)
STATS_DF3=prepare_stats('B_line_df3',FULL_PIDS,line_units,VOCAB_DF3,author_lookup)

# -----------------------------------------------------------------------------
# 3. Frozen chronology draws, window grids, support gate and trajectory engine
# -----------------------------------------------------------------------------
SEED=20260825; MC_DRAWS=1000; MODES=['author_balanced','raw']
ids_array=primary.n_id.to_numpy(object); pidcol={p:i for i,p in enumerate(ids_array)}
lo=primary.composition_min.to_numpy(int); hi=primary.composition_max.to_numpy(int)
rng_dates=np.random.default_rng(SEED); sampled=np.empty((MC_DRAWS,len(primary)),dtype=int)
for j,(a,b) in enumerate(zip(lo,hi)): sampled[:,j]=a if a==b else rng_dates.integers(a,b+1,size=MC_DRAWS)
WIN20=[(s,s+19) for s in range(1565,1606,5)]
WIN15=[(1570,1584),(1575,1589),(1585,1599),(1590,1604),(1595,1609),(1600,1614),(1605,1619),(1610,1624)]
WIN25=[(s,s+24) for s in range(1560,1601,5)]

def transitions_for(windows):
    out=[]
    for i in range(len(windows)-1):
        if windows[i+1][0]-windows[i][0]!=5: continue
        c1=sum(windows[i])/2; c2=sum(windows[i+1])/2
        out.append((i,i+1,(c1+c2)/2))
    return out

def window_ids(draw,win,allowed=None):
    mask=(sampled[draw]>=win[0])&(sampled[draw]<=win[1]); p=ids_array[mask].tolist()
    return tuple(sorted(p if allowed is None else [x for x in p if x in allowed]))

def support_row(ids):
    if not ids: return 0,0,0.0,1.0,False
    aa=[author_lookup[p] for p in ids]; c=Counter(aa); n=len(aa); probs=np.asarray(list(c.values()),float)/n
    neff=float(np.exp(-(probs*np.log(probs)).sum())); top=float(probs.max())
    usable=n>=10 and len(c)>=2 and neff>=1.5 and top<=0.85
    return n,len(c),neff,top,usable

def support_table(windows,allowed=None):
    rows=[]
    for wi,w in enumerate(windows):
        usable=[]; ns=[]; nas=[]; ne=[]; top=[]
        for d in range(MC_DRAWS):
            vals=support_row(window_ids(d,w,allowed)); ns.append(vals[0]); nas.append(vals[1]); ne.append(vals[2]); top.append(vals[3]); usable.append(vals[4])
        rows.append({'window_index':wi,'start':w[0],'end':w[1],'usable_probability':float(np.mean(usable)),
                     'n_poems_median':float(np.median(ns)),'n_authors_median':float(np.median(nas)),
                     'effective_authors_median':float(np.median(ne)),'top_share_median':float(np.median(top)),
                     'stable_usable':float(np.mean(usable))>=0.80})
    return pd.DataFrame(rows)

def observed_trajectory(design,stats,windows,allowed=None):
    trans=transitions_for(windows); memberships=[[window_ids(d,w,allowed) for w in windows] for d in range(MC_DRAWS)]
    unique_ids=sorted(set(x for row in memberships for x in row)); cache={}
    for ids in unique_ids:
        for mode in MODES: cache[(ids,mode)]=build_state(stats,ids,mode)
    rows=[]
    for d in range(MC_DRAWS):
        for li,ri,center in trans:
            left=memberships[d][li]; right=memberships[d][ri]
            for mode in MODES:
                L,R,npers=compare_states(stats,cache[(left,mode)],cache[(right,mode)])
                rows.append({'design':design,'draw':d,'left_start':windows[li][0],'left_end':windows[li][1],
                             'right_start':windows[ri][0],'right_end':windows[ri][1],'transition_center':center,'mode':mode,
                             'lexical_turnover':L,'rewiring_cosine':R,'n_persistent_concepts':npers})
    return pd.DataFrame(rows)

def summarize_traj(df):
    rows=[]
    for (design,center,mode),g in df.groupby(['design','transition_center','mode'],sort=True):
        r={'design':design,'transition_center':center,'mode':mode,'n':len(g)}
        for col in ['lexical_turnover','rewiring_cosine','n_persistent_concepts']:
            x=g[col].astype(float).dropna(); r[f'{col}_median']=float(np.median(x)); r[f'{col}_q10']=float(np.quantile(x,.10)); r[f'{col}_q90']=float(np.quantile(x,.90))
        rows.append(r)
    z=pd.DataFrame(rows); z['rewiring_rank']=z.groupby(['design','mode']).rewiring_cosine_median.rank(method='min',ascending=False)
    return z.sort_values(['design','transition_center','mode'])

bench=observed_trajectory('benchmark_B_line_df2_w20',STATS_B,WIN20); r1=observed_trajectory('R1_token5_df2_w20',STATS_C,WIN20)
r2=observed_trajectory('R2_line_df3_w20',STATS_DF3,WIN20); r3a=observed_trajectory('R3_line_df2_w15',STATS_B,WIN15); r3b=observed_trajectory('R3_line_df2_w25',STATS_B,WIN25)
obs_core=pd.concat([bench,r1,r2,r3a,r3b],ignore_index=True); obs_core_summary=summarize_traj(obs_core)
# Regression checks against executed Phase 13.
rr=obs_core_summary[(obs_core_summary.design=='benchmark_B_line_df2_w20')&(obs_core_summary.transition_center==1592)&(obs_core_summary['mode']=='raw')].iloc[0]
bb=obs_core_summary[(obs_core_summary.design=='benchmark_B_line_df2_w20')&(obs_core_summary.transition_center==1592)&(obs_core_summary['mode']=='author_balanced')].iloc[0]
assert abs(rr.rewiring_cosine_median-0.224870)<5e-6,(rr.rewiring_cosine_median,'Phase13 raw mismatch')
assert abs(bb.rewiring_cosine_median-0.233746)<5e-6,(bb.rewiring_cosine_median,'Phase13 balanced mismatch')
print('Phase-13 benchmark reproduced; R1-R3 observed robustness trajectories complete')

# -----------------------------------------------------------------------------
# 4. R4 paired Navarro/Hernández standardized-text sensitivity
# -----------------------------------------------------------------------------
H_AUTHOR_FILES={'Gongora':'Gongora_Sonetos.txt','GarcilasoDeLaVega':'Garcilaso_Sonetos.txt','FernandoDeHerrera':'Herrera_Sonetos.txt','Cervantes':'Cervantes_Sonetos.txt','Quevedo':'Quevedo_Sonetos.txt'}
def segment_blocks(path):
    raw=Path(path).read_text(encoding='utf-8',errors='replace').replace('\r\n','\n'); out=[]
    for i,block in enumerate(re.split(r'\n\s*\n+',raw),1):
        lines=[x.strip() for x in block.splitlines() if x.strip()]
        if lines: out.append({'h_block_id':i,'h_n_lines':len(lines),'h_lines':lines,'h_text':'\n'.join(lines),'h_signature':norm('\n'.join(lines))})
    return pd.DataFrame(out)

crosswalk_rows=[]
for author,grp in primary.groupby('author_dir',sort=False):
    if author not in H_AUTHOR_FILES:
        for r in grp.itertuples(index=False): crosswalk_rows.append({'n_id':r.n_id,'author_dir':author,'h_block_id':pd.NA,'match_method':'source_unavailable','match_score':pd.NA,'h_lines':pd.NA})
        continue
    hp=HNET/'corpus'/H_AUTHOR_FILES[author]; assert hp.exists(),hp
    hb=segment_blocks(hp); hb14=hb[hb.h_n_lines.eq(14)].copy(); sig_map=hb14.groupby('h_signature').h_block_id.apply(list).to_dict(); prelim=[]
    for r in grp.itertuples(index=False):
        ids=sig_map.get(r.signature,[]); prelim.append((r.n_id,int(ids[0]),'exact',1.0) if len(ids)==1 else (r.n_id,None,'unmatched',np.nan))
    ex=pd.DataFrame(prelim,columns=['n_id','h_block_id','method','score']); used=set(ex.loc[ex.h_block_id.notna(),'h_block_id'].astype(int)); remaining=hb14[~hb14.h_block_id.isin(used)].copy(); fuzzy=[]
    for rr0 in ex[ex.h_block_id.isna()].itertuples(index=False):
        target=grp.loc[grp.n_id.eq(rr0.n_id),'signature'].iloc[0]; best_id,best_score=None,-1.0
        for hr in remaining.itertuples(index=False):
            sc=SequenceMatcher(None,target,hr.h_signature).ratio()
            if sc>best_score: best_id,best_score=int(hr.h_block_id),float(sc)
        fuzzy.append((rr0.n_id,best_id,best_score))
    fz=pd.DataFrame(fuzzy,columns=['n_id','h_block_id','score'])
    if len(fz):
        fz['preaccept']=fz.score.ge(.98); fcoll=set(fz.loc[fz.preaccept,'h_block_id'].value_counts()[lambda s:s>1].index); fz['accept']=fz.preaccept&~fz.h_block_id.isin(fcoll)
        for fr in fz[fz.accept].itertuples(index=False): ex.loc[ex.n_id.eq(fr.n_id),['h_block_id','method','score']]=[fr.h_block_id,'fuzzy_ge_0.98',fr.score]
    lookup=hb14.set_index('h_block_id')
    for er in ex.itertuples(index=False):
        if pd.isna(er.h_block_id): crosswalk_rows.append({'n_id':er.n_id,'author_dir':author,'h_block_id':pd.NA,'match_method':'unmatched','match_score':er.score,'h_lines':pd.NA})
        else: crosswalk_rows.append({'n_id':er.n_id,'author_dir':author,'h_block_id':int(er.h_block_id),'match_method':er.method,'match_score':float(er.score),'h_lines':lookup.loc[int(er.h_block_id),'h_lines']})
crosswalk=pd.DataFrame(crosswalk_rows); matched=crosswalk[crosswalk.h_block_id.notna()].copy(); assert len(matched)==91,len(matched)
MATCHED=set(matched.n_id); h_lines={r.n_id:r.h_lines for r in matched.itertuples(index=False)}; nav_pair_lines={p:tei_lines[p] for p in MATCHED}
nav_pair_line,_,nav_pair_cp=process_poem_lines(nav_pair_lines); h_pair_line,_,h_pair_cp=process_poem_lines(h_lines)
V_NAV_PAIR={c for c,s in nav_pair_cp.items() if len(s)>=2}; V_H_PAIR={c for c,s in h_pair_cp.items() if len(s)>=2}
STATS_NAV_PAIR=prepare_stats('R4_Navarro_paired',list(MATCHED),nav_pair_line,V_NAV_PAIR,author_lookup)
STATS_H_PAIR=prepare_stats('R4_Hernandez_paired',list(MATCHED),h_pair_line,V_H_PAIR,author_lookup)
pair_support=support_table(WIN20,MATCHED); stable_pair_idx=set(pair_support.loc[pair_support.stable_usable,'window_index'].astype(int))
def restricted_windows_and_transitions(windows,stable_idx):
    # Keep all stable windows; trajectory engine itself skips non-5-year gaps.
    return [w for i,w in enumerate(windows) if i in stable_idx]
WIN_PAIR=restricted_windows_and_transitions(WIN20,stable_pair_idx)
r4nav=observed_trajectory('R4_paired_Navarro',STATS_NAV_PAIR,WIN_PAIR,MATCHED) if len(WIN_PAIR)>=2 else pd.DataFrame()
r4h=observed_trajectory('R4_paired_Hernandez',STATS_H_PAIR,WIN_PAIR,MATCHED) if len(WIN_PAIR)>=2 else pd.DataFrame()
obs_r4=pd.concat([x for x in [r4nav,r4h] if len(x)],ignore_index=True) if len(r4nav) or len(r4h) else pd.DataFrame()
obs_r4_summary=summarize_traj(obs_r4) if len(obs_r4) else pd.DataFrame()
coverage_author=(primary[['n_id','author_dir']].assign(matched=lambda x:x.n_id.isin(MATCHED)).groupby('author_dir').agg(primary_poems=('n_id','size'),matched_poems=('matched','sum')).reset_index())
coverage_author['coverage']=coverage_author.matched_poems/coverage_author.primary_poems
print('R4 paired coverage:',len(MATCHED),'/ 97 | Navarro paired vocab',len(V_NAV_PAIR),'| Hernández paired vocab',len(V_H_PAIR),'| stable windows',len(WIN_PAIR))

# -----------------------------------------------------------------------------
# 5. R5 pre-semantic leave-one-author-out feasibility + observed trajectories
# -----------------------------------------------------------------------------
loo_feas=[]; loo_obs=[]
for author in sorted(primary.author_dir.unique()):
    allowed=set(primary.loc[~primary.author_dir.eq(author),'n_id']); st=support_table(WIN20,allowed); st['removed_author']=author; loo_feas.append(st)
    stable=set(st.loc[st.stable_usable,'window_index'].astype(int)); wuse=restricted_windows_and_transitions(WIN20,stable)
    if len(wuse)>=2:
        z=observed_trajectory(f'R5_LOO_{author}',STATS_B,wuse,allowed); z['removed_author']=author; loo_obs.append(z)
loo_feasibility=pd.concat(loo_feas,ignore_index=True); obs_loo=pd.concat(loo_obs,ignore_index=True) if loo_obs else pd.DataFrame(); obs_loo_summary=summarize_traj(obs_loo) if len(obs_loo) else pd.DataFrame()
print('R5 feasibility computed for',primary.author_dir.nunique(),'authors')

# -----------------------------------------------------------------------------
# 6. Robustness nulls: fixed 50 chronology draws x 20 reps = 1000
# -----------------------------------------------------------------------------
ROBUST_NULL_SEED=20260827; ROBUST_DRAW_IDS=np.linspace(0,MC_DRAWS-1,50,dtype=int); ROBUST_REPS=20; ROBUST_TOTAL=len(ROBUST_DRAW_IDS)*ROBUST_REPS
assert len(set(ROBUST_DRAW_IDS))==50 and ROBUST_TOTAL==1000

def local_reassign(left,right,rng,allowed=None):
    L=set(left); R=set(right); pool=L|R
    if allowed is not None: pool&=set(allowed); L&=set(allowed); R&=set(allowed)
    nl=set(); nr=set()
    by=defaultdict(list)
    for p in pool: by[author_lookup[p]].append(p)
    for a,pa in by.items():
        pa=sorted(pa); La=L&set(pa); Ra=R&set(pa); ns=len(La&Ra); nlo=len(La-Ra); nro=len(Ra-La)
        perm=np.asarray(pa,dtype=object)[rng.permutation(len(pa))].tolist(); shared=set(perm[:ns]); onlyl=set(perm[ns:ns+nlo]); onlyr=set(perm[ns+nlo:ns+nlo+nro])
        nl|=shared|onlyl; nr|=shared|onlyr
    return tuple(sorted(nl)),tuple(sorted(nr))

def n1_null(design,stats,windows,allowed=None):
    trans=transitions_for(windows); rng=np.random.default_rng(np.random.SeedSequence([ROBUST_NULL_SEED,abs(hash(design))%(2**31-1),1])); rows=[]
    for d in ROBUST_DRAW_IDS:
        memberships=[window_ids(int(d),w,allowed) for w in windows]
        for rep in range(ROBUST_REPS):
            for li,ri,center in trans:
                nl,nr=local_reassign(memberships[li],memberships[ri],rng,allowed)
                for mode in MODES:
                    L,R,npers=compare_states(stats,build_state(stats,nl,mode),build_state(stats,nr,mode))
                    rows.append({'design':design,'draw':int(d),'rep':rep,'transition_center':center,'mode':mode,'lexical_turnover':L,'rewiring_cosine':R,'n_persistent_concepts':npers})
    return pd.DataFrame(rows)

def n2_null(design,stats,windows,allowed=None):
    allowed=set(FULL_PIDS if allowed is None else allowed); trans=transitions_for(windows); rng=np.random.default_rng(np.random.SeedSequence([ROBUST_NULL_SEED,abs(hash(design))%(2**31-1),2])); rows=[]; mx=[]
    apos={a:[pidcol[p] for p in allowed if author_lookup[p]==a] for a in sorted(set(author_lookup[p] for p in allowed))}
    for d in ROBUST_DRAW_IDS:
        base=sampled[int(d)].copy()
        for rep in range(ROBUST_REPS):
            perm=base.copy()
            for a,idx in apos.items():
                vals=base[idx].copy(); perm[idx]=vals[rng.permutation(len(vals))]
            memberships=[]
            for w in windows:
                ids=tuple(sorted([p for p in allowed if w[0]<=perm[pidcol[p]]<=w[1]])); memberships.append(ids)
            repvals={m:[] for m in MODES}
            for li,ri,center in trans:
                for mode in MODES:
                    L,R,npers=compare_states(stats,build_state(stats,memberships[li],mode),build_state(stats,memberships[ri],mode)); repvals[mode].append(R)
                    rows.append({'design':design,'draw':int(d),'rep':rep,'transition_center':center,'mode':mode,'lexical_turnover':L,'rewiring_cosine':R,'n_persistent_concepts':npers})
            for mode in MODES:
                vals=np.asarray(repvals[mode],float); mx.append({'design':design,'draw':int(d),'rep':rep,'mode':mode,'max_rewiring':float(np.nanmax(vals))})
    return pd.DataFrame(rows),pd.DataFrame(mx)

def null_tests(obs_summary,null_df,model,max_df=None):
    ns=summarize_traj(null_df.rename(columns={'design':'design'})); rows=[]
    # summarize_traj labels medians in generic columns; use draw-level null directly for tails.
    for o in obs_summary.itertuples(index=False):
        g=null_df[(null_df.design==o.design)&(null_df.transition_center==o.transition_center)&(null_df['mode']==o.mode)].rewiring_cosine.dropna().to_numpy(float)
        if len(g)==0: continue
        obs=float(o.rewiring_cosine_median); r={'design':o.design,'transition_center':o.transition_center,'mode':o.mode,'null_model':model,'obs_rewiring_median':obs,
            'null_median':float(np.median(g)),'null_q90':float(np.quantile(g,.90)),'null_q95':float(np.quantile(g,.95)),
            'excess':obs-float(np.median(g)),'null_percentile':float(np.mean(g<=obs)),'empirical_p':float((1+np.sum(g>=obs))/(1+len(g)))}
        if max_df is not None:
            m=max_df[(max_df.design==o.design)&(max_df['mode']==o.mode)].max_rewiring.dropna().to_numpy(float); r['max_fwer_p']=float((1+np.sum(m>=obs))/(1+len(m)))
        rows.append(r)
    return pd.DataFrame(rows)

core_specs=[('R1_token5_df2_w20',STATS_C,WIN20,None),('R2_line_df3_w20',STATS_DF3,WIN20,None),('R3_line_df2_w15',STATS_B,WIN15,None),('R3_line_df2_w25',STATS_B,WIN25,None)]
n1_frames=[]; n2_frames=[]; n2max_frames=[]; test_frames=[]
for design,stats,windows,allowed in core_specs:
    print('Robust nulls:',design)
    a=n1_null(design,stats,windows,allowed); b,bm=n2_null(design,stats,windows,allowed); n1_frames.append(a); n2_frames.append(b); n2max_frames.append(bm)
    os=obs_core_summary[obs_core_summary.design.eq(design)]; test_frames.append(null_tests(os,a,'N1_local')); test_frames.append(null_tests(os,b,'N2_global',bm))

# R4 nulls only if every benchmark window remains stable on the paired subset.
r4_full_support=bool(pair_support.stable_usable.all())
if r4_full_support:
    for design,stats in [('R4_paired_Navarro',STATS_NAV_PAIR),('R4_paired_Hernandez',STATS_H_PAIR)]:
        os=obs_r4_summary[obs_r4_summary.design.eq(design)]; a=n1_null(design,stats,WIN20,MATCHED); n1_frames.append(a); test_frames.append(null_tests(os,a,'N1_local'))
        b,bm=n2_null(design,stats,WIN20,MATCHED); n2_frames.append(b); n2max_frames.append(bm); test_frames.append(null_tests(os,b,'N2_global',bm))

# R5: N1 only on pre-semantically eligible stable-window runs; N2 only if all 9 windows are stable.
for author in sorted(primary.author_dir.unique()):
    allowed=set(primary.loc[~primary.author_dir.eq(author),'n_id']); st=loo_feasibility[loo_feasibility.removed_author.eq(author)]; stable=set(st.loc[st.stable_usable,'window_index'].astype(int)); wuse=restricted_windows_and_transitions(WIN20,stable)
    design=f'R5_LOO_{author}'; os=obs_loo_summary[obs_loo_summary.design.eq(design)] if len(obs_loo_summary) else pd.DataFrame()
    if len(wuse)>=2 and len(os):
        a=n1_null(design,STATS_B,wuse,allowed); n1_frames.append(a); test_frames.append(null_tests(os,a,'N1_local'))
    if bool(st.stable_usable.all()) and len(os):
        b,bm=n2_null(design,STATS_B,WIN20,allowed); n2_frames.append(b); n2max_frames.append(bm); test_frames.append(null_tests(os,b,'N2_global',bm))

n1_all=pd.concat(n1_frames,ignore_index=True) if n1_frames else pd.DataFrame(); n2_all=pd.concat(n2_frames,ignore_index=True) if n2_frames else pd.DataFrame(); n2max_all=pd.concat(n2max_frames,ignore_index=True) if n2max_frames else pd.DataFrame(); robust_tests=pd.concat(test_frames,ignore_index=True) if test_frames else pd.DataFrame()
print('Robustness null simulations complete')

# -----------------------------------------------------------------------------
# 7. Concordance, benchmark-neighborhood summaries, exports and checkpoint
# -----------------------------------------------------------------------------
BENCH=obs_core_summary[obs_core_summary.design.eq('benchmark_B_line_df2_w20')].copy()
all_obs_summaries=pd.concat([obs_core_summary,obs_r4_summary,obs_loo_summary],ignore_index=True,sort=False)
concord=[]
for design in all_obs_summaries.design.dropna().unique():
    if design=='benchmark_B_line_df2_w20': continue
    for mode in MODES:
        b=BENCH[BENCH['mode'].eq(mode)][['transition_center','rewiring_cosine_median']]
        s=all_obs_summaries[(all_obs_summaries.design.eq(design))&(all_obs_summaries['mode'].eq(mode))][['transition_center','rewiring_cosine_median','rewiring_rank']]
        m=b.merge(s,on='transition_center',suffixes=('_benchmark','_sensitivity'))
        rho=np.nan; reason='fewer than 3 exact common transition centers'
        if len(m)>=3:
            rho=float(spearmanr(m.rewiring_cosine_median_benchmark,m.rewiring_cosine_median_sensitivity).statistic); reason='exact common centers'
        peak=s.loc[s.rewiring_cosine_median.idxmax()] if len(s) else None
        concord.append({'design':design,'mode':mode,'n_exact_common_centers':len(m),'spearman_exact_centers':rho,'spearman_note':reason,
                        'sensitivity_peak_center':np.nan if peak is None else float(peak.transition_center),'sensitivity_peak_rewiring':np.nan if peak is None else float(peak.rewiring_cosine_median)})
concordance=pd.DataFrame(concord)

# Pre-specified R3 neighborhood around the previously identified 1592 benchmark episode.
r3_neighborhood=[]
for design in ['R3_line_df2_w15','R3_line_df2_w25']:
    for mode in MODES:
        s=obs_core_summary[(obs_core_summary.design.eq(design))&(obs_core_summary['mode'].eq(mode))].copy(); s['distance_to_1592']=(s.transition_center-1592).abs(); md=s.distance_to_1592.min()
        for r in s[s.distance_to_1592.eq(md)].itertuples(index=False): r3_neighborhood.append({'design':design,'mode':mode,'transition_center':r.transition_center,'distance_to_benchmark_1592':md,'rewiring_median':r.rewiring_cosine_median,'rewiring_rank':r.rewiring_rank})
r3_neighborhood=pd.DataFrame(r3_neighborhood)

spec=pd.DataFrame([
 ('benchmark','B_line_support1','df>=2','20y','Navarro','primary Phase13 benchmark'),
 ('R1','C_token5_support1','df>=2','20y','Navarro','pre-registered alternative context'),
 ('R2','B_line_support1','df>=3','20y','Navarro','pre-registered stricter vocabulary'),
 ('R3a','B_line_support1','df>=2','15y','Navarro','Phase9 stable windows only'),
 ('R3b','B_line_support1','df>=2','25y','Navarro','Phase9 stable windows only'),
 ('R4','B_line_support1','layer-specific df>=2','20y','paired Navarro/Hernandez','same 91 poem identities'),
 ('R5','B_line_support1','df>=2','20y','Navarro','pre-semantic feasible author ablation only'),
],columns=['axis','representation','vocabulary','temporal_design','text_layer','role'])

OUT=Path('/content/gasr_phase14_outputs'); OUT.mkdir(exist_ok=True)
spec.to_csv(OUT/'phase14_robustness_specification.csv',index=False)
obs_core.to_csv(OUT/'phase14_observed_core_sensitivity_draws.csv',index=False); obs_core_summary.to_csv(OUT/'phase14_observed_core_sensitivity_summary.csv',index=False)
if len(obs_r4): obs_r4.to_csv(OUT/'phase14_paired_text_draws.csv',index=False); obs_r4_summary.to_csv(OUT/'phase14_paired_text_summary.csv',index=False)
crosswalk.drop(columns=['h_lines'],errors='ignore').to_csv(OUT/'phase14_paired_text_crosswalk.csv',index=False); coverage_author.to_csv(OUT/'phase14_paired_text_coverage_by_author.csv',index=False); pair_support.to_csv(OUT/'phase14_paired_text_window_support.csv',index=False)
loo_feasibility.to_csv(OUT/'phase14_loo_feasibility.csv',index=False)
if len(obs_loo): obs_loo.to_csv(OUT/'phase14_loo_observed_draws.csv',index=False); obs_loo_summary.to_csv(OUT/'phase14_loo_observed_summary.csv',index=False)
if len(n1_all): n1_all.to_csv(OUT/'phase14_n1_robustness_draws.csv',index=False)
if len(n2_all): n2_all.to_csv(OUT/'phase14_n2_robustness_draws.csv',index=False)
if len(n2max_all): n2max_all.to_csv(OUT/'phase14_n2_maxstat.csv',index=False)
robust_tests.to_csv(OUT/'phase14_robustness_null_tests.csv',index=False); concordance.to_csv(OUT/'phase14_trajectory_concordance.csv',index=False); r3_neighborhood.to_csv(OUT/'phase14_r3_benchmark_neighborhood.csv',index=False)

print('\nPHASE 14 CHECKPOINT')
print('-------------------')
print('Primary chronology:',len(primary),'poems |',primary.author_dir.nunique(),'authors')
print('Phase-13 benchmark reproduced: TRUE')
print('R1 token-5 context trajectory: COMPLETE')
print('R2 DF>=3 vocabulary trajectory: COMPLETE')
print('R3 Phase-9 15y/25y stable-window trajectories: COMPLETE')
print('R4 paired Navarro/Hernandez coverage:',len(MATCHED),'/ 97 | full 20y support:',r4_full_support)
print('R5 leave-one-author-out feasibility and eligible trajectories: COMPLETE')
print('Robust N1 budget:',ROBUST_TOTAL,'counterfactuals per eligible transition/mode/design')
print('Robust N2 budget:',ROBUST_TOTAL,'coherent trajectories for admissible designs')
print('1580/1605 used in robustness construction or tuning: FALSE')
print('Historiographic labels used in robustness construction or tuning: FALSE')
print('Phase-13 primary N1 inference redefined: FALSE')
print('Historical Renaissance/Baroque claim made: FALSE')
print('Next phase: freeze robustness decision, then external historiographic validation + concept-level close reading')
print('Outputs:',OUT)

# Compact displays useful for GitHub-saved Colab output inspection.
print('\nCORE ROBUSTNESS PEAKS')
peaks=obs_core_summary.loc[obs_core_summary.groupby(['design','mode']).rewiring_cosine_median.idxmax(),['design','mode','transition_center','rewiring_cosine_median','rewiring_rank']]
print(peaks.to_string(index=False))
print('\nROBUSTNESS NULL TESTS (sorted by design, model, mode, center)')
print(robust_tests.sort_values(['design','null_model','mode','transition_center']).to_string(index=False))
print('\nTRAJECTORY CONCORDANCE')
print(concordance.to_string(index=False))
print('\nR3 PRE-SPECIFIED NEIGHBORHOOD OF BENCHMARK 1592')
print(r3_neighborhood.to_string(index=False))
print('\nR4 COVERAGE BY AUTHOR')
print(coverage_author.to_string(index=False))
print('\nR5 STABLE WINDOWS BY REMOVED AUTHOR')
print(loo_feasibility.groupby('removed_author').stable_usable.sum().sort_values().to_string())
