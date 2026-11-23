"""Executa a T4 com os artefatos já produzidos pela T3."""
import argparse
import csv
from collections import Counter
from pathlib import Path
from statistics import fmean, pstdev

from atribuicao import atribuir
from dados import carregar
from rotas import distancia_rota, otimizar

RAIZ = Path(__file__).resolve().parents[1]
T3 = RAIZ.parent / "t03-agrupamento-vitimas"
SEMENTE = 42


def escrever_csv(arquivo, campos, linhas):
    with arquivo.open("w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(campos)
        escritor.writerows(linhas)


def estatisticas(rota, vitimas):
    classes = Counter(vitimas[i].tri for i in rota)
    sobr = [float(vitimas[i].sobr) for i in rota]
    distancia = distancia_rota(vitimas[i].posicao for i in rota)
    return tuple(classes[tri] for tri in range(4)) + (len(rota), distancia, fmean(sobr), pstdev(sobr))


def executar(t3, saida, mapa=None):
    saida = saida.resolve()
    protegidas = (t3.resolve(), *(p.resolve() for p in T3.parent.glob("t0[123]-*") if p.is_dir()))
    if any(saida.is_relative_to(pasta) for pasta in protegidas):
        raise ValueError("A pasta de saída deve ficar fora dos projetos anteriores")
    vitimas, grupos = carregar(t3, mapa)
    _, carga_inteira = atribuir(grupos, vitimas, permitir_divisao=False)
    lotes, carga = atribuir(grupos, vitimas)
    clusters = saida / "clusters_ordenados"
    tabelas = saida / "tabelas"
    resultados, associacoes, convergencia, comparacoes = [], [], [], []
    arquivos = {}
    fila = Counter()
    for seq, lote in enumerate(lotes, 1):
        rota, historico, comparacao = otimizar(lote.ids, vitimas, SEMENTE + seq)
        fila[lote.agente] += 1
        arquivo = f"cluster_{seq}.txt"
        arquivos[arquivo] = "".join(f"{i}\n" for i in rota)
        resultados.append((seq, lote.agente, *estatisticas(rota, vitimas)))
        associacoes.append((seq, arquivo, lote.origem, lote.agente, fila[lote.agente],
                            len(rota), sum(vitimas[i].idade <= 12 for i in rota)))
        convergencia.extend((seq, geracao, fitness) for geracao, fitness in historico)
        comparacoes.extend((seq, nome, *valores) for nome, valores in comparacao.items())
    clusters.mkdir(parents=True, exist_ok=True)
    tabelas.mkdir(parents=True, exist_ok=True)
    for arquivo, conteudo in arquivos.items():
        (clusters / arquivo).write_text(conteudo, encoding="utf-8")
    escrever_csv(tabelas / "sequencias.csv",
                 ("seq", "agente", "VD", "AM", "VM", "PR", "total", "distancia", "media_sobr", "dp_sobr"),
                 resultados)
    totais = [linha[6] for linha in resultados]
    distancias = [linha[7] for linha in resultados]
    escrever_csv(tabelas / "agregados.csv", ("metrica", "media", "dp", "soma"),
                 ((nome, fmean(coluna), pstdev(coluna), sum(coluna))
                  for nome, coluna in (("vitimas_por_seq", totais), ("distancia_por_seq", distancias))))
    escrever_csv(tabelas / "atribuicao.csv",
                 ("seq", "arquivo", "cluster_t3", "agente", "ordem_no_agente", "vitimas", "ate_12"),
                 associacoes)
    escrever_csv(tabelas / "convergencia.csv", ("seq", "geracao", "fitness"), convergencia)
    escrever_csv(tabelas / "comparacao.csv", ("seq", "metodo", "distancia", "espera_ponderada"), comparacoes)
    escrever_csv(tabelas / "cargas_estimadas.csv", ("agente", "clusters_inteiros", "estrategia"),
                 zip(range(1, 6), carga_inteira, carga))
    for anterior in clusters.glob("cluster_*.txt"):
        if anterior.stem.removeprefix("cluster_").isdigit() and anterior.name not in arquivos:
            anterior.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t3", type=Path, default=T3)
    parser.add_argument("--saida", type=Path, default=RAIZ / "outputs")
    parser.add_argument("--mapa", type=Path)
    args = parser.parse_args()
    executar(args.t3, args.saida, args.mapa)
