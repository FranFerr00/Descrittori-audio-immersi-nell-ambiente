#!/usr/bin/env python3
"""Banco di prova: controllo bipolare a ancore e distanza.

   v = (dist_dal_-1 - dist_dal_+1) / (dist_dal_-1 + dist_dal_+1)
   identico al +1 -> +1 ; identico al -1 -> -1 ; a meta' -> 0

COME SI USA
-----------
Modifica solo il blocco << CONFIG >> qui sotto, poi:  python3 prova_ancore.py

Un'ancora puoi' scriverla in due modi:
  1) NOME DI UN SUONO  ->  "01_sinusoide_440"   (usa i suoi 16 valori reali)
  2) VALORI A MANO     ->  {"flatness": 0.10, "tpr": 25}  (in valori GREZZI;
                           i descrittori non scritti restano alla media = neutri)

ASSI = quali descrittori contano nella distanza. Lascia tutti per lo spazio
pieno, oppure scegline pochi (es. ["flatness","tpr"]) per un controllo mirato.

Per vedere l'elenco dei suoni e i range dei descrittori:  python3 prova_ancore.py --aiuto

Aggiungi --sbianca per misurare le distanze nello spazio sbiancato (Mahalanobis):
ogni dimensione vera pesa una volta sola, la brightness ridondante smette di
dominare. Senza il flag si usa la distanza z-score classica.
"""
import csv, sys, subprocess, tempfile, os

SOMMARIO = "analisi/tabelle/segnali_sommario.csv"
DESCS = ["centroid", "spread", "rolloff", "slope", "obsir_std", "flatness",
         "crest", "skewness", "kurtosis", "entropy", "tpr", "n_peaks",
         "tonality", "flux", "irregularity", "zcr"]

# Campioni ufficiali dei cataloghi strumentali: id -> etichetta dinamica.
# Sul disco ci sono anche prese di scarto, da escludere negli scan.
# Vedi diario/2026-06-01.md e cataloghi/{clarinettocb,timpano}.md
UFFICIALI = {
    "clarinettocb": {                                   # 9 ufficiali
        "001": "p1", "002": "p2", "003": "mf", "004": "f",          # tenuti
        "005": "cresc1", "006": "cresc2", "007": "dim",
        "010": "cresc-dim", "013": "dim-cresc",                     # gesti
    },
    "timpano": {                                        # 10 ufficiali
        "004": "p", "005": "mf", "006": "f1", "007": "f2",
        "008": "mf2",                                   # 008 e' un outlier
        "015": "cresc", "016": "dim", "018": "dim-cresc-lungo",
        "023": "dim-cresc-corto", "025": "cresc-dim",              # gesti
    },
}

# ======================== << CONFIG >> ========================
ASSI   = DESCS                      # oppure es. ["flatness", "tpr"]
A_PIU  = "01_sinusoide_440"         # +1  -> param SU
A_MENO = "02_noise_bianco"          # -1  -> param GIU
# esempi alternativi:
#   A_PIU  = {"centroid": 5000, "flatness": 0.85}   # punto a mano
#   A_MENO = "17_noise100"
# =============================================================

rows = list(csv.DictReader(open(SOMMARIO)))
names = [r["segnale"] for r in rows]
def col(n): return [float(r[n + "_mean"]) for r in rows]
def stat(n):
    c = col(n); m = sum(c) / len(c)
    sd = (sum((x - m) ** 2 for x in c) / len(c)) ** 0.5 or 1.0
    return m, sd
TAR = {d: stat(d) for d in DESCS}
def z(d, x): m, sd = TAR[d]; return (x - m) / sd
COORD = {names[i]: {d: z(d, col(d)[i]) for d in DESCS} for i in range(len(names))}

if "--aiuto" in sys.argv:
    print("SUONI disponibili:")
    for n in names: print("  " + n)
    print("\nRANGE dei descrittori (per scrivere punti a mano in grezzo):")
    print(f"  {'descrittore':12s} {'min':>10s} {'media':>10s} {'max':>10s}")
    for d in DESCS:
        c = col(d); print(f"  {d:12s} {min(c):10.2f} {sum(c)/len(c):10.2f} {max(c):10.2f}")
    sys.exit()

def punto(spec):
    """Trasforma un'ancora (nome suono o dict grezzo) in coordinate z-score."""
    if isinstance(spec, str):
        return COORD[spec]
    return {d: (z(d, spec[d]) if d in spec else 0.0) for d in DESCS}

