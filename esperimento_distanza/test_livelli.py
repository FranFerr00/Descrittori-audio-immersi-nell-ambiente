import os
import sys
import tempfile
import unittest

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import livelli


class TestRms(unittest.TestCase):
    def test_rms_sinusoide_fondoscala(self):
        t = np.arange(48000) / 48000.0
        x = np.sin(2 * np.pi * 1000 * t)
        self.assertAlmostEqual(livelli.rms(x), 1 / np.sqrt(2), places=3)

    def test_db_meta_ampiezza(self):
        self.assertAlmostEqual(float(livelli.db(0.5) - livelli.db(1.0)), -6.0206, places=2)


class TestFinestraAttiva(unittest.TestCase):
    def test_silenzio_rumore_silenzio(self):
        rng = np.random.default_rng(0)
        sr = 48000
        burst = 0.3 * rng.standard_normal(sr)
        x = np.concatenate([np.zeros(sr), burst, np.zeros(sr)])
        i0, i1 = livelli.finestra_attiva(x, sr, frame=4096, rel_db=-30.0)
        self.assertTrue(sr - 4096 <= i0 <= sr + 4096)
        self.assertTrue(2 * sr - 4096 <= i1 <= 2 * sr + 4096)


class TestRmsPerCanale(unittest.TestCase):
    def test_due_canali_secondo_a_meta(self):
        rng = np.random.default_rng(1)
        sr = 48000
        a = 0.2 * rng.standard_normal(2 * sr)
        data = np.stack([a, 0.5 * a], axis=1)
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'x.wav')
        sf.write(p, data, sr)
        lin, dbfs = livelli.rms_per_canale(p)
        self.assertEqual(len(dbfs), 2)
        self.assertAlmostEqual(float(dbfs[0] - dbfs[1]), 6.0206, places=1)


if __name__ == '__main__':
    unittest.main()
