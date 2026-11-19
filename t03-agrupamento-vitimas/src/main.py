"""Experimento reprodutível da Tarefa 3."""
import argparse
from pathlib import Path
import re
import warnings

import joblib
import matplotlib
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.metrics import adjusted_rand_score, silhouette_samples
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FEATURES = "idade fc fr pas spo2 temp pr sg fx queim".split()
XY = ["x_rel", "y_rel"]
COLUMNS = XY + ["obst", "id"] + FEATURES + ["gcs", "avpu", "tri", "sobr"]
BASE = np.array([30, 40])
SIZE = 75
SEED = 42
WEIGHT = 0.45
KS = (4, 6, 8)
WINNER = 6


def load_map(path):
    with warnings.catch_warnings():
        warnings.simplefilter("error", pd.errors.ParserWarning)
        cells = pd.read_csv(path, index_col=False).apply(pd.to_numeric, errors="raise")
    if list(cells.columns) != COLUMNS or not np.isfinite(cells.to_numpy(dtype=float)).all():
        raise ValueError("Colunas inesperadas ou dados não finitos no mapa")
    integral = cells.drop(columns=["obst", "temp", "sobr"])
    if not (integral % 1 == 0).all().all():
        raise ValueError("Era esperado um inteiro nas colunas discretas")
    coords = cells[XY].to_numpy() + BASE
    if (len(cells) != SIZE**2 or cells.duplicated(XY).any()
            or not ((0 <= coords) & (coords < SIZE)).all()):
        raise ValueError("Grade incompleta ou coordenadas inválidas")
    terrain = cells["obst"].between(0, 3, inclusive="right")
    if not (terrain | cells["obst"].eq(100)).all():
        raise ValueError("Dificuldade de travessia inválida")
    if (cells["id"] < -1).any() or not cells[["tri", "sobr"]].eq(-1).all().all():
        raise ValueError("Sentinelas inválidas na entrada")
    empty = cells["id"].eq(-1)
    if not cells.loc[empty, COLUMNS[4:]].eq(-1).all().all():
        raise ValueError("Célula vazia com atributos de vítima")
    victims = cells.loc[~empty].sort_values("id").copy()
    if len(victims) != 410 or not victims["id"].is_unique or not terrain.loc[victims.index].all():
        raise ValueError("Contagem, identificadores ou posições de vítimas inválidos")
    bounds = {"idade": (1, 90), "fc": (0, 200), "fr": (0, 50),
              "pas": (0, 220), "spo2": (0, 100), "temp": (0, 43),
              "pr": (0, 1), "sg": (0, 3), "fx": (0, 1), "queim": (0, 3),
              "gcs": (3, 15), "avpu": (0, 3)}
    for col, (low, high) in bounds.items():
        if not victims[col].between(low, high).all():
            raise ValueError(f"Valor inválido em {col}")
    return cells, victims


def predict(victims, models):
    with warnings.catch_warnings():
        warnings.simplefilter("error", InconsistentVersionWarning)
        classifier = joblib.load(models / "t1/melhor_rn.joblib")
        scaler = joblib.load(models / "t2/scaler.joblib")
        regressor = joblib.load(models / "t2/melhor_rn.joblib")
    for estimator in (classifier, scaler):
        if list(estimator.feature_names_in_) != FEATURES:
            raise ValueError("Ordem de atributos incompatível com o treino")
    features = victims[FEATURES]
    tri = classifier.predict(features)
    raw = regressor.predict(scaler.transform(features))
    if (tri.shape != (len(victims),) or not np.isin(tri, [0, 1, 2, 3]).all()
            or raw.shape != tri.shape or not np.isfinite(raw).all()):
        raise ValueError("Predições incompletas ou inválidas")
    return victims.assign(tri=tri.astype(int), sobr=np.clip(raw, 0, 1), sobr_bruta=raw)


def strategy_space(victims, weight=WEIGHT):
    xy = (victims[XY].to_numpy() + BASE) / (SIZE - 1)
    return np.column_stack((xy, weight * victims["sobr"].to_numpy()))


