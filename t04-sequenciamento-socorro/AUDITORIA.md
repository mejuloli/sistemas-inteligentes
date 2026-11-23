# Auditoria da Tarefa 4

Referência principal: enunciado v2 de 28/10/2026. As evidências abaixo referem-se à execução final com o mapa fornecido, cujo SHA-256 coincide com o mapa original da T3.

| Requisito | Situação | Evidência |
|---|---|---|
| §1 e §2.1 — Utiliza agrupamentos da T3 | Atendido | `dados.carregar` verifica seis arquivos, 410 IDs únicos e o rótulo de origem em `predicoes.csv`. |
| §2.1 — Mapa do cenário | Atendido | `dados.por_posicao` cruza as 5.625 coordenadas relativas. `entradas.sha256` registra os insumos. |
| Preserva triagem e sobrevivência | Atendido | Os dois CSVs de predição concordam exatamente, incluindo valores decimais de sobrevivência. Há 100 VD, 106 AM, 108 VM e 96 PR. |
| §1 e §2.3 — Implementa atribuição | Atendido | `atribuicao.atribuir` compara grupos inteiros e divisões elegíveis. `atribuicao.csv` vincula agente, sequência, ordem e origem. |
| §2.2 — Cinco agentes e idade | Atendido | As 106 vítimas de até 12 anos estão nas filas 1 e 2. Teste de saída reconfere idade em cada ID exportado. |
| §2.4 e §3.1.2 — AG e parametrização | Atendido | `rotas.otimizar`, relatório §2 e testes da população, operadores, aptidão e reprodutibilidade. |
| §2.5 — Sequências ordenadas em cluster_*.txt | Atendido | 11 arquivos com um ID por linha. O teste compara cada arquivo à rota do AG e reconstrói o conjunto original por cluster. |
| §3.1.1 — Estratégia de socorro e coordenação | Atendido | Seções 1–2 do relatório explicam agrupamento, regras de partição e filas simultâneas. |
| §3.1.3 — Distância euclidiana fechada | Atendido | `distancia_rota` inclui saída e retorno à base relativa (0,0). Os testes calculam a distância novamente pela ordem exportada. |
| §3.1.4 — Tabela de classe, distância e sobrevivência | Atendido | `sequencias.csv`, `agregados.csv` e seção 3 do PDF. Média e DP populacional para sobrevivência e agregados de vítimas e distância. |
| §3.2 — Fontes, clusters e relatório | Atendido | `entrega/` reúne código da T4, 11 listas e PDF. O ZIP espelha esse conteúdo. |

## Verificações

- A execução dupla dos testes em diretórios temporários comparou as saídas byte a byte e confirmou os hashes das fontes antes e depois.
- As quatro páginas do PDF foram renderizadas e inspecionadas. As tabelas foram geradas diretamente dos CSVs.
- A base absoluta (30,40) foi conferida na configuração oficial. O leitor do visualizador soma a base às coordenadas do CSV, confirmando a origem relativa usada na T4. [Configuração oficial](https://github.com/tacla/VictSim3/blob/main/datasets/env/75x75_410v/env_config.txt) · [Leitor oficial](https://github.com/tacla/VictSim3/blob/main/data_vis_and_stats/plot_clusters_and_sequencing.py#L111-L125)

## Decisões e limites

Uma sequência é uma saída da base para um grupo ou subconjunto elegível. O lote 5 preserva a composição inteira. As outras origens têm duas sequências disjuntas. A maior carga aproximada passou de 962,08 para 551,08 no espaço de opções avaliado. Essa carga combina número de visitas e deslocamento aproximado. O quantitativo de vítimas por agente foi 62, 78, 85, 91 e 94.

As atribuições consideram um grupo pediátrico e um adulto por origem quando há divisão. É uma escolha de coordenação que restringe o espaço de busca. As filas são estáticas. Obstáculos, tempos de tratamento, dinâmica de sobrevivência e redistribuição em tempo de execução são questões do resgate posterior. O VictSim3 serve de referência de formato e cenário nesta solução, conforme seu uso opcional no §2.3.
