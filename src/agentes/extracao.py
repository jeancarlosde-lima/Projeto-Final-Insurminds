"""
Agente 2 - Extracao de conteudo.

Responsabilidade unica: transformar o documento (PDF ou imagem) em texto bruto.

Estrategia em dois caminhos, decidida automaticamente por pagina:

  1. Texto nativo - para PDFs gerados digitalmente, o texto e lido diretamente
     com pdfplumber. E rapido, fiel e nao custa nada.
  2. OCR - quando a pagina tem pouco ou nenhum texto recuperavel (documento
     escaneado, foto da apolice), a pagina e rasterizada e passa por Tesseract
     em portugues.

A decisao por pagina importa: apolices reais frequentemente misturam paginas
digitais com anexos escaneados. O metodo efetivamente usado fica registrado e
e exibido ao usuario, porque texto vindo de OCR tem qualidade inferior e isso
precisa ser visivel na auditoria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src import config
from src.agentes.recepcao import DocumentoRecebido


@dataclass
class TextoExtraido:
    nome: str
    texto: str
    paginas: int
    metodo: str  # "texto nativo" | "OCR" | "texto nativo + OCR"
    paginas_ocr: list[int] = field(default_factory=list)
    erro: str | None = None

    @property
    def caracteres(self) -> int:
        return len(self.texto)


class AgenteExtracao:
    nome = "AgenteExtracao"

    def __init__(self, logger=None, permitir_ocr: bool = True) -> None:
        self.log = logger or (lambda _m: None)
        self.permitir_ocr = permitir_ocr

    # -- OCR ---------------------------------------------------------------
    def _ocr_disponivel(self) -> bool:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _ocr_imagem(self, imagem) -> str:
        import pytesseract

        try:
            return pytesseract.image_to_string(imagem, lang=config.OCR_IDIOMA)
        except pytesseract.pytesseract.TesseractError:
            # pacote de idioma nao instalado: tenta o idioma padrao do Tesseract
            self.log(
                f"[{self.nome}] idioma '{config.OCR_IDIOMA}' indisponivel no Tesseract, "
                f"usando o idioma padrao (instale tesseract-ocr-por para melhor qualidade)"
            )
            return pytesseract.image_to_string(imagem)

    def _ocr_paginas(self, caminho: Path, numeros: list[int]) -> dict[int, str]:
        from pdf2image import convert_from_path

        resultado: dict[int, str] = {}
        for numero in numeros:
            try:
                imagens = convert_from_path(
                    str(caminho), dpi=config.OCR_DPI, first_page=numero, last_page=numero
                )
                if imagens:
                    resultado[numero] = self._ocr_imagem(imagens[0])
            except Exception as erro:
                self.log(f"[{self.nome}] falha de OCR na pagina {numero}: {erro}")
        return resultado

    # -- Execucao ----------------------------------------------------------
    def executar(self, documentos: list[DocumentoRecebido]) -> list[TextoExtraido]:
        resultados = []
        for documento in documentos:
            if documento.tipo == "imagem":
                resultados.append(self._extrair_imagem(documento))
            else:
                resultados.append(self._extrair_pdf(documento))
        return resultados

    def _extrair_imagem(self, documento: DocumentoRecebido) -> TextoExtraido:
        if not (self.permitir_ocr and self._ocr_disponivel()):
            return TextoExtraido(
                nome=documento.nome,
                texto="",
                paginas=1,
                metodo="OCR indisponivel",
                erro="Tesseract nao encontrado - instale o OCR para ler documentos em imagem",
            )
        from PIL import Image

        texto = self._ocr_imagem(Image.open(documento.caminho))
        self.log(f"[{self.nome}] {documento.nome}: OCR de imagem, {len(texto)} caracteres")
        return TextoExtraido(
            nome=documento.nome, texto=texto, paginas=1, metodo="OCR", paginas_ocr=[1]
        )

    def _extrair_pdf(self, documento: DocumentoRecebido) -> TextoExtraido:
        import pdfplumber

        partes: dict[int, str] = {}
        pendentes: list[int] = []

        try:
            with pdfplumber.open(documento.caminho) as pdf:
                total = len(pdf.pages)
                for indice, pagina in enumerate(pdf.pages, start=1):
                    texto = (pagina.extract_text() or "").strip()
                    if len(texto) >= config.MIN_CARACTERES_PAGINA:
                        partes[indice] = texto
                    else:
                        pendentes.append(indice)
        except Exception as erro:
            return TextoExtraido(
                nome=documento.nome, texto="", paginas=0, metodo="falha", erro=str(erro)
            )

        paginas_ocr: list[int] = []
        if pendentes:
            if self.permitir_ocr and self._ocr_disponivel():
                self.log(
                    f"[{self.nome}] {documento.nome}: {len(pendentes)} pagina(s) sem texto "
                    f"nativo, acionando OCR"
                )
                recuperadas = self._ocr_paginas(documento.caminho, pendentes)
                partes.update(recuperadas)
                paginas_ocr = sorted(recuperadas)
            else:
                self.log(
                    f"[{self.nome}] {documento.nome}: {len(pendentes)} pagina(s) sem texto e "
                    f"sem OCR disponivel"
                )

        texto = "\n\n".join(partes[n] for n in sorted(partes))
        if paginas_ocr and len(paginas_ocr) < total:
            metodo = "texto nativo + OCR"
        elif paginas_ocr:
            metodo = "OCR"
        else:
            metodo = "texto nativo"

        self.log(
            f"[{self.nome}] {documento.nome}: {total} pagina(s), {len(texto)} caracteres "
            f"({metodo})"
        )
        return TextoExtraido(
            nome=documento.nome,
            texto=texto,
            paginas=total,
            metodo=metodo,
            paginas_ocr=paginas_ocr,
            erro=None if texto else "nenhum texto recuperado",
        )
