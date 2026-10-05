"""
Agente 3 - Identificacao de clausulas e estruturacao.

Responsabilidade unica: transformar o texto corrido da apolice na ficha
padronizada (ApoliceEstruturada), que e o que torna documentos de seguradoras
diferentes comparaveis entre si.

Aqui esta o nucleo de IA Generativa da solucao. O modelo recebe o texto da
apolice e um schema explicito, e devolve JSON. Duas decisoes importantes:

  1. Saida estruturada, nao texto livre. O prompt exige JSON puro aderente ao
     schema; a resposta e validada com Pydantic antes de entrar no sistema.
     Se o modelo devolver algo fora do contrato, o erro aparece na validacao -
     nao vira dado silenciosamente errado no banco.
  2. Evidencia obrigatoria. Para os campos criticos, o modelo precisa devolver
     tambem o trecho do documento que sustenta o valor. O usuario audita a
     extracao sem reler a apolice inteira, e a alucinacao fica visivel.

Quando nao ha chave de API configurada, entra um extrator heuristico baseado em
rotulos e secoes. Ele e menos flexivel - funciona bem em documentos rotulados e
mal em texto corrido juridico -, mas mantem a solucao demonstravel offline. O
metodo usado fica registrado em cada ficha.
"""

from __future__ import annotations

import json
import re
from datetime import datetime

from src import config
from src.agentes.extracao import TextoExtraido
from src.models import ApoliceEstruturada, BaseCobertura, Cobertura

SCHEMA = """{
  "seguradora": "string|null",
  "produto": "string|null",
  "numero_apolice": "string|null",
  "processo_susep": "string|null",
  "tomador": "string|null",
  "vigencia_inicio": "DD/MM/AAAA|null",
  "vigencia_fim": "DD/MM/AAAA|null",
  "moeda": "BRL|USD|EUR|null",
  "limite_maximo_indenizacao": "numero sem simbolo nem separador de milhar, ex 20000000.00|null",
  "premio_total": "numero|null",
  "franquia": "numero|null",
  "franquia_descricao": "string|null",
  "base_cobertura": "claims made|ocorrencia|nao identificado",
  "data_retroatividade": "string|null",
  "prazo_complementar": "string|null",
  "prazo_suplementar": "string|null",
  "ambito_geografico": "string|null",
  "jurisdicao": "string|null",
  "coberturas": [{"nome": "string", "incluida": true, "limite": "string|null", "observacao": "string|null"}],
  "sublimites": ["string"],
  "exclusoes": ["string"],
  "clausulas_especiais": ["string"],
  "evidencias": {"campo": "trecho literal do documento que sustenta o valor"}
}"""

