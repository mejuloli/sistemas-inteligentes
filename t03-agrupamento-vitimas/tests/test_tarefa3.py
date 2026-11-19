"""Testes do pipeline, dos arquivos e da reprodução."""
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import main
from visualizador import capture


class Tarefa3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.victims = main.load_map(ROOT / "map.csv")
        cls.predicted = main.predict(cls.victims, ROOT / "modelos")

    def test_map(self):
        self.assertEqual(len(self.cells), 5625)
        self.assertEqual(len(self.victims), 410)
        self.assertEqual(self.victims.id.nunique(), 410)
        self.assertEqual(self.cells.id.eq(-1).sum(), 5215)
        self.assertTrue(self.cells[["tri", "sobr"]].eq(-1).all().all())
        self.assertTrue(np.isfinite(self.cells.to_numpy()).all())

    def test_reject_invalid_map(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "map.csv"
            cases = [
                self.cells.drop(columns=["avpu"]),
                pd.concat([self.cells.iloc[:-1], self.cells.iloc[:1]]),
                self.cells.assign(tri=0),
                self.cells.assign(obst=np.nan),
                self.cells.assign(obst=-1),
                self.cells.assign(id=self.cells.id.clip(upper=10)),
            ]
            for cells in cases:
                cells.to_csv(path, index=False)
                with self.assertRaises(ValueError):
                    main.load_map(path)

    def test_predictions_transformations_and_no_leakage(self):
        x = self.victims["idade fc fr pas spo2 temp pr sg fx queim".split()]
        t1 = joblib.load(ROOT / "modelos/t1/melhor_rn.joblib")
        t2 = joblib.load(ROOT / "modelos/t2/melhor_rn.joblib")
        scaler = joblib.load(ROOT / "modelos/t2/scaler.joblib")
        self.assertEqual(list(t1.feature_names_in_), list(x))
        self.assertEqual(list(scaler.feature_names_in_), list(x))
        expected = t2.predict((x.to_numpy() - scaler.mean_) / scaler.scale_)
        np.testing.assert_allclose(self.predicted.sobr_bruta, expected)
        np.testing.assert_allclose(self.predicted.sobr, np.clip(expected, 0, 1))
        np.testing.assert_array_equal(self.predicted.tri, t1.predict(x))
        self.assertTrue(self.predicted.tri.isin(range(4)).all())
        self.assertTrue(self.predicted.sobr.between(0, 1).all())
        changed = self.victims.assign(gcs=3, avpu=3, tri=3, sobr=1)
        pd.testing.assert_frame_equal(main.predict(changed, ROOT / "modelos")[["tri", "sobr"]],
                                      self.predicted[["tri", "sobr"]])

    def test_normalization(self):
        points = pd.DataFrame({"x_rel": [-30, 44], "y_rel": [-40, 34], "sobr": [0, 1]})
        np.testing.assert_array_equal(main.strategy_space(points), [[0, 0, 0], [1, 1, 0.45]])
        self.assertTrue(((main.strategy_space(self.predicted) >= 0) &
                         (main.strategy_space(self.predicted) <= 1)).all())

    def test_sse_silhouette_coverage_score(self):
        points = np.array([[0.], [2.], [10.], [12.]])
        with threadpool_limits(limits=1):
            labels, metrics = main.kmeans(points, 2)
        self.assertAlmostEqual(metrics["SSE"], 4.0)
        expected = (2 * (1-2/11) + 2 * (1-2/9)) / 4
        self.assertAlmostEqual(metrics["silhueta"], expected)
        noise_points = np.r_[points, [[100.]]]
        result = main.silhouette_coverage(noise_points, np.r_[labels, -1])
        self.assertEqual(result["clusters"], 2)
        self.assertEqual(result["ruido"], 1)
        self.assertAlmostEqual(result["cobertura"], 0.8)
        self.assertAlmostEqual(result["silhueta"], expected)
        self.assertAlmostEqual(result["score"], 0.8 * expected)
        for missing in ([-1]*4, [0]*4, [0, 1, 2, 3], [0, 1, -1, -1]):
            result = main.silhouette_coverage(points, missing)
            self.assertIsNone(result["silhueta"])
            self.assertIsNone(result["score"])

    def test_cluster_output_and_repeatability(self):
        output = ROOT / "outputs"
        basic = pd.read_csv(output / "basico.csv")
        self.assertEqual(basic.K.tolist(), list(range(2, 13)))
        self.assertTrue(basic.SSE.is_monotonic_decreasing)
        strategy = pd.read_csv(output / "estrategia.csv")
        self.assertEqual(strategy.K.tolist(), list(main.KS))
        main.validate_clusters(output / "clusters", self.victims.id, main.WINNER)
        with tempfile.TemporaryDirectory() as folder, threadpool_limits(limits=1):
            folder = Path(folder)
            main.experiment(ROOT, folder, main.WINNER)
            for path in output.glob("*.csv"):
                self.assertEqual(path.read_bytes(), (folder / path.name).read_bytes(), path.name)
            for path in (output / "clusters").glob("cluster*.txt"):
                self.assertEqual(path.read_bytes(), (folder / "clusters" / path.name).read_bytes())
            first = folder / "clusters/cluster_1.txt"
            original = first.read_text()
            for invalid in ("id\n" + original, original + original, original + "999999\n", ""):
                first.write_text(invalid)
                with self.assertRaises(ValueError):
                    main.validate_clusters(first.parent, self.victims.id, main.WINNER)
            with self.assertRaises(ValueError):
                main.save_clusters(first.parent, self.predicted, np.full(len(self.predicted), -1))

    def test_official_visualizer(self):
        if "VICTSIM3" not in os.environ:
            self.skipTest("Defina VICTSIM3 para testar a leitura e a captura oficiais")
        output = ROOT / "outputs"
        capture(Path(os.environ["VICTSIM3"]), output)
        self.assertGreater((output / "graficos/grid.png").stat().st_size, 3000)

    def test_pdf_integrity(self):
        pdf = ROOT / "relatorio/relatorio_t3.pdf"
        info = subprocess.check_output(["pdfinfo", pdf], text=True)
        self.assertLessEqual(int(re.search(r"Pages:\s+(\d+)", info)[1]), 4)
        report = subprocess.check_output(["pdftotext", "-layout", pdf, "-"], text=True)
        for number in range(1, 5):
            self.assertIn(f"Figura {number}", report)
        for csv, digits in (("basico.csv", 2), ("estrategia.csv", 4)):
            for row in pd.read_csv(ROOT / "outputs" / csv).itertuples():
                self.assertIn(f"{row.SSE:.{digits}f}".replace(".", ","), report)
                self.assertIn(f"{row.silhueta:.4f}".replace(".", ","), report)
        xml = subprocess.check_output(
            ["pdftohtml", "-q", "-xml", "-i", "-zoom", "1", "-stdout", pdf], text=True)
        fonts = dict(re.findall(r'<fontspec id="(\d+)" size="(\d+)"', xml))
        for phrase in ("O mapa explorado", "As escolhas seguiram", "A configuração escolhida",
                       "Círculos por START predito."):
            line = next(line for line in xml.splitlines() if phrase in line)
            self.assertEqual(fonts[re.search(r'font="(\d+)"', line)[1]], "11")
        source = (ROOT / "relatorio/relatorio.tex").read_text()
        self.assertIn(r"\fontsize{11}{14}\selectfont", source)
        for plot in ("sse.pdf", "silhueta.pdf", "nuvem.pdf", "grid.png"):
            self.assertIn(plot, source)
            self.assertGreater((ROOT / "outputs/graficos" / plot).stat().st_size, 3000)


if __name__ == "__main__":
    unittest.main()
