"""Gera as linhas das tabelas que entram no relatório."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"


def number(value, places):
    return f"{value:.{places}f}".replace(".", ",")


def tex_rows(filename, formatter):
    frame = pd.read_csv(OUTPUT / f"{filename}.csv")
    text = "".join(" & ".join(map(str, formatter(r))) + r" \\" + "\n"
                   for r in frame.itertuples(index=False))
    return text + r"\bottomrule" + "\n"


if __name__ == "__main__":
    definitions = [
        ("basico", lambda r: (r.K, number(r.SSE, 2), number(r.silhueta, 4))),
        ("estrategia", lambda r: (1 + (r.K - 4)//2, r.K, number(r.SSE, 4),
                                  number(r.silhueta, 4), f"{r.min_vitimas}–{r.max_vitimas}",
                                  number(r.raio_rms_celulas, 2))),
        ("grupos", lambda r: (r.cluster, r.n, r.ate_12, number(r.x, 1),
                              number(r.y, 1), number(r.dist_base_media, 1))),
    ]
    for name, formatter in definitions:
        (OUTPUT / f"{name}_linhas.tex").write_text(tex_rows(name, formatter), encoding="utf-8")
