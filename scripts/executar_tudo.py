from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import executar  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa validação cruzada, retreino, teste cego e relatório."
    )
    parser.add_argument("--treino", required=True, type=Path)
    parser.add_argument("--teste-cego", required=True, type=Path)
    parser.add_argument(
        "--config", type=Path, default=ROOT / "config" / "experimento.json"
    )
    args = parser.parse_args()

    executar(args.treino, args.teste_cego, args.config)

    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "gerar_relatorio.py")],
        check=True,
    )

    print("\nConcluído.")
    print("- models/melhor_cart.joblib")
    print("- models/melhor_rn.joblib")
    print("- results/resultado_experimento.json")
    print("- results/resultados_cv.csv")
    print("- relatorio/relatorio_final.pdf")


if __name__ == "__main__":
    main()
