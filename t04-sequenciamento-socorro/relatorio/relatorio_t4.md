# Tarefa 4 — Sequenciamento de socorro

UTFPR · Sistemas Inteligentes (CSI30) · Prof. Cesar Augusto Tacla · RA 2588005

## 1. Cenário, atribuição e coordenação

O cenário 75×75_410v contém 5.625 células e 410 vítimas. O mapa fornecido na T4 é idêntico ao mapa original da T3. Cruzamos suas posições e IDs com map_predito.csv, predicoes.csv e os seis arquivos de cluster. A triagem e a sobrevivência são as predições reutilizadas das MLPs das T1 e T2. A idade vem do mapa.

A T3 fixou K = 6 após comparar K = 4, 6 e 8. O K-means usa (x_rel/74, y_rel/74, 0,45 × sobr), com semente 42 e 50 inicializações. A escala comum preserva a geometria espacial. O peso favorece proximidade e permite que sobrevivência influencie a partição. O raio RMS de 11,06 células e silhueta de 0,3756 equilibraram dispersão e coesão. O DBSCAN foi diagnóstico. START orienta a fila e idade determina elegibilidade.

Todos os seis lotes têm vítimas de até 12 anos, 106 no total. Com lotes inteiros, somente os agentes 1 e 2 seriam elegíveis. Avaliamos essa linha de base e depois enumeramos, para cada lote misto, as opções inteiras e a divisão pediátrica/adulta entre um agente 1–2 e um agente 3–5. A carga de um lote é o número de vítimas somado à distância fechada de vizinho mais próximo sem prioridade clínica. Para balancear serviço e deslocamento, o proxy atribui a cada visita o mesmo peso de uma célula. Entre as opções que ocupam os cinco agentes, minimizamos a maior carga individual. Em empate, preferimos menos viagens e depois menor carga total.

| Agente | Só lotes inteiros | Estratégia adotada |
| --- | --- | --- |
| 1 | 962,08 | 543,42 |
| 2 | 931,56 | 551,08 |
| 3 | 0,00 | 358,46 |
| 4 | 0,00 | 506,93 |
| 5 | 0,00 | 509,29 |

A solução divide cinco lotes e mantém o lote 5 inteiro. Cada ID fica reservado a um agente. As filas podem começar em paralelo, inclusive para subconjuntos disjuntos do mesmo lote. Um agente conclui cada circuito antes de iniciar o próximo. Para ordenar sua fila, compara quantidades de vermelhos, amarelos e verdes, nessa ordem, com desempate pelo cluster de origem. Isso prioriza o volume urgente por viagem. Revisão e redistribuição em campo requerem um coordenador durante a execução.

## 2. Algoritmo genético e critérios

Cada indivíduo é uma permutação dos IDs de um lote, representada por quatro blocos na ordem vermelho, amarelo, verde e preto. A ordenação é local à viagem. As vítimas classificadas em preto são mantidas e vistoriadas no fim. A população inicial usa a rota de vizinho mais próximo dentro da classe, com desempate por menor sobr e ID, e mais 63 permutações aleatórias restritas aos blocos.

Para pontos A e B, d(A,B) é a raiz da soma dos quadrados das diferenças dos dois eixos. Se C_i é a distância acumulada da base até a chegada à vítima i, a distância do relatório é D = C_última + d(última, base). Em coordenadas relativas, a base absoluta (30,40) corresponde a (0,0). Cada segmento é euclidiano e o cálculo desconsidera obstáculos. A unidade é a célula.

O AG minimiza F = D/D_ref + 0,25 × E/E_ref. O termo E soma (1 − sobr_i) × C_i para vítimas verdes, amarelas e vermelhas. Preto tem peso zero nesse termo e continua influenciando D. A ponderação segue a proposta da T3 de antecipar menor sobrevivência quando os custos são próximos. Os denominadores fixos vêm do vizinho mais próximo com prioridade START. Se um denominador for zero, usa-se 1. Normalizar pela referência torna os termos adimensionais. O peso de 0,25 faz um ganho relativo de 4% em E compensar 1% de aumento em D. Essa escolha privilegia deslocamento e representa um critério de planejamento, sem calibração clínica.

Selecionamos pais por torneios de três. Com probabilidade de 90% por descendente, o cruzamento de ordem (OX) preserva um trecho do pai em cada bloco e completa as posições livres na ordem cíclica da mãe. Com probabilidade de 35%, a mutação inverte um trecho em um bloco elegível, promovendo mudanças mesmo quando os pais se assemelham. Dois indivíduos de elite passam intactos. A população de 64 mantém variação com custo moderado. Rodamos até 300 gerações, com semente 42 + número da sequência. Uma rota composta apenas de blocos unitários tem uma única ordem factível e dispensa evolução.

A inicialização, OX e inversão só operam nas permutações do mesmo conjunto de IDs dentro da classe. Assim a sequência mantém todos os IDs e a elegibilidade resolvida antes do AG. A trilha da melhor aptidão é registrada por geração. O elitismo conserva a referência como limite superior da aptidão inicial.

## 3. Resultados das sequências