def silhouette_coverage(space, labels):
    labels = np.asarray(labels)
    keep = labels != -1
    kept = labels[keep]
    coverage = keep.mean() if len(keep) else 0.0
    groups = len(np.unique(kept))
    score = float(silhouette_samples(space[keep], kept).mean()) if 2 <= groups < len(kept) else None
    return {"clusters": groups, "ruido": int((~keep).sum()),
            "cobertura": coverage, "silhueta": score,
            "score": None if score is None else score * coverage}


def kmeans(space, k):
    model = KMeans(n_clusters=k, n_init=50, random_state=SEED)
    labels = model.fit_predict(space)
    return labels, {"K": k, "SSE": model.inertia_,
                    "silhueta": silhouette_coverage(space, labels)["silhueta"]}


def elbow(rows):
    ks = np.array([row["K"] for row in rows])
    sse = np.array([row["SSE"] for row in rows])
    x = (ks - ks[0]) / (ks[-1] - ks[0])
    y = (sse - sse[-1]) / (sse[0] - sse[-1])
    return int(ks[np.argmax((1 - x - y) / np.sqrt(2))])


def validate_clusters(folder, expected, k):
    files = {path.name: path for path in folder.glob("cluster*")}
    if set(files) != {f"cluster_{i}.txt" for i in range(1, k + 1)}:
        raise ValueError("Quantidade ou nomes de arquivos incorretos")
    all_ids = []
    for path in files.values():
        content = path.read_text(encoding="ascii")
        if not re.fullmatch(r"(?:[0-9]+\n)+", content):
            raise ValueError(f"Formato inválido em {path}")
        all_ids.extend(map(int, content.splitlines()))
    if len(all_ids) != len(set(all_ids)) or set(all_ids) != set(expected):
        raise ValueError("IDs duplicados, ausentes ou fora do mapa")


def save_clusters(folder, victims, labels):
    folder.mkdir(parents=True, exist_ok=True)
    if np.any(labels < 0):
        raise ValueError("A exportação exige que todas as vítimas tenham um grupo")
    members = [sorted(victims.loc[labels == label, "id"]) for label in np.unique(labels)]
    for path in folder.glob("cluster_*.txt"):
        if path.name not in {f"cluster_{i}.txt" for i in range(1, len(members) + 1)}:
            path.unlink()
    for number, ids in enumerate(members, 1):
        (folder / f"cluster_{number}.txt").write_text("".join(f"{vid}\n" for vid in ids))
    validate_clusters(folder, victims["id"], len(members))


def plots(folder, basic, choice, victims):
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    for metric, name in (("SSE", "sse"), ("silhueta", "silhueta")):
        fig, ax = plt.subplots(figsize=(4.6, 2.75), layout="constrained")
        ax.plot(basic["K"], basic[metric], "o-", color="#145583")
        ax.axvline(choice, linestyle="--", color="#a94d21", linewidth=1)
        ax.set(xlabel="K", ylabel=metric.capitalize() if name != "sse" else "SSE",
               xticks=basic["K"])
        ax.grid(alpha=0.2)
        fig.savefig(folder / f"{name}.pdf")
        plt.close(fig)
    space = strategy_space(victims)
    fig = plt.figure(figsize=(6.9, 3.8), layout="constrained")
    ax = fig.add_subplot(111, projection="3d")
    dots = ax.scatter(*space.T, c=victims["sobr"], cmap="viridis", s=10,
                      alpha=0.75, vmin=0, vmax=1)
    ax.set(xlabel="x normalizado", ylabel="y normalizado", zlabel="0,45 × sobrevivência",
           zlim=(0, WEIGHT))
    ax.view_init(elev=23, azim=-58)
    fig.colorbar(dots, ax=ax, shrink=0.68, pad=0.10, label="Sobrevivência prevista")
    fig.savefig(folder / "nuvem.pdf")
    plt.close(fig)


def group_summary(victims, labels):
    data = victims.assign(cluster=labels + 1, menor_ou_igual_12=victims.idade <= 12,
                          dist_base=np.linalg.norm(victims[XY], axis=1))
    return data.groupby("cluster").agg(
        n=("id", "size"), ate_12=("menor_ou_igual_12", "sum"),
        x=("x_rel", "mean"), y=("y_rel", "mean"),
        dist_base_media=("dist_base", "mean"), sobr_media=("sobr", "mean"))


