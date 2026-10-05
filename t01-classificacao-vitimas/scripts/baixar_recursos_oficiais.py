from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]

RECURSOS = {
    ROOT / "external" / "gerar_dados_vitimas.py": (
        "https://raw.githubusercontent.com/tacla/VictSim3/main/"
        "data_creation/gerar_dados_vitimas.py"
    ),
    ROOT / "data" / "raw" / "teste_ceg1300.csv": (
        "https://raw.githubusercontent.com/tacla/VictSim3/main/"
        "datasets/vict/1300v/data.csv"
    ),
}


def baixar(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)
    print(f"OK: {destino.relative_to(ROOT)} ({len(resposta.content)} bytes)")


def main() -> None:
    for destino, url in RECURSOS.items():
        baixar(url, destino)


if __name__ == "__main__":
    main()
