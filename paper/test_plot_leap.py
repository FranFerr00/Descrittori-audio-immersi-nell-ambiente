"""Test leggeri per gli script delle figure del LEAP.

Verificano che ogni script giri senza errori e produca un PDF non vuoto a partire
dai CSV gia' prodotti dalla pipeline dell'esperimento (analisi/distanza*/).
Stile unittest, coerente con gli altri test del progetto. Eseguire con:
    python -m unittest paper.test_plot_leap
oppure, da dentro paper/:  python -m unittest test_plot_leap
"""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _run(script):
    r = subprocess.run([sys.executable, str(HERE / script)],
                       capture_output=True, text=True)
    return r


class TestFigureLeap(unittest.TestCase):
    def _check(self, script, pdf_name):
        r = _run(script)
        self.assertEqual(r.returncode, 0, f"{script} fallito:\n{r.stderr}")
        pdf = HERE / pdf_name
        self.assertTrue(pdf.exists(), f"{pdf_name} non prodotto")
        self.assertGreater(pdf.stat().st_size, 1000, f"{pdf_name} troppo piccolo")

    def test_centroide_rumore_pdf(self):
        self._check("plot_leap_centroide_rumore.py", "figura_leap_centroide_rumore.pdf")

    def test_onda_ccb_pdf(self):
        self._check("plot_leap_onda_ccb.py", "figura_leap_onda_ccb.pdf")

    def test_attenuazione_pdf(self):
        self._check("plot_leap_attenuazione.py", "figura_leap_attenuazione.pdf")


if __name__ == "__main__":
    unittest.main()