def experiment(root, output, winner):
    cells, victims = load_map(root / "map.csv")
    victims = predict(victims, root / "modelos")
    output.mkdir(parents=True, exist_ok=True)
    graphs = output / "graficos"
    graphs.mkdir(exist_ok=True)
    xy = victims[XY].to_numpy()
    space = strategy_space(victims)
    basic = [kmeans(xy, k)[1] for k in range(2, 13)]
    choice = elbow(basic)
    basic = pd.DataFrame(basic)
    basic.to_csv(output / "basico.csv", index=False)
    labels_by_k = {}
    rows = []
    for k in KS:
        labels, row = kmeans(space, k)
        labels_by_k[k] = labels
        sizes = np.bincount(labels)
        delta = xy - np.array([xy[labels == c].mean(axis=0) for c in labels])
        rows.append(row | {"min_vitimas": sizes.min(), "max_vitimas": sizes.max(),
                           "raio_rms_celulas": np.sqrt(np.mean(np.sum(delta**2, axis=1)))})
    strategy = pd.DataFrame(rows)
    strategy.to_csv(output / "estrategia.csv", index=False)
    labels = labels_by_k[winner]
    sensitivity = []
    for weight in (0.25, WEIGHT, 0.70):
        alternative, row = kmeans(strategy_space(victims, weight), winner)
        sensitivity.append(row | {"peso": weight, "ARI": adjusted_rand_score(labels, alternative)})
    pd.DataFrame(sensitivity).to_csv(output / "sensibilidade.csv", index=False)
    distances = NearestNeighbors(n_neighbors=5).fit(space).kneighbors(space)[0][:, -1]
    eps_values = np.quantile(distances, [0.25, 0.50, 0.75])
    density = [dict(eps=eps, min_samples=5,
                    **silhouette_coverage(space, DBSCAN(eps=eps, min_samples=5).fit_predict(space)))
               for eps in eps_values]
    spread = victims[XY + ["sobr"]].corr(method="spearman")["sobr"]
    diagnostics = {
        "tri_0": int(victims.tri.eq(0).sum()), "tri_1": int(victims.tri.eq(1).sum()),
        "tri_2": int(victims.tri.eq(2).sum()), "tri_3": int(victims.tri.eq(3).sum()),
        "sobr_bruta_min": victims.sobr_bruta.min(), "sobr_bruta_max": victims.sobr_bruta.max(),
        "clipping": int(victims.sobr.ne(victims.sobr_bruta).sum()),
        "ate_12": int(victims.idade.le(12).sum()), "paredes": int(cells.obst.eq(100).sum()),
        "spearman_x": spread["x_rel"], "spearman_y": spread["y_rel"],
        "vizinho_5_mediana": float(np.median(distances)), "vizinho_5_max": distances.max(),
    }
    pd.DataFrame([diagnostics]).to_csv(output / "diagnostico.csv", index=False)
    victims.groupby("tri").sobr.agg(["min", "median", "max"]).to_csv(output / "sobr_por_tri.csv")
    pd.DataFrame(density).to_csv(output / "diagnostico_dbscan.csv", index=False)
    victims.assign(cluster=labels + 1).to_csv(output / "predicoes.csv", index=False)
    cells.loc[victims.index, "tri"] = victims["tri"]
    cells["sobr"] = cells["sobr"].astype(float)
    cells.loc[victims.index, "sobr"] = victims["sobr"]
    cells.to_csv(output / "map_predito.csv", index=False)
    save_clusters(output / "clusters", victims, labels)
    group_summary(victims, labels).to_csv(output / "grupos.csv")
    plots(graphs, basic, choice, victims)
    print(f"Cotovelo K={choice}. Estratégia K={winner}. Vítimas: {len(victims)}")
    print(strategy.to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ROOT)
    parser.add_argument("--saida", type=Path, default=ROOT / "outputs")
    parser.add_argument("--k", type=int, choices=KS, default=WINNER)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        experiment(args.entrada, args.saida, args.k)
