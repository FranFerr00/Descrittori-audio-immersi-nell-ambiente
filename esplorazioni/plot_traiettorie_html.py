#!/usr/bin/env python3
"""Traiettorie 3D dei gesti in un HTML navigabile col mouse (plotly).

Stessa figura interpretabile (x=centroid, y=tpr, z=flux, colore=flatness) ma
fermo e navigabile: ruota, zoom, e passando sopra una linea mostra gesto e
frame. La libreria JavaScript e' incorporata: l'HTML funziona offline, senza
plotly installato. Esce: traiettorie_3d.html
"""
import csv
import numpy as np
import plotly.graph_objects as go

AX, AY, AZ, AC = "centroid", "tpr", "flux", "flatness"
ET = {"centroid": "centroid (brillantezza, Hz)", "tpr": "tpr (tonalita')",
      "flux": "flux (movimento)", "flatness": "flatness (rumorosita')"}
PASSO = 3

GESTI = {
    "clarinetto": [("clarinettocb", c) for c in
                   ["001", "002", "003", "004", "005", "006", "007", "010", "013"]],
    "timpano": [("timpano", c) for c in
                ["004", "005", "006", "007", "008", "015", "016", "018", "023", "025"]],
}


def frames(strum, cid, cols):
    path = f"analisi/{strum}/analisi/{cid}/{cid}_hann_ov50_10000hz_analisi.csv"
    rows = [r for r in csv.DictReader(open(path)) if r.get("gated", "0") != "1"]
    rows = rows[::PASSO]
    return np.array([[float(r[c]) for c in cols] for r in rows])


def liscia(a, w=7):
    if len(a) < w:
        return a
    return np.convolve(a, np.ones(w) / w, mode="same")


cols = [AX, AY, AZ, AC]
traj, allf = {}, []
for fam, lst in GESTI.items():
    for strum, cid in lst:
        D = frames(strum, cid, cols)
        traj[(fam, cid)] = D
        allf.append(D)
allD = np.vstack(allf)
cmin, cmax = np.percentile(allD[:, 3], 2), np.percentile(allD[:, 3], 98)

fig = go.Figure()
first = True
visto_fam = set()      # intestazione del gruppo solo sulla prima traccia
for (fam, cid), D in traj.items():
    x, y, z, c = (liscia(D[:, 0]), liscia(D[:, 1]), liscia(D[:, 2]), liscia(D[:, 3]))
    txt = [f"{fam} {cid}<br>frame {i*PASSO}<br>{AX} {x[i]:.0f}<br>{AY} {y[i]:.1f}"
           f"<br>{AZ} {z[i]:.4f}<br>{AC} {c[i]:.3f}" for i in range(len(x))]
    # marcatore d'inizio dentro la stessa traccia: dimensione > 0 solo sul frame 0,
    # cosi' si spegne insieme alla linea quando clicchi la sua voce di legenda
    msize = np.zeros(len(x)); msize[0] = 7.0
    grouptitle = fam if fam not in visto_fam else None
    visto_fam.add(fam)
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z, mode="lines+markers",
        line=dict(color=c, colorscale="Plasma", width=5, cmin=cmin, cmax=cmax,
                  showscale=first,
                  colorbar=dict(title=ET[AC], len=0.45, y=0.22, yanchor="middle",
                                x=1.02) if first else None),
        marker=dict(size=msize, color="black",
                    symbol="circle" if fam == "clarinetto" else "diamond"),
        name=f"{fam} {cid}", text=txt, hoverinfo="text",
        legendgroup=fam,
        legendgrouptitle=dict(text=grouptitle) if grouptitle else None))
    first = False

fig.update_layout(
    title="Traiettorie dei gesti su assi interpretabili (navigabile col mouse). "
          "Clic in legenda = spegne il singolo gesto",
    scene=dict(xaxis_title=ET[AX], yaxis_title=ET[AY], zaxis_title=ET[AZ]),
    width=1100, height=800,
    legend=dict(itemsizing="constant", groupclick="toggleitem",
                x=1.02, y=1.0, yanchor="top"))
fig.write_html("traiettorie_3d.html", include_plotlyjs=True)
print("scritto traiettorie_3d.html")
