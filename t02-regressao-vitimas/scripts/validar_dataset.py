from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.dados import carregar_dataset, resumo_dataset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida um dataset de vítimas."
    )

    parser.add_argument(
        "dataset",
        help="Caminho para o arquivo CSV.",
    )

    args = parser.parse_args()

    caminho = Path(args.dataset)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {caminho}"
        )

    df = carregar_dataset(caminho)
    resumo = resumo_dataset(df)

    print(f"Linhas: {resumo['n_linhas']}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Classes tri: {resumo['contagem_classes']}")
    print(f"Idade média observada: {resumo['idade_media']:.4f}")
    print(
        "DPA amostral da idade: "
        f"{resumo['idade_dpa_amostral']:.4f}"
    )
    print(f"sobr mínimo: {resumo['sobr_min']:.6f}")
    print(f"sobr máximo: {resumo['sobr_max']:.6f}")


if __name__ == "__main__":
    main()
