from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

from src.avaliacao import escolher_melhor, validar_cart, validar_rn
from src.dados import carregar_dataset, resumo_dataset, separar_xy
from src.modelos import criar_cart, criar_rn


ROOT = Path(__file__).resolve().parents[1]

MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = ROOT / "plots"


def carregar_config(caminho: str | Path) -> dict[str, Any]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def _avaliar_regressao(y_real, y_pred) -> dict[str, float]:
    mse = float(mean_squared_error(y_real, y_pred))

    return {
        "mse": mse,
        "rmse": float(math.sqrt(mse)),
    }


def _ganho_percentual(
    valor_cart: float,
    valor_rn: float,
) -> dict[str, Any]:
    if valor_cart < valor_rn:
        melhor = "cart"
        ganho = (1.0 - valor_cart / valor_rn) * 100.0
    elif valor_rn < valor_cart:
        melhor = "rn"
        ganho = (1.0 - valor_rn / valor_cart) * 100.0
    else:
        melhor = "empate"
        ganho = 0.0

    return {
        "melhor": melhor,
        "ganho_percentual": float(ganho),
    }


def _salvar_dispersao(
    y_real,
    y_pred,
    titulo: str,
    caminho: Path,
) -> None:
    minimo = float(min(0.0, min(y_real), min(y_pred)))
    maximo = float(max(1.0, max(y_real), max(y_pred)))

    plt.figure(figsize=(6.2, 5.2))
    plt.scatter(y_real, y_pred, alpha=0.45, s=12)
    plt.plot(
        [minimo, maximo],
        [minimo, maximo],
        linestyle="--",
        linewidth=1,
    )
    plt.xlabel("Valor real de sobrevivência")
    plt.ylabel("Valor predito")
    plt.title(titulo)
    plt.xlim(minimo, maximo)
    plt.ylim(minimo, maximo)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(caminho, dpi=180)
    plt.close()


