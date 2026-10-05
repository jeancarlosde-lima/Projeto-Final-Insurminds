"""
Modelos de dados do Projeto Final.

A ficha estruturada da apolice (ApoliceEstruturada) e o coracao da solucao: ela
define QUAIS informacoes precisam ser extraidas de um documento juridico longo
para que duas apolices se tornem comparaveis campo a campo.

Cada campo extraido carrega uma evidencia - o trecho do documento original que
sustenta o valor. Isso permite que o usuario audite a extracao em vez de
confiar cegamente no modelo.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BaseCobertura(str, Enum):
    CLAIMS_MADE = "claims made"
    OCORRENCIA = "ocorrencia"
    NAO_IDENTIFICADO = "nao identificado"


class Cobertura(BaseModel):
    nome: str
    incluida: bool = True
    limite: str | None = None
    observacao: str | None = None


class ApoliceEstruturada(BaseModel):
    """Ficha padronizada de uma apolice D&O."""

    # identificacao
    arquivo: str
    seguradora: str | None = None
    produto: str | None = None
    numero_apolice: str | None = None
    processo_susep: str | None = None
    tomador: str | None = None

    # vigencia e valores
    vigencia_inicio: str | None = None
    vigencia_fim: str | None = None
    moeda: str | None = None
    limite_maximo_indenizacao: float | None = None
    premio_total: float | None = None
    franquia: float | None = None
    franquia_descricao: str | None = None

    # estrutura da cobertura
    base_cobertura: BaseCobertura = BaseCobertura.NAO_IDENTIFICADO
    data_retroatividade: str | None = None
    prazo_complementar: str | None = None
    prazo_suplementar: str | None = None
    ambito_geografico: str | None = None
    jurisdicao: str | None = None

    # clausulas
    coberturas: list[Cobertura] = Field(default_factory=list)
    sublimites: list[str] = Field(default_factory=list)
    exclusoes: list[str] = Field(default_factory=list)
    clausulas_especiais: list[str] = Field(default_factory=list)

    # rastreabilidade
    evidencias: dict[str, str] = Field(default_factory=dict)
    extraido_por: str = ""
    extraido_em: datetime | None = None
    paginas: int = 0
    metodo_leitura: str = ""

    @property
    def rotulo(self) -> str:
        partes = [p for p in [self.seguradora, self.numero_apolice] if p]
        return " - ".join(partes) if partes else self.arquivo

    def nomes_coberturas(self) -> set[str]:
        return {c.nome.strip().lower() for c in self.coberturas if c.incluida}


class LinhaComparativo(BaseModel):
    """Uma linha do quadro comparativo entre duas ou mais apolices."""

    campo: str
    rotulo: str
    valores: dict[str, str]
    divergente: bool
    impacto: str = "neutro"  # favorece:<rotulo> | neutro | atencao
    comentario: str = ""


class Comparativo(BaseModel):
    gerado_em: datetime
    apolices: list[str]
    linhas: list[LinhaComparativo] = Field(default_factory=list)
    coberturas_exclusivas: dict[str, list[str]] = Field(default_factory=dict)
    exclusoes_exclusivas: dict[str, list[str]] = Field(default_factory=dict)
    sumario_executivo: str = ""
    gerado_sumario_por: str = ""

    @property
    def divergencias(self) -> list[LinhaComparativo]:
        return [linha for linha in self.linhas if linha.divergente]


class RespostaConsulta(BaseModel):
    pergunta: str
    resposta: str
    fontes: list[str] = Field(default_factory=list)
    gerado_por: str = ""
