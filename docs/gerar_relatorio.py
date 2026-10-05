"""
Gera o relatorio tecnico em PDF exigido pelo Projeto Final.

O documento nao e estatico: ele executa o pipeline e escreve os resultados
reais da execucao (fichas extraidas, quadro comparativo, sumario executivo).
Basta regerar para que o PDF reflita a versao atual da solucao.

Uso:
    python docs/gerar_relatorio.py              # extracao heuristica (offline)
    python docs/gerar_relatorio.py --com-llm    # extracao com Gemini
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config  # noqa: E402
from src.agentes.comparacao import formatar  # noqa: E402
from src.orquestrador import processar  # noqa: E402

AZUL = colors.HexColor("#1F4E79")
AZUL_CLARO = colors.HexColor("#D6E4F0")
CINZA = colors.HexColor("#F2F2F2")

estilos = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=estilos["Heading1"], textColor=AZUL, fontSize=16, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=estilos["Heading2"], textColor=AZUL, fontSize=12.5, spaceBefore=12)
CORPO = ParagraphStyle(
    "Corpo", parent=estilos["BodyText"], fontSize=9.5, leading=14, alignment=TA_JUSTIFY
)
CELULA = ParagraphStyle("Celula", parent=estilos["BodyText"], fontSize=8.5, leading=11)
CELULA_B = ParagraphStyle("CelulaB", parent=CELULA, fontName="Helvetica-Bold", textColor=colors.white)
MONO = ParagraphStyle(
    "Mono",
    parent=estilos["BodyText"],
    fontName="Courier",
    fontSize=7.8,
    leading=10.5,
    backColor=CINZA,
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=8,
)


def escapar(texto: str) -> str:
    return (
        str(texto)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def tabela(dados: list[list[str]], larguras: list[float]) -> Table:
    linhas = [[Paragraph(c, CELULA_B) for c in dados[0]]]
    linhas += [[Paragraph(str(c), CELULA) for c in linha] for linha in dados[1:]]
    t = Table(linhas, colWidths=larguras, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, AZUL_CLARO]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0B0B0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2 * cm, 1.2 * cm, "InsurMinds - Projeto Final | Squad 4one")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"pág. {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
    canvas.line(2 * cm, 1.6 * cm, 19 * cm, 1.6 * cm)
    canvas.restoreState()


def construir(resultado, destino: Path) -> None:
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="InsurMinds - Projeto Final - Relatório Técnico",
        author="Squad 4one",
    )
    s: list = []
    comparativo = resultado.comparativo

    # ----------------------------------------------------------------- capa
    s.append(Spacer(1, 3 * cm))
    s.append(
        Paragraph(
            "<font size=22 color='#1F4E79'><b>Plataforma Inteligente para Análise e "
            "Comparação de Apólices D&amp;O</b></font>",
            estilos["Title"],
        )
    )
    s.append(Spacer(1, 0.6 * cm))
    s.append(
        Paragraph(
            "<para align='center'><font size=13>Relatório Técnico — Projeto Final</font><br/>"
            "<font size=11>Curso InsurMinds · Instituto de Inteligência Artificial Aplicada "
            "(I2A2)</font></para>",
            estilos["Normal"],
        )
    )
    s.append(Spacer(1, 2 * cm))
    s.append(
        Paragraph(
            f"<para align='center'><b>Grupo:</b> Squad 4one<br/>"
            f"<b>Data:</b> {datetime.now(tz=config.FUSO):%d/%m/%Y}<br/>"
            f"<b>Licença:</b> MIT</para>",
            estilos["Normal"],
        )
    )
    s.append(Spacer(1, 1.5 * cm))
    s.append(
        Paragraph(
            "<para align='center'><i>Solução que recebe apólices de Responsabilidade Civil de "
            "Administradores em PDF ou imagem, extrai o conteúdo com OCR quando necessário, "
            "estrutura as cláusulas com IA Generativa, armazena em banco relacional e produz um "
            "quadro comparativo auditável entre apólices.</i></para>",
            CORPO,
        )
    )
    s.append(PageBreak())

    # ------------------------------------------------------------ 1 problema
    s.append(Paragraph("1. Problema abordado", H1))
    s.append(
        Paragraph(
            "Comparar duas apólices de D&amp;O é um trabalho manual, lento e dependente de "
            "especialista. São documentos longos, redigidos em linguagem jurídica, em que cada "
            "seguradora organiza as mesmas informações de maneira diferente: o que uma chama de "
            "Limite Máximo de Indenização, outra traz dentro de um quadro de limites; o que uma "
            "lista como cobertura, outra concede por cláusula particular. O analista precisa ler "
            "os dois documentos inteiros para responder perguntas simples — qual tem maior "
            "retroatividade, qual exclui danos morais, qual franquia incide sobre custos de defesa.",
            CORPO,
        )
    )
    s.append(
        Paragraph(
            "O custo disso não é só o tempo. É a assimetria: quem compara às pressas decide com "
            "base no prêmio e no limite, que são os campos fáceis de achar, e descobre as "
            "diferenças de cláusula no momento do sinistro. A plataforma ataca exatamente esse "
            "ponto — transforma documentos heterogêneos em uma ficha padronizada e coloca as "
            "divergências lado a lado antes da decisão.",
            CORPO,
        )
    )

    # --------------------------------------------------------- 2 arquitetura
    s.append(Paragraph("2. Arquitetura da solução", H1))
    s.append(
        Paragraph(
            "A solução implementa as sete etapas previstas no enunciado como agentes "
            "especializados, cada um com responsabilidade única e contrato de dados explícito "
            "(classes Pydantic). O orquestrador encadeia os agentes e registra um log passo a "
            "passo de cada execução.",
            CORPO,
        )
    )
    s.append(Spacer(1, 0.2 * cm))
    s.append(
        Paragraph(
            "PDF / imagem &rarr; <b>1. Recepção</b> &rarr; <b>2. Extração (texto nativo ou OCR)</b> "
            "&rarr; <b>3. Estruturação (IA Generativa)</b> &rarr; <b>4. Armazenamento (SQLite)</b> "
            "&rarr; <b>5. Comparação (determinística)</b> &rarr; <b>6. Relatório (IA Generativa)</b> "
            "&rarr; <b>7. Consulta em linguagem natural</b>",
            ParagraphStyle("fluxo", parent=CORPO, alignment=1, backColor=CINZA, borderPadding=8),
        )
    )
    s.append(Spacer(1, 0.3 * cm))
    s.append(Paragraph("2.1 Descrição dos agentes", H2))
    s.append(
        tabela(
            [
                ["Agente", "Responsabilidade", "Entrada &rarr; Saída"],
                [
                    "<b>1. AgenteRecepcao</b><br/>src/agentes/recepcao.py",
                    "Valida formato, tamanho e integridade dos arquivos. Documentos recusados são "
                    "reportados com o motivo, sem interromper o processamento dos demais.",
                    "arquivos &rarr;<br/>list[DocumentoRecebido]",
                ],
                [
                    "<b>2. AgenteExtracao</b><br/>src/agentes/extracao.py",
                    "Lê o texto nativo com pdfplumber e decide <b>página a página</b> se precisa de "
                    "OCR (Tesseract). Registra o método usado em cada documento.",
                    "documentos &rarr;<br/>list[TextoExtraido]",
                ],
                [
                    "<b>3. AgenteEstruturacao</b><br/>src/agentes/estruturacao.py",
                    "Núcleo de IA Generativa: envia o texto e um schema ao Gemini e recebe JSON "
                    "validado com Pydantic, incluindo a evidência textual de cada campo. Sem chave "
                    "de API, usa extração heurística por rótulos e seções.",
                    "textos &rarr;<br/>list[ApoliceEstruturada]",
                ],
                [
                    "<b>4. AgenteArmazenamento</b><br/>src/agentes/armazenamento.py",
                    "Persiste as fichas em SQLite, com campos escalares consultáveis em SQL e as "
                    "listas serializadas em JSON na mesma linha. Reprocessar gera nova versão.",
                    "fichas &rarr;<br/>ids no banco",
                ],
                [
                    "<b>5. AgenteComparacao</b><br/>src/agentes/comparacao.py",
                    "Monta o quadro campo a campo, calcula a direção do impacto e apura coberturas "
                    "e exclusões exclusivas de cada apólice por sobreposição de termos.",
                    "fichas &rarr;<br/>Comparativo",
                ],
                [
                    "<b>6. AgenteRelatorio</b><br/>src/agentes/relatorio.py",
                    "Escreve o sumário executivo a partir das divergências já apuradas — nunca do "
                    "documento original.",
                    "Comparativo &rarr;<br/>Comparativo + sumário",
                ],
                [
                    "<b>7. AgenteConsulta</b><br/>src/agentes/consulta.py",
                    "Responde perguntas em linguagem natural usando as fichas estruturadas como "
                    "contexto, citando a apólice de origem.",
                    "pergunta + fichas &rarr;<br/>RespostaConsulta",
                ],
            ],
            [3.7 * cm, 8.3 * cm, 4.5 * cm],
        )
    )
    s.append(PageBreak())

    # ------------------------------------------------- 3 decisões de projeto
    s.append(Paragraph("3. Justificativa das decisões arquiteturais", H1))
    for titulo, texto in [
        (
            "A IA extrai e redige; ela não decide",
            "A identificação do evento comparativo — qual limite é maior, qual exclusão existe só "
            "em uma apólice — é aritmética e teoria de conjuntos sobre a ficha estruturada, e foi "
            "implementada de forma determinística. Se o LLM decidisse isso, duas execuções sobre "
            "os mesmos documentos poderiam divergir, e nenhuma delas seria auditável. O modelo faz "
            "o que só ele faz bem: ler linguagem jurídica heterogênea e devolver campos "
            "padronizados, e depois escrever o resumo a partir de diferenças já apuradas.",
        ),
        (
            "Saída estruturada com validação, não texto livre",
            "O prompt de extração exige JSON aderente a um schema explícito, e a resposta passa por "
            "validação Pydantic antes de entrar no banco. Uma resposta fora do contrato falha na "
            "validação em vez de virar dado silenciosamente errado — e o sistema cai para a "
            "extração heurística, registrando isso na ficha.",
        ),
        (
            "Evidência obrigatória por campo",
            "Para cada campo preenchido, o modelo devolve o trecho literal do documento que "
            "sustenta o valor. É o que permite ao analista auditar a extração sem reler a apólice "
            "inteira, e é também o mecanismo que torna a alucinação visível: um valor sem trecho "
            "correspondente é um sinal de alerta, não um dado.",
        ),
        (
            "OCR decidido por página, não por documento",
            "Apólices reais misturam páginas digitais com anexos escaneados. Rodar OCR no documento "
            "inteiro desperdiça tempo e degrada o texto de páginas que já tinham camada nativa; não "
            "rodar perde o anexo. A decisão por página resolve os dois casos, e o método efetivo "
            "fica registrado porque texto de OCR tem qualidade inferior e isso precisa ser visível.",
        ),
        (
            "Banco relacional em vez de arquivo",
            "SQLite dá consulta por campo e histórico de versões sem exigir servidor, mantendo o "
            "protótipo executável com um clone e um pip install. Listas (coberturas, exclusões) "
            "ficam em JSON na mesma linha: para o volume de um MVP isso basta e evita cinco tabelas "
            "de apoio que não agregariam à demonstração.",
        ),
        (
            "Degradação controlada em vez de falha",
            "Sem chave de API, sem Tesseract ou sem rede, a solução continua executável com "
            "capacidade reduzida e informa qual caminho usou. Isso é o que permite demonstrar o "
            "fluxo completo em qualquer máquina — e é também o comportamento correto em produção, "
            "onde um provedor fora do ar não pode derrubar a plataforma inteira.",
        ),
    ]:
        s.append(Paragraph(titulo, H2))
        s.append(Paragraph(texto, CORPO))

    s.append(PageBreak())

    # ----------------------------------------------------------- 4 tecnologias
    s.append(Paragraph("4. Tecnologias utilizadas", H1))
    s.append(
        tabela(
            [
                ["Camada", "Tecnologia", "Papel na solução"],
                ["Linguagem", "Python 3.11+", "Base de toda a aplicação."],
                [
                    "Leitura de documentos",
                    "pdfplumber, pdf2image, Pillow",
                    "Extração de texto nativo e rasterização de páginas para OCR.",
                ],
                [
                    "OCR",
                    "Tesseract (pytesseract), idioma por",
                    "Leitura de apólices digitalizadas ou fotografadas.",
                ],
                [
                    "IA Generativa",
                    "Google Gemini via LangChain",
                    "Estruturação das cláusulas, sumário executivo e consulta em linguagem natural.",
                ],
                [
                    "Contratos de dados",
                    "Pydantic v2",
                    "Schema da ficha da apólice e validação da saída do modelo.",
                ],
                ["Persistência", "SQLite", "Armazenamento estruturado e consulta SQL."],
                ["Interface", "Streamlit", "Demonstração do fluxo etapa por etapa."],
                ["Relatórios", "ReportLab, python-pptx", "Relatório técnico em PDF e pitch deck."],
                [
                    "Segredos",
                    "python-dotenv",
                    "Chaves em .env, fora do versionamento (.gitignore).",
                ],
            ],
            [3.2 * cm, 4.6 * cm, 8.7 * cm],
        )
    )

    # ---------------------------------------------------- 5 fluxo demonstrado
    s.append(Paragraph("5. Fluxo completo de processamento — execução demonstrada", H1))
    s.append(
        Paragraph(
            f"Execução de {resultado.executado_em:%d/%m/%Y às %H:%M:%S}. "
            f"<b>Modo de extração:</b> {escapar(resultado.modo_ia)}.",
            CORPO,
        )
    )
    s.append(
        tabela(
            [["Documento", "Páginas", "Leitura", "Caracteres"]]
            + [
                [t.nome, str(t.paginas), t.metodo, str(t.caracteres)]
                for t in resultado.textos
            ],
            [7.5 * cm, 2.2 * cm, 4.3 * cm, 3 * cm],
        )
    )
    s.append(Spacer(1, 0.3 * cm))
    s.append(Paragraph("5.1 Fichas estruturadas", H2))
    s.append(
        tabela(
            [["Campo"] + [f.rotulo for f in resultado.fichas]]
            + [
                ["LMI"] + [formatar(f.limite_maximo_indenizacao) for f in resultado.fichas],
                ["Prêmio"] + [formatar(f.premio_total) for f in resultado.fichas],
                ["Franquia"] + [formatar(f.franquia) for f in resultado.fichas],
                ["Base"] + [f.base_cobertura.value for f in resultado.fichas],
                ["Retroatividade"] + [f.data_retroatividade or "-" for f in resultado.fichas],
                ["Coberturas"] + [str(len(f.coberturas)) for f in resultado.fichas],
                ["Exclusões"] + [str(len(f.exclusoes)) for f in resultado.fichas],
                ["Leitura"] + [f.metodo_leitura for f in resultado.fichas],
            ],
            [3 * cm, *[((17 - 3) / max(1, len(resultado.fichas))) * cm] * len(resultado.fichas)],
        )
    )
    s.append(PageBreak())

    # -------------------------------------------------------- 6 comparativo
    s.append(Paragraph("6. Comparação entre apólices", H1))
    if comparativo:
        s.append(
            Paragraph(
                f"{len(comparativo.divergencias)} divergência(s) em "
                f"{len(comparativo.linhas)} campos comparados.",
                CORPO,
            )
        )
        materiais = [
            linha
            for linha in comparativo.divergencias
            if linha.campo
            not in {"seguradora", "produto", "numero_apolice", "processo_susep", "tomador"}
        ]
        cabecalho = ["Campo"] + list(materiais[0].valores) if materiais else ["Campo"]
        linhas = [cabecalho]
        for linha in materiais[:12]:
            linhas.append([linha.rotulo] + [escapar(v) for v in linha.valores.values()])
        largura = (17 - 4.2) / max(1, len(cabecalho) - 1)
        s.append(tabela(linhas, [4.2 * cm, *[largura * cm] * (len(cabecalho) - 1)]))

        s.append(Paragraph("6.1 Cláusulas exclusivas de cada apólice", H2))
        linhas = [["Apólice", "Coberturas só nela", "Exclusões só nela"]]
        for rotulo in comparativo.apolices:
            linhas.append(
                [
                    rotulo,
                    escapar("; ".join(comparativo.coberturas_exclusivas.get(rotulo, [])[:4]) or "nenhuma"),
                    escapar("; ".join(comparativo.exclusoes_exclusivas.get(rotulo, [])[:4]) or "nenhuma"),
                ]
            )
        s.append(tabela(linhas, [4 * cm, 6.5 * cm, 6.5 * cm]))

        s.append(Paragraph("6.2 Sumário executivo gerado pela solução", H2))
        s.append(Paragraph(escapar(comparativo.sumario_executivo), MONO))
        s.append(
            Paragraph(
                f"<font size=7.5 color='#666666'>Gerado por: "
                f"{escapar(comparativo.gerado_sumario_por)}</font>",
                CORPO,
            )
        )
    else:
        s.append(Paragraph("Execução sem comparativo (menos de duas apólices).", CORPO))

    s.append(PageBreak())

    # ---------------------------------------------------------- 7 log e dados
    s.append(Paragraph("7. Rastreabilidade e dados utilizados", H1))
    s.append(
        Paragraph(
            "As apólices usadas na demonstração são <b>fictícias</b>, criadas especificamente para "
            "este trabalho (script <font face='Courier' size=8.5>data/gerar_apolices_exemplo.py</font>). "
            "A redação segue a estrutura e a terminologia usuais de condições particulares de "
            "D&amp;O no mercado brasileiro — limite máximo de indenização, retroatividade, prazos "
            "complementar e suplementar, base claims made —, mas nomes de seguradora, números de "
            "apólice, valores e processos SUSEP não correspondem a nenhum produto real. Uma das "
            "três é gerada sem camada de texto, simulando um documento digitalizado, para "
            "exercitar o caminho de OCR. A plataforma aceita igualmente documentos públicos reais "
            "(modelos de apólice publicados por seguradoras ou material da SUSEP).",
            CORPO,
        )
    )
    s.append(Paragraph("7.1 Log da execução", H2))
    s.append(Paragraph(escapar("\n".join(resultado.log[:28])), MONO))

    # ------------------------------------------------------------ 8 limitações
    s.append(Paragraph("8. Limitações conhecidas", H1))
    for item in [
        "A qualidade da extração depende da qualidade do documento: páginas digitalizadas com "
        "baixa resolução ou ruído produzem texto degradado, e o erro se propaga para a ficha.",
        "O extrator heurístico (usado sem chave de API) funciona bem em documentos rotulados e "
        "mal em texto corrido jurídico; ele é um recurso de contingência, não uma alternativa "
        "equivalente ao modelo.",
        "A comparação de cláusulas usa sobreposição de termos, não equivalência jurídica: duas "
        "redações diferentes com o mesmo efeito legal podem ser apontadas como divergentes.",
        "A leitura de impacto (quem a diferença favorece) segue regras simples — mais limite é "
        "melhor, menos franquia é melhor — e não substitui parecer técnico ou jurídico.",
        "Não há tratamento de endossos, apólices em múltiplos arquivos, moedas diferentes entre "
        "documentos nem conversão cambial.",
        "O protótipo não implementa autenticação, controle de acesso por usuário nem criptografia "
        "dos documentos em repouso — necessários antes de qualquer uso com dados reais de clientes.",
    ]:
        s.append(Paragraph(f"• {item}", CORPO))

    # ---------------------------------------------------------- 9 evolução
    s.append(Paragraph("9. Possibilidades de evolução futura", H1))
    for item in [
        "Camada de RAG sobre o texto integral das apólices, permitindo perguntas sobre trechos que "
        "não cabem na ficha estruturada, com citação de página.",
        "Base de cláusulas padrão do mercado para classificar cada redação encontrada como mais "
        "restritiva, equivalente ou mais ampla que a referência.",
        "Registro de concordância humana: o analista confirma ou corrige cada campo extraído, "
        "gerando métrica de acurácia por seguradora e por tipo de documento.",
        "Comparação de versões da mesma apólice ao longo das renovações, destacando o que mudou "
        "de um ano para o outro — caso de uso frequente em resseguro.",
        "Extensão a outros ramos com schema próprio (RC Profissional, Cyber, Riscos Nomeados), "
        "mantendo a mesma arquitetura e trocando apenas a ficha.",
        "Exportação do quadro comparativo em formato de parecer, pronto para anexar à proposta "
        "enviada ao cliente.",
    ]:
        s.append(Paragraph(f"• {item}", CORPO))

    s.append(Paragraph("10. Como executar", H1))
    s.append(
        Paragraph(
            escapar(
                "pip install -r requirements.txt\n"
                "cp .env.example .env            # informe a GOOGLE_API_KEY\n"
                "python data/gerar_apolices_exemplo.py\n"
                "streamlit run app.py            # interface de demonstração\n"
                "python main.py --sem-llm        # execução offline, extração heurística"
            ),
            MONO,
        )
    )
    s.append(
        Paragraph(
            "O repositório é público e está licenciado sob a licença MIT. O README.md traz as "
            "instruções completas, a estrutura do projeto e a identificação dos integrantes. "
            "A apresentação e o vídeo estão na pasta Projeto_Final_Artefatos.",
            CORPO,
        )
    )

    doc.build(s, onFirstPage=rodape, onLaterPages=rodape)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--com-llm", action="store_true")
    argumentos = parser.parse_args()

    caminhos = sorted(str(p) for p in config.DIR_EXEMPLOS.glob("*.pdf"))
    resultado = processar(caminhos, usar_llm=argumentos.com_llm, persistir=False)
    destino = Path(__file__).resolve().parent / "InsurMinds_Projeto_Final_Relatorio_Tecnico.pdf"
    construir(resultado, destino)
    print(f"Relatório gerado: {destino}")


if __name__ == "__main__":
    main()
