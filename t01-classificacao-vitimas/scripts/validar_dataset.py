from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dados import carregar_dataset, resumo_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()

    df = carregar_dataset(args.csv)
    resumo = resumo_dataset(df)
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Classes tri: {resumo['contagem_classes']}")
    print(f"Idade média observada: {resumo['idade_media_observada']:.4f}")
    print(f"DPA amostral da idade: {resumo['idade_dpa_amostral']:.4f}")


if __name__ == "__main__":
    main()
