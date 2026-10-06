from __future__ import annotations

from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor


def criar_cart(params: dict, random_state: int):
    return DecisionTreeRegressor(
        max_depth=params["max_depth"],
        min_samples_leaf=params["min_samples_leaf"],
        criterion=params["criterion"],
        random_state=random_state,
    )


def criar_rn(params: dict, random_state: int):
    return MLPRegressor(
        hidden_layer_sizes=tuple(params["hidden_layer_sizes"]),
        activation=params["activation"],
        learning_rate_init=params["learning_rate_init"],
        solver=params["solver"],
        alpha=params["alpha"],
        max_iter=params["max_iter"],
        random_state=random_state,
    )
