# T01 - Classificação de vítimas com CART e Rede Neural MLP

Projeto para a **Tarefa 1 - Classificação** de Sistemas Inteligentes 1 (UTFPR/Curitiba, 2026/2).

O objetivo é treinar e comparar:

- uma árvore de decisão CART;
- uma rede neural MLP;
- usando apenas as variáveis 1 a 10 como entrada;
- predizendo `tri` (0=verde, 1=amarelo, 2=vermelho, 3=preto);
- com validação cruzada no treinamento/validação;
- e teste cego apenas depois do retreino final.

## Estrutura

```text
config/                  hiperparâmetros e parâmetros do experimento
data/raw/                dataset de treino e teste cego (não versionados)
docs/                    enunciado original
external/                gerador oficial do professor (baixado pelo script)
models/                   melhor_cart.joblib e melhor_rn.joblib
results/                  métricas em JSON/CSV
relatorio/                relatório final em PDF
scripts/                  comandos executáveis do trabalho
src/                      implementação de validação, treino e avaliação
```

## 1. Criar o ambiente

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## 2. Baixar os recursos oficiais

```bash
python scripts/baixar_recursos_oficiais.py
```

Esse comando baixa:

- `external/gerar_dados_vitimas.py` do VictSim3;
- `data/raw/teste_ceg1300.csv`, o dataset de 1300 vítimas reservado para teste cego.

## 3. Gerar o dataset de treino/validação

O enunciado exige **10.000 vítimas**, semente fixa, e que sejam registrados idade, desvio padrão, ruído e tipo de acidente. O gerador é do professor e pode mudar sua interface; por isso o projeto não inventa uma interface própria para ele.

Execute o gerador oficial e salve o CSV produzido como:

```text
data/raw/treino_10000.csv
```

Depois atualize `config/experimento.json` para registrar exatamente os parâmetros usados no gerador, principalmente `idade_parametro`, `desvio_padrao_parametro`, `ruido` e `tipo_acidente`.

## 4. Rodar o trabalho inteiro

```bash
python scripts/executar_tudo.py \
  --treino data/raw/treino_10000.csv \
  --teste-cego data/raw/teste_ceg1300.csv
```

Saídas:

```text
models/melhor_cart.joblib
models/melhor_rn.joblib
results/resultado_experimento.json
results/resultados_cv.csv
relatorio/relatorio_final.pdf
```

## Decisão de modelagem

A validação usa `StratifiedKFold` com 5 folds e `random_state=42`. O F1 usado para comparação é `f1_macro`. Para cada hiperparametrização são guardados os F1 de treino e validação por fold, média, desvio padrão e diferença absoluta entre treino e validação.

O melhor CART e a melhor RN são escolhidos por um critério explícito que usa as duas informações pedidas no enunciado: `F1 validação - gap absoluto médio entre treino e validação`. Isso evita escolher automaticamente um modelo muito sobreajustado só porque ganhou alguns pontos de F1 de validação.

A MLP é treinada dentro de um `Pipeline(StandardScaler + MLPClassifier)`, para que a normalização seja aprendida apenas com a parte de treino de cada fold e não provoque vazamento.

## Regra de ouro do teste cego

`data/raw/teste_ceg1300.csv` não entra em validação cruzada, seleção de hiperparâmetros nem retreino. Ele é lido apenas na etapa final de avaliação.

## Git

Este repositório foi organizado com branches de feature e merges para preservar uma história simples de desenvolvimento. Veja:

```bash
git log --oneline --graph --all --decorate
```
