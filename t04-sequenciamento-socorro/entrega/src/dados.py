"""Validação cruzada do cenário, das predições e dos agrupamentos da T3."""
import csv
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from itertools import product

CAMPOS = "x_rel y_rel obst id idade fc fr pas spo2 temp pr sg fx queim gcs avpu tri sobr".split()


@dataclass(frozen=True)
class Vitima:
    posicao: tuple[int, int]
    idade: int
    tri: int
    sobr: Decimal


def ler_csv(arquivo, campos):
    with arquivo.open(newline="", encoding="utf-8") as entrada:
        leitor = csv.DictReader(entrada)
        if leitor.fieldnames != campos:
            raise ValueError(f"Colunas inesperadas em {arquivo}")
        linhas = []
        for linha in leitor:
            if None in linha or any(not valor for valor in linha.values()):
                raise ValueError(f"Linha incompleta em {arquivo}: {leitor.line_num}")
            valores = {campo: Decimal(valor) for campo, valor in linha.items()}
            if not all(valor.is_finite() for valor in valores.values()):
                raise ValueError(f"Valor não finito em {arquivo}: {leitor.line_num}")
            linhas.append(valores)
    return linhas


def inteiro(valor):
    if valor != int(valor):
        raise ValueError(f"Esperado inteiro: {valor}")
    return int(valor)


def por_posicao(linhas):
    mapa = {(inteiro(l["x_rel"]), inteiro(l["y_rel"])): l for l in linhas}
    if len(linhas) != 5625 or set(mapa) != set(product(range(-30, 45), range(-40, 35))):
        raise ValueError("Grade relativa inválida")
    return mapa


def carregar(pasta, arquivo_mapa=None):
    original = por_posicao(ler_csv(arquivo_mapa or pasta / "map.csv", CAMPOS))
    saidas = pasta / "outputs"
    predito = por_posicao(ler_csv(saidas / "map_predito.csv", CAMPOS))
    vitimas = {}
    for posicao, antes in original.items():
        depois = predito[posicao]
        if any(antes[c] != depois[c] for c in CAMPOS[:-2]) or (antes["tri"], antes["sobr"]) != (-1, -1):
            raise ValueError(f"Mapa original e enriquecido incompatíveis em {posicao}")
        ident = inteiro(antes["id"])
        if ident == -1:
            if (depois["tri"], depois["sobr"]) != (-1, -1):
                raise ValueError(f"Predição em célula sem vítima: {posicao}")
            continue
        idade, tri, sobr = inteiro(depois["idade"]), inteiro(depois["tri"]), depois["sobr"]
        if ident < 0 or ident in vitimas or not 1 <= idade <= 90 or tri not in range(4) or not 0 <= sobr <= 1:
            raise ValueError(f"Dados inválidos para ID {ident}")
        vitimas[ident] = Vitima(posicao, idade, tri, sobr)
    if len(vitimas) != 410:
        raise ValueError("Esperadas 410 vítimas distintas")

    grupos = {
        numero: tuple(map(int, (saidas / "clusters" / f"cluster_{numero}.txt").read_text().splitlines()))
        for numero in range(1, 7)
    }
    if not all(grupos.values()) or Counter(i for ids in grupos.values() for i in ids) != Counter(vitimas.keys()):
        raise ValueError("Arquivos de cluster não particionam os IDs do mapa")
    grupo_por_id = {i: grupo for grupo, ids in grupos.items() for i in ids}
    predicoes = ler_csv(saidas / "predicoes.csv", CAMPOS + ["sobr_bruta", "cluster"])
    if Counter(l["id"] for l in predicoes) != Counter(vitimas.keys()):
        raise ValueError("IDs de predicoes.csv incompatíveis com o mapa")
    for linha in predicoes:
        ident = inteiro(linha["id"])
        registro = predito[vitimas[ident].posicao]
        if any(linha[c] != registro[c] for c in CAMPOS) or linha["cluster"] != grupo_por_id[ident]:
            raise ValueError(f"Predição ou cluster divergente para ID {ident}")
    return vitimas, grupos
