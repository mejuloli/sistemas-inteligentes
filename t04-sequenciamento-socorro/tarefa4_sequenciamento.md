# Tarefa 4 — Atribuir e ordenar o socorro no VictSim3

A T3 responde **quais vítimas pertencem à mesma região de trabalho**. A T4 responde **quem atende cada vítima e em qual ordem**. O código usa o mapa com os sinais vitais, as idades e as predições já calculadas. A classe START vem da MLP de classificação e a sobrevivência da MLP de regressão. O mapa original tinha `tri = sobr = -1`. A T4 confere o mapa predito, a lista de predições e os clusters antes de planejar qualquer rota.

## Por que seis grupos deram 11 rotas?

O K-means da T3 agrupou as 410 vítimas no espaço `(x_rel/74, y_rel/74, 0,45 × sobr)`. A primeira e a segunda coordenadas mantêm a escala espacial comum. A terceira permite que a sobrevivência influencie a separação. Os seis grupos têm vítimas com até 12 anos. Com atribuição inteira, só os agentes 1 e 2 poderiam sair da base. Os agentes 3 a 5 têm limite estrito de idade maior que 12.

Em `src/atribuicao.py`, função `atribuir`, a primeira separação possível de um grupo tem esta forma:

```python
criancas = tuple(i for i in ids if vitimas[i].idade <= 12)
adultos = tuple(i for i in ids if vitimas[i].idade > 12)
```

O programa avalia a alternativa de manter cada origem inteira, além da divisão por idade. Um subconjunto pediátrico vai para 1 ou 2 e o adulto para 3, 4 ou 5. Para cada combinação, soma-se a carga dos lotes de cada agente. Um lote custa a quantidade de vítimas mais o percurso aproximado de vizinho mais próximo, em células. Por exemplo, 10 vítimas com percurso de 45 células dão carga 55. Entre combinações que ocupam os cinco agentes, minimiza-se a maior carga. Em empate, o menor número de viagens tem preferência, seguido da menor carga somada.

O resultado manteve a origem 5 inteira e dividiu as outras cinco. A associação aparece em `outputs/tabelas/atribuicao.csv`. Quando um agente recebe mais de uma viagem, primeiro vem a que contém mais vítimas vermelhas, usando amarelas, verdes e a origem em caso de empate. A reserva de IDs é disjunta, permitindo que agentes trabalhem ao mesmo tempo.

## O que o AG evolui?

Cada indivíduo é uma permutação do lote. A representação guarda quatro blocos fixos por classe, na ordem vermelho, amarelo, verde e preto. Se vermelho tem IDs 17, 42 e 8 e amarelo tem 103, tanto `[17, 42, 8, 103]` quanto `[42, 17, 8, 103]` são possíveis. O ID 103 permanece após os vermelhos. Casos pretos permanecem na rota. O programa parte de 64 indivíduos. Um é construído por vizinho mais próximo com prioridade de classe. Os demais embaralham apenas dentro de cada bloco.

### Seleção, cruzamento e mutação

A seleção por torneio escolhe o melhor de três candidatos sorteados. Com probabilidade de 90%, o cruzamento de ordem OX preserva um trecho do primeiro pai e preenche as demais posições na ordem cíclica do segundo, pulando os IDs reservados. Por exemplo, para `[1, 2, 3, 4, 5]` e `[5, 4, 3, 2, 1]`, se o trecho preservado for `[2, 3]`, o cursor do segundo pai começa no item 2. Os disponíveis aparecem na ordem 1, 5, 4. Preenchendo a partir da posição depois do trecho e circulando, o filho fica `[4, 2, 3, 1, 5]`.

Com probabilidade de 35% por descendente, o AG sorteia um bloco com pelo menos dois IDs e inverte um trecho. Em `[4, 2, 3, 1, 5]`, inverter `[2, 3, 1]` produz `[4, 1, 3, 2, 5]`. A inversão preserva todos os IDs e muda as conexões do caminho. Dois indivíduos de elite passam intactos. O orçamento é de 300 gerações, com semente 42 mais o número da sequência.