Pp = punto(A_PIU); Pm = punto(A_MENO)

SBIANCA = "--sbianca" in sys.argv
if SBIANCA:
    # distanza di Mahalanobis sugli assi scelti: scorrela e rimette in scala,
    # cosi' la brightness ridondante non viene contata piu' volte
    import numpy as np
    ai = list(ASSI)
    Zmat = np.array([[z(d, col(d)[i]) for d in ai] for i in range(len(names))])
    MAH = np.linalg.inv(np.atleast_2d(np.corrcoef(Zmat.T)))
    def dist(a, b):
        d = np.array([a[x] - b[x] for x in ai])
        return float(d @ MAH @ d) ** 0.5
else:
    def dist(a, b): return sum((a[d] - b[d]) ** 2 for d in ASSI) ** 0.5

def vval(coord):
    dp = dist(coord, Pp); dm = dist(coord, Pm)
    return (dm - dp) / (dm + dp) if (dm + dp) else 0.0

print(f"assi   : {ASSI if ASSI != DESCS else 'tutti e 16'}")
print(f"metrica: {'sbiancata (Mahalanobis)' if SBIANCA else 'z-score'}")
print(f"+1 (SU): {A_PIU}")
print(f"-1(GIU): {A_MENO}")

# --- modo 1: un file audio tuo (--wav PATH) -> v frame per frame ---
if "--wav" in sys.argv:
    wav = sys.argv[sys.argv.index("--wav") + 1]
    tmp = tempfile.mktemp(suffix=".csv")
    print(f"\nanalizzo {wav} ...")
    subprocess.run(["python3", "analisi.py", wav, "-w", "hann", "--overlap", "0.5",
                    "--max-freq", "10000", "--no-plot", "-o", tmp], check=True)
    serie = []
    for r in csv.DictReader(open(tmp)):
        if r.get("gated", "0") == "1":
            continue
        coord = {d: z(d, float(r[d])) for d in DESCS}
        serie.append((float(r["time"]), vval(coord)))
    os.remove(tmp)
    if not serie:
        print("nessun frame sopra soglia."); sys.exit()
    ts = [t for t, _ in serie]; vs = [v for _, v in serie]
    # v lisciato: media mobile ~1 s (10 frame)
    N = 10
    vlis = [sum(vs[max(0, i - N + 1):i + 1]) / len(vs[max(0, i - N + 1):i + 1])
            for i in range(len(vs))]
    print(f"\nframe analizzati: {len(serie)}")
    print(f"v   minimo {min(vs):+.2f}   medio {sum(vs)/len(vs):+.2f}   massimo {max(vs):+.2f}")
    base = os.path.splitext(os.path.basename(wav))[0]
    # CSV completo tempo, v, v_lisciato
    out_csv = f"desc/v_{base}.csv"
    os.makedirs("desc", exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["time", "v", "v_lisciato"])
        for t, v, vl in zip(ts, vs, vlis):
            w.writerow([f"{t:.3f}", f"{v:.4f}", f"{vl:.4f}"])
    # grafico
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(13, 5))
        ax.plot(ts, vs, color="#9aa0a6", lw=0.6, label="v grezzo")
        ax.plot(ts, vlis, color="#2471a3", lw=1.8, label="v lisciato (~1 s)")
        ax.axhline(0, color="k", lw=0.6)
        ax.axhline(1, color="#2471a3", ls=":", lw=0.8); ax.axhline(-1, color="#c0392b", ls=":", lw=0.8)
        ax.set_ylim(-1.05, 1.05); ax.set_xlabel("tempo (s)"); ax.set_ylabel("v")
        ax.set_title(f"v frame per frame  {base}\n+1={A_PIU}   -1={A_MENO}")
        ax.legend(loc="upper right"); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(f"desc/v_{base}.png", dpi=120)
        print(f"salvato desc/v_{base}.png  e  {out_csv}")
    except Exception as e:
        print(f"(grafico saltato: {e})  serie salvata in {out_csv}")
    sys.exit()

# --- modo 2 (default): classifica dei 45 suoni del corpus ---
V = {n: vval(COORD[n]) for n in names}
print(f"corsa  : {min(V.values()):+.2f} -> {max(V.values()):+.2f}\n")
for n in sorted(names, key=lambda n: V[n])[::-1]:
    print(f"  {V[n]:+.2f}  {n}")
