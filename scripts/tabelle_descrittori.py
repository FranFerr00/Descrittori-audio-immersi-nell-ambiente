"""Genera tabelle per descrittore: righe = segnali/modi di ripresa, colonne = statistiche.

Legge i file *_analisi.csv prodotti da analisi.py e produce, per ciascun descrittore,
una tabella che mostra come quel descrittore si comporta nei vari segnali (o nei vari
modi di ripresa). Utile per confrontare il comportamento del singolo descrittore
attraverso l'intero corpus di test.
"""

import csv
import os
import glob
import numpy as np

# Filtro di banda: se DESC_BAND e' impostato (es. "48000"), i glob *_analisi.csv
# selezionano solo i CSV di quella banda, evitando ambiguita' quando convivono piu'
# bande nella stessa cartella (es. _10000hz e _48000hz). Vuoto = comportamento storico.
BAND = os.environ.get("DESC_BAND", "")


def _glob_analisi(folder):
    pat = f"*_{BAND}hz_analisi.csv" if BAND else "*_analisi.csv"
    return glob.glob(os.path.join(folder, pat))


DESCRIPTORS = [
    'centroid', 'spread', 'rolloff', 'slope', 'obsir_std',
    'flatness', 'crest', 'skewness', 'kurtosis', 'entropy',
    'tpr', 'n_peaks', 'tonality',
    'flux', 'irregularity', 'zcr',
]

STATS = ['min', 'max', 'mean', 'std', 'median']


def read_csv(path):
    """Legge un _analisi.csv e ritorna un dict {descrittore: array}."""
    data = {k: [] for k in DESCRIPTORS}
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k in DESCRIPTORS:
                if k in row:
                    data[k].append(float(row[k]))
    return {k: np.array(v) for k, v in data.items()}


def compute_stats(values):
    if len(values) == 0:
        return {s: 0.0 for s in STATS}
    return {
        'min': float(np.min(values)),
        'max': float(np.max(values)),
        'mean': float(np.mean(values)),
        'std': float(np.std(values)),
        'median': float(np.median(values)),
    }


def collect_signals(segnali_dir):
    """Scansiona le sottocartelle numerate e ritorna [(nome, path_csv), ...]."""
    entries = []
    for sub in sorted(os.listdir(segnali_dir)):
        full = os.path.join(segnali_dir, sub)
        if not os.path.isdir(full):
            continue
        if not sub[:2].isdigit():
            continue
        csvs = _glob_analisi(full)
        if csvs:
            entries.append((sub, sorted(csvs)[0]))
    return entries


def collect_recs(segnali_dir):
    """Raccoglie i CSV dei modi di ripresa (recs-*_analisi.csv in segnali/)."""
    entries = []
    for path in sorted(glob.glob(os.path.join(segnali_dir, 'recs-*_analisi.csv'))):
        name = os.path.basename(path).split('_hann')[0]
        entries.append((name, path))
    return entries


def collect_modes(analisi_dir):
    """Ritorna struttura per confronto per-segnale attraverso i modi di ripresa.

    {nome_segnale: {modo: path_csv}}. Il modo 'sintetico' e' il taglio di
    test_segnali.wav (analisi/sintetici/NN_*/). Ogni altra sottocartella
    di primo livello (es. analisi/recs-002/, analisi/test_segnali_-30db/) che
    contiene segmenti NN_* e' trattata come un ulteriore modo.
    """
    result = {}
    # sintetici: analisi/sintetici/NN_*/
    sintetici_dir = os.path.join(analisi_dir, 'sintetici')
    if os.path.isdir(sintetici_dir):
        for sub in sorted(os.listdir(sintetici_dir)):
            full = os.path.join(sintetici_dir, sub)
            if not os.path.isdir(full) or not sub[:2].isdigit():
                continue
            csvs = _glob_analisi(full)
            if csvs:
                result.setdefault(sub, {})['sintetico'] = sorted(csvs)[0]
    # altri modi: analisi/<modo>/NN_*/
    for sub in sorted(os.listdir(analisi_dir)):
        if sub in ('sintetici', 'tabelle') or sub.startswith('.'):
            continue
        full = os.path.join(analisi_dir, sub)
        if not os.path.isdir(full):
            continue
        mode = sub
        for sub2 in sorted(os.listdir(full)):
            full2 = os.path.join(full, sub2)
            if not os.path.isdir(full2) or not sub2[:2].isdigit():
                continue
            csvs = _glob_analisi(full2)
            if csvs:
                result.setdefault(sub2, {})[mode] = sorted(csvs)[0]
    return result


def build_table(entries):
    """Ritorna {descrittore: [(nome, stats_dict), ...]}."""
    tables = {d: [] for d in DESCRIPTORS}
    for name, path in entries:
        data = read_csv(path)
        for d in DESCRIPTORS:
            tables[d].append((name, compute_stats(data[d])))
    return tables


def save_tables(tables, out_dir, prefix):
    os.makedirs(out_dir, exist_ok=True)
    for d, rows in tables.items():
        path = os.path.join(out_dir, f'{prefix}_{d}.csv')
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['segnale'] + STATS)
            for name, stats in rows:
                writer.writerow([name] + [f'{stats[s]:.6g}' for s in STATS])
        print(f'  {path}')


