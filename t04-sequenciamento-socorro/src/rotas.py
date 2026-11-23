"""Distância fechada, avaliação clínica e evolução de permutações."""
from math import dist
from random import Random

BASE = (0, 0)
PRIORIDADE = {2: 0, 1: 1, 0: 2, 3: 3}
POPULACAO = 64
GERACOES = 300
CRUZAMENTO = 0.90
MUTACAO = 0.35
ELITE = 2
TORNEIO = 3


def distancia_rota(posicoes):
    pontos = (BASE, *posicoes, BASE)
    return sum(dist(a, b) for a, b in zip(pontos, pontos[1:]))


def vizinho(ids, vitimas, clinico=True):
    pendentes = set(ids)
    posicao = BASE
    rota = []
    while pendentes:
        ident = min(pendentes, key=lambda i: (
            PRIORIDADE[vitimas[i].tri] if clinico else 0,
            dist(posicao, vitimas[i].posicao), vitimas[i].sobr, i,
        ))
        rota.append(ident)
        pendentes.remove(ident)
        posicao = vitimas[ident].posicao
    return tuple(rota)


def medidas(rota, distancias, pesos):
    anterior = None
    chegada = espera = 0.0
    for ident in rota:
        chegada += distancias[anterior][ident]
        espera += pesos[ident] * chegada
        anterior = ident
    return chegada + distancias[anterior][None], espera


def crossover(pai, mae, rng):
    if len(pai) < 2:
        return pai
    inicio, fim = sorted(rng.sample(range(len(pai)), 2))
    centro = pai[inicio:fim + 1]
    reservados = set(centro)
    livres = tuple(i for i in mae[fim + 1:] + mae[:fim + 1] if i not in reservados)
    cauda = len(pai) - fim - 1
    return livres[cauda:] + centro + livres[:cauda]


def mutar(bloco, rng):
    if len(bloco) < 2:
        return bloco
    inicio, fim = sorted(rng.sample(range(len(bloco)), 2))
    return bloco[:inicio] + bloco[inicio:fim + 1][::-1] + bloco[fim + 1:]


def montar_blocos(rota, vitimas):
    return tuple(tuple(i for i in rota if PRIORIDADE[vitimas[i].tri] == p) for p in range(4))


def rota_de(individuo):
    return tuple(i for bloco in individuo for i in bloco)


def iniciar_populacao(referencia, rng):
    return [referencia] + [
        tuple(tuple(rng.sample(bloco, len(bloco))) for bloco in referencia)
        for _ in range(POPULACAO - 1)
    ]


def otimizar(ids, vitimas, semente):
    rng = Random(semente)
    referencia = vizinho(ids, vitimas)
    pontos = {None: BASE, **{i: vitimas[i].posicao for i in ids}}
    distancias = {i: {j: dist(a, b) for j, b in pontos.items()} for i, a in pontos.items()}
    pesos = {i: float(1 - vitimas[i].sobr) if vitimas[i].tri != 3 else 0.0 for i in ids}
    escala_dist, escala_espera = medidas(referencia, distancias, pesos)

    def avaliar(individuo):
        distancia, espera = medidas(rota_de(individuo), distancias, pesos)
        return distancia / (escala_dist or 1) + 0.25 * espera / (escala_espera or 1)

    blocos = montar_blocos(referencia, vitimas)
    populacao = [blocos] if all(len(b) < 2 for b in blocos) else iniciar_populacao(blocos, rng)
    avaliados = sorted((avaliar(pessoa), pessoa) for pessoa in populacao)
    historico = [(0, avaliados[0][0])]
    if len(avaliados) > 1:
        for geracao in range(1, GERACOES + 1):
            proxima = avaliados[:ELITE]
            while len(proxima) < POPULACAO:
                pai = min(rng.sample(avaliados, TORNEIO))[1]
                filho = pai
                if rng.random() < CRUZAMENTO:
                    mae = min(rng.sample(avaliados, TORNEIO))[1]
                    filho = tuple(crossover(a, b, rng) for a, b in zip(pai, mae))
                mutaveis = [p for p, bloco in enumerate(filho) if len(bloco) >= 2]
                if mutaveis and rng.random() < MUTACAO:
                    p = rng.choice(mutaveis)
                    filho = filho[:p] + (mutar(filho[p], rng),) + filho[p + 1:]
                proxima.append((avaliar(filho), filho))
            avaliados = sorted(proxima)
            historico.append((geracao, avaliados[0][0]))

    rota = rota_de(avaliados[0][1])
    comparacao = {}
    for nome, ordem in (("original", ids), ("vizinho_clinico", referencia), ("ag", rota)):
        distancia, espera = medidas(ordem, distancias, pesos)
        comparacao[nome] = (distancia, espera)
    return rota, historico, comparacao
