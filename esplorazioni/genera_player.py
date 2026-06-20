#!/usr/bin/env python3
"""Player HTML: ascolta il gesto e vedi il percorso disegnarsi nello spazio.

Per ogni gesto strumentale: la traiettoria sui descrittori interpretabili
(x=centroid, y=tpr, z=flux, colore=flatness) e l'audio compresso, sincronizzati.
Premi play: il percorso cresce seguendo il suono, un punto nero segna "adesso".
Tutto incorporato (plotly.js + audio in base64): l'HTML e' autonomo e offline.

Esce: player_gesti.html
"""
import csv
import base64
import json
import subprocess
import tempfile
import os
import numpy as np

PLOTLYJS = "/tmp/plotly-venv/lib/python3.14/site-packages/plotly/package_data/plotly.min.js"
AX, AY, AZ, AC = "centroid", "tpr", "flux", "flatness"
ETX = "centroid (brillantezza, Hz)"
ETY = "tpr (tonalita')"
ETZ = "flux (movimento)"
ETC = "flatness (rumorosita')"
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


GEST = {}
allx, ally, allz, allc = [], [], [], []
for fam, strum, cid in GESTI:
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"][::PASSO]
    x = liscia([float(r[AX]) for r in rows])
    y = liscia([float(r[AY]) for r in rows])
    z = liscia([float(r[AZ]) for r in rows])
    c = liscia([float(r[AC]) for r in rows])
    t = [float(r["time"]) for r in rows]
    allx += list(x); ally += list(y); allz += list(z); allc += list(c)
    key = f"{fam} {cid}"
    GEST[key] = {
        "x": [round(float(v), 1) for v in x],
        "y": [round(float(v), 3) for v in y],
        "z": [round(float(v), 5) for v in z],
        "c": [round(float(v), 4) for v in c],
        "t": [round(v, 3) for v in t],
        "audio": audio_b64(strum, cid),
        "fam": fam,
    }
    print(f"  {key}: {len(t)} frame, audio {len(GEST[key]['audio'])//1024} KB")

R = lambda a: [float(np.percentile(a, 1)), float(np.percentile(a, 99))]
RANGES = {"x": R(allx), "y": R(ally), "z": R(allz)}
CCOL = {"cmin": float(np.percentile(allc, 2)), "cmax": float(np.percentile(allc, 98))}

plotlyjs = open(PLOTLYJS).read()
data_js = json.dumps(GEST)
meta_js = json.dumps({"ranges": RANGES, "ccol": CCOL,
                      "etx": ETX, "ety": ETY, "etz": ETZ, "etc": ETC})

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
 body{font-family:sans-serif;margin:14px;background:#fafafa}
 #bar{margin-bottom:8px}
 select,button{font-size:15px;padding:3px 6px}
 audio{vertical-align:middle;margin-left:10px}
 h3{margin:4px 0}
</style>
<script>__PLOTLYJS__</script>
</head><body>
<h3>Player dei gesti: ascolta e guarda il percorso disegnarsi</h3>
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
  var o=document.createElement('option'); o.value=k; o.text=k; sel.add(o);
});
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
open("player_gesti.html", "w").write(HTML)
print("scritto player_gesti.html  (%.1f MB)" % (len(HTML) / 1e6))
