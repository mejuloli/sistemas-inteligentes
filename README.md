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

Experimento de clustering com 410 vítimas em uma grade 75 × 75 do VictSim3. A primeira parte avalia K-means com coordenadas espaciais para K de 2 a 12 e identifica o cotovelo em K=4.

A estratégia de socorro reutiliza os modelos da T01 e da T02 para estimar a triagem START e a sobrevivência. O agrupamento final combina coordenadas normalizadas e probabilidade de sobrevivência, com K=6, SSE de 14,7754 e silhueta de 0,3756. As 410 vítimas foram agrupadas. O relatório descreve como distribuir os lotes entre cinco socorristas com restrições de idade.

- [Projeto e instruções de reprodução](t03-agrupamento-vitimas/README.md)
- [Auditoria do enunciado](t03-agrupamento-vitimas/AUDITORIA.md)
