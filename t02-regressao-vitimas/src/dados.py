from __future__ import annotations

from pathlib import Path

import pandas as pd


FEATURES = [
    "idade",
    "fc",
    "fr",
    "pas",
    "spo2",
    "temp",
    "pr",
    "sg",
    "fx",
    "queim",
]

TARGET = "sobr"

PROIBIDAS = ["gcs", "avpu", "tri", "sobr"]


def carregar_dataset(caminho: str | Path) -> pd.DataFrame:
    df = pd.read_csv(caminho)

    obrigatorias = FEATURES + ["gcs", "avpu", "tri", TARGET]
    ausentes = [col for col in obrigatorias if col not in df.columns]

    if ausentes:
        raise ValueError(
            f"Dataset sem as colunas obrigatórias: {ausentes}"
        )

    return df


def separar_xy(df: pd.DataFrame):
    x = df[FEATURES].copy()
    y = df[TARGET].astype(float).copy()

    return x, y


def resumo_dataset(df: pd.DataFrame) -> dict:
    contagem = (
        df["tri"]
        .value_counts()
        .sort_index()
        .reindex([0, 1, 2, 3], fill_value=0)
    )

    return {
        "n_linhas": int(len(df)),
        "contagem_classes": {
            str(int(k)): int(v)
            for k, v in contagem.items()
        },
        "idade_media": float(df["idade"].mean()),
        "idade_dpa_amostral": float(df["idade"].std(ddof=1)),
        "sobr_min": float(df[TARGET].min()),
        "sobr_max": float(df[TARGET].max()),
    }


def validar_features() -> None:
    intersecao = set(FEATURES) & set(PROIBIDAS)

    if intersecao:
        raise AssertionError(
            f"Features proibidas encontradas: {sorted(intersecao)}"
        )
