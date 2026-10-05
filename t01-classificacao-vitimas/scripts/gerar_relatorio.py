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
    HRFlowable,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTADO = ROOT / "results" / "resultado_experimento.json"
SAIDA = ROOT / "relatorio" / "relatorio_final.pdf"

ROXO = colors.HexColor("#c5b3d7")
AZUL = colors.HexColor("#d7eaf0")
LARANJA = colors.HexColor("#f5dfcf")
CINZA = colors.HexColor("#eeeeee")


def _fmt(v: float) -> str:
    return f"{v:.5f}"


def _fmt_cv(bloco: dict[str, Any]) -> str:
    return f"{_fmt(bloco['media'])} ({_fmt(bloco['dpa'])})"


def _topologia(params: dict[str, Any]) -> str:
    return "[" + " ".join(str(v) for v in params["hidden_layer_sizes"]) + "]"


def _cabecalho(canvas, doc) -> None:
    """Cabecalho discreto para as paginas posteriores a primeira."""
    canvas.saveState()

    if doc.page > 1:
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            1.6 * cm,
            A4[1] - 1.05 * cm,
            "UTFPR - Sistemas Inteligentes - ICSI30 - T01",
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
            ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.2),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
    )


def _tabela(dados, larguras, cor, alinhamento_primeira="LEFT") -> Table:
    t = Table(dados, colWidths=larguras, hAlign="LEFT", repeatRows=1)
    st = _estilo_tabela(cor)
    st.add("ALIGN", (0, 1), (0, -1), alinhamento_primeira)
    t.setStyle(st)
    return t


def _titulo(texto: str, estilo: ParagraphStyle) -> Paragraph:
    return Paragraph(texto, estilo)


def _secao_cv(resultado: dict[str, Any]) -> list[str]:
    return [
        _fmt_cv(resultado["treino"]),
        _fmt_cv(resultado["validacao"]),
        _fmt_cv(resultado["diferencas_abs"]),
    ]


def _matriz_confusao_tabela(titulo: str, matriz: list[list[int]]) -> Table:
    dados = [[titulo, "G", "Y", "R", "B"]]
    nomes = ["G", "Y", "R", "B"]
    for nome, linha in zip(nomes, matriz):
        dados.append([nome] + [str(int(v)) for v in linha])
    t = Table(dados, colWidths=[1.25 * cm] + [0.95 * cm] * 4, rowHeights=0.55 * cm)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ROXO),
                ("BACKGROUND", (0, 1), (0, -1), CINZA),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.55, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ]
        )
    )
    return t


