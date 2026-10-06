# T02 — Regressão da Probabilidade de Sobrevivência

Trabalho da disciplina **Sistemas Inteligentes 1 — ICSI30**, da UTFPR.

## Objetivo

Construir e comparar modelos de regressão utilizando:

- CART (`DecisionTreeRegressor`)
- Rede Neural MLP (`MLPRegressor`)

O objetivo é estimar a variável `sobr`, que representa a probabilidade de sobrevivência da vítima.

## Variáveis utilizadas

São utilizadas exclusivamente as características de 1 a 10:

- `idade`
- `fc`
- `fr`
- `pas`
- `spo2`
- `temp`
- `pr`
- `sg`
- `fx`
- `queim`

Variável alvo:

- `sobr`

As variáveis `gcs`, `avpu` e `tri` não são utilizadas como entrada dos modelos.

## Estrutura

```text
t02-regressao-vitimas/
├── config/
│   └── experimento.json
├── data/
│   ├── processed/
│   └── raw/
├── docs/
│   └── T02_enunciado_regres.pdf
├── entrega/
├── external/
├── models/
├── plots/
├── relatorio/
├── results/
├── scripts/
│   ├── baixar_recursos_oficiais.py
│   ├── executar_tudo.py
│   ├── gerar_relatorio.py
│   ├── gerar_treino.py
│   └── validar_dataset.py
├── src/
│   ├── __init__.py
│   ├── avaliacao.py
│   ├── dados.py
│   ├── modelos.py
│   └── pipeline.py
├── tests/
│   └── test_smoke.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Execução completa do zero

Entre na pasta do projeto:

```bash
cd t02-regressao-vitimas
```

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Baixe os recursos oficiais:

```bash
python scripts/baixar_recursos_oficiais.py
```

Gere o dataset de treinamento com 10.000 vítimas:

```bash
python scripts/gerar_treino.py
```

Valide o dataset:

```bash
python scripts/validar_dataset.py data/raw/treino_10000.csv
```

Execute os testes:

```bash
python -m unittest discover -s tests -v
```

Execute todo o experimento:

```bash
python scripts/executar_tudo.py \
  --treino data/raw/treino_10000.csv \
  --teste-cego data/raw/teste_ceg1300.csv
```

## Configuração experimental

- Random state: `42`
- Validação cruzada: `5 folds`
- Dataset de treinamento/validação: `10.000 vítimas`
- Média de idade usada na geração: `40`
- Desvio padrão configurado da idade: `25`
- Ruído: `0.05`

### CART

| Modelo | max_depth | min_samples_leaf | criterion |
|---|---:|---:|---|
| U | 2 | 100 | squared_error |
| E | 8 | 8 | squared_error |
| O | None | 1 | squared_error |

### Rede Neural MLP

| Modelo | Topologia | Ativação | Learning rate | Alpha | Max iter |
|---|---|---|---:|---:|---:|
| U | [2] | tanh | 0.01 | 0.1 | 300 |
| E | [16, 8] | tanh | 0.005 | 0.01 | 500 |
| O | [128, 128, 64] | relu | 0.001 | 0.000001 | 700 |

Todas as redes utilizam solver `adam`.

## Resultados da validação cruzada

| Modelo | MSE treino | MSE validação | Diferença |
|---|---:|---:|---:|
| CART U | 0.007110 | 0.007115 | 0.000279 |
| CART E | 0.002117 | 0.002719 | 0.000602 |
| CART O | 0.000000 | 0.004066 | 0.004066 |
| RN U | 0.003038 | 0.003053 | 0.000083 |
| RN E | 0.002308 | 0.002386 | 0.000113 |
| RN O | 0.001612 | 0.002134 | 0.000522 |

Modelos selecionados:

- Melhor CART: **E**
- Melhor RN: **E**

A seleção considera simultaneamente o MSE médio de validação e a diferença absoluta entre os MSEs de treino e validação.

## Teste cego

Os modelos selecionados foram retreinados utilizando todas as 10.000 amostras antes da avaliação no conjunto cego de 1.300 vítimas.

| Métrica | CART E | RN E |
|---|---:|---:|
| MSE | 0.00275686 | 0.00241382 |
| RMSE | 0.05250576 | 0.04913060 |

A Rede Neural obteve:

- ganho de MSE: **12.44314%**
- ganho de RMSE: **6.42818%**

## Arquivos gerados

A execução completa produz:

```text
models/melhor_cart.joblib
models/melhor_rn.joblib
models/scaler.joblib
results/resultado_experimento.json
results/resultados_cv.csv
plots/dispersao_cart.png
plots/dispersao_rn.png
relatorio/relatorio_final.pdf
```

## Autora

Julia Kamilly de Oliveira  
Sistemas de Informação — UTFPR
