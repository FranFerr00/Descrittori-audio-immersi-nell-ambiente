import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrazione_rms as cal


class TestScarti(unittest.TestCase):
    def test_scarto_dalla_media(self):
        dbfs = np.array([-10.0, -12.0, -8.0, -10.0])
        scarto = cal.scarti_db(dbfs)
        self.assertAlmostEqual(float(scarto.mean()), 0.0, places=6)
        self.assertAlmostEqual(float(scarto[2]), 2.0)  # -8 e' 2 dB sopra la media -10

    def test_dispersione(self):
        dbfs = np.array([-10.0, -12.0, -8.0, -10.0])
        s = cal.scarti_db(dbfs)
        self.assertAlmostEqual(float(s.max() - s.min()), 4.0)  # max-min


if __name__ == '__main__':
    unittest.main()
