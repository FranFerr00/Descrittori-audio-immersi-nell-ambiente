#!/usr/bin/env python3
"""Genera il catalogo suoni per Pd dai dati del corpus.

Produce due file in pd-externals/monolitici/ancore/:
  - suoni.pd    motore impacchettato: numero (1..N) -> 16 grezzi (leggero,
                sta dentro ogni [ancora])
  - catalogo.pd pannello-elenco: i N suoni come message box con indice e nome
                (uno solo, al primo livello, per sfogliare)

I 16 grezzi sono in ordine DESCS. Per aggiungere suoni: estendi le sorgenti
qui sotto e rilancia  python3 genera_suoni_pd.py
"""
import csv
DESCS=["centroid","spread","rolloff","slope","obsir_std","flatness","crest",
       "skewness","kurtosis","entropy","tpr","n_peaks","tonality","flux",
       "irregularity","zcr"]
OUT="pd-externals/monolitici/ancore"

def raccogli():
    cat=[]
    for r in csv.DictReader(open("analisi/tabelle/segnali_sommario.csv")):
        cat.append((r["segnale"], [float(r[d+"_mean"]) for d in DESCS]))
    UFF={"clarinettocb":[("001","p1"),("002","p2"),("003","mf"),("004","f"),
            ("005","cresc1"),("006","cresc2"),("007","dim"),("010","cresc-dim"),("013","dim-cresc")],
         "timpano":[("004","p"),("005","mf"),("006","f1"),("007","f2"),("008","mf2"),
            ("015","cresc"),("016","dim"),("018","dim-cresc-lungo"),("023","dim-cresc-corto"),("025","cresc-dim")]}
    pref={"clarinettocb":"clar","timpano":"timp"}
    for strum,items in UFF.items():
        for cid,lab in items:
            path=f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
            rows=[r for r in csv.DictReader(open(path)) if r.get("gated","0")!="1"]
            c=rows[len(rows)//2]
            cat.append((f"{pref[strum]}{cid}_{lab}", [float(c[d]) for d in DESCS]))
    return cat

def scrivi_suoni(cat):
    flat=[x for _,v in cat for x in v]
    big=" ".join(f"{x:g}" for x in flat)
    n=len(cat)
    L=[f"#N canvas 200 60 1000 760 10;",
       "#X obj 30 40 inlet;","#X obj 30 80 moses 1;","#X obj 30 120 t b f;",
       "#X obj 120 160 - 1;","#X obj 120 190 * 16;",f"#X msg 30 230 {big};",
       "#X obj 30 280 list split;","#X obj 30 320 list split 16;","#X obj 30 370 outlet;",
       f"#X text 28 18 numero del suono (1..{n}) -> 16 grezzi;",
       "#X text 250 230 catalogo impacchettato (16 valori per suono);"]
    percol=(n+3)//4
    for i,(nome,_) in enumerate(cat):
        x=30+(i//percol)*240; y=420+(i%percol)*20
        L.append(f"#X text {x} {y} {i+1} {nome};")
    for a,b,c,d in [(0,0,1,0),(1,1,2,0),(2,1,3,0),(3,0,4,0),(4,0,6,1),
                    (2,0,5,0),(5,0,6,0),(6,1,7,0),(7,0,8,0)]:
        L.append(f"#X connect {a} {b} {c} {d};")
    open(f"{OUT}/suoni.pd","w").write("\n".join(L)+"\n")

def scrivi_catalogo(cat):
    n=len(cat)
    L=[f"#N canvas 120 40 1000 {120+n*24} 10;",
       "#X text 20 14 elenco suoni (indice nome valori). clic = manda all'outlet;"]
    OUTLET=1  # placeholder, lo metto dopo gli oggetti
    # oggetti: per suono comment + msg ; alla fine un outlet
    objs=[]; cons=[]
    idx=2  # 0=canvas? no: idx parte da quanti #X gia' messi (header text = idx1, ma
    # ricalcolo: idx0 = primo #X dopo canvas. Header text e' idx0. Quindi:
    # idx0 = "#X text 20 14 ..."  -> gia' in L[1]
    # ricomincio pulito:
    L=[f"#N canvas 120 40 1000 {140+n*24} 10;"]
    L.append("#X text 20 14 elenco suoni: indice  nome  valori (clic = manda all'outlet);")  # idx0
    L.append("#X obj 20 50 outlet;")  # idx1 (outlet in alto)
    base=2
    msg_idx=[]
    for i,(nome,vals) in enumerate(cat):
        y=80+i*24
        L.append(f"#X text 20 {y} {i+1} {nome};")            # comment
        vs=" ".join(f"{x:g}" for x in vals)
        L.append(f"#X msg 200 {y} {vs};")                    # msg
        msg_idx.append(base+1+i*2)  # ogni iter aggiunge 2 oggetti: comment, msg
    # indici: comment a base+ i*2, msg a base+1+i*2
    for i in range(n):
        m=base+1+i*2
        L.append(f"#X connect {m} 0 1 0;")  # msg -> outlet(1)
    open(f"{OUT}/catalogo.pd","w").write("\n".join(L)+"\n")

cat=raccogli()
scrivi_suoni(cat)
scrivi_catalogo(cat)
print(f"generati suoni.pd e catalogo.pd con {len(cat)} suoni")
