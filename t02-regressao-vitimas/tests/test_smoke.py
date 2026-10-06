import unittest

import pandas as pd

from src.dados import (
    FEATURES,
    PROIBIDAS,
    TARGET,
    separar_xy,
    validar_features,
)


class TestDados(unittest.TestCase):
    def test_features_nao_usam_variaveis_proibidas(self):
        validar_features()

        self.assertEqual(
            set(FEATURES) & set(PROIBIDAS),
            set(),
        )

    def test_target_e_sobr(self):
        self.assertEqual(TARGET, "sobr")

    def test_separacao_xy(self):
        df = pd.DataFrame(
            {
                "idade": [20],
                "fc": [80],
                "fr": [18],
                "pas": [120],
                "spo2": [98],
                "temp": [36.5],
                "pr": [1],
                "sg": [0],
                "fx": [0],
                "queim": [0],
                "gcs": [15],
                "avpu": [0],
                "tri": [0],
                "sobr": [0.95],
            }
        )

        x, y = separar_xy(df)

        self.assertEqual(list(x.columns), FEATURES)
        self.assertEqual(y.name, "sobr")
        self.assertNotIn("gcs", x.columns)
        self.assertNotIn("avpu", x.columns)
        self.assertNotIn("tri", x.columns)
        self.assertNotIn("sobr", x.columns)


if __name__ == "__main__":
    unittest.main()
