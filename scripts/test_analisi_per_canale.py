# scripts/test_analisi_per_canale.py
import os, sys, tempfile, unittest
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analisi


def _wav_2ch(path, sr=16000, dur=1.0):
    """canale 0 = seno 200 Hz, canale 1 = seno 4000 Hz."""
    t = np.arange(int(sr * dur)) / sr
    ch0 = 0.5 * np.sin(2 * np.pi * 200 * t)
    ch1 = 0.5 * np.sin(2 * np.pi * 4000 * t)
    sf.write(path, np.column_stack([ch0, ch1]), sr, subtype='FLOAT')


class TestLoadAudioCanale(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix='.wav'); os.close(fd)
        _wav_2ch(self.path)

    def tearDown(self):
        os.remove(self.path)

    def test_channel_seleziona_la_colonna(self):
        full, sr = sf.read(self.path)
        d0, _ = analisi.load_audio(self.path, channel=0)
        d1, _ = analisi.load_audio(self.path, channel=1)
        np.testing.assert_allclose(d0, full[:, 0])
        np.testing.assert_allclose(d1, full[:, 1])

    def test_default_media_invariata(self):
        full, sr = sf.read(self.path)
        dm, _ = analisi.load_audio(self.path)
        np.testing.assert_allclose(dm, np.mean(full, axis=1))


class TestAnalyzeCanale(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix='.wav'); os.close(fd)
        _wav_2ch(self.path)

    def tearDown(self):
        os.remove(self.path)

    def _centroide_media(self, channel):
        res, sr = analisi.analyze(self.path, max_freq=8000, channel=channel)
        vals = [r['centroid'] for r in res if not r.get('gated', 0)]
        return float(np.mean(vals))

    def test_canali_separati_differiscono(self):
        c0 = self._centroide_media(0)   # ~200 Hz
        c1 = self._centroide_media(1)   # ~4000 Hz
        cmix = self._centroide_media(None)
        self.assertLess(c0, c1)                 # basso < alto
        self.assertNotAlmostEqual(c0, cmix, delta=1.0)
        self.assertNotAlmostEqual(c1, cmix, delta=1.0)


class TestDescriptorMeans(unittest.TestCase):
    def test_media_esclude_i_gated(self):
        results = [
            {'centroid': 100.0, 'gated': 0},
            {'centroid': 200.0, 'gated': 0},
            {'centroid': 999.0, 'gated': 1},   # va ignorato
        ]
        stats = analisi.descriptor_means(results, only=['centroid'])
        media, std = stats['centroid']
        self.assertAlmostEqual(media, 150.0)
        self.assertAlmostEqual(std, 50.0)

    def test_nessun_frame_valido_ritorna_vuoto(self):
        results = [{'centroid': 1.0, 'gated': 1}]
        self.assertEqual(analisi.descriptor_means(results, only=['centroid']), {})


class TestPathConCanale(unittest.TestCase):
    def test_inserisce_prima_estensione(self):
        self.assertEqual(analisi._path_con_canale('1811.csv', 1), '1811_ch1.csv')
        self.assertEqual(analisi._path_con_canale('a/b/1811.csv', 8), 'a/b/1811_ch8.csv')

    def test_senza_estensione(self):
        self.assertEqual(analisi._path_con_canale('1811', 2), '1811_ch2')


class TestPerCanaleCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.wav2 = os.path.join(self.tmp, 'rec.wav')
        _wav_2ch(self.wav2)
        self.wav1 = os.path.join(self.tmp, 'mono.wav')
        sr = 16000
        t = np.arange(sr) / sr
        sf.write(self.wav1, 0.5 * np.sin(2 * np.pi * 1000 * t), sr, subtype='FLOAT')

    def tearDown(self):
        import shutil; shutil.rmtree(self.tmp)

    def test_due_canali_due_csv(self):
        out = os.path.join(self.tmp, 'rec.csv')
        analisi.main([self.wav2, '--only', 'centroid', '--max-freq', '8000',
                      '--no-plot', '--per-canale', '-o', out])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'rec_ch1.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'rec_ch2.csv')))
        self.assertFalse(os.path.exists(out))  # il nome nudo non viene usato

    def test_mono_avvisa_e_non_suffissa(self):
        out = os.path.join(self.tmp, 'mono.csv')
        analisi.main([self.wav1, '--only', 'centroid', '--max-freq', '8000',
                      '--no-plot', '--per-canale', '-o', out])
        self.assertTrue(os.path.exists(out))                      # output standard
        self.assertFalse(os.path.exists(
            os.path.join(self.tmp, 'mono_ch1.csv')))              # niente _ch1


if __name__ == '__main__':
    unittest.main()