| Seq. | Agente | VD | AM | VM | PR | Total | Dist. | μ sobr | σ sobr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 12 | 9 | 8 | 1 | 30 | 234,64 | 0,7546 | 0,2158 |
| 2 | 1 | 6 | 5 | 5 | 2 | 18 | 222,57 | 0,7396 | 0,2174 |
| 3 | 1 | 5 | 4 | 5 | 0 | 14 | 145,61 | 0,7812 | 0,1743 |
| 4 | 2 | 7 | 15 | 13 | 11 | 46 | 331,26 | 0,6131 | 0,2472 |
| 5 | 2 | 6 | 11 | 5 | 2 | 24 | 285,15 | 0,7389 | 0,2085 |
| 6 | 2 | 2 | 3 | 3 | 0 | 8 | 102,73 | 0,7313 | 0,1686 |
| 7 | 3 | 23 | 22 | 23 | 17 | 85 | 495,78 | 0,6406 | 0,2595 |
| 8 | 4 | 7 | 5 | 13 | 10 | 35 | 275,53 | 0,5527 | 0,2594 |
| 9 | 4 | 13 | 15 | 12 | 16 | 56 | 376,33 | 0,5825 | 0,2783 |
| 10 | 5 | 10 | 9 | 12 | 29 | 60 | 312,14 | 0,4904 | 0,2761 |
| 11 | 5 | 9 | 8 | 9 | 8 | 34 | 305,40 | 0,6369 | 0,2556 |

| Agregado por sequência | Média ± DP | Soma |
| --- | --- | --- |
| Vítimas | 37,27 ± 21,82 | 410 |
| Distância | 280,65 ± 102,26 | 3 087,13 |

Totais por classe, na ordem da tabela: 100, 106, 108, 96. O desvio é populacional, com divisor N, porque as tabelas descrevem o conjunto completo de vítimas de cada rota e, nos agregados, todas as rotas. Uma sequência unitária tem desvio zero.

| Seq. | Cluster T3 | Agente | Posição na fila | Idade ≤ 12 |
| --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 1 | 30 |
| 2 | 4 | 1 | 2 | 18 |
| 3 | 2 | 1 | 3 | 14 |
| 4 | 5 | 2 | 1 | 12 |
| 5 | 3 | 2 | 2 | 24 |
| 6 | 6 | 2 | 3 | 8 |
| 7 | 1 | 3 | 1 | 0 |
| 8 | 2 | 4 | 1 | 0 |
| 9 | 3 | 4 | 2 | 0 |
| 10 | 6 | 5 | 1 | 0 |
| 11 | 4 | 5 | 2 | 0 |

O arquivo cluster_N.txt representa a sequência N. A tabela de associação mantém a origem na T3 mesmo quando mais de uma sequência deriva de um grupo.

## 4. Referências de comparação e limites

| Método | Distância somada | Espera ponderada somada |
| --- | --- | --- |
| Ordem original restrita ao lote | 3 560,08 | 17 818,16 |
| Vizinho com START | 3 370,43 | 7 260,19 |
| Algoritmo genético | 3 087,13 | 7 141,09 |

Com a mesma restrição START, o AG reduziu a distância somada em 8,4% e a espera ponderada em 1,6% frente ao vizinho. A ordem original mantém a ordem dos IDs no arquivo da T3 após a divisão. A comparação com ela inclui o efeito de introduzir a prioridade por classe.

| Seq. | Aptidão inicial | Aptidão final | Primeira geração do melhor |
| --- | --- | --- | --- |
| 1 | 1,2500 | 1,0475 | 51 |
| 2 | 1,2500 | 1,1816 | 12 |
| 3 | 1,2500 | 1,2500 | 0 |
| 4 | 1,2500 | 1,2101 | 36 |
| 5 | 1,2500 | 1,1625 | 26 |
| 6 | 1,2304 | 1,2304 | 0 |
| 7 | 1,2500 | 1,1989 | 179 |
| 8 | 1,2500 | 1,1636 | 43 |
| 9 | 1,2500 | 1,1612 | 161 |
| 10 | 1,2500 | 1,0878 | 240 |
| 11 | 1,2500 | 1,1793 | 55 |

No ensaio com semente fixa, a última melhora registrada ocorreu na geração 240. A trilha permite avaliar o orçamento de 300 gerações neste ensaio. A configuração é heurística e a análise é de uma execução reproduzível, sem alegação de ótimo global.

A soma das distâncias mede percurso total. O tempo de conclusão em paralelo também depende da fila de cada agente, do terreno, das paredes, da velocidade e do atendimento. A prioridade é local à rota e à sua fila. As estimativas de sobrevivência são fixas e carregam erros dos modelos das tarefas anteriores. O recorte por idade pode aumentar o número de saídas e o custo total quando comparado a roteiros sem paralelismo.

Fontes consultadas: Tacla, Tarefa 4 — Sequenciamento de socorro, v2, 28/10/2026, seções 1–3. Relatório da Tarefa 3, seções 2–3, e sua metodologia. VictSim3, documentação dos atributos e código de integração do visualizador na T3.
