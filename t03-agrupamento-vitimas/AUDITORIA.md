# Auditoria do enunciado v2 · Tarefa 3

| Requisito do enunciado | Implementado? | Arquivo ou evidência |
|---|---|---|
| §1.1 Prioridades com triagem, idade e distâncias | Atendido | Relatório, p. 3. START organiza a prioridade, idade define elegibilidade e a distância informa o custo. |
| §1.2 Agrupar pela estratégia | Atendido | `src/main.py`, `outputs/estrategia.csv` e seis arquivos de saída. |
| §1.3 Definir atribuição aos socorristas | Atendido | Relatório, p. 3, proposta por elegibilidade e carga. |
| §1.4 Definir coordenação do socorro | Atendido | Relatório, p. 3, reserva única de ID, paralelismo e redistribuição. |
| §1 Implementar atribuição e execução do resgate | Não aplicável | A especificação pede somente o agrupamento e a descrição das etapas futuras. |
| §2.1 Cenário 75×75, 410 vítimas, base (30,40), terreno e paredes | Atendido | `load_map`, `test_map` e verificação cruzada no visualizador. |
| §2.2 Cinco agentes, com atendimento de todas as idades pelos agentes 1 e 2 e idade >12 para 3–5 | Atendido | Relatório, p. 3. |
| §2.3a Critério com tri e/ou sobr e atributo adicional, com exclusão de gcs/avpu do critério | Atendido | `strategy_space` combina x, y e sobr. |
| §2.3b Justificativa geométrica e nuvem quando há até três características | Atendido | Relatório, p. 2, Fig. 3, diagnóstico de densidade e vizinhança. |
| §2.3c Normalização ou padronização | Atendido | Normalização espacial isotrópica, sobrevivência em [0,1], ponderação explícita e teste numérico. |
| §2.4a–b.i–v Ler o mapa com coordenadas relativas, dificuldade, ID e sinais vitais | Atendido | `load_map`, `test_map` e `test_reject_invalid_map`. |
| §2.4b.vi–vii Estimar tri e sobr usando os modelos anteriores | Atendido | `predict`, artefatos T1/T2, `test_predictions_transformations_and_no_leakage`. |
| §2.5 Um arquivo por cluster com um ID original por linha | Atendido | `validate_clusters` e `test_cluster_output_and_repeatability`. 410 IDs únicos. |
| §3.1.1 K-means básico com posição somente | Atendido | `experiment` usa x_rel, y_rel na parte básica. |
| §3.1.1.1 Tabela K=2–12, SSE e silhueta | Atendido | Relatório, Tabela 1, e `outputs/basico.csv`. A definição de SSE segue o notebook do professor. |
| §3.1.1.2 Gráfico de SSE por K | Atendido | Relatório, Fig. 1. |
| §3.1.1.3 Gráfico de silhueta por K | Atendido | Relatório, Fig. 2. |
| §3.1.1.4 Cotovelo e justificativa | Atendido | Relatório, p. 1, maior distância à corda em K=4. |
| §3.1.2.1.1 Critérios, intuição e número de agrupamentos | Atendido | Relatório, pp. 2–3, critérios e seis lotes fixos. |
| §3.1.2.1.2 Atribuição e coordenação | Atendido | Relatório, p. 3, duas propostas operacionais vinculadas aos dados dos lotes. |
| §3.1.2.2 Forma e regiões densas/esparsas | Atendido | Relatório, p. 2, Fig. 3 e estatísticas de vizinhança. |
| §3.1.2.3 Escolha justificada do algoritmo | Atendido | Relatório, p. 2, geometria, ruído observado e cobertura dos lotes. |
| §3.1.2.4 K-means, três parametrizações na tabela exigida | Atendido | Relatório, Tabela 2, K=4/6/8. |
| §3.1.2.4 DBSCAN, Tabela 1 | Não aplicável | A escolha final é K-means. `diagnostico_dbscan.csv` guarda as condições exploratórias completas. |
| §3.1.2.4 Silhueta global, cobertura, score e tratamento do ruído | Atendido | `silhouette_coverage` calcula a média por ponto. Cobertura e score são testados e constam no diagnóstico DBSCAN. No K-means a cobertura é 1, sem exclusões. |
| §3.1.2.5 Justificar a melhor configuração | Atendido | Relatório, p. 3, comparação de SSE, silhueta, dispersão e carga. |
| §3.1.2.6 Plotar clusters e tri no grid com o programa oficial | Atendido | `src/visualizador.py`, `test_official_visualizer` e relatório, Fig. 4. |
| §3.2.1 PDF com até quatro páginas e fonte 11 | Atendido | Quatro páginas A4, fonte nominal de 11 pt verificada no PDF, as quatro páginas renderizadas e inspecionadas. |
| §3.2.2 Códigos dos programas, sem código do simulador | Atendido | `entrega_moodle/src/` contém apenas a implementação T3 e o adaptador. |
| §3.2.3 Arquivos cluster*.txt | Atendido | `entrega_moodle/cluster_1.txt` a `cluster_6.txt`. |

## Verificação executada

- Oito testes passaram com a cópia oficial do VictSim3 configurada. A segunda execução do experimento produziu os mesmos CSVs e os mesmos arquivos de IDs.
- Os fontes da pasta Moodle foram executados com a entrada do projeto completo e reproduziram os seis arquivos.
- A compilação gerou quatro páginas. A auditoria conferiu o corpo em 11 pt nas quatro páginas e confrontou os números das duas tabelas de métricas com os CSVs.
