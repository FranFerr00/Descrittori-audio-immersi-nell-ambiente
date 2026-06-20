#!/usr/bin/env python3
"""Player PCA: come genera_player.py ma con assi = componenti principali.

Gli assi PC1/PC2/PC3 + colore PC4 inglobano TUTTI e 16 i descrittori (ognuno e'
una miscela). Spazio "completo ma opaco", da confrontare col player a descrittori
"parziale ma chiaro". Su ogni asse e' indicato di cosa pesa di piu' la componente.
Esce: player_gesti_pca.html
"""
import csv
import base64
import json
import subprocess
import tempfile
import os
import numpy as np

PLOTLYJS = "/tmp/plotly-venv/lib/python3.14/site-packages/plotly/package_data/plotly.min.js"
DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]
PASSO = 2

GESTI = [("clarinetto", "clarinettocb", c) for c in
         ["001", "002", "003", "004", "005", "006", "007", "010", "013"]] + \
        [("timpano", "timpano", c) for c in
         ["004", "005", "006", "007", "008", "015", "016", "018", "023", "025"]]


def liscia(a, w=7):
    a = np.asarray(a, float)
    if len(a) < w:
        return a
    return np.convolve(a, np.ones(w) / w, mode="same")


def audio_b64(strum, cid):
    wav = f"analisi/{strum}/samples/{cid}.wav"
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    subprocess.run(["ffmpeg", "-y", "-i", wav, "-ac", "1", "-b:a", "64k", tmp],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = base64.b64encode(open(tmp, "rb").read()).decode()
    os.unlink(tmp)
    return "data:audio/mp3;base64," + data


# raccogli i frame grezzi (16 descrittori) di ogni gesto
raw, times, audio = {}, {}, {}
allraw = []
for fam, strum, cid in GESTI:
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"][::PASSO]
    R = np.array([[float(r[d]) for d in DESCS] for r in rows])
    key = f"{fam} {cid}"
    raw[key] = R
    times[key] = [round(float(r["time"]), 3) for r in rows]
    audio[key] = audio_b64(strum, cid)
    allraw.append(R)

allR = np.vstack(allraw)
cmean, cstd = allR.mean(axis=0), allR.std(axis=0)
cstd[cstd == 0] = 1.0
allZ = (allR - cmean) / cstd
mu = allZ.mean(axis=0)
U, S, Vt = np.linalg.svd(allZ - mu, full_matrices=False)
for k in range(4):
    if Vt[k][np.argmax(np.abs(Vt[k]))] < 0:
        Vt[k] = -Vt[k]
var = (S ** 2) / (S ** 2).sum() * 100


def etich(k):
    top = sorted(zip(DESCS, Vt[k]), key=lambda t: -abs(t[1]))[:3]
    return f"PC{k+1} ({var[k]:.0f}%): " + ", ".join(d for d, _ in top)


GEST = {}
allP = []
for key, R in raw.items():
    P = ((R - cmean) / cstd - mu) @ Vt[:4].T
    x, y, z, c = liscia(P[:, 0]), liscia(P[:, 1]), liscia(P[:, 2]), liscia(P[:, 3])
    allP.append(np.column_stack([x, y, z, c]))
    GEST[key] = {
        "x": [round(float(v), 3) for v in x],
        "y": [round(float(v), 3) for v in y],
        "z": [round(float(v), 3) for v in z],
        "c": [round(float(v), 3) for v in c],
        "t": times[key],
        "audio": audio[key],
    }
    print(f"  {key}: {len(times[key])} frame")
allP = np.vstack(allP)

Rg = lambda col: [float(np.percentile(allP[:, col], 1)), float(np.percentile(allP[:, col], 99))]
RANGES = {"x": Rg(0), "y": Rg(1), "z": Rg(2)}
CCOL = {"cmin": float(np.percentile(allP[:, 3], 2)), "cmax": float(np.percentile(allP[:, 3], 98))}

plotlyjs = open(PLOTLYJS).read()
data_js = json.dumps(GEST)
meta_js = json.dumps({"ranges": RANGES, "ccol": CCOL,
                      "etx": etich(0), "ety": etich(1), "etz": etich(2), "etc": etich(3)})

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
 body{font-family:sans-serif;margin:14px;background:#fafafa}
 #bar{margin-bottom:8px} select,button{font-size:15px;padding:3px 6px}
 audio{vertical-align:middle;margin-left:10px} h3{margin:4px 0}
</style>
<script>__PLOTLYJS__</script>
</head><body>
<h3>Player PCA: assi = componenti che inglobano tutti e 16 i descrittori</h3>
<div id="bar">
  gesto: <select id="sel"></select>
  <audio id="au" controls></audio>
</div>
<div id="plot" style="width:1000px;height:720px"></div>
<script>
var GEST=__DATA__, M=__META__;
var gd=document.getElementById('plot'), au=document.getElementById('au'),
    sel=document.getElementById('sel'), cur=null, raf=null;
Object.keys(GEST).forEach(function(k){
  var o=document.createElement('option'); o.value=k; o.text=k; sel.add(o);});
function layout(key){return{
  title:'gesto: '+key,
  scene:{xaxis:{title:{text:M.etx},range:M.ranges.x},
         yaxis:{title:{text:M.ety},range:M.ranges.y},
         zaxis:{title:{text:M.etz},range:M.ranges.z}},
  margin:{l:10,r:10,t:34,b:10}};}
function initPlot(key){
  cur=GEST[key];
  var ghost={type:'scatter3d',mode:'lines',x:cur.x,y:cur.y,z:cur.z,
    line:{color:'rgba(150,150,150,0.35)',width:2},hoverinfo:'skip',name:'percorso'};
  var prog={type:'scatter3d',mode:'lines',x:[cur.x[0]],y:[cur.y[0]],z:[cur.z[0]],
    line:{color:[cur.c[0]],colorscale:'Plasma',cmin:M.ccol.cmin,cmax:M.ccol.cmax,
          width:6,colorbar:{title:M.etc}},hoverinfo:'skip',name:'suonato'};
  var mk={type:'scatter3d',mode:'markers',x:[cur.x[0]],y:[cur.y[0]],z:[cur.z[0]],
    marker:{size:6,color:'black'},hoverinfo:'skip',name:'adesso'};
  Plotly.react(gd,[ghost,prog,mk],layout(key));
  au.src=cur.audio;
}
function nFrames(tc){var t=cur.t,n=0;while(n<t.length&&t[n]<=tc)n++;return n;}
function tick(){
  if(!cur)return;
  var n=nFrames(au.currentTime); if(n<1)n=1;
  Plotly.restyle(gd,{x:[cur.x.slice(0,n)],y:[cur.y.slice(0,n)],z:[cur.z.slice(0,n)],
    'line.color':[cur.c.slice(0,n)]},[1]);
  Plotly.restyle(gd,{x:[[cur.x[n-1]]],y:[[cur.y[n-1]]],z:[[cur.z[n-1]]]},[2]);
  if(!au.paused&&!au.ended) raf=requestAnimationFrame(tick);
}
au.addEventListener('play',function(){if(raf)cancelAnimationFrame(raf);tick();});
au.addEventListener('seeked',tick);
au.addEventListener('pause',tick);
au.addEventListener('ended',tick);
sel.addEventListener('change',function(){if(raf)cancelAnimationFrame(raf);initPlot(sel.value);});
initPlot(Object.keys(GEST)[0]);
</script>
</body></html>"""

HTML = (HTML.replace("__PLOTLYJS__", plotlyjs)
            .replace("__DATA__", data_js)
            .replace("__META__", meta_js))
open("player_gesti_pca.html", "w").write(HTML)
print("scritto player_gesti_pca.html  (%.1f MB)" % (len(HTML) / 1e6))
print("assi:", etich(0), "|", etich(1), "|", etich(2), "| colore", etich(3))
