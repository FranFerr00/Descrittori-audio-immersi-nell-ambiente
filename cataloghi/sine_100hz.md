# Test sinusoide a 100 Hz — riferimento per il timpano sostenuto

Nota di controllo: sia il catalogo clarinetto contrabbasso sia il
catalogo timpano aumentato sono stati registrati con **fondamentale
fissa attorno a 100 Hz**. Su nessuno dei 16 descrittori questa
informazione e' esplicita: nessun descrittore del set restituisce
"100 Hz" come valore atteso per la fondamentale. Volevo vedere cosa
fanno i 16 descrittori su un segnale in cui la fondamentale e' *tutto*
quello che c'e', cioe' una sinusoide pura a 100 Hz, per avere un
riferimento numerico contro cui leggere il regime sostenuto del timpano
aumentato.

## Il segnale

Generato con numpy:

```python
sr = 96000
dur = 3.0
t = np.arange(int(sr*dur))/sr
x = 0.5*np.sin(2*np.pi*100*t)
sf.write('segnali/test_sine_100hz.wav', x, sr, subtype='FLOAT')
```

3 secondi, 96 kHz, sinusoide pura a 100 Hz, ampiezza 0.5. Analizzato
con la stessa pipeline dei cataloghi (`analisi.py`, FFT 8192, hop 4096,
Hann, max_freq 10 kHz).

Parametri rilevanti della FFT a 96 kHz con finestra 8192:
risoluzione ~11.72 Hz/bin, quindi i primi bin utili sono a
**93.75 Hz** e **105.47 Hz**. Una sinusoide a 100 Hz cade *fra* i due
bin: la maggior parte dell'energia finisce sul bin 105.47 ma c'e'
dispersione spettrale (il leakage della finestra Hann) sul bin 93.75
e sui vicini.

## Valori dei 16 descrittori sulla sinusoide pura

| descrittore  | valore     |
|--------------|------------|
| centroid     | 100.0      |
| spread       | **11.7**   |
| rolloff      | 105.47     |
| slope        | ~0         |
| obsir_std    | 0.301      |
| flatness     | 0.099      |
| crest        | 6.1        |
| skewness     | -0.21      |
| kurtosis     | 6.7        |
| entropy      | 0.128      |
| tonality     | 0.171      |
| tpr          | 0.99       |
| n_peaks      | ~1         |
| flux         | ~0         |
| irregularity | 25         |
| zcr          | 0.00208    |

Il centroid esce esattamente a 100 Hz: e' il baricentro fra i due bin
93.75 e 105.47 pesati in ampiezza, che coincide numericamente con la
frequenza della sinusoide. Il rolloff e' **105.47 Hz**, cioe' il primo
bin dove l'energia cumulata supera la soglia: e' il secondo bin utile
della FFT, non una "saturazione" e non un minimo del filtro. E' il
valore reale di una sinusoide a 100 Hz.

## Confronto con il timpano 004 (p) in regime sostenuto

| descrittore  | sine 100 Hz | timp 004 p | delta |
|--------------|-------------|------------|-------|
| centroid     | 100.0       | 125        | +25   |
| spread       | **11.7**    | **127**    | **+115** |
| rolloff      | 105.47      | 130        | +25   |
| flatness     | 0.099       | 0.104      | ~0    |
| crest        | 6.1         | 14.7       | +8.6  |
| tonality     | 0.171       | 0.167      | ~0    |
| zcr          | 0.00208     | 0.00283    | ~0    |
| irregularity | 25          | 53         | +28   |

**L'unico descrittore che separa chiaramente la sinusoide pura dal
timpano sostenuto e' lo spread:** 11.7 Hz contro 127 Hz, un fattore 11.
La sinusoide ha uno spread pari a *un solo bin* (il limite di
risoluzione della FFT), il timpano ne ha circa 10: significa che lo
spettro del timpano in regime non e' solo la fondamentale ma contiene
qualcosa d'altro, probabilmente armonici deboli e rumore di banda
introdotto dal circuito di induzione. Tutti gli altri descrittori
(tonality, zcr, flatness, crest nella stessa scala) lo vedono come
"sinusoidale".

