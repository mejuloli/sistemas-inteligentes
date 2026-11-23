"""Gera o Markdown e compila o PDF a partir das tabelas da execução."""
import csv
import subprocess
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parents[1]
TABELAS = RAIZ / "outputs/tabelas"
DESTINO = RAIZ / "relatorio"
CARACTERES_TEX = {"&": r"\&", "%": r"\%", "_": r"\_", "#": r"\#",
                  "≤": r"$\le$", "±": r"$\pm$", "−": r"$-$", "μ": r"$\mu$", "σ": r"$\sigma$"}


def tex(texto):
    return "".join(CARACTERES_TEX.get(letra, letra) for letra in str(texto))


def num(valor, casas=2):
    return f"{float(valor):,.{casas}f}".replace(",", " ").replace(".", ",")


def ler(nome):
    with (TABELAS / f"{nome}.csv").open(newline="", encoding="utf-8") as entrada:
        return list(csv.DictReader(entrada))


class Relatorio:
    def __init__(self):
        self.md = ["# Tarefa 4 — Sequenciamento de socorro",
                   "UTFPR · Sistemas Inteligentes (CSI30) · Prof. Cesar Augusto Tacla · RA 2588005"]
        self.latex = [r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[portuguese]{babel}
\usepackage{lmodern,booktabs}
\usepackage[margin=2.35cm]{geometry}
\usepackage{microtype}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\begin{document}
{\small UTFPR · Sistemas Inteligentes (CSI30) · Prof. Cesar Augusto Tacla · RA 2588005}
\par\medskip
{\LARGE\bfseries Tarefa 4 — Sequenciamento de socorro\par}
"""]

    def secao(self, titulo, pagina=False):
        self.md.append("## " + titulo)
        if pagina:
            self.latex.append(r"\newpage")
        self.latex.append(r"\section*{" + tex(titulo) + "}")

    def paragrafo(self, texto):
        self.md.append(texto)
        self.latex.append(tex(texto))

    def tabela(self, nomes, linhas):
        self.md.append("\n".join(
            "| " + " | ".join(map(str, linha)) + " |"
            for linha in (nomes, ["---"] * len(nomes), *linhas)
        ))
        self.latex.extend([
            r"\begin{center}\small",
            r"\begin{tabular}{" + "l" + "r" * (len(nomes) - 1) + "}",
            r"\toprule",
            " & ".join(map(tex, nomes)) + r" \\ \midrule",
            *(" & ".join(map(tex, linha)) + r" \\" for linha in linhas),
            r"\bottomrule\end{tabular}\end{center}",
        ])

    def salvar(self):
        (DESTINO / "relatorio_t4.md").write_text("\n\n".join(self.md) + "\n", encoding="utf-8")
        with TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            (pasta / "relatorio_t4.tex").write_text("\n\n".join(self.latex + [r"\end{document}"]),
                                                  encoding="utf-8")
            compilacao = subprocess.run(
                ["pdflatex", "-halt-on-error", "-interaction=nonstopmode", "relatorio_t4.tex"],
                cwd=pasta, text=True, capture_output=True,
            )
            if compilacao.returncode:
                raise RuntimeError(compilacao.stdout + compilacao.stderr)
            problemas = [linha for linha in compilacao.stdout.splitlines() if "Overfull" in linha]
            if problemas:
                raise RuntimeError("\n".join(problemas))
            (DESTINO / "relatorio_t4.pdf").write_bytes((pasta / "relatorio_t4.pdf").read_bytes())


def gerar():
    rel = Relatorio()
    cargas = ler("cargas_estimadas")
    seqs = ler("sequencias")
    atribuicoes = ler("atribuicao")
    total = {r["metrica"]: r for r in ler("agregados")}
    rel.secao("1. Cenário, atribuição e coordenação")
    rel.paragrafo(
        "O cenário 75×75_410v contém 5.625 células e 410 vítimas. O mapa fornecido na T4 é "
        "idêntico ao mapa original da T3. Cruzamos suas posições e IDs com map_predito.csv, "
        "predicoes.csv e os seis arquivos de cluster. A triagem e a sobrevivência são as "
        "predições reutilizadas das MLPs das T1 e T2. A idade vem do mapa."
    )
    rel.paragrafo(
        "A T3 fixou K = 6 após comparar K = 4, 6 e 8. O K-means usa (x_rel/74, y_rel/74, 0,45 × sobr), "
        "com semente 42 e 50 inicializações. A escala comum preserva a geometria espacial. "
        "O peso favorece proximidade e permite que sobrevivência influencie a partição. "
        "O raio RMS de 11,06 células e silhueta de 0,3756 equilibraram dispersão e coesão. "
        "O DBSCAN foi diagnóstico. START orienta a fila e idade determina elegibilidade."
    )
    rel.paragrafo(
        "Todos os seis lotes têm vítimas de até 12 anos, 106 no total. Com lotes inteiros, "
        "somente os agentes 1 e 2 seriam elegíveis. Avaliamos essa linha de base e depois "
        "enumeramos, para cada lote misto, as opções inteiras e a divisão pediátrica/adulta "
        "entre um agente 1–2 e um agente 3–5. A carga de um lote é o número de vítimas somado "
        "à distância fechada de vizinho mais próximo sem prioridade clínica. Para balancear "
        "serviço e deslocamento, o proxy atribui a cada visita o mesmo peso de uma célula. "
        "Entre as opções que ocupam os cinco agentes, minimizamos a maior carga individual. "
        "Em empate, preferimos menos viagens e depois menor carga total."
    )
    rel.tabela(("Agente", "Só lotes inteiros", "Estratégia adotada"),
               [(r["agente"], num(r["clusters_inteiros"]), num(r["estrategia"])) for r in cargas])
    rel.paragrafo(
        "A solução divide cinco lotes e mantém o lote 5 inteiro. Cada ID fica reservado a "
        "um agente. As filas podem começar em paralelo, inclusive para subconjuntos disjuntos "
        "do mesmo lote. Um agente conclui cada circuito antes de iniciar o próximo. Para "
        "ordenar sua fila, compara quantidades de vermelhos, amarelos e verdes, nessa ordem, "
        "com desempate pelo cluster de origem. Isso prioriza o volume urgente por viagem. "
        "Revisão e redistribuição em campo requerem um coordenador durante a execução."
    )

    rel.secao("2. Algoritmo genético e critérios", pagina=True)
    rel.paragrafo(
        "Cada indivíduo é uma permutação dos IDs de um lote, representada por quatro blocos "
        "na ordem vermelho, amarelo, verde e preto. A ordenação é local à viagem. As vítimas "
        "classificadas em preto são mantidas e vistoriadas no fim. A população inicial "
        "usa a rota de vizinho mais próximo dentro da classe, com desempate por menor sobr "
        "e ID, e mais 63 permutações aleatórias restritas aos blocos."
    )
    rel.paragrafo(
        "Para pontos A e B, d(A,B) é a raiz da soma dos quadrados das diferenças dos dois eixos. "
        "Se C_i é a distância acumulada da base até a chegada à vítima i, a distância do relatório "
        "é D = C_última + d(última, base). Em coordenadas relativas, a base absoluta (30,40) "
        "corresponde a (0,0). Cada segmento é euclidiano e o cálculo desconsidera obstáculos. "
        "A unidade é a célula."
    )
    rel.paragrafo(
        "O AG minimiza F = D/D_ref + 0,25 × E/E_ref. O termo E soma (1 − sobr_i) × C_i para "
        "vítimas verdes, amarelas e vermelhas. Preto tem peso zero nesse termo e continua "
        "influenciando D. A ponderação segue a proposta da T3 de antecipar menor sobrevivência "
        "quando os custos são próximos. Os denominadores fixos vêm do vizinho mais próximo "
        "com prioridade START. Se um denominador for zero, usa-se 1. Normalizar pela "
        "referência torna os termos adimensionais. O peso de 0,25 faz um ganho relativo de "
        "4% em E compensar 1% de aumento em D. Essa escolha privilegia deslocamento e "
        "representa um critério de planejamento, sem calibração clínica."
    )
    rel.paragrafo(
        "Selecionamos pais por torneios de três. Com probabilidade de 90% por descendente, "
        "o cruzamento de ordem (OX) preserva um trecho do pai em cada bloco e completa as "
        "posições livres na ordem cíclica da mãe. Com probabilidade de 35%, a mutação "
        "inverte um trecho em um bloco elegível, promovendo mudanças mesmo quando os pais "
        "se assemelham. Dois indivíduos de elite passam intactos. A população de 64 mantém "
        "variação com custo moderado. Rodamos até 300 gerações, com semente 42 + número "
        "da sequência. Uma rota composta apenas de blocos unitários tem uma única ordem "
        "factível e dispensa evolução."
    )
    rel.paragrafo(
        "A inicialização, OX e inversão só operam nas permutações do mesmo conjunto de "
        "IDs dentro da classe. Assim a sequência mantém todos os IDs e a elegibilidade "
        "resolvida antes do AG. A trilha da melhor aptidão é registrada por geração. "
        "O elitismo conserva a referência como limite superior da aptidão inicial."
    )

    rel.secao("3. Resultados das sequências", pagina=True)
    linhas = [tuple(r[c] for c in ("seq", "agente", "VD", "AM", "VM", "PR", "total"))
              + (num(r["distancia"]), num(r["media_sobr"], 4), num(r["dp_sobr"], 4)) for r in seqs]
    rel.tabela(("Seq.", "Agente", "VD", "AM", "VM", "PR", "Total", "Dist.", "μ sobr", "σ sobr"), linhas)
    rel.tabela(("Agregado por sequência", "Média ± DP", "Soma"),
               [(nome, f"{num(total[chave]['media'])} ± {num(total[chave]['dp'])}", num(total[chave]["soma"], casas))
                for chave, nome, casas in (("vitimas_por_seq", "Vítimas", 0), ("distancia_por_seq", "Distância", 2))])
    classes = [sum(int(r[c]) for r in seqs) for c in ("VD", "AM", "VM", "PR")]
    rel.paragrafo(
        f"Totais por classe, na ordem da tabela: {', '.join(map(str, classes))}. "
        "O desvio é populacional, com divisor N, porque as tabelas descrevem o conjunto "
        "completo de vítimas de cada rota e, nos agregados, todas as rotas. "
        "Uma sequência unitária tem desvio zero."
    )
    rel.tabela(("Seq.", "Cluster T3", "Agente", "Posição na fila", "Idade ≤ 12"),
               [tuple(r[c] for c in ("seq", "cluster_t3", "agente", "ordem_no_agente", "ate_12"))
                for r in atribuicoes])
    rel.paragrafo("O arquivo cluster_N.txt representa a sequência N. A tabela de associação "
                  "mantém a origem na T3 mesmo quando mais de uma sequência deriva de um grupo.")

    rel.secao("4. Referências de comparação e limites", pagina=True)
    comparacoes = defaultdict(list)
    for r in ler("comparacao"):
        comparacoes[r["metodo"]].append((float(r["distancia"]), float(r["espera_ponderada"])))
    somas = {metodo: tuple(map(sum, zip(*valores))) for metodo, valores in comparacoes.items()}
    rel.tabela(("Método", "Distância somada", "Espera ponderada somada"),
               [(rotulo, *map(num, somas[chave])) for chave, rotulo in (
                   ("original", "Ordem original restrita ao lote"), ("vizinho_clinico", "Vizinho com START"),
                   ("ag", "Algoritmo genético"),
               )])
    d, e = somas["ag"]
    dref, eref = somas["vizinho_clinico"]
    rel.paragrafo(
        f"Com a mesma restrição START, o AG reduziu a distância somada em {num(100 * (1 - d / dref), 1)}% "
        f"e a espera ponderada em {num(100 * (1 - e / eref), 1)}% frente ao vizinho. "
        "A ordem original mantém a ordem dos IDs no arquivo da T3 após a divisão. "
        "A comparação com ela inclui o efeito de introduzir a prioridade por classe."
    )
    trajetorias = defaultdict(list)
    for r in ler("convergencia"):
        trajetorias[r["seq"]].append(float(r["fitness"]))
    rel.tabela(("Seq.", "Aptidão inicial", "Aptidão final", "Primeira geração do melhor"),
               [(seq, num(valores[0], 4), num(valores[-1], 4), valores.index(valores[-1]))
                for seq, valores in trajetorias.items()])
    rel.paragrafo(
        "No ensaio com semente fixa, a última melhora registrada ocorreu na geração "
        f"{max(v.index(v[-1]) for v in trajetorias.values())}. A trilha permite avaliar "
        "o orçamento de 300 gerações neste ensaio. A configuração é heurística e "
        "a análise é de uma execução reproduzível, sem alegação de ótimo global."
    )
    rel.paragrafo(
        "A soma das distâncias mede percurso total. O tempo de conclusão em paralelo também "
        "depende da fila de cada agente, do terreno, das paredes, da velocidade e do atendimento. "
        "A prioridade é local à rota e à sua fila. As estimativas de sobrevivência são fixas "
        "e carregam erros dos modelos das tarefas anteriores. O recorte por idade pode "
        "aumentar o número de saídas e o custo total quando comparado a roteiros sem paralelismo."
    )
    rel.paragrafo(
        "Fontes consultadas: Tacla, Tarefa 4 — Sequenciamento de socorro, v2, 28/10/2026, "
        "seções 1–3. Relatório da Tarefa 3, seções 2–3, e sua metodologia. "
        "VictSim3, documentação dos atributos e código de integração do visualizador na T3."
    )
    rel.salvar()


if __name__ == "__main__":
    gerar()
