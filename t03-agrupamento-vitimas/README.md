# Tarefa 3 · Agrupamento de vítimas no VictSim3

UTFPR · Sistemas Inteligentes (CSI30) · 2026/2 · RA 2588005

## Reproduzir

Use Python 3.12. Para recompilar o relatório, instale pdfLaTeX com Latin Modern e os pacotes usuais do TeX Live. A auditoria do PDF usa `pdfinfo`, `pdftotext` e `pdftohtml` do Poppler. Execute na pasta `t03-agrupamento-vitimas`.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py
```

A entrada padrão é a própria pasta do projeto. Passe `--entrada /caminho` para indicar uma pasta com `map.csv` e `modelos/`, ou `--saida /pasta` para escolher o diretório de resultados. Por padrão, os clusters finais são os de K=6. A opção `--k` permite inspecionar também K=4 e K=8 em outra pasta de saída.

Os insumos são mantidos localmente. Coloque o `map.csv` fornecido pelo professor na raiz da T03 e extraia os modelos das entregas anteriores conforme a tabela.

| Origem | Arquivo no ZIP | Destino na T03 |
|---|---|---|
| ZIP da T01 | `modelos/melhor_rn.joblib` | `modelos/t1/melhor_rn.joblib` |
| ZIP da T02 | `modelos/melhor_rn.joblib` | `modelos/t2/melhor_rn.joblib` |
| ZIP da T02 | `modelos/scaler.joblib` | `modelos/t2/scaler.joblib` |

Use `sha256sum -c entradas.sha256` para conferir os insumos usados no relatório. Use apenas artefatos Joblib de origem conhecida. A T1 carrega `t1/melhor_rn.joblib` como pipeline completo. A T2 carrega `t2/scaler.joblib` e aplica `transform` uma vez antes de `t2/melhor_rn.joblib`. A versão gravada nos estimadores é scikit-learn 1.9.1. Nenhum modelo foi retreinado. O mapa enriquecido preserva o formato de 18 colunas do original. `predicoes.csv` registra também a predição bruta e o cluster.

### Visualizador, PDF e testes

Obtenha o VictSim3 fora do projeto, no mesmo commit usado na verificação. A captura roda sem abrir janela e usa o desenho original com células de 14 pixels, preservando o tamanho de 3 pixels das bordas por cluster. O adaptador cruza ID, posição e sinais vitais com o cenário oficial antes da captura. A triagem mostrada nos círculos vem do mapa enriquecido. O visualizador lê o gabarito para marcar divergências e imprimir métricas depois de o agrupamento já ter sido gravado.

```sh
git clone https://github.com/tacla/VictSim3.git ../VictSim3
git -C ../VictSim3 checkout 803a01e54bfa01cde797538d8f2b98d66f12afe2
python src/visualizador.py ../VictSim3
python relatorio/gerar_tabelas.py
(cd relatorio && pdflatex -halt-on-error -jobname=relatorio_t3 relatorio.tex)
VICTSIM3=../VictSim3 python -m unittest discover -s tests -v
```

O texto do relatório documenta o cenário e a configuração final do mapa fornecido. As três tabelas em LaTeX são geradas dos CSVs. Os testes repetem o experimento e comparam os arquivos de dados e os IDs byte a byte no mesmo ambiente. As figuras são auditadas estrutural e visualmente.

O [checklist](AUDITORIA.md) e a [metodologia](METODOLOGIA.md) registram as decisões, verificações e fontes.

### Arquivos locais gerados

Para montar a pasta de submissão após gerar os resultados e o PDF, execute:

```sh
mkdir -p entrega_moodle/src
cp src/main.py src/visualizador.py entrega_moodle/src/
cp relatorio/relatorio_t3.pdf outputs/clusters/cluster_*.txt entrega_moodle/
```


| Local | Conteúdo |
|---|---|
| `entrega_moodle/` | PDF, fontes do experimento e da visualização, seis arquivos com IDs |
| `outputs/clusters/` | Um arquivo por cluster, com um ID por linha |
| `outputs/basico.csv` e `outputs/estrategia.csv` | Métricas de K=2–12 e das três configurações da estratégia |
| `outputs/diagnostico_dbscan.csv`, `outputs/diagnostico.csv`, `outputs/sensibilidade.csv` | Densidade, predições e efeito dos pesos |
| `outputs/predicoes.csv`, `outputs/map_predito.csv` | Auditoria da inferência e entrada do visualizador |
| `outputs/graficos/` | SSE, silhueta, nuvem 3D e captura oficial |
