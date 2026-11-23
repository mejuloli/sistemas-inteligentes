# Tarefa 4 — Sequenciamento de socorro

UTFPR · Sistemas Inteligentes (CSI30) · Prof. Cesar Augusto Tacla

## Reproduzir a execução

Use Python 3.10 ou superior. O sequenciamento e os testes usam a biblioteca padrão. Para gerar o PDF, use pdfLaTeX com Latin Modern, Babel português, Booktabs, Geometry e Microtype.

Execute dentro de `t04-sequenciamento-socorro`:

```sh
python src/main.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
python relatorio/gerar_relatorio.py
```

Por padrão, a leitura usa o projeto vizinho `t03-agrupamento-vitimas`, incluindo `map.csv`, `outputs/map_predito.csv`, `outputs/predicoes.csv` e os seis arquivos de `outputs/clusters`. Para conferir diretamente o mapa do enunciado na reprodução, passe `--mapa '/caminho/map(2).csv'`. A cópia conferida tem o mesmo SHA-256 do mapa da T3, registrado em `entradas.sha256`. Para escolher outra localização dos insumos, use `--t3`. A opção `--saida` permite escolher uma pasta de resultados isolada.

A T4 reaproveita todas as predições das MLPs e os agrupamentos de K-means da T3. Cada arquivo de saída contém o circuito fechado de um agente para um único grupo ou subconjunto elegível. O agente é identificado na tabela de atribuição e na seção 3 do relatório.

| Caminho | Conteúdo |
|---|---|
| `src/dados.py` | Validação cruzada do mapa, predições e partição da T3 |
| `src/atribuicao.py` | Enumeração de alocações elegíveis e ordem das filas |
| `src/rotas.py` | AG de permutações, vizinho mais próximo, medidas de rota |
| `src/main.py` | Execução, estatísticas e exportação |
| `outputs/clusters_ordenados/` | 11 arquivos de IDs, um ID por linha |
| `outputs/tabelas/atribuicao.csv` | Sequência, cluster de origem, agente e posição na fila |
| `outputs/tabelas/sequencias.csv`, `agregados.csv` | Tabela de sequência e agregados do enunciado |
| `outputs/tabelas/comparacao.csv`, `convergencia.csv`, `cargas_estimadas.csv` | Referências, evolução da aptidão e cargas aproximadas |
| `relatorio/` | Gerador, relatório Markdown e PDF |
| `AUDITORIA.md` | Checklist e verificações |
| `entrega/` e `entrega_moodle.zip` | Arquivos preparados para submissão |

O gráfico de sequenciamento do VictSim3 pode ler os pares mapa predito e pasta de rotas. O leitor oficial percorre os nomes em ordem lexicográfica, de modo que `cluster_10.txt` aparece antes de `cluster_2.txt` na lista do visualizador. A fila de cada agente é dada pela coluna `ordem_no_agente`.

## Referências

- Enunciado T4 v2, 28/10/2026, seções 1–3. Relatório da T3, seções 2–3, `METODOLOGIA.md` e `AUDITORIA.md`.
- Base absoluta do cenário e conversão de coordenadas relativas. [Configuração 75×75](https://github.com/tacla/VictSim3/blob/main/datasets/env/75x75_410v/env_config.txt) · [Visualizador oficial](https://github.com/tacla/VictSim3/blob/main/data_vis_and_stats/plot_clusters_and_sequencing.py#L111-L125)
- Codificação START e dados de referência. [Atributos do VictSim3](https://github.com/tacla/VictSim3/blob/main/data_creation/atributos.md)
- Materiais da disciplina e exemplos da arquitetura. [Sistemas-Inteligentes](https://github.com/tacla/Sistemas-Inteligentes) · [VictSim3](https://github.com/tacla/VictSim3) · [Exemplos SMA](https://github.com/tacla/VictSim3/tree/main/sma)
