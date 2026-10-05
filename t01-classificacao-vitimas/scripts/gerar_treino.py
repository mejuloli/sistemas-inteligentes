from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ARQUIVO_GERADOR = Path("external/gerar_dados_vitimas.py")
ARQUIVO_SAIDA = Path("data/raw/treino_10000.csv")


def carregar_gerador():
    if not ARQUIVO_GERADOR.exists():
        raise FileNotFoundError(
            "Gerador oficial não encontrado.\n"
            "Execute primeiro:\n"
            "python scripts/baixar_recursos_oficiais.py"
        )

    spec = spec_from_file_location("gerador_vitimas", ARQUIVO_GERADOR)

    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar o gerador oficial.")

    modulo = module_from_spec(spec)
    spec.loader.exec_module(modulo)

    return modulo


def main():
    gerador = carregar_gerador()

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    # O gerador oficial utiliza OUTPUT_CSV como destino global.
    gerador.OUTPUT_CSV = ARQUIVO_SAIDA

    gerador.gerar_dataset_vitimas(
        distrib_tri={
            0: 2500,
            1: 2500,
            2: 2500,
            3: 2500,
        },
        media_idade=40,
        desvio_idade=25,
        nivel_ruido=0.05,
        seed=42,
    )

    print(f"\nDataset de treinamento disponível em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
