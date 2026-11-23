import csv
from collections import Counter
from contextlib import ExitStack
from hashlib import sha256
from math import dist
from pathlib import Path
from random import Random
from statistics import mean, pstdev
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atribuicao import atribuir
from dados import carregar, por_posicao
from main import T3, executar, estatisticas
from rotas import (
    BASE, PRIORIDADE, crossover, distancia_rota, iniciar_populacao, medidas,
    montar_blocos, mutar, otimizar, rota_de, vizinho,
)


def ler(arquivo):
    with arquivo.open(newline="", encoding="utf-8") as entrada:
        return list(csv.DictReader(entrada))


class TesteT4(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vitimas, cls.grupos = carregar(T3)

    def test_integridade_fontes(self):
        esperadas = {int(r["id"]): r for r in ler(T3 / "outputs/predicoes.csv")}
        self.assertEqual(len(self.vitimas), 410)
        self.assertEqual(set(esperadas), set(self.vitimas))
        self.assertEqual(Counter(v.tri for v in self.vitimas.values()), {0: 100, 1: 106, 2: 108, 3: 96})
        for ident, vitima in self.vitimas.items():
            self.assertEqual(vitima.sobr, type(vitima.sobr)(esperadas[ident]["sobr"]))
            self.assertEqual(vitima.tri, int(esperadas[ident]["tri"]))
        self.assertEqual(sum(v.idade <= 12 for v in self.vitimas.values()), 106)
        with self.assertRaises(ValueError):
            por_posicao([])

    def test_rejeita_cluster_duplicado_e_predicao_ausente(self):
        for alvo, conteudo in (
            (T3 / "outputs/clusters/cluster_1.txt", "0\n0\n"),
            (T3 / "outputs/predicoes.csv",
             (T3 / "outputs/predicoes.csv").read_text().replace(",0.504895570452598,", ",,", 1)),
        ):
            with self.subTest(arquivo=alvo.name), TemporaryDirectory() as temp:
                raiz = Path(temp)
                (raiz / "outputs/clusters").mkdir(parents=True)
                fontes = [T3 / "map.csv", T3 / "outputs/map_predito.csv", T3 / "outputs/predicoes.csv",
                          *sorted((T3 / "outputs/clusters").glob("cluster_*.txt"))]
                for origem in fontes:
                    destino = raiz / origem.relative_to(T3)
                    if origem == alvo:
                        destino.write_text(conteudo)
                    else:
                        destino.symlink_to(origem)
                with self.assertRaises(ValueError):
                    carregar(raiz)

    def test_atribuicao(self):
        _, inteira = atribuir(self.grupos, self.vitimas, permitir_divisao=False)
        lotes, carga = atribuir(self.grupos, self.vitimas)
        self.assertEqual(inteira[2:], [0, 0, 0])
        self.assertLess(max(carga), max(inteira))
        self.assertEqual({lote.agente for lote in lotes}, set(range(1, 6)))
        for origem, ids in self.grupos.items():
            self.assertCountEqual([i for lote in lotes if lote.origem == origem for i in lote.ids], ids)
        for lote in lotes:
            self.assertTrue(all(lote.agente < 3 or self.vitimas[i].idade > 12 for i in lote.ids))

    def test_distancia_e_espera_manuais(self):
        a, b = (3, 4), (0, 4)
        self.assertEqual(dist(a, a), 0)
        self.assertEqual(dist(a, b), dist(b, a))
        self.assertEqual(distancia_rota([a, b]), 12)
        self.assertEqual(distancia_rota([a]), 10)
        self.assertEqual(distancia_rota([]), 0)
        pontos = {None: BASE, 0: a, 1: b}
        matriz = {i: {j: dist(x, y) for j, y in pontos.items()} for i, x in pontos.items()}
        self.assertEqual(medidas((0, 1), matriz, {0: 0.5, 1: 0.25}), (12, 4.5))
        self.assertEqual(estatisticas([0], self.vitimas)[-1], 0)

    def test_populacao_operadores_e_elitismo(self):
        ids = self.grupos[1][:30]
        rng = Random(42)
        referencia = montar_blocos(vizinho(ids, self.vitimas), self.vitimas)
        populacao = iniciar_populacao(referencia, rng)
        for individuo in populacao:
            self.assertCountEqual(rota_de(individuo), ids)
            for pai, mae in zip(referencia, individuo):
                filho = crossover(pai, mae, rng)
                self.assertCountEqual(filho, pai)
                self.assertCountEqual(mutar(filho, rng), pai)
        rota, historico, comparacao = resultado = otimizar(ids, self.vitimas, 42)
        self.assertEqual(resultado, otimizar(ids, self.vitimas, 42))
        self.assertCountEqual(rota, ids)
        self.assertEqual([h[1] for h in historico], sorted((h[1] for h in historico), reverse=True))
        d, e = comparacao["ag"]
        d0, e0 = comparacao["vizinho_clinico"]
        self.assertAlmostEqual(historico[-1][1], d / d0 + 0.25 * e / e0)

    def test_execucao_exportacao_e_reprodutibilidade(self):
        fontes = [T3 / "map.csv", T3 / "outputs/map_predito.csv", T3 / "outputs/predicoes.csv",
                  *sorted((T3 / "outputs/clusters").glob("cluster_*.txt"))]
        hashes = {p: sha256(p.read_bytes()).digest() for p in fontes}
        with ExitStack() as stack:
            primeira, segunda = [Path(stack.enter_context(TemporaryDirectory())) for _ in range(2)]
            rotas = []
            from main import otimizar as executar_ag

            def capturar(*args):
                resultado = executar_ag(*args)
                rotas.append(resultado[0])
                return resultado

            with patch("main.otimizar", side_effect=capturar):
                executar(T3, primeira)
            executar(T3, segunda)
            self.assertEqual({p.relative_to(primeira): p.read_bytes() for p in primeira.rglob("*") if p.is_file()},
                             {p.relative_to(segunda): p.read_bytes() for p in segunda.rglob("*") if p.is_file()})
            tabelas = primeira / "tabelas"
            atribuicoes = ler(tabelas / "atribuicao.csv")
            registros = ler(tabelas / "sequencias.csv")
            self.assertEqual(len(rotas), len(registros))
            self.assertEqual(len(rotas), len(atribuicoes))
            encontrados = []
            for esperada, lote, metricas in zip(rotas, atribuicoes, registros):
                texto = (primeira / "clusters_ordenados" / lote["arquivo"]).read_text()
                ids = tuple(map(int, texto.splitlines()))
                self.assertEqual(texto, "".join(f"{i}\n" for i in esperada))
                self.assertEqual((lote["seq"], lote["agente"]), (metricas["seq"], metricas["agente"]))
                encontrados.extend(ids)
                self.assertTrue(set(ids) <= set(self.grupos[int(lote["cluster_t3"])]))
                vs = [self.vitimas[i] for i in ids]
                self.assertTrue(all(int(lote["agente"]) < 3 or v.idade > 12 for v in vs))
                classes = [PRIORIDADE[v.tri] for v in vs]
                self.assertEqual(classes, sorted(classes))
                self.assertEqual(int(metricas["total"]), len(ids))
                for tri, chave in enumerate(("VD", "AM", "VM", "PR")):
                    self.assertEqual(int(metricas[chave]), sum(v.tri == tri for v in vs))
                pontos = [BASE, *(v.posicao for v in vs), BASE]
                self.assertAlmostEqual(float(metricas["distancia"]), sum(map(dist, pontos, pontos[1:])))
                self.assertAlmostEqual(float(metricas["media_sobr"]), mean(float(v.sobr) for v in vs))
                self.assertAlmostEqual(float(metricas["dp_sobr"]), pstdev(float(v.sobr) for v in vs))
            self.assertCountEqual(encontrados, self.vitimas.keys())
            agregados = ler(tabelas / "agregados.csv")
            for linha, campo in zip(agregados, ("total", "distancia")):
                valores = [float(r[campo]) for r in registros]
                self.assertAlmostEqual(float(linha["media"]), mean(valores))
                self.assertAlmostEqual(float(linha["dp"]), pstdev(valores))
                self.assertAlmostEqual(float(linha["soma"]), sum(valores))
        self.assertEqual(hashes, {p: sha256(p.read_bytes()).digest() for p in fontes})
