from __future__ import annotations

from typing import Callable, Any
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold

from .dados import CLASSES


def _estatisticas(valores: list[float]) -> dict[str, Any]:
    arr = np.asarray(valores, dtype=float)
    return {
        "por_fold": [float(v) for v in arr],
        "media": float(arr.mean()),
        # O exemplo do enunciado usa np.std com ddof=0 para os folds.
        "dpa": float(arr.std(ddof=0)),
    }


def avaliar_validacao_cruzada(
    modelo,
    x: pd.DataFrame,
    y: pd.Series,
    folds: int,
    random_state: int,
) -> dict[str, Any]:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    treino_f1: list[float] = []
    validacao_f1: list[float] = []
    diferencas: list[float] = []

    for idx_treino, idx_validacao in cv.split(x, y):
        atual = clone(modelo)
        x_treino, x_validacao = x.iloc[idx_treino], x.iloc[idx_validacao]
        y_treino, y_validacao = y.iloc[idx_treino], y.iloc[idx_validacao]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ConvergenceWarning)
            atual.fit(x_treino, y_treino)

        pred_treino = atual.predict(x_treino)
        pred_validacao = atual.predict(x_validacao)

        f1_t = f1_score(y_treino, pred_treino, average="macro", zero_division=0)
        f1_v = f1_score(y_validacao, pred_validacao, average="macro", zero_division=0)

        treino_f1.append(float(f1_t))
        validacao_f1.append(float(f1_v))
        diferencas.append(float(abs(f1_t - f1_v)))

    return {
        "treino": _estatisticas(treino_f1),
        "validacao": _estatisticas(validacao_f1),
        "diferencas_abs": _estatisticas(diferencas),
    }


def escolher_melhor(resultados: dict[str, dict[str, Any]]) -> str:
    if not resultados:
        raise ValueError("Nenhum resultado recebido para seleção do melhor modelo.")

    # O enunciado pede comparar desempenho e viés para subsidiar a escolha.
    # Usamos um critério simples e explícito de generalização:
    #     score = F1_validacao - |F1_treino - F1_validacao|
    # Assim, um ganho pequeno de validação não compensa um gap muito alto.
    return max(
        resultados,
        key=lambda nome: (
            resultados[nome]["validacao"]["media"]
            - resultados[nome]["diferencas_abs"]["media"],
            resultados[nome]["validacao"]["media"],
            -resultados[nome]["diferencas_abs"]["media"],
        ),
    )


def avaliar_teste_cego(modelo, x: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    pred = modelo.predict(x)
    return {
        "precisao_macro": float(
            precision_score(y, pred, average="macro", zero_division=0)
        ),
        "recall_macro": float(recall_score(y, pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y, pred, average="macro", zero_division=0)),
        "acuracia": float(accuracy_score(y, pred)),
        "matriz_confusao": confusion_matrix(y, pred, labels=CLASSES).astype(int).tolist(),
    }
