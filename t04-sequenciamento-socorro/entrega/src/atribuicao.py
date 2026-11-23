"""Reserva estática de vítimas, preservando a origem de cada lote."""
from dataclasses import dataclass
from itertools import product

from rotas import distancia_rota, vizinho


@dataclass(frozen=True)
class Lote:
    origem: int
    agente: int
    ids: tuple[int, ...]


def atribuir(grupos, vitimas, permitir_divisao=True):
    def custo(ids):
        rota = vizinho(ids, vitimas, clinico=False)
        return len(ids) + distancia_rota(vitimas[i].posicao for i in rota)

    opcoes = []
    for origem, ids in sorted(grupos.items()):
        criancas = tuple(i for i in ids if vitimas[i].idade <= 12)
        adultos = tuple(i for i in ids if vitimas[i].idade > 12)
        inteiro = custo(ids)
        elegiveis = (1, 2) if criancas else range(1, 6)
        escolhas = [((Lote(origem, a, ids), inteiro),) for a in elegiveis]
        if permitir_divisao and criancas and adultos:
            pediatrico, adulto = custo(criancas), custo(adultos)
            escolhas.extend(
                ((Lote(origem, a, criancas), pediatrico), (Lote(origem, b, adultos), adulto))
                for a in (1, 2) for b in (3, 4, 5)
            )
        opcoes.append(escolhas)

    melhor = None
    for selecao in product(*opcoes):
        cargas = [0.0] * 5
        lotes = []
        for escolha in selecao:
            for lote, valor in escolha:
                cargas[lote.agente - 1] += valor
                lotes.append(lote)
        if permitir_divisao and not all(cargas):
            continue
        criterio = max(cargas), len(lotes), sum(cargas)
        if melhor is None or criterio < melhor[0]:
            melhor = criterio, lotes, cargas
    if melhor is None:
        raise ValueError("Nenhuma alocação elegível utiliza os cinco agentes")
    _, lotes, cargas = melhor

    def fila(lote):
        urgencia = tuple(-sum(vitimas[i].tri == tri for i in lote.ids) for tri in (2, 1, 0))
        return urgencia, lote.origem

    return sorted(lotes, key=lambda lote: (lote.agente, fila(lote))), cargas
