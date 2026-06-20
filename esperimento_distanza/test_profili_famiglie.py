import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import profili_famiglie as pf


class TestMedieFile(unittest.TestCase):
    def _scrivi(self, folder, base, ch, righe):
        path = os.path.join(folder, f'{base}_ch{ch}_hann_ov50_10000hz_analisi.csv')
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['frame', 'time', 'centroid', 'gated'])
            for i, (t, g, c) in enumerate(righe):
                w.writerow([i, t, c, g])

    def test_media_in_finestra(self):
        d = tempfile.mkdtemp()
        base = 'CCB_x_oriz_CLUSTER1'
        folder = os.path.join(d, base)
        os.makedirs(folder, exist_ok=True)
        for ch in (1, 2):
            self._scrivi(folder, base, ch, [
                (0.0, '1', 0.0),
                (4.0, '0', 100.0 * ch),
                (5.0, '0', 200.0 * ch),
                (6.0, '0', 300.0 * ch),
                (10.0, '1', 0.0),
            ])
        res = pf.medie_file(folder, base)
        # frame non-gated a t=4,5,6 -> centro 5, finestra [4,6] -> tutti e 3
        self.assertAlmostEqual(res[1]['centroid'], 200.0)
        self.assertAlmostEqual(res[2]['centroid'], 400.0)


if __name__ == '__main__':
    unittest.main()
