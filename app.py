"""
Interface da plataforma (Streamlit).

Organizada nas sete etapas do fluxo, para que a demonstracao acompanhe o
caminho do documento: upload -> extracao -> ficha estruturada -> banco ->
comparacao -> consulta em linguagem natural.

Execucao:  streamlit run app.py
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config
from src.agentes.armazenamento import AgenteArmazenamento
from src.agentes.comparacao import formatar
from src.agentes.consulta import AgenteConsulta
from src.orquestrador import comparar_fichas, processar

st.set_page_config(page_title="InsurMinds | Apolices D&O", page_icon="📄", layout="wide")

st.title("Plataforma de Analise e Comparacao de Apolices D&O")
st.caption(
    "InsurMinds - Projeto Final | recepcao -> extracao (OCR quando necessario) -> "
    "estruturacao com IA Generativa -> armazenamento -> comparacao -> consulta"
)

banco = AgenteArmazenamento()

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Parametros")
    usar_llm = st.toggle(
        "Extrair com IA Generativa",
        value=bool(config.GOOGLE_API_KEY),
        help="Requer GOOGLE_API_KEY no .env. Sem chave, a extracao usa heuristica por rotulos.",
    )
    permitir_ocr = st.toggle(
        "Acionar OCR em paginas digitalizadas",
        value=True,
        help="Requer Tesseract instalado no sistema.",
    )
    if config.GOOGLE_API_KEY:
        st.success("Chave do modelo detectada")
    else:
        st.warning("Sem GOOGLE_API_KEY: extracao heuristica")

    st.divider()
    st.subheader("Base de apolices")
    armazenadas = banco.listar()
    st.write(f"{len(armazenadas)} apolice(s) no banco")
    if st.button("Carregar apolices de exemplo", use_container_width=True):
        exemplos = sorted(str(p) for p in config.DIR_EXEMPLOS.glob("*.pdf"))
        if exemplos:
            with st.spinner("Processando apolices de exemplo..."):
                st.session_state["resultado"] = processar(
                    exemplos, usar_llm=usar_llm, permitir_ocr=permitir_ocr
                )
            st.rerun()
        else:
            st.error("Gere os exemplos: python data/gerar_apolices_exemplo.py")

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
st.subheader("1. Recebimento dos documentos")
enviados = st.file_uploader(
    "Envie as apolices em PDF ou imagem (minimo duas para comparar)",
    type=["pdf", "png", "jpg", "jpeg", "tif", "tiff"],
    accept_multiple_files=True,
)

if enviados and st.button("Processar documentos", type="primary"):
    temporario = Path(tempfile.mkdtemp(prefix="insurminds_"))
    caminhos = []
    for arquivo in enviados:
        destino = temporario / arquivo.name
        destino.write_bytes(arquivo.getbuffer())
        caminhos.append(str(destino))
    with st.spinner("Lendo, estruturando e comparando..."):
        st.session_state["resultado"] = processar(
            caminhos, usar_llm=usar_llm, permitir_ocr=permitir_ocr
        )
    shutil.rmtree(temporario, ignore_errors=True)

resultado = st.session_state.get("resultado")

if resultado is None:
    st.info(
        "Envie dois ou mais documentos, ou use o botao **Carregar apolices de exemplo** na "
        "barra lateral. Os exemplos incluem uma apolice digitalizada, que exercita o caminho "
        "de OCR."
    )
    if armazenadas:
        st.subheader("Apolices ja armazenadas")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "id": identificador,
                        "Seguradora": ficha.seguradora,
                        "Apolice": ficha.numero_apolice,
                        "LMI": formatar(ficha.limite_maximo_indenizacao),
                        "Vigencia": f"{ficha.vigencia_inicio} a {ficha.vigencia_fim}",
                        "Leitura": ficha.metodo_leitura,
                    }
                    for identificador, ficha in armazenadas
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    st.stop()

if resultado.recusados:
    for nome, motivo in resultado.recusados:
        st.error(f"{nome}: {motivo}")

col1, col2, col3 = st.columns(3)
col1.metric("Documentos processados", len(resultado.fichas))
col2.metric(
    "Divergencias", len(resultado.comparativo.divergencias) if resultado.comparativo else 0
)
col3.metric("Paginas lidas", sum(t.paginas for t in resultado.textos))
st.caption(f"Extracao: {resultado.modo_ia} | {resultado.executado_em:%d/%m/%Y %H:%M:%S}")

abas = st.tabs(
    [
        "2. Extracao",
        "3. Ficha estruturada",
        "4. Armazenamento",
        "5. Comparacao",
        "6. Consulta",
        "Log",
    ]
)

# 2. Extracao ----------------------------------------------------------------
with abas[0]:
    st.subheader("Conteudo extraido de cada documento")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Arquivo": t.nome,
                    "Paginas": t.paginas,
                    "Metodo": t.metodo,
                    "Paginas via OCR": ", ".join(map(str, t.paginas_ocr)) or "-",
                    "Caracteres": t.caracteres,
                    "Erro": t.erro or "-",
                }
                for t in resultado.textos
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
    if resultado.textos:
        escolhido = st.selectbox("Ver texto bruto", [t.nome for t in resultado.textos])
        texto = next(t for t in resultado.textos if t.nome == escolhido)
        st.text_area("Texto extraido", texto.texto, height=300)

# 3. Ficha -------------------------------------------------------------------
with abas[1]:
    st.subheader("Ficha padronizada por apolice")
    for ficha in resultado.fichas:
        with st.expander(f"{ficha.rotulo} — {ficha.arquivo}", expanded=False):
            esquerda, direita = st.columns(2)
            with esquerda:
                st.markdown(
                    f"**Produto:** {ficha.produto or '-'}  \n"
                    f"**Tomador:** {ficha.tomador or '-'}  \n"
                    f"**Vigencia:** {ficha.vigencia_inicio} a {ficha.vigencia_fim}  \n"
                    f"**LMI:** {formatar(ficha.limite_maximo_indenizacao)}  \n"
                    f"**Premio:** {formatar(ficha.premio_total)}  \n"
                    f"**Franquia:** {formatar(ficha.franquia)}"
                )
            with direita:
                st.markdown(
                    f"**Base:** {ficha.base_cobertura.value}  \n"
                    f"**Retroatividade:** {ficha.data_retroatividade or '-'}  \n"
                    f"**Prazo complementar:** {ficha.prazo_complementar or '-'}  \n"
                    f"**Prazo suplementar:** {ficha.prazo_suplementar or '-'}  \n"
                    f"**Ambito:** {ficha.ambito_geografico or '-'}  \n"
                    f"**Jurisdicao:** {ficha.jurisdicao or '-'}"
                )
            st.markdown("**Coberturas**")
            st.write("\n".join(f"- {c.nome}" for c in ficha.coberturas) or "nao localizadas")
            st.markdown("**Exclusoes**")
            st.write("\n".join(f"- {e}" for e in ficha.exclusoes) or "nao localizadas")
            if ficha.evidencias:
                with st.expander("Evidencias da extracao (trechos do documento)"):
                    for campo, trecho in ficha.evidencias.items():
                        st.markdown(f"**{campo}** — _{trecho}_")
            st.caption(
                f"Extraido por {ficha.extraido_por} | leitura: {ficha.metodo_leitura}"
            )

# 4. Armazenamento -----------------------------------------------------------
with abas[2]:
    st.subheader("Base estruturada (SQLite)")
    st.caption(
        "Cada processamento grava uma nova versao da ficha, preservando o historico. "
        "A consulta abaixo roda SQL direto na tabela."
    )
    registros = banco.listar()
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "id": identificador,
                    "Arquivo": ficha.arquivo,
                    "Seguradora": ficha.seguradora,
                    "Apolice": ficha.numero_apolice,
                    "LMI": ficha.limite_maximo_indenizacao,
                    "Franquia": ficha.franquia,
                    "Extraido por": ficha.extraido_por,
                }
                for identificador, ficha in registros
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
    sql = st.text_input(
        "Consulta SQL (somente SELECT)",
        "SELECT seguradora, numero_apolice, limite_maximo_indenizacao, franquia FROM apolices "
        "ORDER BY limite_maximo_indenizacao DESC",
    )
    if st.button("Executar consulta"):
        try:
            st.dataframe(pd.DataFrame(banco.consultar_sql(sql)), use_container_width=True)
        except Exception as erro:
            st.error(str(erro))

# 5. Comparacao --------------------------------------------------------------
with abas[3]:
    st.subheader("Quadro comparativo")
    comparativo = resultado.comparativo
    if comparativo is None and len(resultado.fichas) >= 2:
        comparativo = comparar_fichas(resultado.fichas, usar_llm=usar_llm)
    if comparativo is None:
        st.info("A comparacao exige pelo menos duas apolices processadas.")
    else:
        somente_divergentes = st.checkbox("Mostrar apenas divergencias", value=True)
        linhas = comparativo.divergencias if somente_divergentes else comparativo.linhas
        tabela = pd.DataFrame(
            [{"Campo": linha.rotulo, **linha.valores, "Leitura": linha.comentario} for linha in linhas]
        )
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        st.markdown("### Coberturas presentes em apenas uma apolice")
        for rotulo, itens in comparativo.coberturas_exclusivas.items():
            st.markdown(f"**{rotulo}**")
            st.write("\n".join(f"- {i}" for i in itens) or "- nenhuma")

        st.markdown("### Exclusoes presentes em apenas uma apolice")
        for rotulo, itens in comparativo.exclusoes_exclusivas.items():
            st.markdown(f"**{rotulo}**")
            st.write("\n".join(f"- {i}" for i in itens) or "- nenhuma")

        st.markdown("### Sumario executivo")
        st.info(comparativo.sumario_executivo)
        st.caption(f"Gerado por: {comparativo.gerado_sumario_por}")

        esquerda, direita = st.columns(2)
        esquerda.download_button(
            "Baixar comparativo (CSV)",
            data=tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
            file_name="comparativo_apolices.csv",
            mime="text/csv",
        )
        direita.download_button(
            "Baixar comparativo (JSON)",
            data=json.dumps(comparativo.model_dump(mode="json"), ensure_ascii=False, indent=2),
            file_name="comparativo_apolices.json",
            mime="application/json",
        )
        st.caption(
            "Leitura tecnica de apoio a decisao, gerada a partir dos campos extraidos. "
            "Nao substitui a analise das condicoes contratuais originais."
        )

# 6. Consulta ----------------------------------------------------------------
with abas[4]:
    st.subheader("Consulta em linguagem natural")
    st.caption("As respostas usam as fichas estruturadas, nao o PDF bruto.")
    exemplos = [
        "Qual apolice tem a maior retroatividade?",
        "Alguma delas exclui danos morais?",
        "Qual tem o menor custo total considerando premio e franquia?",
        "Quais coberturas existem na Aurora e nao existem nas demais?",
    ]
    pergunta = st.text_input("Pergunta", exemplos[0])
    st.caption("Exemplos: " + " · ".join(exemplos[1:]))
    if st.button("Consultar"):
        agente = AgenteConsulta(usar_llm=usar_llm)
        with st.spinner("Consultando..."):
            resposta = agente.executar(pergunta, resultado.fichas)
        st.markdown(resposta.resposta)
        st.caption(
            f"Gerado por: {resposta.gerado_por} | fontes: {', '.join(resposta.fontes)}"
        )

# Log ------------------------------------------------------------------------
with abas[5]:
    st.subheader("Rastreabilidade da execucao")
    st.code("\n".join(resultado.log), language="text")
