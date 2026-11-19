# Sistemas Inteligentes

Repositório destinado aos trabalhos desenvolvidos na disciplina **Sistemas Inteligentes**, da UTFPR - Campus Curitiba, durante o semestre 2026/2.

## Trabalhos

### T01 - Classificação de Vítimas

Implementação e comparação de modelos para classificação de vítimas segundo o protocolo START.

Modelos utilizados:

- Árvore de Decisão CART;
- Rede Neural Artificial MLP.

O trabalho utiliza validação cruzada, diferentes hiperparametrizações, retreino dos melhores modelos e avaliação em um conjunto de teste cego.

Diretório:

`t01-classificacao-vitimas/`

O README dentro do diretório do projeto contém as instruções completas para instalação, geração dos dados, execução dos modelos e reprodução dos resultados.

---

### T02 - Regressão da Probabilidade de Sobrevivência

Implementação e comparação de modelos de regressão para estimar a probabilidade de sobrevivência de vítimas.

Modelos utilizados:

- Árvore de Decisão CART;
- Rede Neural Artificial MLP.

O trabalho utiliza validação cruzada, três hiperparametrizações para cada modelo — subajustada, equilibrada e sobreajustada —, retreino dos melhores modelos e avaliação em um conjunto de teste cego.

A avaliação utiliza métricas de **MSE** e **RMSE**, além de gráficos de dispersão entre os valores reais e preditos.

Diretório:

`t02-regressao-vitimas/`

O README dentro do diretório do projeto contém as instruções completas para instalação, geração dos dados, execução dos modelos e reprodução dos resultados.

---

### T03 - Agrupamento de Vítimas

Implementação e avaliação de estratégias de agrupamento de vítimas para apoiar a organização do socorro no VictSim3.

Algoritmos utilizados:

- K-means para os experimentos de agrupamento;
- DBSCAN para a análise exploratória da densidade.

O trabalho avalia o agrupamento por posição espacial e compara três parametrizações de K-means que combinam posição e probabilidade de sobrevivência estimada pelo modelo da T02. A triagem START estimada pelo modelo da T01 apoia a proposta de priorização do socorro.

A avaliação utiliza **SSE** e **coeficiente de silhueta**, além do método do cotovelo no experimento espacial e da visualização dos grupos no mapa.

Diretório:

`t03-agrupamento-vitimas/`

O README dentro do diretório do projeto contém as instruções completas para instalação, preparação dos dados e modelos, execução dos experimentos e reprodução dos resultados.
