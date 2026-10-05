from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import sklearn

from .avaliacao import avaliar_teste_cego, avaliar_validacao_cruzada, escolher_melhor
from .dados import carregar_dataset, extrair_xy, resumo_dataset
from .modelos import criar_cart, criar_rn

ROOT = Path(__file__).resolve().parents[1]


def carregar_config(caminho: str | Path | None = None) -> dict[str, Any]:
    caminho = Path(caminho) if caminho else ROOT / "config" / "experimento.json"
    with caminho.open("r", encoding="utf-8") as f:
        return json.load(f)


def _avaliar_familia(
    nome_familia: str,
    configuracoes: dict[str, dict[str, Any]],
    x: pd.DataFrame,
    y: pd.Series,
    folds: int,
    random_state: int,
) -> dict[str, dict[str, Any]]:
    resultados: dict[str, dict[str, Any]] = {}

    for rotulo, params in configuracoes.items():
        if nome_familia == "cart":
            modelo = criar_cart(params, random_state)
        elif nome_familia == "rn":
            modelo = criar_rn(params, random_state)
        else:
            raise ValueError(nome_familia)

        print(f"[{nome_familia.upper()} {rotulo}] validação cruzada...")
        resultados[rotulo] = avaliar_validacao_cruzada(
            modelo=modelo,
            x=x,
            y=y,
            folds=folds,
            random_state=random_state,
        )
        r = resultados[rotulo]
        print(
            f"  treino={r['treino']['media']:.5f} | "
            f"validação={r['validacao']['media']:.5f} | "
            f"gap={r['diferencas_abs']['media']:.5f}"
        )

    return resultados


def _resultado_cv_em_linhas(
    familia: str,
    resultados: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    linhas: list[dict[str, Any]] = []
    for rotulo, resultado in resultados.items():
        linhas.append(
            {
                "familia": familia,
                "modelo": rotulo,
                "treino_f1_media": resultado["treino"]["media"],
                "treino_f1_dpa": resultado["treino"]["dpa"],
                "validacao_f1_media": resultado["validacao"]["media"],
                "validacao_f1_dpa": resultado["validacao"]["dpa"],
                "gap_media": resultado["diferencas_abs"]["media"],
                "gap_dpa": resultado["diferencas_abs"]["dpa"],
            }
        )
    return linhas


def executar(
    treino_csv: str | Path,
    teste_cego_csv: str | Path,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    config = carregar_config(config_path)
    random_state = int(config["random_state"])
    folds = int(config["cv_folds"])

    treino_csv = Path(treino_csv).resolve()
    teste_cego_csv = Path(teste_cego_csv).resolve()
    if treino_csv == teste_cego_csv:
        raise ValueError("Treino e teste cego apontam para o mesmo arquivo: data leakage.")

    # ETAPA 1-4: somente treino/validação.
    df_treino = carregar_dataset(treino_csv)
    n_esperado = int(config["dataset"]["n_vitimas"])
    if len(df_treino) != n_esperado:
        raise ValueError(
            f"O enunciado exige {n_esperado} vítimas para treino/validação; "
            f"o arquivo possui {len(df_treino)}."
        )

    x_treino, y_treino = extrair_xy(df_treino)

    resultados_cart = _avaliar_familia(
        "cart", config["cart"], x_treino, y_treino, folds, random_state
    )
    resultados_rn = _avaliar_familia(
        "rn", config["rn"], x_treino, y_treino, folds, random_state
    )

    melhor_cart = escolher_melhor(resultados_cart)
    melhor_rn = escolher_melhor(resultados_rn)
    print(f"Melhor CART: {melhor_cart}")
    print(f"Melhor RN: {melhor_rn}")

    # ETAPA 5: retreino com as 10.000 amostras, sem split/CV.
    modelo_cart = criar_cart(config["cart"][melhor_cart], random_state)
    modelo_rn = criar_rn(config["rn"][melhor_rn], random_state)
    modelo_cart.fit(x_treino, y_treino)
    modelo_rn.fit(x_treino, y_treino)

    (ROOT / "models").mkdir(exist_ok=True)
    joblib.dump(modelo_cart, ROOT / "models" / "melhor_cart.joblib")
    joblib.dump(modelo_rn, ROOT / "models" / "melhor_rn.joblib")

    # Só agora o teste cego é lido.
    df_teste = carregar_dataset(teste_cego_csv)
    x_teste, y_teste = extrair_xy(df_teste)
    teste_cart = avaliar_teste_cego(modelo_cart, x_teste, y_teste)
    teste_rn = avaliar_teste_cego(modelo_rn, x_teste, y_teste)

    resultado = {
        "config": config,
        "dataset_treino": resumo_dataset(df_treino),
        "dataset_teste_cego": {"n_amostras": int(len(df_teste))},
        "cv": {
            "cart": resultados_cart,
            "rn": resultados_rn,
        },
        "melhores": {
            "cart": melhor_cart,
            "rn": melhor_rn,
        },
        "teste_cego": {
            "cart": teste_cart,
            "rn": teste_rn,
        },
        "versoes": {
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }

    (ROOT / "results").mkdir(exist_ok=True)
    with (ROOT / "results" / "resultado_experimento.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    linhas = _resultado_cv_em_linhas("CART", resultados_cart)
    linhas += _resultado_cv_em_linhas("RN", resultados_rn)
    pd.DataFrame(linhas).to_csv(ROOT / "results" / "resultados_cv.csv", index=False)

    return resultado
