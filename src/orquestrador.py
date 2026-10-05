"""
Orquestrador da plataforma.

Encadeia os agentes na ordem das sete etapas pedidas pelo desafio:

  1. Recebimento dos documentos      -> AgenteRecepcao
  2. Extracao automatica do conteudo -> AgenteExtracao (texto nativo / OCR)
  3. Organizacao das informacoes     -> AgenteEstruturacao (IA Generativa)
  4. Armazenamento estruturado       -> AgenteArmazenamento (SQLite)
  5. Consulta das informacoes        -> AgenteConsulta (sob demanda, na interface)
  6. Comparacao entre apolices       -> AgenteComparacao (deterministica)
  7. Apresentacao dos resultados     -> AgenteRelatorio + interface Streamlit

Devolve um ResultadoProcessamento com tudo que aconteceu, incluindo o log passo
a passo usado para auditar a execucao.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src import config
from src.agentes.armazenamento import AgenteArmazenamento
from src.agentes.comparacao import AgenteComparacao
from src.agentes.estruturacao import AgenteEstruturacao
from src.agentes.extracao import AgenteExtracao, TextoExtraido
from src.agentes.recepcao import AgenteRecepcao
from src.agentes.relatorio import AgenteRelatorio
from src.models import ApoliceEstruturada, Comparativo


@dataclass
class ResultadoProcessamento:
    executado_em: datetime
    modo_ia: str
    fichas: list[ApoliceEstruturada] = field(default_factory=list)
    textos: list[TextoExtraido] = field(default_factory=list)
    recusados: list[tuple[str, str]] = field(default_factory=list)
    ids_banco: list[int] = field(default_factory=list)
    comparativo: Comparativo | None = None
    log: list[str] = field(default_factory=list)


def processar(
    caminhos: list[str | Path],
    usar_llm: bool = True,
    permitir_ocr: bool = True,
    comparar: bool = True,
    persistir: bool = True,
) -> ResultadoProcessamento:
    registros: list[str] = []

    def log(mensagem: str) -> None:
        carimbo = datetime.now(tz=config.FUSO).strftime("%H:%M:%S")
        registros.append(f"{carimbo} {mensagem}")

    log("[Orquestrador] inicio do processamento")

    recepcao = AgenteRecepcao(logger=log)
    extracao = AgenteExtracao(logger=log, permitir_ocr=permitir_ocr)
    estruturacao = AgenteEstruturacao(usar_llm=usar_llm, logger=log)
    armazenamento = AgenteArmazenamento(logger=log)
    comparacao = AgenteComparacao(logger=log)
    relatorio = AgenteRelatorio(usar_llm=usar_llm, logger=log)

    documentos = recepcao.executar(caminhos)
    textos = extracao.executar(documentos)
    fichas = estruturacao.executar(textos)

    ids: list[int] = []
    if persistir and fichas:
        ids = armazenamento.executar(fichas)

    comparativo = None
    if comparar and len(fichas) >= 2:
        comparativo = comparacao.executar(fichas)
        comparativo = relatorio.executar(comparativo)
    elif comparar:
        log("[Orquestrador] comparacao exige pelo menos duas apolices processadas")

    log("[Orquestrador] processamento concluido")

    return ResultadoProcessamento(
        executado_em=datetime.now(tz=config.FUSO),
        modo_ia=estruturacao.modo,
        fichas=fichas,
        textos=textos,
        recusados=recepcao.recusados,
        ids_banco=ids,
        comparativo=comparativo,
        log=registros,
    )


def comparar_fichas(
    fichas: list[ApoliceEstruturada], usar_llm: bool = True
) -> Comparativo:
    """Compara fichas ja existentes (por exemplo, recuperadas do banco)."""
    comparativo = AgenteComparacao().executar(fichas)
    return AgenteRelatorio(usar_llm=usar_llm).executar(comparativo)
