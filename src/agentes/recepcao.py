"""
Agente 1 - Recepcao de documentos.

Responsabilidade unica: receber os arquivos enviados pelo usuario, validar
formato e integridade, normalizar a entrada e devolver uma lista de documentos
aptos a seguir no fluxo.

Aceita PDF (nativo ou digitalizado) e imagens (PNG/JPG), conforme o requisito
do desafio. Qualquer arquivo recusado e reportado com o motivo, em vez de
quebrar o processamento dos demais.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FORMATOS_ACEITOS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
TAMANHO_MAXIMO_MB = 30


@dataclass
class DocumentoRecebido:
    caminho: Path
    nome: str
    extensao: str
    tamanho_kb: float
    tipo: str  # "pdf" | "imagem"


class AgenteRecepcao:
    nome = "AgenteRecepcao"

    def __init__(self, logger=None) -> None:
        self.log = logger or (lambda _m: None)
        self.recusados: list[tuple[str, str]] = []

    def executar(self, caminhos: list[str | Path]) -> list[DocumentoRecebido]:
        aceitos: list[DocumentoRecebido] = []
        self.recusados = []

        for item in caminhos:
            caminho = Path(item)
            if not caminho.exists():
                self._recusar(caminho.name, "arquivo nao encontrado")
                continue

            extensao = caminho.suffix.lower()
            if extensao not in FORMATOS_ACEITOS:
                self._recusar(caminho.name, f"formato {extensao or 'desconhecido'} nao suportado")
                continue

            tamanho_kb = caminho.stat().st_size / 1024
            if tamanho_kb == 0:
                self._recusar(caminho.name, "arquivo vazio")
                continue
            if tamanho_kb / 1024 > TAMANHO_MAXIMO_MB:
                self._recusar(caminho.name, f"arquivo acima de {TAMANHO_MAXIMO_MB} MB")
                continue

            aceitos.append(
                DocumentoRecebido(
                    caminho=caminho,
                    nome=caminho.name,
                    extensao=extensao,
                    tamanho_kb=round(tamanho_kb, 1),
                    tipo="pdf" if extensao == ".pdf" else "imagem",
                )
            )
            self.log(f"[{self.nome}] aceito: {caminho.name} ({tamanho_kb:.0f} KB)")

        for nome, motivo in self.recusados:
            self.log(f"[{self.nome}] RECUSADO: {nome} - {motivo}")

        self.log(f"[{self.nome}] {len(aceitos)} documento(s) apto(s), {len(self.recusados)} recusado(s)")
        return aceitos

    def _recusar(self, nome: str, motivo: str) -> None:
        self.recusados.append((nome, motivo))
