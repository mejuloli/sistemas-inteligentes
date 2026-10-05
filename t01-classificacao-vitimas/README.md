# T01 — Classificação de Vítimas com CART e Rede Neural MLP


## Execução completa do zero

Para reproduzir todo o trabalho a partir de um clone novo do repositório, execute os passos abaixo na ordem apresentada.

### 1. Entrar na pasta do projeto

~~~bash
cd t01-classificacao-vitimas
~~~

### 2. Criar o ambiente virtual

~~~bash
python -m venv .venv
~~~

### 3. Ativar o ambiente virtual

No Linux:

~~~bash
source .venv/bin/activate
~~~

### 4. Instalar as dependências

~~~bash
pip install -r requirements.txt
~~~

### 5. Baixar os recursos oficiais

~~~bash
python scripts/baixar_recursos_oficiais.py
~~~

Esse comando obtém:

~~~text
external/gerar_dados_vitimas.py
data/raw/teste_ceg1300.csv
~~~

### 6. Gerar o dataset de treinamento

~~~bash
python scripts/gerar_treino.py
~~~

Esse comando gera, de forma reproduzível:

~~~text
data/raw/treino_10000.csv
~~~

São utilizadas 10.000 vítimas, ruído 0.05 e semente fixa 42.

### 7. Validar o dataset

~~~bash
python scripts/validar_dataset.py data/raw/treino_10000.csv
~~~

### 8. Executar os testes automatizados

~~~bash
python -m unittest discover -s tests -v
~~~

### 9. Executar o experimento completo

~~~bash
python scripts/executar_tudo.py \
  --treino data/raw/treino_10000.csv \
  --teste-cego data/raw/teste_ceg1300.csv
~~~

O pipeline realiza automaticamente:

1. validação cruzada dos modelos CART;
2. validação cruzada das redes neurais;
3. seleção das melhores hiperparametrizações;
4. retreino utilizando as 10.000 vítimas;
5. avaliação no teste cego de 1.300 vítimas;
6. salvamento dos modelos;
7. geração dos resultados;
8. geração do relatório final.

Ao final devem existir:

~~~text
models/melhor_cart.joblib
models/melhor_rn.joblib
results/resultado_experimento.json
results/resultados_cv.csv
relatorio/relatorio_final.pdf
~~~

---


Trabalho desenvolvido para a disciplina **Sistemas Inteligentes 1**, da UTFPR — Campus Curitiba, no semestre 2026/2.

O objetivo é construir e comparar modelos de classificação capazes de determinar a classificação START (`tri`) de vítimas de catástrofes naturais, desastres ou grandes acidentes.

Foram utilizados dois tipos de classificadores:

- Árvore de Decisão CART;
- Rede Neural Artificial MLP.

---

## 1. Problema de classificação

A variável de saída do problema é `tri`, que representa a classificação da vítima segundo o protocolo START:

| Valor | Classe | Significado |
|---:|---|---|
| 0 | Verde | Ferimentos leves que não representam risco à vida |
| 1 | Amarelo | Ferimentos graves, mas que podem aguardar atendimento |
| 2 | Vermelho | Ferimentos críticos que exigem atendimento imediato |
| 3 | Preto | Salvamento inviável |

---

## 2. Variáveis utilizadas

Os modelos utilizam exclusivamente as características de entrada de 1 a 10:

| Variável | Descrição |
|---|---|
| `idade` | Idade da vítima |
| `fc` | Frequência cardíaca |
| `fr` | Frequência respiratória |
| `pas` | Pressão arterial sistólica |
| `spo2` | Saturação de oxigênio |
| `temp` | Temperatura corporal |
| `pr` | Pulso radial |
| `sg` | Sangramento |
| `fx` | Fratura exposta |
| `queim` | Queimadura |

As variáveis abaixo **não são utilizadas como entrada dos classificadores**:

- `gcs`;
- `avpu`;
- `tri`;
- `sobr`.

A variável `tri` é utilizada somente como variável-alvo da classificação.

---

## 3. Estrutura do projeto

~~~text
t01-classificacao-vitimas/
├── config/
│   └── experimento.json
│
├── data/
│   ├── raw/
│   │   ├── treino_10000.csv
│   │   └── teste_ceg1300.csv
│   └── processed/
│
├── docs/
│   ├── T01_enunciado_classif.pdf
│   └── git-historico.txt
│
├── external/
│   └── gerar_dados_vitimas.py
│
├── models/
│   ├── melhor_cart.joblib
│   └── melhor_rn.joblib
│
├── relatorio/
│   └── relatorio_final.pdf
│
├── results/
│   ├── resultado_experimento.json
│   └── resultados_cv.csv
│
├── scripts/
│   ├── baixar_recursos_oficiais.py
│   ├── executar_tudo.py
│   ├── gerar_relatorio.py
│   ├── gerar_treino.py
│   └── validar_dataset.py
│
├── src/
│   ├── __init__.py
│   ├── avaliacao.py
│   ├── dados.py
│   ├── modelos.py
│   └── pipeline.py
│
├── tests/
│   └── test_smoke.py
│
├── .gitignore
├── README.md
└── requirements.txt
~~~