def gerar(resultado: dict[str, Any], saida: Path) -> None:
    saida.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(saida),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.75 * cm,
        bottomMargin=1.35 * cm,
        title="T01 - Classificacao de Vitimas com CART e Rede Neural MLP",
        author="Julia Kamilly de Oliveira",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="padrao", frames=frame, onPage=_cabecalho)])

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
        spaceAfter=6,
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
    estilo_obs = ParagraphStyle(
        "obs",
        fontName="Helvetica-Bold",
        fontSize=8.4,
        leading=10,
        alignment=TA_LEFT,
    )

    cfg = resultado["config"]
    dados_treino = resultado["dataset_treino"]
    cart_cv = resultado["cv"]["cart"]
    rn_cv = resultado["cv"]["rn"]
    melhor_cart = resultado["melhores"]["cart"]
    melhor_rn = resultado["melhores"]["rn"]
    teste_cart = resultado["teste_cego"]["cart"]
    teste_rn = resultado["teste_cego"]["rn"]

    story = []

    # Cabecalho institucional da primeira pagina
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
            "T01 - CLASSIFICAÇÃO DE VÍTIMAS COM CART E REDE NEURAL MLP",
            estilo_trabalho,
        )
    )

    # 1
    story.append(_titulo("1) DATASET DE TREINAMENTO/VALIDACAO", estilo_titulo))
    c = dados_treino["contagem_classes"]
    dados = [
        ["MODELO", "VALOR"],
        ["Vitimas tri=verde", c["0"]],
        ["Vitimas tri=amarelo", c["1"]],
        ["Vitimas tri=vermelho", c["2"]],
        ["Vitimas tri=preto", c["3"]],
        ["Idade das vitimas", cfg["dataset"]["idade_parametro"]],
        ["Desvio padrao amostral da idade", f"{dados_treino['idade_dpa_amostral']:.5f}"],
        ["ruido", cfg["dataset"]["ruido"]],
    ]
    story.append(_tabela(dados, [10.0 * cm, 5.0 * cm], ROXO))
    story.append(Spacer(1, 0.15 * cm))

    # 2
    story.append(_titulo("2) HIPERPARAMETRIZACOES CART", estilo_titulo))
    dados = [
        ["MODELO", "U", "E", "O"],
        ["Min_samples_leaf"] + [cfg["cart"][k]["min_samples_leaf"] for k in "UEO"],
        ["Max_depth"] + [str(cfg["cart"][k]["max_depth"]) for k in "UEO"],
        ["Criterion (gini, ent)"] + [cfg["cart"][k]["criterion"] for k in "UEO"],
    ]
    story.append(_tabela(dados, [5.6 * cm] + [3.15 * cm] * 3, AZUL))
    story.append(Spacer(1, 0.12 * cm))

    # 3
    story.append(_titulo("3) RESULTADOS DOS MODELOS CART", estilo_titulo))
    linhas = {k: _secao_cv(cart_cv[k]) for k in "UEO"}
    dados = [
        ["MODELO", "U", "E", "O"],
        ["TREINO F1 MACRO MEDIO (DPA)"] + [linhas[k][0] for k in "UEO"],
        ["VALIDACAO F1 MACRO MEDIO (DPA)"] + [linhas[k][1] for k in "UEO"],
        ["MEDIA DAS DIFS. (DPA)"] + [linhas[k][2] for k in "UEO"],
    ]
    story.append(_tabela(dados, [5.6 * cm] + [3.15 * cm] * 3, AZUL))
    story.append(Spacer(1, 0.12 * cm))

    # 4
    story.append(_titulo("4) HIPERPARAMETRIZACOES REDE NEURAL", estilo_titulo))
    dados = [
        ["MODELO", "U", "E", "O"],
        ["Topologia"] + [_topologia(cfg["rn"][k]) for k in "UEO"],
        ["Funcao de ativacao"] + [cfg["rn"][k]["activation"] for k in "UEO"],
        ["Learning rate"] + [cfg["rn"][k]["learning_rate_init"] for k in "UEO"],
        ["solver"] + [cfg["rn"][k]["solver"] for k in "UEO"],
        ["alpha"] + [cfg["rn"][k]["alpha"] for k in "UEO"],
        ["max_iter"] + [cfg["rn"][k]["max_iter"] for k in "UEO"],
    ]
    story.append(_tabela(dados, [5.6 * cm] + [3.15 * cm] * 3, LARANJA))
    story.append(Spacer(1, 0.2 * cm))

    # 5
    story.append(_titulo("5) RESULTADOS DOS MODELOS RN", estilo_titulo))
    linhas = {k: _secao_cv(rn_cv[k]) for k in "UEO"}
    dados = [
        ["MODELO", "U", "E", "O"],
        ["TREINO F1 MACRO MEDIO (DPA)"] + [linhas[k][0] for k in "UEO"],
        ["VALIDACAO F1 MACRO MEDIO (DPA)"] + [linhas[k][1] for k in "UEO"],
        ["MEDIA DAS DIFS. (DPA)"] + [linhas[k][2] for k in "UEO"],
    ]
    story.append(_tabela(dados, [5.6 * cm] + [3.15 * cm] * 3, LARANJA))
    story.append(Spacer(1, 0.12 * cm))

    # 6
    story.append(_titulo("6) MELHOR MODELO CART X MELHOR MODELO RN", estilo_titulo))
    cart_m = _secao_cv(cart_cv[melhor_cart])
    rn_m = _secao_cv(rn_cv[melhor_rn])
    dados = [
        ["MODELO", f"Melhor CART ({melhor_cart})", f"Melhor RN ({melhor_rn})"],
        ["TREINO F1 MACRO MEDIO (DPA)", cart_m[0], rn_m[0]],
        ["VALIDACAO F1 MACRO MEDIO (DPA)", cart_m[1], rn_m[1]],
        ["MEDIA DAS DIFS. (DPA)", cart_m[2], rn_m[2]],
    ]
    story.append(_tabela(dados, [7.1 * cm, 4.2 * cm, 4.2 * cm], ROXO))
    story.append(Spacer(1, 0.12 * cm))

    # 7
    titulo7 = _titulo("7) RESULTADOS DO TESTE CEGO MELHOR CART X MELHOR RN", estilo_titulo)
    dados = [
        ["MODELO", f"Melhor CART ({melhor_cart})", f"Melhor RN ({melhor_rn})"],
        ["MEDIA PRECISAO (macro)", _fmt(teste_cart["precisao_macro"]), _fmt(teste_rn["precisao_macro"])],
        ["MEDIA RECALL (macro)", _fmt(teste_cart["recall_macro"]), _fmt(teste_rn["recall_macro"])],
        ["F1 SCORE (macro)", _fmt(teste_cart["f1_macro"]), _fmt(teste_rn["f1_macro"])],
        ["ACURACIA", _fmt(teste_cart["acuracia"]), _fmt(teste_rn["acuracia"])],
    ]
    tabela7 = _tabela(dados, [7.1 * cm, 4.2 * cm, 4.2 * cm], ROXO)
    story.append(KeepTogether([titulo7, tabela7]))
    story.append(Spacer(1, 0.18 * cm))

    # 8
    titulo8 = _titulo(
        "8) MATRIZ DE CONFUSAO DO MELHOR CART E MATRIZ DE CONFUSAO DA MELHOR RN",
        estilo_titulo,
    )
    legenda8 = Paragraph("G=verde, Y=amarelo, R=vermelho, B=preto", estilo_obs)

    cart_mat = _matriz_confusao_tabela("CART", teste_cart["matriz_confusao"])
    rn_mat = _matriz_confusao_tabela("RN", teste_rn["matriz_confusao"])
    lado_a_lado = Table([[cart_mat, rn_mat]], colWidths=[7.5 * cm, 7.5 * cm])
    lado_a_lado.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0.3 * cm),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(KeepTogether([titulo8, legenda8, Spacer(1, 0.08 * cm), lado_a_lado]))

    doc.build(story)


def main() -> None:
    if not RESULTADO.exists():
        raise FileNotFoundError(
            "results/resultado_experimento.json ainda nao existe. "
            "Execute o pipeline de treino primeiro."
        )
    with RESULTADO.open("r", encoding="utf-8") as f:
        resultado = json.load(f)
    gerar(resultado, SAIDA)
    print(f"Relatorio gerado: {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
