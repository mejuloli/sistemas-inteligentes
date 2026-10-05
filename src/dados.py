from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

FEATURES = ["idade", "fc", "fr", "pas", "spo2", "temp", "pr", "sg", "fx", "queim"]
TARGET = "tri"
PROIBIDAS = ["gcs", "avpu", "sobr"]
CLASSES = [0, 1, 2, 3]


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    copia = df.copy()
    copia.columns = [str(c).strip().lower() for c in copia.columns]
    colunas_indice = [c for c in copia.columns if c.startswith("unnamed:")]
    if colunas_indice:
        copia = copia.drop(columns=colunas_indice)
    return copia


def carregar_dataset(caminho: str | Path) -> pd.DataFrame:
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho}")

    # sep=None faz detecção automática entre vírgula, ponto e vírgula, tab etc.
    df = pd.read_csv(caminho, sep=None, engine="python")
    df = _normalizar_colunas(df)

    obrigatorias = FEATURES + [TARGET]
    faltantes = [c for c in obrigatorias if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Dataset inválido. Colunas obrigatórias ausentes: {faltantes}. "
            f"Encontradas: {list(df.columns)}"
        )

    if df[obrigatorias].isna().any().any():
        por_coluna = df[obrigatorias].isna().sum()
        por_coluna = por_coluna[por_coluna > 0].to_dict()
        raise ValueError(f"Há valores ausentes nas colunas usadas pelo modelo: {por_coluna}")

    for coluna in obrigatorias:
        df[coluna] = pd.to_numeric(df[coluna], errors="raise")

    classes = sorted(pd.unique(df[TARGET]).tolist())
    invalidas = [c for c in classes if c not in CLASSES]
    if invalidas:
        raise ValueError(f"Valores inválidos em tri: {invalidas}. Esperado: {CLASSES}")

    return df


def extrair_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    # Guardas explícitas contra data leakage por atributos proibidos.
    if set(FEATURES) & set(PROIBIDAS + [TARGET]):
        raise RuntimeError("A lista de FEATURES contém variável proibida.")

    x = df[FEATURES].copy()
    y = df[TARGET].astype(int).copy()
    return x, y


def resumo_dataset(df: pd.DataFrame) -> dict[str, Any]:
    contagens = df[TARGET].astype(int).value_counts().reindex(CLASSES, fill_value=0)
    return {
        "n_amostras": int(len(df)),
        "contagem_classes": {str(int(k)): int(v) for k, v in contagens.items()},
        "idade_media_observada": float(df["idade"].mean()),
        # O relatório pede desvio padrão amostral da idade: ddof=1.
        "idade_dpa_amostral": float(df["idade"].std(ddof=1)),
    }