INSTRUCOES = """Voce e um analista tecnico de seguros especializado em apolices de Responsabilidade Civil
de Administradores (D&O) do mercado brasileiro. Sua funcao e ler o documento fornecido e devolver
uma ficha estruturada em JSON.

Regras obrigatorias:
1. Devolva APENAS o objeto JSON, sem markdown, sem cercas de codigo, sem comentarios.
2. Use exatamente as chaves do schema. Campo que nao constar no documento recebe null (ou lista vazia).
3. NUNCA invente valores. Se o documento nao informa a franquia, devolva null - jamais um valor tipico de mercado.
4. Valores monetarios vao como numero puro: "R$ 20.000.000,00" vira 20000000.00.
5. Em "evidencias", inclua para cada campo preenchido o trecho literal (ate 200 caracteres) do
   documento que sustenta aquele valor. Use as mesmas chaves do schema.
6. Em "coberturas", liste o que o documento declara como coberto; marque "incluida": false apenas
   quando o documento explicitar que determinada cobertura nao foi contratada.
7. Nao confunda sublimite com limite maximo de indenizacao: o LMI e o teto agregado da apolice.
"""


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------
def _para_numero(texto: str | float | None) -> float | None:
    if texto is None:
        return None
    if isinstance(texto, (int, float)):
        return float(texto)
    bruto = str(texto)
    # pega o primeiro valor monetario da frase: "R$ 150.000,00 por reclamacao..." -> 150000.0
    achado = re.search(r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+,\d{1,2}|\d+(?:\.\d+)?", bruto)
    if not achado:
        return None
    limpo = achado.group(0)
    if "," in limpo and "." in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    elif "," in limpo:
        limpo = limpo.replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return None


def _limpar_json(bruto: str) -> str:
    texto = bruto.strip()
    texto = re.sub(r"^```(?:json)?", "", texto).strip()
    texto = re.sub(r"```$", "", texto).strip()
    inicio, fim = texto.find("{"), texto.rfind("}")
    return texto[inicio : fim + 1] if inicio >= 0 and fim > inicio else texto


class AgenteEstruturacao:
    nome = "AgenteEstruturacao"

    def __init__(self, usar_llm: bool = True, logger=None) -> None:
        self.log = logger or (lambda _m: None)
        self.cadeia = None
        self.modo = "heuristico (sem LLM)"
        if usar_llm and config.GOOGLE_API_KEY:
            self.cadeia = self._montar_cadeia()
        elif usar_llm:
            self.log(f"[{self.nome}] GOOGLE_API_KEY ausente - extracao heuristica")

    def _montar_cadeia(self):
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=config.MODELO_LLM,
                temperature=config.TEMPERATURA_LLM,
                google_api_key=config.GOOGLE_API_KEY,
                max_output_tokens=config.MAX_TOKENS_SAIDA,
            )
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", INSTRUCOES),
                    (
                        "human",
                        "Schema esperado:\n{schema}\n\n"
                        "Documento (arquivo {arquivo}):\n<<<\n{documento}\n>>>\n\n"
                        "Devolva o JSON da ficha estruturada.",
                    ),
                ]
            )
            self.modo = f"IA Generativa ({config.MODELO_LLM} via LangChain)"
            self.log(f"[{self.nome}] cadeia LangChain + {config.MODELO_LLM} inicializada")
            return prompt | llm | StrOutputParser()
        except Exception as erro:
            self.log(f"[{self.nome}] falha ao iniciar o LLM ({erro}) - extracao heuristica")
            return None

    # -- Execucao ----------------------------------------------------------
    def executar(self, textos: list[TextoExtraido]) -> list[ApoliceEstruturada]:
        fichas = []
        for item in textos:
            if not item.texto.strip():
                self.log(f"[{self.nome}] {item.nome}: sem texto para estruturar")
                continue
            ficha = self._estruturar(item)
            fichas.append(ficha)
            self.log(
                f"[{self.nome}] {item.nome}: {len(ficha.coberturas)} cobertura(s), "
                f"{len(ficha.exclusoes)} exclusao(oes), LMI={ficha.limite_maximo_indenizacao} "
                f"({ficha.extraido_por})"
            )
        return fichas

    def _estruturar(self, item: TextoExtraido) -> ApoliceEstruturada:
        if self.cadeia is not None:
            try:
                bruto = self.cadeia.invoke(
                    {
                        "schema": SCHEMA,
                        "arquivo": item.nome,
                        "documento": item.texto[: config.MAX_CARACTERES_PROMPT],
                    }
                )
                dados = json.loads(_limpar_json(bruto))
                ficha = self._montar_ficha(dados, item, self.modo)
                return ficha
            except json.JSONDecodeError as erro:
                self.log(f"[{self.nome}] {item.nome}: JSON invalido do modelo ({erro}) - heuristica")
            except Exception as erro:
                self.log(f"[{self.nome}] {item.nome}: erro no modelo ({erro}) - heuristica")
        return self._heuristica(item)

    def _montar_ficha(self, dados: dict, item: TextoExtraido, origem: str) -> ApoliceEstruturada:
        coberturas = []
        for bruta in dados.get("coberturas") or []:
            if isinstance(bruta, str):
                coberturas.append(Cobertura(nome=bruta))
            elif isinstance(bruta, dict) and bruta.get("nome"):
                coberturas.append(
                    Cobertura(
                        nome=str(bruta["nome"]),
                        incluida=bool(bruta.get("incluida", True)),
                        limite=bruta.get("limite"),
                        observacao=bruta.get("observacao"),
                    )
                )

        base = str(dados.get("base_cobertura") or "").lower()
        if "claims" in base:
            base_cobertura = BaseCobertura.CLAIMS_MADE
        elif "ocorr" in base:
            base_cobertura = BaseCobertura.OCORRENCIA
        else:
            base_cobertura = BaseCobertura.NAO_IDENTIFICADO

        return ApoliceEstruturada(
            arquivo=item.nome,
            seguradora=dados.get("seguradora"),
            produto=dados.get("produto"),
            numero_apolice=dados.get("numero_apolice"),
            processo_susep=dados.get("processo_susep"),
            tomador=dados.get("tomador"),
            vigencia_inicio=dados.get("vigencia_inicio"),
            vigencia_fim=dados.get("vigencia_fim"),
            moeda=dados.get("moeda"),
            limite_maximo_indenizacao=_para_numero(dados.get("limite_maximo_indenizacao")),
            premio_total=_para_numero(dados.get("premio_total")),
            franquia=_para_numero(dados.get("franquia")),
            franquia_descricao=dados.get("franquia_descricao"),
            base_cobertura=base_cobertura,
            data_retroatividade=dados.get("data_retroatividade"),
            prazo_complementar=dados.get("prazo_complementar"),
            prazo_suplementar=dados.get("prazo_suplementar"),
            ambito_geografico=dados.get("ambito_geografico"),
            jurisdicao=dados.get("jurisdicao"),
            coberturas=coberturas,
            sublimites=[str(s) for s in (dados.get("sublimites") or [])],
            exclusoes=[str(s) for s in (dados.get("exclusoes") or [])],
            clausulas_especiais=[str(s) for s in (dados.get("clausulas_especiais") or [])],
            evidencias={k: str(v)[:300] for k, v in (dados.get("evidencias") or {}).items()},
            extraido_por=origem,
            extraido_em=datetime.now(tz=config.FUSO),
            paginas=item.paginas,
            metodo_leitura=item.metodo,
        )

    # -- Extrator heuristico ----------------------------------------------
    ROTULOS = {
        "numero_apolice": r"n[uú]mero da ap[oó]lice",
        "processo_susep": r"processo susep",
        "tomador": r"tomador(?:\s*/\s*segurado)?",
        "vigencia_inicio": r"in[ií]cio de vig[eê]ncia",
        "vigencia_fim": r"fim de vig[eê]ncia",
        "moeda": r"moeda",
        "limite_maximo_indenizacao": r"limite m[aá]ximo de indeniza[cç][aã]o(?:\s*\(lmi\))?",
        "premio_total": r"pr[eê]mio total",
        "franquia": r"franquia",
        "data_retroatividade": r"data de retroatividade",
        "prazo_complementar": r"prazo complementar",
        "prazo_suplementar": r"prazo suplementar",
        "ambito_geografico": r"[aâ]mbito geogr[aá]fico",
        "jurisdicao": r"jurisdi[cç][aã]o",
    }

    SECOES = {
        "coberturas": r"coberturas?(?:\s+contratadas?)?",
        "sublimites": r"sublimites?",
        "exclusoes": r"(?:riscos\s+)?exclu[sií][oõ]es|riscos excluidos|riscos exclu[ií]dos",
        "clausulas_especiais": r"cl[aá]usulas?\s+(?:particulares|especiais)",
    }

    def _heuristica(self, item: TextoExtraido) -> ApoliceEstruturada:
        texto = item.texto
        linhas = [linha.strip() for linha in texto.splitlines()]
        dados: dict = {}
        evidencias: dict[str, str] = {}

        for campo, padrao in self.ROTULOS.items():
            achado = re.search(rf"{padrao}\s*:\s*(.+)", texto, flags=re.IGNORECASE)
            if achado:
                valor = achado.group(1).strip()
                dados[campo] = valor
                evidencias[campo] = achado.group(0)[:300]

        if "franquia" in dados:
            dados["franquia_descricao"] = dados["franquia"]

        # seguradora: primeira linha nao vazia costuma ser o cabecalho do documento
        for linha in linhas:
            if linha:
                dados["seguradora"] = linha.title() if linha.isupper() else linha
                break
        for linha in linhas[1:6]:
            if re.search(r"d&o|administradores|respons", linha, flags=re.IGNORECASE):
                dados["produto"] = linha
                break

        if re.search(r"claims made|base de reclama|reclama[cç][oõ]es apresentadas", texto, re.IGNORECASE):
            dados["base_cobertura"] = "claims made"
        elif re.search(r"ocorr[eê]ncia", texto, re.IGNORECASE):
            dados["base_cobertura"] = "ocorrencia"

        for campo, padrao in self.SECOES.items():
            dados[campo] = self._coletar_secao(linhas, padrao)

        dados["coberturas"] = [{"nome": nome} for nome in dados.get("coberturas", [])]
        return self._montar_ficha(dados, item, "heuristica (rotulos e secoes)")

    @staticmethod
    def _coletar_secao(linhas: list[str], padrao: str) -> list[str]:
        """Recorta o bloco da secao e separa seus itens.

        Dois formatos sao tratados: documentos nativos, em que cada item vem
        prefixado por um marcador ("- Custos de defesa..."), e texto vindo de
        OCR, em que o Tesseract costuma descartar os marcadores e separar os
        itens por linha em branco.
        """
        cabecalho = re.compile(rf"^\s*(?:\d+[.)]\s*)?(?:{padrao})\b", re.IGNORECASE)
        outro_cabecalho = re.compile(r"^\s*\d+[.)]\s+\S")
        marcador = re.compile(r"^[-•*\u2022\u00b7]\s*")

        bloco: list[str] = []
        dentro = False
        for linha in linhas:
            if not dentro:
                # cabecalhos sao curtos; evita casar com um paragrafo que cite a palavra
                if len(linha) <= 60 and cabecalho.match(linha):
                    dentro = True
                continue
            if outro_cabecalho.match(linha) and len(linha) <= 60:
                break
            bloco.append(linha)

        if not bloco:
            return []

        itens: list[str] = []
        if any(marcador.match(linha) for linha in bloco):
            for linha in bloco:
                if marcador.match(linha):
                    itens.append(marcador.sub("", linha).strip())
                elif itens and linha and not re.search(r"^\s*\S+\s*:\s*\S", linha):
                    itens[-1] = f"{itens[-1]} {linha}".strip()
        else:
            atual: list[str] = []
            for linha in bloco:
                if linha:
                    atual.append(linha)
                elif atual:
                    itens.append(" ".join(atual).strip())
                    atual = []
            if atual:
                itens.append(" ".join(atual).strip())

        return [item for item in itens if len(item) > 3]
