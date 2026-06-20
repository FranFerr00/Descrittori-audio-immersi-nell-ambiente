import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attenuazione_distanza as att


class TestTeorico(unittest.TestCase):
    def test_campo_libero_6db_per_raddoppio(self):
        v = att.teorico_campolibero([1, 2, 4, 8])
        self.assertAlmostEqual(float(v[0]), 0.0)
        self.assertAlmostEqual(float(v[1]), -6.0206, places=2)
        self.assertAlmostEqual(float(v[2]), -12.0412, places=2)
        self.assertAlmostEqual(float(v[3]), -18.0618, places=2)

    def test_per_raddoppio_3db(self):
        v = att.teorico_per_raddoppio([1, 2, 4, 8], -3.0)
        self.assertAlmostEqual(float(v[0]), 0.0)
        self.assertAlmostEqual(float(v[1]), -3.0)
        self.assertAlmostEqual(float(v[2]), -6.0)
        self.assertAlmostEqual(float(v[3]), -9.0)


class TestRaddoppi(unittest.TestCase):
    def test_delta_per_raddoppio(self):
        rel = np.array([0.0, -5.0, -7.0, -11.0, -12.0, -13.0, -14.0, -19.0])
        r = att.raddoppi(np.arange(1, 9), rel)
        self.assertEqual([(a, b) for a, b, _ in r], [(1, 2), (2, 4), (4, 8)])
        self.assertAlmostEqual(r[0][2], -5.0)   # 1->2 m
        self.assertAlmostEqual(r[1][2], -6.0)   # 2->4 m: -11 - (-5)
        self.assertAlmostEqual(r[2][2], -8.0)   # 4->8 m: -19 - (-11)


if __name__ == '__main__':
    unittest.main()