Os datasets, modelos treinados, resultados e relatório são artefatos gerados localmente e podem estar ignorados pelo Git.

---

## 4. Preparação do ambiente

### Criar o ambiente virtual

~~~bash
python -m venv .venv
~~~

### Ativar no Linux

~~~bash
source .venv/bin/activate
~~~

### Instalar as dependências

~~~bash
pip install -r requirements.txt
~~~

---

## 5. Recursos oficiais

O projeto possui um script para baixar os recursos disponibilizados pelo professor:

~~~bash
python scripts/baixar_recursos_oficiais.py
~~~

São obtidos:

~~~text
external/gerar_dados_vitimas.py
data/raw/teste_ceg1300.csv
~~~

O arquivo `teste_ceg1300.csv` contém **1.300 vítimas** e é reservado exclusivamente para a etapa de teste cego.

Ele não deve ser utilizado durante:

- treinamento;
- validação cruzada;
- escolha de hiperparâmetros;
- retreino dos modelos.

---

## 6. Dataset de treinamento e validação

Foi utilizado um dataset com **10.000 vítimas** para treinamento e validação.

Parâmetros utilizados no gerador:

~~~text
Número de vítimas: 10000

Distribuição inicial:
Verde:     2500
Amarelo:   2500
Vermelho:  2500
Preto:     2500

Média de idade: 40
Desvio padrão usado na geração: 25
Ruído: 0.05
Semente aleatória: 42
~~~

A versão utilizada do gerador oficial não possui parâmetro específico para tipo de acidente.

O dataset foi salvo em:

~~~text
data/raw/treino_10000.csv
~~~

Após a aplicação do ruído, a distribuição final foi:

| Classe | Quantidade |
|---|---:|
| Verde | 2448 |
| Amarelo | 2567 |
| Vermelho | 2561 |
| Preto | 2424 |
| **Total** | **10000** |

A média de idade observada foi:

~~~text
39.9198
~~~

O desvio padrão amostral observado da idade foi:

~~~text
23.20156
~~~

---

## 7. Validação cruzada

Foi utilizada validação cruzada estratificada com:

~~~text
Número de folds: 5
Random state: 42
Métrica principal: F1 macro
~~~

Para cada hiperparametrização são calculados:

- F1 macro de treino em cada fold;
- F1 macro de validação em cada fold;
- média do F1 macro de treino;
- média do F1 macro de validação;
- desvio padrão amostral;
- diferença absoluta entre treino e validação.

---

## 8. Modelos CART

Foram avaliadas três hiperparametrizações.

### CART U — subajustado

~~~text
max_depth = 2
min_samples_leaf = 100
criterion = gini
~~~

Resultados:

~~~text
F1 macro médio de treino:    0.81554
F1 macro médio de validação: 0.81405
~~~

---

### CART E — equilibrado

~~~text
max_depth = 8
min_samples_leaf = 8
criterion = entropy
~~~

Resultados:

~~~text
F1 macro médio de treino:    0.94259
F1 macro médio de validação: 0.93990
~~~

---

### CART O — sobreajustado

~~~text
max_depth = None
min_samples_leaf = 1
criterion = gini
~~~

Resultados:

~~~text
F1 macro médio de treino:    1.00000
F1 macro médio de validação: 0.88314
~~~

O modelo CART escolhido foi:

~~~text
CART E
~~~

---

## 9. Redes Neurais MLP

Para as redes neurais, é utilizado `StandardScaler` em conjunto com o `MLPClassifier`.

A normalização é feita dentro do pipeline de aprendizado, evitando utilizar informações do conjunto de validação durante o ajuste do scaler.

### RN U

~~~text
Topologia: [2]
Função de ativação: tanh
Learning rate: 0.01
Solver: adam
Alpha: 0.1
Max iter: 300
~~~

Resultados:

~~~text
F1 macro médio de treino:    0.89784
F1 macro médio de validação: 0.89539
~~~

---

### RN E

~~~text
Topologia: [8]
Função de ativação: tanh
Learning rate: 0.01
Solver: adam
Alpha: 0.01
Max iter: 300
~~~

Resultados:

~~~text
F1 macro médio de treino:    0.94323
F1 macro médio de validação: 0.94042
~~~

---

### RN O

~~~text
Topologia: [128, 128, 64]
Função de ativação: relu
Learning rate: 0.001
Solver: adam
Alpha: 0.000001
Max iter: 700
~~~

Resultados:

~~~text
F1 macro médio de treino:    0.98100
F1 macro médio de validação: 0.92606
~~~

A rede neural escolhida foi:

~~~text
RN E
~~~

---

## 10. Comparação dos melhores modelos

Os melhores modelos obtidos durante a validação cruzada foram:

| Métrica | CART E | RN E |
|---|---:|---:|
| F1 treino | 0.94259 | 0.94323 |
| DPA treino | 0.00088 | 0.00140 |
| F1 validação | 0.93990 | 0.94042 |
| DPA validação | 0.00797 | 0.00915 |
| Média das diferenças | 0.00763 | 0.00838 |

