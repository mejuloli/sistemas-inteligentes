from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.modelos import criar_cart, criar_rn


def _resumo(valores: list[float]) -> dict:
    arr = np.asarray(valores, dtype=float)

    return {
        "valores": arr.tolist(),
        "media": float(arr.mean()),
        "dpa": float(arr.std(ddof=1)),
    }


def validar_cart(
    x,
    y,
    params: dict,
    folds: int,
    random_state: int,
) -> dict:
    kfold = KFold(
        n_splits=folds,
        shuffle=True,
        random_state=random_state,
    )

    mse_treino = []
    mse_validacao = []
    diferencas = []

    for treino_idx, valid_idx in kfold.split(x):
        x_treino = x.iloc[treino_idx]
        x_valid = x.iloc[valid_idx]
        y_treino = y.iloc[treino_idx]
        y_valid = y.iloc[valid_idx]

        modelo = criar_cart(params, random_state)
        modelo.fit(x_treino, y_treino)

        pred_treino = modelo.predict(x_treino)
        pred_valid = modelo.predict(x_valid)

        mse_tr = mean_squared_error(y_treino, pred_treino)
        mse_va = mean_squared_error(y_valid, pred_valid)

        mse_treino.append(float(mse_tr))
        mse_validacao.append(float(mse_va))
        diferencas.append(float(abs(mse_va - mse_tr)))

    return {
        "treino": _resumo(mse_treino),
        "validacao": _resumo(mse_validacao),
        "diferencas_abs": _resumo(diferencas),
    }


def validar_rn(
    x,
    y,
    params: dict,
    folds: int,
    random_state: int,
) -> dict:
    kfold = KFold(
        n_splits=folds,
        shuffle=True,
        random_state=random_state,
    )

    mse_treino = []
    mse_validacao = []
    diferencas = []

    for treino_idx, valid_idx in kfold.split(x):
        x_treino = x.iloc[treino_idx]
        x_valid = x.iloc[valid_idx]
        y_treino = y.iloc[treino_idx]
        y_valid = y.iloc[valid_idx]

        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("rn", criar_rn(params, random_state)),
            ]
        )

        pipeline.fit(x_treino, y_treino)

        pred_treino = pipeline.predict(x_treino)
        pred_valid = pipeline.predict(x_valid)

        mse_tr = mean_squared_error(y_treino, pred_treino)
        mse_va = mean_squared_error(y_valid, pred_valid)

        mse_treino.append(float(mse_tr))
        mse_validacao.append(float(mse_va))
        diferencas.append(float(abs(mse_va - mse_tr)))

    return {
        "treino": _resumo(mse_treino),
        "validacao": _resumo(mse_validacao),
        "diferencas_abs": _resumo(diferencas),
    }


def escolher_melhor(resultados: dict) -> str:
    """
    Seleciona o modelo buscando simultaneamente baixo erro de validação
    e pequena diferença entre treino e validação.

    O score utilizado é:

        MSE médio de validação + média das diferenças absolutas

    Quanto menor o score, melhor o compromisso entre erro e
    capacidade de generalização.
    """
    return min(
        resultados,
        key=lambda nome: (
            resultados[nome]["validacao"]["media"]
            + resultados[nome]["diferencas_abs"]["media"]
        ),
    )

