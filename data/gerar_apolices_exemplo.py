"""
Gera as apolices D&O de exemplo usadas na demonstracao.

Os tres documentos sao FICTICIOS, criados especificamente para este trabalho
academico. A redacao segue a estrutura e a terminologia usuais de condicoes
particulares de D&O no mercado brasileiro (limite maximo de indenizacao,
retroatividade, prazo complementar e suplementar, base claims made), mas os
nomes de seguradora, numeros de apolice, valores e processos SUSEP nao
correspondem a nenhum produto real.

A terceira apolice e gerada como PDF digitalizado (apenas imagem, sem camada
de texto), para exercitar o caminho de OCR da solucao.

Uso: python data/gerar_apolices_exemplo.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

DESTINO = Path(__file__).resolve().parent / "apolices_exemplo"
DESTINO.mkdir(exist_ok=True)

estilos = getSampleStyleSheet()
TITULO = ParagraphStyle("T", parent=estilos["Title"], fontSize=15, spaceAfter=14)
SECAO = ParagraphStyle(
    "S", parent=estilos["Heading2"], fontSize=11.5, textColor=colors.HexColor("#1F3864"), spaceBefore=12
)
TEXTO = ParagraphStyle("C", parent=estilos["BodyText"], fontSize=9.5, leading=13.5, alignment=4)

APOLICES = [
    {
        "arquivo": "apolice_do_horizonte.pdf",
        "seguradora": "Horizonte Seguros S.A.",
        "produto": "Seguro de Responsabilidade Civil de Administradores (D&O) - Condicoes Particulares",
        "numero": "DO-2026-004471",
        "susep": "15414.900123/2024-11",
        "tomador": "Agroindustrial Vale Verde S.A.",
        "vigencia": ("01/03/2026", "01/03/2027"),
        "moeda": "BRL",
        "lmi": "R$ 20.000.000,00 (vinte milhoes de reais)",
        "premio": "R$ 184.500,00",
        "franquia": "R$ 150.000,00 por reclamacao, nao aplicavel a custos de defesa de pessoas fisicas seguradas",
        "base": "A presente apolice e emitida na modalidade a base de reclamacoes (claims made).",
        "retroatividade": "01/03/2019",
        "complementar": "12 (doze) meses, sem cobranca de premio adicional",
        "suplementar": "36 (trinta e seis) meses, mediante pagamento de premio adicional de 75% do premio anual",
        "ambito": "Territorio nacional brasileiro",
        "jurisdicao": "Foro da Comarca de Sao Paulo/SP, excluidas reclamacoes ajuizadas nos Estados Unidos da America e no Canada",
        "coberturas": [
            "Custos de defesa de administradores em processos civis, administrativos e arbitrais",
            "Danos morais decorrentes de ato de gestao, ate o limite de R$ 5.000.000,00",
            "Multas e penalidades civis impostas por orgao regulador, ate R$ 2.000.000,00",
            "Custos de fianca e garantias processuais, ate R$ 1.000.000,00",
            "Reembolso a pessoa juridica pelos valores adiantados a administradores",
            "Custos de publicidade e gerenciamento de crise, ate R$ 500.000,00",
            "Cobertura para investigacoes e inqueritos conduzidos por autoridade competente",
            "Extensao a ex-administradores, conjuges, herdeiros e espolio",
        ],
        "sublimites": [
            "Danos morais: R$ 5.000.000,00",
            "Multas e penalidades civis: R$ 2.000.000,00",
            "Custos de fianca: R$ 1.000.000,00",
            "Publicidade e gerenciamento de crise: R$ 500.000,00",
        ],
        "exclusoes": [
            "Atos dolosos, fraudulentos ou criminosos comprovados por decisao judicial transitada em julgado",
            "Obtencao de vantagem pessoal ou remuneracao indevida",
            "Danos materiais e corporais, inclusive os decorrentes de poluicao",
            "Reclamacoes relacionadas a fatos conhecidos e nao comunicados antes do inicio de vigencia",
            "Obrigacoes trabalhistas e previdenciarias da pessoa juridica",
            "Reclamacoes ajuizadas nos Estados Unidos da America e no Canada",
        ],
        "especiais": [
            "Clausula de ordem de pagamento: custos de defesa das pessoas fisicas tem prioridade sobre qualquer outro pagamento",
            "Clausula de nao cancelamento em caso de mudanca de controle, ate o fim da vigencia",
            "Clausula de arbitragem facultativa para disputas sobre a cobertura",
        ],
    },
    {
        "arquivo": "apolice_do_meridiano.pdf",
        "seguradora": "Meridiano Companhia de Seguros",
        "produto": "D&O - Responsabilidade Civil de Diretores e Administradores",
        "numero": "MD-DO-77.902-3",
        "susep": "15414.610987/2023-45",
        "tomador": "Agroindustrial Vale Verde S.A.",
        "vigencia": ("01/03/2026", "01/03/2027"),
        "moeda": "BRL",
        "lmi": "R$ 15.000.000,00 (quinze milhoes de reais)",
        "premio": "R$ 142.000,00",
        "franquia": "R$ 250.000,00 por reclamacao, aplicavel inclusive a custos de defesa",
        "base": "Cobertura concedida sob a forma de reclamacoes apresentadas (claims made) durante a vigencia.",
        "retroatividade": "01/03/2023",
        "complementar": "6 (seis) meses, sem premio adicional",
        "suplementar": "24 (vinte e quatro) meses, mediante premio adicional de 100% do premio anual",
        "ambito": "Mundial, exceto Estados Unidos da America e Canada",
        "jurisdicao": "Foro da Comarca do Rio de Janeiro/RJ",
        "coberturas": [
            "Custos de defesa em processos civis e administrativos",
            "Multas e penalidades civis, ate R$ 1.000.000,00",
            "Custos de fianca, ate R$ 500.000,00",
            "Responsabilidade da pessoa juridica em reclamacoes de valores mobiliarios",
            "Despesas de emergencia incorridas antes da comunicacao formal a seguradora",
            "Extensao a ex-administradores",
        ],
        "sublimites": [
            "Multas e penalidades civis: R$ 1.000.000,00",
            "Custos de fianca: R$ 500.000,00",
            "Despesas de emergencia: 10% do limite maximo de indenizacao",
        ],
        "exclusoes": [
            "Atos dolosos e fraudulentos",
            "Vantagem pessoal indevida",
            "Danos corporais e materiais",
            "Fatos anteriores conhecidos",
            "Danos morais",
            "Reclamacoes relacionadas a questoes ambientais e climaticas",
            "Reclamacoes decorrentes de operacoes de fusao e aquisicao nao comunicadas previamente",
            "Obrigacoes trabalhistas e previdenciarias",
        ],
        "especiais": [
            "Clausula de rescisao automatica em caso de mudanca de controle acionario",
            "Clausula de sub-rogacao integral em favor da seguradora",
        ],
    },
    {
        "arquivo": "apolice_do_aurora_digitalizada.pdf",
        "digitalizada": True,
        "seguradora": "Aurora Seguradora Brasil S.A.",
        "produto": "Apolice de Seguro D&O - Condicoes Particulares",
        "numero": "AUR-DO-2026-8812",
        "susep": "15414.330221/2025-07",
        "tomador": "Agroindustrial Vale Verde S.A.",
        "vigencia": ("01/03/2026", "01/03/2027"),
        "moeda": "BRL",
        "lmi": "R$ 25.000.000,00 (vinte e cinco milhoes de reais)",
        "premio": "R$ 231.800,00",
        "franquia": "R$ 100.000,00 por reclamacao, nao aplicavel a pessoas fisicas seguradas",
        "base": "Apolice emitida a base de reclamacoes (claims made), com periodo de retroatividade ilimitado.",
        "retroatividade": "Ilimitada",
        "complementar": "12 (doze) meses, sem premio adicional",
        "suplementar": "72 (setenta e dois) meses, mediante premio adicional de 150% do premio anual",
        "ambito": "Mundial, inclusive Estados Unidos da America e Canada",
        "jurisdicao": "Foro da Comarca de Sao Paulo/SP",
        "coberturas": [
            "Custos de defesa em processos civis, administrativos, arbitrais e criminais",
            "Danos morais, ate R$ 8.000.000,00",
            "Multas e penalidades civis, ate R$ 3.000.000,00",
            "Custos de fianca e garantias processuais, ate R$ 2.000.000,00",
            "Responsabilidade da pessoa juridica em valores mobiliarios",
            "Reembolso a pessoa juridica",
            "Custos de publicidade e gerenciamento de crise, ate R$ 1.000.000,00",
            "Investigacoes e inqueritos, inclusive pre-reclamacao",
            "Obrigacoes trabalhistas e previdenciarias decorrentes de ato de gestao, ate R$ 1.500.000,00",
            "Extensao a ex-administradores, conjuges, herdeiros e espolio",
            "Despesas de emergencia",
        ],
        "sublimites": [
            "Danos morais: R$ 8.000.000,00",
            "Multas e penalidades civis: R$ 3.000.000,00",
            "Custos de fianca: R$ 2.000.000,00",
            "Publicidade e gerenciamento de crise: R$ 1.000.000,00",
            "Obrigacoes trabalhistas e previdenciarias: R$ 1.500.000,00",
        ],
        "exclusoes": [
            "Atos dolosos ou fraudulentos reconhecidos por decisao judicial definitiva",
            "Vantagem pessoal indevida reconhecida por decisao judicial definitiva",
            "Danos corporais e materiais",
            "Fatos conhecidos e nao declarados na proposta",
            "Responsabilidade contratual assumida por terceiros",
        ],
        "especiais": [
            "Clausula de ordem de pagamento em favor das pessoas fisicas seguradas",
            "Clausula de manutencao de cobertura (run-off) de 72 meses em caso de mudanca de controle",
            "Clausula de reintegracao unica do limite maximo de indenizacao para pessoas fisicas",
            "Clausula de livre escolha de advogado pelo segurado, mediante anuencia previa da seguradora",
        ],
    },
]


def construir_pdf(dados: dict, destino: Path) -> None:
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"{dados['seguradora']} - {dados['numero']}",
    )
    s: list = []
    s.append(Paragraph(dados["seguradora"].upper(), TITULO))
    s.append(Paragraph(dados["produto"].replace("&", "&amp;"), TEXTO))
    s.append(Spacer(1, 0.4 * cm))
    s.append(
        Paragraph(
            "<i>Documento ficticio, elaborado para fins academicos. Nao corresponde a produto "
            "comercializado nem a condicoes contratuais reais.</i>",
            TEXTO,
        )
    )

    s.append(Paragraph("1. Identificacao", SECAO))
    for rotulo, valor in [
        ("Numero da apolice", dados["numero"]),
        ("Processo SUSEP", dados["susep"]),
        ("Tomador / Segurado", dados["tomador"]),
        ("Inicio de vigencia", dados["vigencia"][0]),
        ("Fim de vigencia", dados["vigencia"][1]),
        ("Moeda", dados["moeda"]),
    ]:
        s.append(Paragraph(f"<b>{rotulo}:</b> {valor}", TEXTO))

    s.append(Paragraph("2. Limites e valores", SECAO))
    s.append(Paragraph(f"<b>Limite Maximo de Indenizacao (LMI):</b> {dados['lmi']}", TEXTO))
    s.append(Paragraph(f"<b>Premio total:</b> {dados['premio']}", TEXTO))
    s.append(Paragraph(f"<b>Franquia:</b> {dados['franquia']}", TEXTO))

    s.append(Paragraph("3. Base de cobertura e prazos", SECAO))
    s.append(Paragraph(dados["base"], TEXTO))
    s.append(Paragraph(f"<b>Data de retroatividade:</b> {dados['retroatividade']}", TEXTO))
    s.append(Paragraph(f"<b>Prazo complementar:</b> {dados['complementar']}", TEXTO))
    s.append(Paragraph(f"<b>Prazo suplementar:</b> {dados['suplementar']}", TEXTO))
    s.append(Paragraph(f"<b>Ambito geografico:</b> {dados['ambito']}", TEXTO))
    s.append(Paragraph(f"<b>Jurisdicao:</b> {dados['jurisdicao']}", TEXTO))

    for titulo, chave in [
        ("4. Coberturas contratadas", "coberturas"),
        ("5. Sublimites", "sublimites"),
        ("6. Riscos excluidos", "exclusoes"),
        ("7. Clausulas particulares", "especiais"),
    ]:
        s.append(Paragraph(titulo, SECAO))
        s.append(
            ListFlowable(
                [ListItem(Paragraph(item, TEXTO), leftIndent=12) for item in dados[chave]],
                bulletType="bullet",
                start="-",
            )
        )

    doc.build(s)


def rasterizar(origem: Path) -> None:
    """Converte o PDF em imagens e remonta sem camada de texto (simula digitalizacao)."""
    from pdf2image import convert_from_path
    from reportlab.pdfgen import canvas as rl_canvas

    paginas = convert_from_path(str(origem), dpi=150, grayscale=True)
    temporarios = []
    c = rl_canvas.Canvas(str(origem), pagesize=A4)
    largura, altura = A4
    for i, pagina in enumerate(paginas):
        caminho = origem.parent / f"_tmp_{i}.png"
        pagina.save(caminho)
        temporarios.append(caminho)
        c.drawImage(str(caminho), 0, 0, width=largura, height=altura)
        c.showPage()
    c.save()
    for caminho in temporarios:
        caminho.unlink(missing_ok=True)


def main() -> None:
    for dados in APOLICES:
        destino = DESTINO / dados["arquivo"]
        construir_pdf(dados, destino)
        if dados.get("digitalizada"):
            rasterizar(destino)
            print(f"gerado (digitalizado/OCR): {destino.name}")
        else:
            print(f"gerado: {destino.name}")


if __name__ == "__main__":
    main()