## Como se calcula a qualidade?

A rota contém os segmentos da base à primeira vítima, entre vítimas e da última vítima à base. A distância entre (0,0) e (3,4) é a raiz de 3² + 4², ou 5. Se a segunda vítima está em (0,4), a distância do segundo segmento é 3 e a volta mede 4. O total é 5 + 3 + 4 = 12 células. A base (30,40) do ambiente corresponde à origem (0,0) neste CSV. O código que calcula a distância em `src/rotas.py` usa:

```python
pontos = (BASE, *posicoes, BASE)
return sum(dist(a, b) for a, b in zip(pontos, pontos[1:]))
```

Na avaliação do AG, a distância acumulada à chegada às duas vítimas é C₁ = 5 e C₂ = 8. Para sobrevivências de 0,50 e 0,75, seus pesos são 1 − 0,50 = 0,50 e 1 − 0,75 = 0,25. A espera ponderada E é 0,50 × 5 + 0,25 × 8 = 4,50. O segmento de retorno entra em D, a distância fechada. E usa apenas a chegada a cada vítima e atribui peso zero à classe preta.

O AG minimiza `D/D_ref + 0,25 × E/E_ref`. As referências medem o vizinho mais próximo com prioridade START, então o valor dele em uma rota com ambos os denominadores positivos é 1,25. A normalização impede que a escala da soma de esperas domine a distância. Uma proposta que reduza D em 1% da referência pode aumentar E em até 4% da referência sem piorar a aptidão. Esse peso expressa uma escolha de planejamento da T4.

## Como interpretar o resultado?

Todas as 410 vítimas aparecem uma vez em 11 arquivos, com 100 verdes, 106 amarelas, 108 vermelhas e 96 pretas. O AG somou 3.087,13 células. Vizinho com prioridade START somou 3.370,43 células, e a ordem herdada da T3 nos mesmos lotes somou 3.560,08. O melhor valor de aptidão das rotas foi atingido até a geração 240 nesta execução. Os valores detalhados estão em `outputs/tabelas`; consulte `convergencia.csv` para ver o efeito do elitismo ao longo das gerações.

Por sequência, o relatório apresenta contagens, distância, média de sobrevivência e desvio padrão populacional. Com duas sobrevivências de 0,50 e 0,75, a média é 0,625. Cada desvio absoluto à média é 0,125. A raiz da média dos dois quadrados desses desvios é 0,125. O desvio descreve a heterogeneidade do lote e vale zero para uma vítima só. Os agregados do enunciado descrevem vítimas e distância por sequência. A soma de distâncias mede o trabalho total de deslocamento. A duração da operação paralela depende dos tempos individuais.

## Perguntas para defender a solução

- **Por que separar grupos se a T3 os formou?** Todos são mistos. Preservá-los inteiros restringe a operação a dois agentes. A separação usa a elegibilidade e preserva o grupo de origem em cada rota.
- **Como se sabe que o AG não perdeu vítimas?** Cada bloco recebe exatamente os IDs da sua classe, OX conserva esse conjunto e a mutação só inverte a ordem. O teste de integração confere os 410 IDs dos arquivos finais.
- **Uma vítima vermelha sempre vem antes de qualquer verde?** Dentro da mesma rota, sim. O plano tem rotas paralelas e filas por agente, então essa ordem é local.
- **Por que usar distância em vez de tempo real?** A especificação pede distância euclidiana fechada. A chegada acumulada é uma aproximação espacial da espera. Paredes, terreno, tempos de atendimento e atualizações em campo pertencem à execução posterior.
- **Como reproduzir?** Com a T3 ao lado da T4, executar `python src/main.py` na pasta da T4. Os testes repetem o processo em duas pastas temporárias e comparam os resultados byte a byte.