def _fmt(x):
    """Formattazione compatta per markdown."""
    ax = abs(x)
    if ax == 0:
        return '0'
    if ax >= 1000:
        return f'{x:.0f}'
    if ax >= 10:
        return f'{x:.1f}'
    if ax >= 1:
        return f'{x:.2f}'
    if ax >= 0.01:
        return f'{x:.3f}'
    return f'{x:.2e}'


def save_markdown(tables, out_dir, prefix, title):
    """Un unico file .md con una tabella per descrittore."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'{prefix}_tabelle.md')
    with open(path, 'w') as f:
        f.write(f'# {title}\n\n')
        for d in DESCRIPTORS:
            rows = tables[d]
            if not rows:
                continue
            f.write(f'## {d}\n\n')
            f.write('| Segnale | Min | Max | Media | Std | Mediana |\n')
            f.write('|---|---|---|---|---|---|\n')
            for name, stats in rows:
                f.write(f'| {name} | {_fmt(stats["min"])} | {_fmt(stats["max"])} '
                        f'| {_fmt(stats["mean"])} | {_fmt(stats["std"])} '
                        f'| {_fmt(stats["median"])} |\n')
            f.write('\n')
    print(f'  {path}')


def save_confronto_markdown(modes_data, out_dir):
    """Per ogni descrittore, tabella con righe = segnale, colonne = modo di ripresa (media)."""
    os.makedirs(out_dir, exist_ok=True)
    # ordine colonne: sintetico, poi gli altri modi in ordine alfabetico
    all_modes = set()
    for sig, mmap in modes_data.items():
        all_modes.update(mmap.keys())
    mode_order = ['sintetico'] + sorted(m for m in all_modes if m != 'sintetico')
    mode_order = [m for m in mode_order if m in all_modes]

    signals = sorted(modes_data.keys())

    # pre-calcola medie: {segnale: {modo: {descrittore: mean}}}
    cache = {}
    for sig in signals:
        cache[sig] = {}
        for mode, path in modes_data[sig].items():
            data = read_csv(path)
            cache[sig][mode] = {d: float(np.mean(data[d])) if len(data[d]) else 0.0
                                for d in DESCRIPTORS}

    path = os.path.join(out_dir, 'confronto_modi_tabelle.md')
    with open(path, 'w') as f:
        f.write('# Confronto dei descrittori: segnale sintetico vs modi di ripresa\n\n')
        f.write('Valori medi del descrittore sul singolo segnale. Colonne: `sintetico` '
                '(taglio di test_segnali.wav), `test_segnali_-30db` (stesso file scalato '
                'di -30 dB), `recs-002` (microfono a 1 m), `recs-003` (microfono a 2 m, '
                'ambiente sporco), `recs-004` (microfono a 2 m, ambiente pulito).\n\n')
        for d in DESCRIPTORS:
            f.write(f'## {d}\n\n')
            header = '| Segnale | ' + ' | '.join(mode_order) + ' |\n'
            sep = '|---' * (len(mode_order) + 1) + '|\n'
            f.write(header)
            f.write(sep)
            for sig in signals:
                row = [sig]
                for mode in mode_order:
                    if mode in cache[sig]:
                        row.append(_fmt(cache[sig][mode][d]))
                    else:
                        row.append('—')
                f.write('| ' + ' | '.join(row) + ' |\n')
            f.write('\n')
    print(f'  {path}')


def save_combined(tables, out_dir, prefix):
    """Tabella unica: righe = segnali, colonne = descrittore_stat (solo mean e std)."""
    os.makedirs(out_dir, exist_ok=True)
    if not tables[DESCRIPTORS[0]]:
        return
    names = [n for n, _ in tables[DESCRIPTORS[0]]]
    path = os.path.join(out_dir, f'{prefix}_sommario.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['segnale']
        for d in DESCRIPTORS:
            header += [f'{d}_mean', f'{d}_std']
        writer.writerow(header)
        for i, name in enumerate(names):
            row = [name]
            for d in DESCRIPTORS:
                stats = tables[d][i][1]
                row += [f'{stats["mean"]:.6g}', f'{stats["std"]:.6g}']
            writer.writerow(row)
    print(f'  {path}')


if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analisi_dir = os.path.join(root_dir, 'analisi')
    sintetici_dir = os.path.join(analisi_dir, 'sintetici')
    out_dir = os.path.join(analisi_dir, 'tabelle')

    print('Segnali sintetici:')
    signals = collect_signals(sintetici_dir)
    if signals:
        tables = build_table(signals)
        save_tables(tables, out_dir, 'segnali')
        save_combined(tables, out_dir, 'segnali')
        save_markdown(tables, out_dir, 'segnali', 'Descrittori sui segnali sintetici')
    else:
        print('  nessun CSV trovato')

    print('\nConfronto per-segnale attraverso i modi di ripresa:')
    modes = collect_modes(analisi_dir)
    if modes:
        save_confronto_markdown(modes, out_dir)
    else:
        print('  nessun CSV trovato')
