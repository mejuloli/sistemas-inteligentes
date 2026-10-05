from __future__ import annotations

import unittest

import pandas as pd

from src.dados import FEATURES, extrair_xy, resumo_dataset


class TestDados(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame(
            {
                "idade": [20, 40, 60, 80],
                "fc": [80, 90, 100, 110],
                "fr": [16, 20, 24, 30],
                "pas": [120, 110, 100, 80],
                "spo2": [99, 97, 93, 85],
                "temp": [36.5, 36.7, 37.0, 37.5],
                "pr": [1, 1, 1, 0],
                "sg": [0, 1, 2, 3],
                "fx": [0, 0, 1, 1],
                "queim": [0, 1, 2, 3],
                "gcs": [15, 14, 10, 3],
                "avpu": [0, 0, 2, 3],
                "tri": [0, 1, 2, 3],
                "sobr": [0.99, 0.9, 0.5, 0.05],
            }
        )

    def test_features_nao_usam_variaveis_proibidas(self):
        x, y = extrair_xy(self.df)
        self.assertEqual(list(x.columns), FEATURES)
        self.assertNotIn("gcs", x.columns)
        self.assertNotIn("avpu", x.columns)
        self.assertNotIn("tri", x.columns)
        self.assertNotIn("sobr", x.columns)
        self.assertEqual(y.tolist(), [0, 1, 2, 3])

    def test_resumo_classes(self):
        r = resumo_dataset(self.df)
        self.assertEqual(r["contagem_classes"], {"0": 1, "1": 1, "2": 1, "3": 1})
        self.assertEqual(r["n_amostras"], 4)


if __name__ == "__main__":
    unittest.main()
