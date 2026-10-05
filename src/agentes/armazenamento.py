"""
Agente 4 - Armazenamento estruturado.

Responsabilidade unica: persistir as fichas extraidas em um banco relacional
(SQLite) e devolve-las quando solicitado.

Por que SQLite e nao um arquivo JSON: o requisito pede armazenamento
estruturado, e a persistencia relacional da a solucao duas propriedades que o
arquivo nao da - consulta por campo (quais apolices tem LMI acima de X) e
historico, ja que a mesma apolice reprocessada vira uma nova versao em vez de
sobrescrever a anterior. O banco e um arquivo unico, sem servidor, o que mantem
o protoipo facil de executar.

Modelo: uma tabela de apolices com os campos escalares (consultaveis em SQL) e
as listas (coberturas, exclusoes, sublimites, evidencias) serializadas em JSON
na mesma linha. Para o volume de um MVP isso e suficiente e evita cinco tabelas
de apoio que nao agregariam nada a demonstracao.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from src import config
from src.models import ApoliceEstruturada

DDL = """
CREATE TABLE IF NOT EXISTS apolices (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    arquivo                   TEXT NOT NULL,
    seguradora                TEXT,
    produto                   TEXT,
    numero_apolice            TEXT,
    processo_susep            TEXT,
    tomador                   TEXT,
    vigencia_inicio           TEXT,
    vigencia_fim              TEXT,
    moeda                     TEXT,
    limite_maximo_indenizacao REAL,
    premio_total              REAL,
    franquia                  REAL,
    franquia_descricao        TEXT,
    base_cobertura            TEXT,
    data_retroatividade       TEXT,
    prazo_complementar        TEXT,
    prazo_suplementar         TEXT,
    ambito_geografico         TEXT,
    jurisdicao                TEXT,
    coberturas_json           TEXT,
    sublimites_json           TEXT,
    exclusoes_json            TEXT,
    clausulas_json            TEXT,
    evidencias_json           TEXT,
    extraido_por              TEXT,
    metodo_leitura            TEXT,
    paginas                   INTEGER,
    criado_em                 TEXT
);
CREATE INDEX IF NOT EXISTS idx_apolices_arquivo ON apolices(arquivo);
"""


class AgenteArmazenamento:
    nome = "AgenteArmazenamento"

    def __init__(self, caminho: Path | None = None, logger=None) -> None:
        self.caminho = caminho or config.BANCO
        self.log = logger or (lambda _m: None)
        self._criar_schema()

    def _conectar(self) -> sqlite3.Connection:
        conexao = sqlite3.connect(self.caminho)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_schema(self) -> None:
        with self._conectar() as conexao:
            conexao.executescript(DDL)

    # -- Escrita -----------------------------------------------------------
    def executar(self, fichas: list[ApoliceEstruturada]) -> list[int]:
        ids = []
        with self._conectar() as conexao:
            for ficha in fichas:
                cursor = conexao.execute(
                    """
                    INSERT INTO apolices (
                        arquivo, seguradora, produto, numero_apolice, processo_susep, tomador,
                        vigencia_inicio, vigencia_fim, moeda, limite_maximo_indenizacao,
                        premio_total, franquia, franquia_descricao, base_cobertura,
                        data_retroatividade, prazo_complementar, prazo_suplementar,
                        ambito_geografico, jurisdicao, coberturas_json, sublimites_json,
                        exclusoes_json, clausulas_json, evidencias_json, extraido_por,
                        metodo_leitura, paginas, criado_em
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        ficha.arquivo,
                        ficha.seguradora,
                        ficha.produto,
                        ficha.numero_apolice,
                        ficha.processo_susep,
                        ficha.tomador,
                        ficha.vigencia_inicio,
                        ficha.vigencia_fim,
                        ficha.moeda,
                        ficha.limite_maximo_indenizacao,
                        ficha.premio_total,
                        ficha.franquia,
                        ficha.franquia_descricao,
                        ficha.base_cobertura.value,
                        ficha.data_retroatividade,
                        ficha.prazo_complementar,
                        ficha.prazo_suplementar,
                        ficha.ambito_geografico,
                        ficha.jurisdicao,
                        json.dumps([c.model_dump() for c in ficha.coberturas], ensure_ascii=False),
                        json.dumps(ficha.sublimites, ensure_ascii=False),
                        json.dumps(ficha.exclusoes, ensure_ascii=False),
                        json.dumps(ficha.clausulas_especiais, ensure_ascii=False),
                        json.dumps(ficha.evidencias, ensure_ascii=False),
                        ficha.extraido_por,
                        ficha.metodo_leitura,
                        ficha.paginas,
                        datetime.now(tz=config.FUSO).isoformat(),
                    ),
                )
                ids.append(cursor.lastrowid)
        self.log(f"[{self.nome}] {len(ids)} ficha(s) gravada(s) em {self.caminho.name}")
        return ids

    # -- Leitura -----------------------------------------------------------
    @staticmethod
    def _para_ficha(linha: sqlite3.Row) -> ApoliceEstruturada:
        from src.models import Cobertura

        return ApoliceEstruturada(
            arquivo=linha["arquivo"],
            seguradora=linha["seguradora"],
            produto=linha["produto"],
            numero_apolice=linha["numero_apolice"],
            processo_susep=linha["processo_susep"],
            tomador=linha["tomador"],
            vigencia_inicio=linha["vigencia_inicio"],
            vigencia_fim=linha["vigencia_fim"],
            moeda=linha["moeda"],
            limite_maximo_indenizacao=linha["limite_maximo_indenizacao"],
            premio_total=linha["premio_total"],
            franquia=linha["franquia"],
            franquia_descricao=linha["franquia_descricao"],
            base_cobertura=linha["base_cobertura"] or "nao identificado",
            data_retroatividade=linha["data_retroatividade"],
            prazo_complementar=linha["prazo_complementar"],
            prazo_suplementar=linha["prazo_suplementar"],
            ambito_geografico=linha["ambito_geografico"],
            jurisdicao=linha["jurisdicao"],
            coberturas=[Cobertura(**c) for c in json.loads(linha["coberturas_json"] or "[]")],
            sublimites=json.loads(linha["sublimites_json"] or "[]"),
            exclusoes=json.loads(linha["exclusoes_json"] or "[]"),
            clausulas_especiais=json.loads(linha["clausulas_json"] or "[]"),
            evidencias=json.loads(linha["evidencias_json"] or "{}"),
            extraido_por=linha["extraido_por"] or "",
            paginas=linha["paginas"] or 0,
            metodo_leitura=linha["metodo_leitura"] or "",
        )

    def listar(self, limite: int = 50) -> list[tuple[int, ApoliceEstruturada]]:
        with self._conectar() as conexao:
            linhas = conexao.execute(
                "SELECT * FROM apolices ORDER BY id DESC LIMIT ?", (limite,)
            ).fetchall()
        return [(linha["id"], self._para_ficha(linha)) for linha in linhas]

    def obter(self, identificadores: list[int]) -> list[ApoliceEstruturada]:
        if not identificadores:
            return []
        marcadores = ",".join("?" for _ in identificadores)
        with self._conectar() as conexao:
            linhas = conexao.execute(
                f"SELECT * FROM apolices WHERE id IN ({marcadores}) ORDER BY id",
                identificadores,
            ).fetchall()
        return [self._para_ficha(linha) for linha in linhas]

    def consultar_sql(self, sql: str, parametros: tuple = ()) -> list[dict]:
        """Consulta livre somente leitura, usada pela interface de pesquisa."""
        if not sql.strip().lower().startswith("select"):
            raise ValueError("apenas consultas SELECT sao permitidas")
        with self._conectar() as conexao:
            linhas = conexao.execute(sql, parametros).fetchall()
        return [dict(linha) for linha in linhas]
