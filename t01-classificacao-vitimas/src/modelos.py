from __future__ import annotations

from typing import Any

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier


def criar_cart(parametros: dict[str, Any], random_state: int) -> DecisionTreeClassifier:
    return DecisionTreeClassifier(
        max_depth=parametros.get("max_depth"),
        min_samples_leaf=int(parametros.get("min_samples_leaf", 1)),
        criterion=str(parametros.get("criterion", "gini")),
        random_state=random_state,
    )


def criar_rn(parametros: dict[str, Any], random_state: int) -> Pipeline:
    topologia = tuple(int(v) for v in parametros["hidden_layer_sizes"])
    mlp = MLPClassifier(
        hidden_layer_sizes=topologia,
        activation=str(parametros.get("activation", "relu")),
        learning_rate_init=float(parametros.get("learning_rate_init", 0.001)),
        solver=str(parametros.get("solver", "adam")),
        alpha=float(parametros.get("alpha", 0.0001)),
        max_iter=int(parametros.get("max_iter", 500)),
        random_state=random_state,
    )

    # O scaler fica dentro do Pipeline para ser ajustado apenas no treino de cada fold.
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("mlp", mlp),
        ]
    )