def executar(
    treino: str | Path,
    teste_cego: str | Path,
    config_path: str | Path,
) -> dict[str, Any]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    cfg = carregar_config(config_path)

    # ---------------------------------------------------------
    # TREINAMENTO / VALIDAÇÃO
    # ---------------------------------------------------------

    df_treino = carregar_dataset(treino)

    if len(df_treino) != 10000:
        raise ValueError(
            "O dataset de treinamento/validação deve conter "
            f"exatamente 10000 vítimas; recebido: {len(df_treino)}."
        )

    x, y = separar_xy(df_treino)

    folds = int(cfg["cv_folds"])
    random_state = int(cfg["random_state"])

    resultados_cart: dict[str, Any] = {}
    resultados_rn: dict[str, Any] = {}

    for nome in ("U", "E", "O"):
        print(f"[CART {nome}] validação cruzada...")

        resultado = validar_cart(
            x=x,
            y=y,
            params=cfg["cart"][nome],
            folds=folds,
            random_state=random_state,
        )

        resultados_cart[nome] = resultado

        print(
            f"  treino={resultado['treino']['media']:.6f} | "
            f"validação={resultado['validacao']['media']:.6f} | "
            f"gap={resultado['diferencas_abs']['media']:.6f}"
        )

    for nome in ("U", "E", "O"):
        print(f"[RN {nome}] validação cruzada...")

        resultado = validar_rn(
            x=x,
            y=y,
            params=cfg["rn"][nome],
            folds=folds,
            random_state=random_state,
        )

        resultados_rn[nome] = resultado

        print(
            f"  treino={resultado['treino']['media']:.6f} | "
            f"validação={resultado['validacao']['media']:.6f} | "
            f"gap={resultado['diferencas_abs']['media']:.6f}"
        )

    melhor_cart = escolher_melhor(resultados_cart)
    melhor_rn = escolher_melhor(resultados_rn)

    print(f"Melhor CART: {melhor_cart}")
    print(f"Melhor RN: {melhor_rn}")

    # ---------------------------------------------------------
    # RETREINO COM TODAS AS 10.000 AMOSTRAS
    # ---------------------------------------------------------

    cart_final = criar_cart(
        cfg["cart"][melhor_cart],
        random_state,
    )
    cart_final.fit(x, y)

    scaler = StandardScaler()
    x_normalizado = scaler.fit_transform(x)

    rn_final = criar_rn(
        cfg["rn"][melhor_rn],
        random_state,
    )
    rn_final.fit(x_normalizado, y)

    caminho_cart = MODELS_DIR / "melhor_cart.joblib"
    caminho_rn = MODELS_DIR / "melhor_rn.joblib"
    caminho_scaler = MODELS_DIR / "scaler.joblib"

    joblib.dump(cart_final, caminho_cart)
    joblib.dump(rn_final, caminho_rn)
    joblib.dump(scaler, caminho_scaler)

    # ---------------------------------------------------------
    # TESTE CEGO
    # Somente agora o arquivo é lido.
    # ---------------------------------------------------------

    df_teste = carregar_dataset(teste_cego)

    if len(df_teste) != 1300:
        raise ValueError(
            "O teste cego deve conter exatamente 1300 vítimas; "
            f"recebido: {len(df_teste)}."
        )

    x_teste, y_teste = separar_xy(df_teste)

    pred_cart = cart_final.predict(x_teste)

    x_teste_normalizado = scaler.transform(x_teste)
    pred_rn = rn_final.predict(x_teste_normalizado)

    metricas_cart = _avaliar_regressao(y_teste, pred_cart)
    metricas_rn = _avaliar_regressao(y_teste, pred_rn)

    ganho_mse = _ganho_percentual(
        metricas_cart["mse"],
        metricas_rn["mse"],
    )

    ganho_rmse = _ganho_percentual(
        metricas_cart["rmse"],
        metricas_rn["rmse"],
    )

    caminho_plot_cart = PLOTS_DIR / "dispersao_cart.png"
    caminho_plot_rn = PLOTS_DIR / "dispersao_rn.png"

    _salvar_dispersao(
        y_teste,
        pred_cart,
        f"CART {melhor_cart} - Real x Predito",
        caminho_plot_cart,
    )

    _salvar_dispersao(
        y_teste,
        pred_rn,
        f"RN {melhor_rn} - Real x Predito",
        caminho_plot_rn,
    )

    resultado = {
        "config": cfg,
        "dataset_treino": resumo_dataset(df_treino),
        "cv": {
            "cart": resultados_cart,
            "rn": resultados_rn,
        },
        "melhores": {
            "cart": melhor_cart,
            "rn": melhor_rn,
        },
        "teste_cego": {
            "cart": {
                **metricas_cart,
                "predicoes": [float(v) for v in pred_cart],
            },
            "rn": {
                **metricas_rn,
                "predicoes": [float(v) for v in pred_rn],
            },
            "ganho_mse": ganho_mse,
            "ganho_rmse": ganho_rmse,
        },
        "arquivos": {
            "melhor_cart": str(caminho_cart.relative_to(ROOT)),
            "melhor_rn": str(caminho_rn.relative_to(ROOT)),
            "scaler": str(caminho_scaler.relative_to(ROOT)),
            "plot_cart": str(caminho_plot_cart.relative_to(ROOT)),
            "plot_rn": str(caminho_plot_rn.relative_to(ROOT)),
        },
    }

    caminho_json = RESULTS_DIR / "resultado_experimento.json"

    with open(caminho_json, "w", encoding="utf-8") as arquivo:
        json.dump(
            resultado,
            arquivo,
            ensure_ascii=False,
            indent=2,
        )

    linhas_csv = []

    for familia, resultados in (
        ("CART", resultados_cart),
        ("RN", resultados_rn),
    ):
        for nome, bloco in resultados.items():
            linhas_csv.append(
                {
                    "familia": familia,
                    "modelo": nome,
                    "mse_treino_media": bloco["treino"]["media"],
                    "mse_treino_dpa": bloco["treino"]["dpa"],
                    "mse_validacao_media": bloco["validacao"]["media"],
                    "mse_validacao_dpa": bloco["validacao"]["dpa"],
                    "diferenca_media": bloco["diferencas_abs"]["media"],
                    "diferenca_dpa": bloco["diferencas_abs"]["dpa"],
                }
            )

    pd.DataFrame(linhas_csv).to_csv(
        RESULTS_DIR / "resultados_cv.csv",
        index=False,
    )

    return resultado