Os dois modelos apresentaram resultados muito próximos durante a validação cruzada.

---

## 11. Retreino

Após a seleção das melhores hiperparametrizações, o melhor CART e a melhor rede neural são retreinados utilizando **todas as 10.000 amostras** do dataset de treinamento/validação.

Nessa etapa não é realizado split nem validação cruzada.

Os modelos finais são salvos como:

~~~text
models/melhor_cart.joblib
models/melhor_rn.joblib
~~~

---

## 12. Teste cego

Somente depois da seleção e do retreino dos modelos é utilizado o dataset:

~~~text
data/raw/teste_ceg1300.csv
~~~

Ele possui 1.300 vítimas.

Os resultados obtidos foram:

| Métrica | CART E | RN E |
|---|---:|---:|
| Precisão macro | 0.93023 | 0.93332 |
| Recall macro | 0.92438 | 0.92775 |
| F1 macro | 0.92714 | 0.93020 |
| Acurácia | 0.93000 | 0.93385 |

A rede neural apresentou resultado ligeiramente superior no teste cego.

---

## 13. Matrizes de confusão

Legenda:

~~~text
G = Verde
Y = Amarelo
R = Vermelho
B = Preto
~~~

### CART E

~~~text
Real \ Predito     G     Y     R     B

G                 95    11     0     0
Y                  7   357    15     0
R                  0    17   377    25
B                  0     0    16   380
~~~

### RN E

~~~text
Real \ Predito     G     Y     R     B

G                 95    11     0     0
Y                  7   362    10     0
R                  0    19   375    25
B                  0     0    14   382
~~~

---

## 14. Execução completa

Com os datasets disponíveis em `data/raw/`, o experimento completo pode ser executado com:

~~~bash
python scripts/executar_tudo.py \
  --treino data/raw/treino_10000.csv \
  --teste-cego data/raw/teste_ceg1300.csv
~~~

O script executa:

1. leitura e validação do dataset de treinamento;
2. validação cruzada dos três modelos CART;
3. validação cruzada das três redes neurais;
4. seleção dos melhores modelos;
5. retreino utilizando as 10.000 vítimas;
6. salvamento dos modelos finais;
7. leitura do conjunto de teste cego;
8. avaliação dos modelos;
9. geração dos arquivos de resultados;
10. geração do relatório final.

Os principais arquivos produzidos são:

~~~text
models/melhor_cart.joblib
models/melhor_rn.joblib
results/resultado_experimento.json
results/resultados_cv.csv
relatorio/relatorio_final.pdf
~~~

---

## 15. Validação do dataset

Para verificar as características básicas do dataset:

~~~bash
python scripts/validar_dataset.py data/raw/treino_10000.csv
~~~

---

## 16. Testes automatizados

Para executar os testes:

~~~bash
python -m unittest discover -s tests -v
~~~

Os testes verificam aspectos como:

- utilização somente das características permitidas;
- exclusão de `gcs`, `avpu` e `sobr` das entradas;
- utilização de `tri` somente como variável-alvo;
- funcionamento das rotinas principais do projeto.

---

## 17. Arquivos de configuração

As hiperparametrizações e configurações gerais do experimento ficam em:

~~~text
config/experimento.json
~~~

Nesse arquivo são definidos:

- número de folds;
- random state;
- parâmetros do dataset;
- hiperparâmetros dos modelos CART;
- hiperparâmetros das redes neurais.

---

## 18. Histórico Git

O desenvolvimento foi separado em branches para organizar as etapas do trabalho.

Branches utilizadas:

~~~text
main
feat/modelagem
feat/relatorio
test/validacao
~~~

Histórico resumido:

~~~text
feat/modelagem
    implementação da validação cruzada e dos modelos CART e MLP

feat/relatorio
    implementação da geração do relatório final

test/validacao
    testes e validações do projeto

main
    integração e versão final
~~~

Para visualizar o histórico:

~~~bash
git log --oneline --graph --decorate --all
~~~

---

## 19. Principais commits

O histórico do projeto inclui commits para:

- criação da estrutura inicial;
- implementação da modelagem;
- integração da branch de modelagem;
- geração do relatório;
- integração do relatório;
- testes e validações;
- integração das validações;
- finalização dos modelos e teste cego;
- remoção de metadados do Windows;
- organização final do repositório.

---

## 20. Entrega

A entrega final é preparada na pasta local:

~~~text
entrega/
~~~

Os arquivos destinados ao Moodle são:

~~~text
relatorio_final.pdf
codigos_e_modelos.zip
~~~

O arquivo `codigos_e_modelos.zip` contém os códigos-fonte e os modelos:

~~~text
melhor_cart.joblib
melhor_rn.joblib
~~~

O relatório contém as oito seções solicitadas no enunciado da atividade, incluindo:

1. dataset de treinamento/validação;
2. hiperparametrizações CART;
3. resultados CART;
4. hiperparametrizações da rede neural;
5. resultados das redes neurais;
6. comparação dos melhores modelos;
7. resultados do teste cego;
8. matrizes de confusão.
