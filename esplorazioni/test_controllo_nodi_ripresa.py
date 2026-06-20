# esplorazioni/test_controllo_nodi_ripresa.py
import os, sys, unittest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import controllo_nodi_ripresa as cnr


class TestCostanti(unittest.TestCase):
    def test_nodi_distinti_e_nel_set(self):
        self.assertNotEqual(cnr.NODO_PIU, cnr.NODO_MENO)
        # i nodi devono essere descrittori? no: sono nomi di segnali, qui basta
        # che siano stringhe non vuote
        self.assertTrue(cnr.NODO_PIU and cnr.NODO_MENO)


class TestVSeries(unittest.TestCase):
    def setUp(self):
        self.MAH = np.eye(16)
        self.pP = np.zeros(16); self.pP[0] = 1.0     # polo +1
        self.pM = np.zeros(16); self.pM[0] = -1.0    # polo -1

    def test_su_un_nodo_da_piu_uno_e_meno_uno(self):
        vP = cnr.v_series(self.pP[None, :], self.pP, self.pM, self.MAH)[0]
        vM = cnr.v_series(self.pM[None, :], self.pP, self.pM, self.MAH)[0]
        self.assertAlmostEqual(vP, +1.0)
        self.assertAlmostEqual(vM, -1.0)

    def test_a_meta_strada_e_zero(self):
        mid = np.zeros(16)
        v = cnr.v_series(mid[None, :], self.pP, self.pM, self.MAH)[0]
        self.assertAlmostEqual(v, 0.0)

    def test_traslazione_comune_si_elide(self):
        # se ingresso E nodi si spostano dello stesso delta (firma del luogo
        # uniforme), v non cambia: e' la condizione di elisione del paper.
        x = np.linspace(-2, 2, 16)
        v0 = cnr.v_series(x[None, :], self.pP, self.pM, self.MAH)[0]
        delta = np.full(16, 0.7)
        v1 = cnr.v_series((x + delta)[None, :], self.pP + delta, self.pM + delta,
                          self.MAH)[0]
        self.assertAlmostEqual(v0, v1)

    def test_traslazione_non_comune_sposta_v(self):
        # se solo l'ingresso si sposta (nodi fermi), v cambia: niente elisione.
        x = np.linspace(-2, 2, 16)
        v0 = cnr.v_series(x[None, :], self.pP, self.pM, self.MAH)[0]
        v1 = cnr.v_series((x + 0.7)[None, :], self.pP, self.pM, self.MAH)[0]
        self.assertNotAlmostEqual(v0, v1)

    def test_distanze_nulle_danno_zero_non_nan(self):
        # nodi coincidenti e ingresso sul nodo: denominatore 0 -> 0, non NaN
        p = np.zeros(16)
        v = cnr.v_series(p[None, :], p, p, self.MAH)[0]
        self.assertEqual(v, 0.0)


class TestFit(unittest.TestCase):
    def test_retta_perfetta(self):
        x = np.linspace(-1, 1, 10)
        R, k = cnr.fit(x, 0.5 * x + 0.1)   # y = 0.5 x + 0.1
        self.assertAlmostEqual(R, 1.0)
        self.assertAlmostEqual(k, 0.5)

    def test_anticorrelazione_R_negativo(self):
        x = np.linspace(-1, 1, 10)
        R, k = cnr.fit(x, -0.3 * x)
        self.assertLess(R, 0.0)
        self.assertAlmostEqual(k, -0.3)

    def test_pochi_punti_da_nan(self):
        R, k = cnr.fit([0.0, 1.0], [0.0, 1.0])   # n < 3
        self.assertTrue(np.isnan(R) and np.isnan(k))

    def test_corr_summary_su_righe_finte(self):
        # due config, relazione nota fra v_studio e i due casi
        rows = []
        for cfg in ("recs-002", "recs-003"):
            for vs in np.linspace(-0.8, 0.8, 6):
                rows.append(dict(config=cfg, v_studio=vs,
                                 v_frozen=0.25 * vs, v_coripresi=0.6 * vs))
        out = cnr.corr_summary(rows)
        self.assertAlmostEqual(out["recs-002"]["k_frozen"], 0.25)
        self.assertAlmostEqual(out["recs-002"]["k_cori"], 0.6)
        self.assertAlmostEqual(out["recs-002"]["R_cori"], 1.0)


if __name__ == "__main__":
    unittest.main()