Il centroid a 125 invece di 100, e rolloff a 130 invece di 105.47, sono
spostamenti minimi che corrispondono alla presenza di *un po'* di
energia un bin piu' in alto. Crest a 14.7 vs 6.1 e' l'altra differenza
sensibile, e riflette il fatto che sulla sinusoide tutta l'energia e'
in uno o due bin (picco relativamente poco piccato nello spettro di
potenza normalizzato), mentre sul timpano c'e' un picco piu' marcato
rispetto alla coda di bin circostanti.

## Confronto con il clarinetto 001 (p1)

| descrittore  | sine 100 Hz | clar 001 p1 | delta |
|--------------|-------------|-------------|-------|
| centroid     | 100.0       | 211         | +111  |
| spread       | 11.7        | 295         | +283  |
| rolloff      | 105.47      | 314         | +208  |
| crest        | 6.1         | 29.3        | +23   |
| irregularity | 25          | 150         | +125  |

Il clarinetto anche sul piano piu' basso si separa nettamente dalla
sinusoide: centroid piu' che raddoppiato, spread 25x, rolloff 3x.
Questo conferma che sul clarinetto gli armonici sopra la fondamentale
a 100 Hz sono gia' al piano molto piu' forti della fondamentale
stessa, e sono quelli che contano per i descrittori di forma.
Sul timpano sostenuto invece gli armonici sono cosi' deboli che i
descrittori di forma "vedono" praticamente solo la fondamentale.

## Cosa ne ricavo

1. **La sinusoide a 100 Hz e' il baseline numerico del timpano in
   regime sostenuto.** Il timpano sostenuto e' una quasi-sinusoide a
   100 Hz, non un "colpo" o un "tono percussivo" con coda. Su quasi
   tutti i descrittori i due segnali sono indistinguibili: la
   differenza e' solo nello spread (e in parte nel crest e
   nell'irregularity).

2. **Il rolloff 105.47 Hz del timpano NON e' un artefatto da
   risoluzione FFT o una saturazione del filtro:** e' il rolloff vero
   di un segnale a 100 Hz con pochi parziali e calcolato con FFT 8192
   @ 96 kHz. Su qualunque segnale quasi-sinusoidale a 100 Hz con
   questa pipeline si otterra' lo stesso valore.

3. **Lo spread e' il descrittore spettrale piu' sensibile alla
   presenza di contenuto oltre la fondamentale** su segnali dominati
   dalla fondamentale: la sinusoide pura sta al limite di risoluzione
   (1 bin = 11.7 Hz), il timpano sostenuto e' a ~10 bin. Puo' essere
   utile come indicatore di "quanta struttura c'e' oltre la
   fondamentale" nei casi in cui centroid e rolloff sono inchiodati
   al bin della fondamentale.

4. **Sul clarinetto la fondamentale a 100 Hz non e' "visibile"
   direttamente nei descrittori** perche' gli armonici dominano lo
   spettro gia' al piano. Questo spiega perche' il catalogo
   clarinetto ha dinamica leggibile sui descrittori di forma mentre
   il timpano sostenuto no: non e' che i descrittori funzionano meglio
   sul clarinetto, e' che sul clarinetto c'e' semplicemente *piu'
   contenuto spettrale* che varia con la dinamica.

## Riutilizzo

Il file `segnali/test_sine_100hz.wav` e' rigenerabile in ogni momento
con lo snippet all'inizio di questa scheda. Utile come riferimento
fisso: quando un campione del corpus restituisce centroid ~100 e
rolloff ~105, il confronto diretto con questo file dice se si tratta
di una fondamentale isolata o di una fondamentale con armonici
deboli.
