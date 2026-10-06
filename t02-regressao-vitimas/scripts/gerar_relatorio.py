from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]

RESULTADO = ROOT / "results" / "resultado_experimento.json"
PLOT_CART = ROOT / "plots" / "dispersao_cart.png"
PLOT_RN = ROOT / "plots" / "dispersao_rn.png"
SAIDA = ROOT / "relatorio" / "relatorio_final.pdf"

ROXO = colors.HexColor("#c5b3d7")
AZUL = colors.HexColor("#d7eaf0")
LARANJA = colors.HexColor("#f5dfcf")
CINZA = colors.HexColor("#eeeeee")


def _fmt(valor: float) -> str:
    return f"{valor:.5f}"


def _fmt_cv(bloco: dict[str, Any]) -> str:
    return f"{_fmt(bloco['media'])} ({_fmt(bloco['dpa'])})"


def _topologia(params: dict[str, Any]) -> str:
    return "[" + " ".join(str(v) for v in params["hidden_layer_sizes"]) + "]"


def _cabecalho_paginas(canvas, doc) -> None:
    canvas.saveState()

    if doc.page > 1:
        canvas.setFont("Helvetica", 8)

        canvas.drawString(
            1.6 * cm,
            A4[1] - 1.05 * cm,
            "UTFPR - Sistemas Inteligentes - ICSI30 - T02",
        )

        canvas.drawRightString(
            A4[0] - 1.6 * cm,
            A4[1] - 1.05 * cm,
            f"Pagina {doc.page}",
        )

    canvas.restoreState()


def _estilo_tabela(cor_cabecalho: colors.Color) -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), cor_cabecalho),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.55, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 8.2),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    )


def _tabela(
    dados,
    larguras,
    cor,
    alinhamento_primeira="LEFT",
) -> Table:
    tabela = Table(
        dados,
        colWidths=larguras,
        hAlign="LEFT",
        repeatRows=1,
    )

    estilo = _estilo_tabela(cor)
    estilo.add(
        "ALIGN",
        (0, 1),
        (0, -1),
        alinhamento_primeira,
    )

    tabela.setStyle(estilo)

    return tabela


def _titulo(
    texto: str,
    estilo: ParagraphStyle,
) -> Paragraph:
    return Paragraph(texto, estilo)


def _secao_cv(resultado: dict[str, Any]) -> list[str]:
    return [
        _fmt_cv(resultado["treino"]),
        _fmt_cv(resultado["validacao"]),
        _fmt_cv(resultado["diferencas_abs"]),
    ]


