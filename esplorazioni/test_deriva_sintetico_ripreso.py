# esplorazioni/test_deriva_sintetico_ripreso.py
import os, sys, math, tempfile, csv, unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deriva_sintetico_ripreso as drv


class TestCostanti(unittest.TestCase):
    def test_descs_sedici_e_unici(self):
        self.assertEqual(len(drv.DESCS), 16)
        self.assertEqual(len(set(drv.DESCS)), 16)

    def test_configs_quattro_con_controllo(self):
        self.assertIn("test_segnali_-30db", drv.CONFIGS)
        self.assertEqual(len(drv.CONFIGS), 4)


class TestTaratura(unittest.TestCase):
    def _sommario(self, righe):
        # scrive un segnali_sommario.csv minimo con colonne <descr>_mean
        fd, path = tempfile.mkstemp(suffix=".csv"); os.close(fd)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["segnale"] + [d + "_mean" for d in drv.DESCS])
            for nome, vals in righe:
                w.writerow([nome] + vals)
        return path

    def test_media_e_std_congelate(self):
        # centroid vale 0 e 10 nei due segnali -> media 5, std 5 (popolazione)
        v0 = [0.0] * len(drv.DESCS)
        v10 = [10.0] * len(drv.DESCS)
        path = self._sommario([("a", v0), ("b", v10)])
        tar = drv.load_taratura(path)
        m, sd = tar["centroid"]
        self.assertAlmostEqual(m, 5.0)
        self.assertAlmostEqual(sd, 5.0)


class TestLoadFrames(unittest.TestCase):
    def _analisi_csv(self, frames):
        # frames: lista di (dict descr->raw, gated_str)
        fd, path = tempfile.mkstemp(suffix=".csv"); os.close(fd)
        cols = ["frame", "time"] + drv.DESCS + ["gated"]
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for i, (vals, g) in enumerate(frames):
                row = {"frame": i, "time": i * 0.05, "gated": g}
                row.update({d: vals[d] for d in drv.DESCS})
                w.writerow(row)
        return path

    def test_zscore_dai_grezzi_e_gated(self):
        tar = {d: (0.0, 2.0) for d in drv.DESCS}  # z = raw/2
        raw = {d: 4.0 for d in drv.DESCS}
        path = self._analisi_csv([(raw, "0"), (raw, "1")])
        Z, gated = drv.load_frames(path, tar)
        self.assertEqual(Z.shape, (2, 16))
        self.assertTrue(np.allclose(Z, 2.0))      # 4/2 = 2
        self.assertEqual(list(gated), [False, True])


class TestSbiancamento(unittest.TestCase):
    def test_whitening_from_Z_quasi_identita_se_scorrelati(self):
        rng = np.random.default_rng(0)
        Z = rng.standard_normal((4000, 16))   # colonne indipendenti, var 1
        MAH = drv.whitening_from_Z(Z)
        self.assertEqual(MAH.shape, (16, 16))
        self.assertTrue(np.allclose(MAH, np.eye(16), atol=0.15))

    def test_whitening_simmetrica(self):
        rng = np.random.default_rng(1)
        Z = rng.standard_normal((500, 16))
        MAH = drv.whitening_from_Z(Z)
        self.assertTrue(np.allclose(MAH, MAH.T, atol=1e-8))


class TestFrameDrift(unittest.TestCase):
    def test_sintetico_con_se_stesso_e_zero(self):
        Z = np.arange(48, dtype=float).reshape(3, 16)
        g = np.zeros(3, dtype=bool)
        d_z, d_mah, nv, nt = drv.frame_drift(Z, g, Z, g, np.eye(16))
        self.assertEqual((nv, nt), (3, 3))
        self.assertTrue(np.allclose(d_z, 0.0))
        self.assertTrue(np.allclose(d_mah, 0.0))

    def test_solo_frame_validi_in_entrambe(self):
        Z0 = np.zeros((4, 16))
        Z1 = np.ones((4, 16))
        gref = np.array([False, True, False, False])
        gcfg = np.array([False, False, True, False])
        d_z, d_mah, nv, nt = drv.frame_drift(Z0, gref, Z1, gcfg, np.eye(16))
        self.assertEqual((nv, nt), (2, 4))            # frame 0 e 3 validi in entrambe
        self.assertTrue(np.allclose(d_z, 4.0))        # sqrt(16 * 1^2) = 4

    def test_mah_identita_uguale_euclidea(self):
        rng = np.random.default_rng(2)
        Zr = rng.standard_normal((10, 16)); Zc = rng.standard_normal((10, 16))
        g = np.zeros(10, dtype=bool)
        d_z, d_mah, _, _ = drv.frame_drift(Zr, g, Zc, g, np.eye(16))
        self.assertTrue(np.allclose(d_z, d_mah))


class TestSummarize(unittest.TestCase):
    def test_statistiche_e_copertura(self):
        d_z = np.array([1.0, 3.0])
        d_mah = np.array([2.0, 4.0])
        s = drv.summarize(d_z, d_mah, n_valid=2, n_total=4)
        self.assertAlmostEqual(s["mean_z"], 2.0)
        self.assertAlmostEqual(s["median_z"], 2.0)
        self.assertAlmostEqual(s["max_z"], 3.0)
        self.assertAlmostEqual(s["mean_mah"], 3.0)
        self.assertAlmostEqual(s["median_mah"], 3.0)
        self.assertAlmostEqual(s["coverage"], 0.5)

    def test_zero_validi_da_nan_e_copertura_zero(self):
        s = drv.summarize(np.array([]), np.array([]), n_valid=0, n_total=5)
        self.assertTrue(math.isnan(s["mean_z"]))
        self.assertTrue(math.isnan(s["mean_mah"]))
        self.assertEqual(s["coverage"], 0.0)


if __name__ == "__main__":
    unittest.main()
