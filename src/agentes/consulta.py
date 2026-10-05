"""
Agente 7 - Consulta em linguagem natural.

Responsabilidade unica: responder perguntas do usuario sobre as apolices ja
processadas ("qual tem a maior retroatividade?", "alguma exclui danos morais?").

O contexto enviado ao modelo nao e o PDF original, e sim as FICHAS
ESTRUTURADAS. Essa escolha resolve tres problemas de uma vez: cabe no prompt
sem fragmentar o documento, mantem a resposta ancorada no que foi efetivamente
extraido e auditado, e permite citar a apolice de origem de cada afirmacao.

Sem chave de API, o agente responde por busca textual simples nas fichas - o
suficiente para demonstrar o caminho, embora sem interpretacao da pergunta.
"""

from __future__ import annotations

from src import config
from src.models import ApoliceEstruturada, RespostaConsulta

INSTRUCOES = """Voce responde perguntas sobre apolices de seguro D&O ja processadas por um sistema de
extracao. Recebe as fichas estruturadas dessas apolices e a pergunta do usuario.

Regras obrigatorias:
1. Responda exclusivamente com base nas fichas fornecidas. Se a informacao nao estiver ali, diga
   que o campo nao foi localizado na extracao e sugira conferir o documento original.
2. Sempre identifique de qual apolice vem cada informacao.
3. Nao emita parecer juridico nem opine sobre qual apolice contratar; apresente os fatos e, quando
   fizer sentido, o trade-off.
4. Portugues do Brasil, resposta direta, no maximo 200 palavras. Sem markdown.
"""


def ficha_para_texto(ficha: ApoliceEstruturada) -> str:
    linhas = [
        f"APOLICE: {ficha.rotulo} (arquivo {ficha.arquivo})",
        f"- Produto: {ficha.produto}",
        f"- Tomador: {ficha.tomador}",
        f"- Vigencia: {ficha.vigencia_inicio} a {ficha.vigencia_fim}",
        f"- Limite maximo de indenizacao: {ficha.limite_maximo_indenizacao}",
        f"- Premio total: {ficha.premio_total}",
        f"- Franquia: {ficha.franquia} ({ficha.franquia_descricao})",
        f"- Base de cobertura: {ficha.base_cobertura.value}",
        f"- Retroatividade: {ficha.data_retroatividade}",
        f"- Prazo complementar: {ficha.prazo_complementar}",
        f"- Prazo suplementar: {ficha.prazo_suplementar}",
        f"- Ambito geografico: {ficha.ambito_geografico}",
        f"- Jurisdicao: {ficha.jurisdicao}",
        f"- Coberturas: {'; '.join(c.nome for c in ficha.coberturas) or 'nao localizadas'}",
        f"- Sublimites: {'; '.join(ficha.sublimites) or 'nao localizados'}",
        f"- Exclusoes: {'; '.join(ficha.exclusoes) or 'nao localizadas'}",
        f"- Clausulas especiais: {'; '.join(ficha.clausulas_especiais) or 'nao localizadas'}",
    ]
    return "\n".join(linhas)


class AgenteConsulta:
    nome = "AgenteConsulta"

    def __init__(self, usar_llm: bool = True, logger=None) -> None:
        self.log = logger or (lambda _m: None)
        self.cadeia = None
        self.modo = "busca textual"
        if usar_llm and config.GOOGLE_API_KEY:
            self.cadeia = self._montar_cadeia()

    def _montar_cadeia(self):
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=config.MODELO_LLM,
                temperature=0.2,
                google_api_key=config.GOOGLE_API_KEY,
            )
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", INSTRUCOES),
                    ("human", "Fichas:\n{fichas}\n\nPergunta: {pergunta}"),
                ]
            )
            self.modo = f"IA Generativa ({config.MODELO_LLM})"
            return prompt | llm | StrOutputParser()
        except Exception as erro:
            self.log(f"[{self.nome}] falha ao iniciar o LLM ({erro}) - busca textual")
            return None

    def executar(
        self, pergunta: str, fichas: list[ApoliceEstruturada]
    ) -> RespostaConsulta:
        if not fichas:
            return RespostaConsulta(
                pergunta=pergunta,
                resposta="Nenhuma apolice processada ainda. Envie os documentos antes de consultar.",
                gerado_por="sistema",
            )

        contexto = "\n\n".join(ficha_para_texto(f) for f in fichas)
        fontes = [f.rotulo for f in fichas]

        if self.cadeia is not None:
            try:
                resposta = self.cadeia.invoke({"fichas": contexto, "pergunta": pergunta})
                if resposta and resposta.strip():
                    return RespostaConsulta(
                        pergunta=pergunta,
                        resposta=resposta.strip(),
                        fontes=fontes,
                        gerado_por=self.modo,
                    )
            except Exception as erro:
                self.log(f"[{self.nome}] erro no modelo ({erro}) - busca textual")

        return self._busca_textual(pergunta, fichas)

    @staticmethod
    def _busca_textual(pergunta: str, fichas: list[ApoliceEstruturada]) -> RespostaConsulta:
        termos = [t for t in pergunta.lower().split() if len(t) > 4]
        achados: list[str] = []
        for ficha in fichas:
            texto = ficha_para_texto(ficha)
            for linha in texto.splitlines():
                if any(termo in linha.lower() for termo in termos):
                    achados.append(f"{ficha.rotulo}: {linha.lstrip('- ')}")
        if not achados:
            resposta = (
                "Nao encontrei esse termo nas fichas extraidas. Sem o modelo de linguagem "
                "configurado, a consulta se limita a busca textual nos campos estruturados."
            )
        else:
            resposta = "\n".join(dict.fromkeys(achados[:12]))
        return RespostaConsulta(
            pergunta=pergunta,
            resposta=resposta,
            fontes=[f.rotulo for f in fichas],
            gerado_por="busca textual (sem LLM)",
        )