def gerar(
    resultado: dict[str, Any],
    saida: Path,
) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(saida),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.75 * cm,
        bottomMargin=1.35 * cm,
        title="T02 - Regressao da Probabilidade de Sobrevivencia",
        author="Julia Kamilly de Oliveira",
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )

    doc.addPageTemplates(
        [
            PageTemplate(
                id="padrao",
                frames=frame,
                onPage=_cabecalho_paginas,
            )
        ]
    )

    estilo_universidade = ParagraphStyle(
        "universidade",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    estilo_dados = ParagraphStyle(
        "dados_academicos",
        fontName="Helvetica",
        fontSize=8.3,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    estilo_trabalho = ParagraphStyle(
        "titulo_trabalho",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=12,
    )

    estilo_titulo = ParagraphStyle(
        "secao",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceBefore=6,
        spaceAfter=4,
    )

    cfg = resultado["config"]
    dados_treino = resultado["dataset_treino"]

    cart_cv = resultado["cv"]["cart"]
    rn_cv = resultado["cv"]["rn"]

    melhor_cart = resultado["melhores"]["cart"]
    melhor_rn = resultado["melhores"]["rn"]

    teste_cart = resultado["teste_cego"]["cart"]
    teste_rn = resultado["teste_cego"]["rn"]

    ganho_mse = resultado["teste_cego"]["ganho_mse"]
    ganho_rmse = resultado["teste_cego"]["ganho_rmse"]

    story = []

    # Identificação acadêmica
    story.append(
        Paragraph(
            "UNIVERSIDADE TECNOLÓGICA FEDERAL DO PARANÁ - UTFPR",
            estilo_universidade,
        )
    )

    story.append(
        Paragraph(
            "<b>ALUNA:</b> JULIA KAMILLY DE OLIVEIRA"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<b>RA:</b> 2588005"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<b>CURSO:</b> SISTEMAS DE INFORMAÇÃO - S73",
            estilo_dados,
        )
    )

    story.append(
        Paragraph(
            "<b>DISCIPLINA:</b> SISTEMAS INTELIGENTES - ICSI30"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<b>PROF:</b> CESAR AUGUSTO TACLA",
            estilo_dados,
        )
    )

    story.append(
        Paragraph(
            "T02 - REGRESSÃO DA PROBABILIDADE DE SOBREVIVÊNCIA",
            estilo_trabalho,
        )
    )

    # ---------------------------------------------------------
    # 1
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "1) DATASET DE TREINAMENTO/VALIDAÇÃO",
            estilo_titulo,
        )
    )

    contagem = dados_treino["contagem_classes"]

    dados = [
        ["MODELO", "VALOR"],
        ["Vítimas tri=verde", contagem["0"]],
        ["Vítimas tri=amarelo", contagem["1"]],
        ["Vítimas tri=vermelho", contagem["2"]],
        ["Vítimas tri=preto", contagem["3"]],
        [
            "Idade das vítimas",
            cfg["dataset"]["idade_parametro"],
        ],
        [
            "Desvio padrão amostral da idade",
            f"{dados_treino['idade_dpa_amostral']:.5f}",
        ],
        [
            "ruído",
            cfg["dataset"]["ruido"],
        ],
    ]

    story.append(
        _tabela(
            dados,
            [10.0 * cm, 5.0 * cm],
            ROXO,
        )
    )

    story.append(Spacer(1, 0.15 * cm))

    # ---------------------------------------------------------
    # 2
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "2) HIPERPARAMETRIZAÇÕES CART",
            estilo_titulo,
        )
    )

    dados = [
        ["MODELO", "U", "E", "O"],
        [
            "Min_samples_leaf",
            *[
                cfg["cart"][k]["min_samples_leaf"]
                for k in "UEO"
            ],
        ],
        [
            "Max_depth",
            *[
                str(cfg["cart"][k]["max_depth"])
                for k in "UEO"
            ],
        ],
        [
            "Criterion",
            *[
                cfg["cart"][k]["criterion"]
                for k in "UEO"
            ],
        ],
    ]

    story.append(
        _tabela(
            dados,
            [5.6 * cm] + [3.15 * cm] * 3,
            AZUL,
        )
    )

    story.append(Spacer(1, 0.12 * cm))

    # ---------------------------------------------------------
    # 3
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "3) RESULTADOS DOS MODELOS CART",
            estilo_titulo,
        )
    )

    linhas = {
        k: _secao_cv(cart_cv[k])
        for k in "UEO"
    }

    dados = [
        ["MODELO", "CART U", "CART E", "CART O"],
        [
            "TREINO MSE MÉDIO (DPA)",
            *[linhas[k][0] for k in "UEO"],
        ],
        [
            "VALIDAÇÃO MSE MÉDIO (DPA)",
            *[linhas[k][1] for k in "UEO"],
        ],
        [
            "MÉDIA DAS DIFS. (DPA)",
            *[linhas[k][2] for k in "UEO"],
        ],
    ]

    story.append(
        _tabela(
            dados,
            [5.6 * cm] + [3.15 * cm] * 3,
            AZUL,
        )
    )

    story.append(Spacer(1, 0.12 * cm))

    # ---------------------------------------------------------
    # 4
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "4) HIPERPARAMETRIZAÇÕES REDE NEURAL",
            estilo_titulo,
        )
    )

    dados = [
        ["MODELO", "U", "E", "O"],
        [
            "Topologia",
            *[
                _topologia(cfg["rn"][k])
                for k in "UEO"
            ],
        ],
        [
            "Função de ativação",
            *[
                cfg["rn"][k]["activation"]
                for k in "UEO"
            ],
        ],
        [
            "Learning rate",
            *[
                cfg["rn"][k]["learning_rate_init"]
                for k in "UEO"
            ],
        ],
        [
            "solver",
            *[
                cfg["rn"][k]["solver"]
                for k in "UEO"
            ],
        ],
        [
            "alpha",
            *[
                cfg["rn"][k]["alpha"]
                for k in "UEO"
            ],
        ],
        [
            "max_iter",
            *[
                cfg["rn"][k]["max_iter"]
                for k in "UEO"
            ],
        ],
    ]

    story.append(
        _tabela(
            dados,
            [5.6 * cm] + [3.15 * cm] * 3,
            LARANJA,
        )
    )

    story.append(Spacer(1, 0.12 * cm))

    # ---------------------------------------------------------
    # 5
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "5) RESULTADOS DOS MODELOS RN",
            estilo_titulo,
        )
    )

    linhas = {
        k: _secao_cv(rn_cv[k])
        for k in "UEO"
    }

    dados = [
        ["MODELO", "RN U", "RN E", "RN O"],
        [
            "TREINO MSE MÉDIO (DPA)",
            *[linhas[k][0] for k in "UEO"],
        ],
        [
            "VALIDAÇÃO MSE MÉDIO (DPA)",
            *[linhas[k][1] for k in "UEO"],
        ],
        [
            "MÉDIA DAS DIFS. (DPA)",
            *[linhas[k][2] for k in "UEO"],
        ],
    ]

    story.append(
        _tabela(
            dados,
            [5.6 * cm] + [3.15 * cm] * 3,
            LARANJA,
        )
    )

    story.append(Spacer(1, 0.12 * cm))

    # ---------------------------------------------------------
    # 6
    # ---------------------------------------------------------

    titulo6 = _titulo(
        "6) MELHOR MODELO CART X MELHOR MODELO RN",
        estilo_titulo,
    )

    cart_m = _secao_cv(cart_cv[melhor_cart])
    rn_m = _secao_cv(rn_cv[melhor_rn])

    dados = [
        [
            "MODELO",
            f"Melhor CART ({melhor_cart})",
            f"Melhor RN ({melhor_rn})",
        ],
        [
            "TREINO MSE MÉDIO (DPA)",
            cart_m[0],
            rn_m[0],
        ],
        [
            "VALIDAÇÃO MSE MÉDIO (DPA)",
            cart_m[1],
            rn_m[1],
        ],
        [
            "MÉDIA DAS DIFS. (DPA)",
            cart_m[2],
            rn_m[2],
        ],
    ]

    tabela6 = _tabela(
        dados,
        [7.1 * cm, 4.2 * cm, 4.2 * cm],
        ROXO,
    )

    story.append(
        KeepTogether(
            [
                titulo6,
                tabela6,
            ]
        )
    )

    story.append(Spacer(1, 0.15 * cm))

    # ---------------------------------------------------------
    # 7
    # ---------------------------------------------------------

    titulo7 = _titulo(
        "7) RESULTADOS DO TESTE CEGO: MELHOR CART X MELHOR RN",
        estilo_titulo,
    )

    ganho_mse_cart = "-"
    ganho_mse_rn = "-"

    if ganho_mse["melhor"] == "cart":
        ganho_mse_cart = f"{ganho_mse['ganho_percentual']:.5f}%"
    elif ganho_mse["melhor"] == "rn":
        ganho_mse_rn = f"{ganho_mse['ganho_percentual']:.5f}%"

    ganho_rmse_cart = "-"
    ganho_rmse_rn = "-"

    if ganho_rmse["melhor"] == "cart":
        ganho_rmse_cart = f"{ganho_rmse['ganho_percentual']:.5f}%"
    elif ganho_rmse["melhor"] == "rn":
        ganho_rmse_rn = f"{ganho_rmse['ganho_percentual']:.5f}%"

    dados = [
        [
            "MODELO",
            f"Melhor CART ({melhor_cart})",
            f"Melhor RN ({melhor_rn})",
        ],
        [
            "MSE",
            _fmt(teste_cart["mse"]),
            _fmt(teste_rn["mse"]),
        ],
        [
            "Ganho % de MSE",
            ganho_mse_cart,
            ganho_mse_rn,
        ],
        [
            "RMSE",
            _fmt(teste_cart["rmse"]),
            _fmt(teste_rn["rmse"]),
        ],
        [
            "Ganho % de RMSE",
            ganho_rmse_cart,
            ganho_rmse_rn,
        ],
    ]

    tabela7 = _tabela(
        dados,
        [7.1 * cm, 4.2 * cm, 4.2 * cm],
        ROXO,
    )

    story.append(
        KeepTogether(
            [
                titulo7,
                tabela7,
            ]
        )
    )

    story.append(Spacer(1, 0.2 * cm))

    # ---------------------------------------------------------
    # 8
    # ---------------------------------------------------------

    story.append(
        _titulo(
            "8) GRÁFICO DE DISPERSÃO",
            estilo_titulo,
        )
    )

    imagem_cart = Image(
        str(PLOT_CART),
        width=7.6 * cm,
        height=6.5 * cm,
    )

    imagem_rn = Image(
        str(PLOT_RN),
        width=7.6 * cm,
        height=6.5 * cm,
    )

    graficos = Table(
        [[imagem_cart, imagem_rn]],
        colWidths=[7.8 * cm, 7.8 * cm],
    )

    graficos.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story.append(graficos)

    doc.build(story)


def main() -> None:
    if not RESULTADO.exists():
        raise FileNotFoundError(
            "Resultado do experimento não encontrado. "
            "Execute primeiro scripts/executar_tudo.py."
        )

    if not PLOT_CART.exists():
        raise FileNotFoundError(
            f"Gráfico CART não encontrado: {PLOT_CART}"
        )

    if not PLOT_RN.exists():
        raise FileNotFoundError(
            f"Gráfico RN não encontrado: {PLOT_RN}"
        )

    resultado = json.loads(
        RESULTADO.read_text(encoding="utf-8")
    )

    gerar(
        resultado,
        SAIDA,
    )

    print(f"Relatório gerado: {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
