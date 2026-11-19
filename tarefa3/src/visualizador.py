"""Captura um quadro do visualizador oficial com seus próprios leitores e desenho."""
import argparse
import importlib.util
import os
from pathlib import Path

import math

import pandas as pd

from main import BASE, FEATURES, ROOT, SIZE, XY, validate_clusters


def capture(repository, output):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    script = repository / "data_vis_and_stats/plot_clusters_and_sequencing.py"
    spec = importlib.util.spec_from_file_location("victsim3_plot", script)
    official = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(official)
    official.path_config = repository / "datasets/env/75x75_410v"
    official.path_vict = repository / "datasets/vict/410v"
    official.path_maps = output
    official.map_file = "map_predito.csv"
    official.path_clusters = output / "clusters"
    official.PLOTAR_SEQUENCIAMENTO = False

    config = official.read_config()
    if (config["GRID_WIDTH"], config["GRID_HEIGHT"], config["BASE"]) != (SIZE, SIZE, tuple(BASE)):
        raise ValueError("Configuração do visualizador incompatível com o mapa")
    cells = official.read_map(config)
    clusters = official.read_clusters()
    victims = pd.read_csv(output / "predicoes.csv").set_index("id")
    source = pd.read_csv(official.path_config / "env_victims.txt", header=None, names=XY)
    if not (victims[XY].add(BASE).eq(source.reindex(victims.index))).all().all():
        raise ValueError("O mapa e o cenário oficial não relacionam as mesmas posições e IDs")
    vital_names = FEATURES + ["gcs", "avpu"]
    reference = pd.read_csv(official.path_vict / "data.csv")
    if not victims[vital_names].eq(reference.loc[victims.index, vital_names]).all().all():
        raise ValueError("O gabarito oficial não corresponde aos sinais vitais do mapa")
    validate_clusters(official.path_clusters, victims.index, len(clusters))
    if len(cells) != SIZE**2:
        raise ValueError("Leitura incompleta do grid no visualizador")
    for vid, victim in victims.iterrows():
        cell = cells[tuple(victim[XY].to_numpy() + BASE)]
        if (cell["id"] != vid or cell["vitals"]["tri"] != victim["tri"]
                or not math.isclose(cell["vitals"]["sobr"], victim["sobr"], abs_tol=1e-12)):
            raise ValueError(f"Leitura divergente para a vítima {vid}")
    for number, ids in enumerate(clusters, 1):
        if set(ids) != set(victims.index[victims.cluster.eq(number)]):
            raise ValueError(f"Cluster {number} divergente no visualizador")

    # A borda oficial tem 3 px fixos. Células de 14 px deixam o círculo visível.
    side = SIZE * 14
    official.read_config = lambda: config | {"WINDOW_WIDTH": side, "WINDOW_HEIGHT": side}
    pygame = official.pygame
    original_flip = pygame.display.flip

    def save_frame():
        original_flip()
        screen = pygame.display.get_surface()
        pygame.image.save(screen, output / "graficos/grid.png")
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    pygame.display.flip = save_frame
    try:
        official.run()
    finally:
        pygame.display.flip = original_flip


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("victsim3", type=Path)
    parser.add_argument("--saida", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    capture(args.victsim3, args.saida)
