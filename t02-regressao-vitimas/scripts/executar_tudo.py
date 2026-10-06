from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import executar


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa o experimento completo do T02."
    )

    parser.add_argument(
        "--treino",
        required=True,
        help="CSV com as 10000 vítimas de treinamento/validação.",
    )

    parser.add_argument(
        "--teste-cego",
        required=True,
        help="CSV com as 1300 vítimas do teste cego.",
    )

    parser.add_argument(
        "--config",
        default="config/experimento.json",
        help="Arquivo JSON de configuração.",
    )

    args = parser.parse_args()

    resultado = executar(
        treino=args.treino,
        teste_cego=args.teste_cego,
        config_path=args.config,
    )

    print()
    print("Concluído.")
    print(f"- Melhor CART: {resultado['melhores']['cart']}")
    print(f"- Melhor RN: {resultado['melhores']['rn']}")
    print("- models/melhor_cart.joblib")
    print("- models/melhor_rn.joblib")
    print("- models/scaler.joblib")
    print("- results/resultado_experimento.json")
    print("- results/resultados_cv.csv")
    print("- plots/dispersao_cart.png")
    print("- plots/dispersao_rn.png")


if __name__ == "__main__":
    main()
