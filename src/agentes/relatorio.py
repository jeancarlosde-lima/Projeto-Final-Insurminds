"""
Agente 6 - Relatorio comparativo.

Responsabilidade unica: transformar o quadro de divergencias ja apurado em um
texto que um subscritor, corretor ou gestor de riscos consiga ler em dois
minutos.

O modelo recebe apenas o resultado da comparacao - nunca o documento inteiro -
e e instruido a nao introduzir informacao nova. Isso o impede de "lembrar" de
clausulas tipicas de D&O que nao estao nas apolices analisadas.

Sem chave de API, um gerador por template monta o mesmo resumo a partir das
mesmas divergencias. O texto fica mais seco, e o fluxo continua demonstravel.
"""

from __future__ import annotations

from src import config
from src.models import Comparativo

INSTRUCOES = """Voce e um analista tecnico de seguros. Escreve resumos executivos comparando apolices
de Responsabilidade Civil de Administradores (D&O) para apoiar uma decisao de contratacao.

Regras obrigatorias:
1. Use somente as diferencas listadas no contexto. Nao acrescente clausulas, valores, praticas de
   mercado ou conhecimento externo que nao estejam ali.
2. Nao emita parecer juridico nem recomende a contratacao de forma categorica. Aponte trade-offs.
3. Portugues do Brasil, tom tecnico e objetivo, sem adjetivos de marketing.
4. Estrutura: um paragrafo de panorama; depois "Principais diferencas" com ate 5 marcadores
   iniciados por hifen; depois um paragrafo curto "Pontos de atencao" com o que o analista deve
   verificar antes de decidir.
5. Maximo de 300 palavras. Sem markdown, sem titulos em negrito, sem emojis.
"""


class AgenteRelatorio:
    nome = "AgenteRelatorio"

    def __init__(self, usar_llm: bool = True, logger=None) -> None:
        self.log = logger or (lambda _m: None)
        self.cadeia = None
        self.modo = "template"
        if usar_llm and config.GOOGLE_API_KEY:
            self.cadeia = self._montar_cadeia()

    def _montar_cadeia(self):
        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model=config.MODELO_LLM,
                temperature=0.3,
                google_api_key=config.GOOGLE_API_KEY,
            )
            prompt = ChatPromptTemplate.from_messages(
                [("system", INSTRUCOES), ("human", "Contexto da comparacao:\n{contexto}")]
            )
            self.modo = f"IA Generativa ({config.MODELO_LLM})"
            return prompt | llm | StrOutputParser()
        except Exception as erro:
            self.log(f"[{self.nome}] falha ao iniciar o LLM ({erro}) - template")
            return None

    def executar(self, comparativo: Comparativo) -> Comparativo:
        contexto = self._montar_contexto(comparativo)
        if self.cadeia is not None:
            try:
                texto = self.cadeia.invoke({"contexto": contexto})
                if texto and texto.strip():
                    comparativo.sumario_executivo = texto.strip()
                    comparativo.gerado_sumario_por = self.modo
                    self.log(f"[{self.nome}] sumario executivo gerado ({self.modo})")
                    return comparativo
            except Exception as erro:
                self.log(f"[{self.nome}] erro no modelo ({erro}) - template")

        comparativo.sumario_executivo = self._template(comparativo)
        comparativo.gerado_sumario_por = "template (fallback)"
        self.log(f"[{self.nome}] sumario executivo gerado por template")
        return comparativo

    @staticmethod
    def _montar_contexto(comparativo: Comparativo) -> str:
        linhas = [f"Apolices comparadas: {', '.join(comparativo.apolices)}", "", "Divergencias:"]
        for linha in comparativo.divergencias:
            valores = "; ".join(f"{k}: {v}" for k, v in linha.valores.items())
            linhas.append(f"- {linha.rotulo} -> {valores}. {linha.comentario}".strip())
        linhas.append("")
        linhas.append("Coberturas presentes em apenas uma das apolices:")
        for rotulo, itens in comparativo.coberturas_exclusivas.items():
            linhas.append(f"- {rotulo}: {'; '.join(itens) if itens else 'nenhuma'}")
        linhas.append("")
        linhas.append("Exclusoes presentes em apenas uma das apolices:")
        for rotulo, itens in comparativo.exclusoes_exclusivas.items():
            linhas.append(f"- {rotulo}: {'; '.join(itens) if itens else 'nenhuma'}")
        return "\n".join(linhas)

    # Campos de identificacao divergem por natureza (sao apolices diferentes) e
    # nao ajudam a decidir; ficam fora do topo do resumo.
    IDENTIFICACAO = {"seguradora", "produto", "numero_apolice", "processo_susep", "tomador"}

    @classmethod
    def _template(cls, comparativo: Comparativo) -> str:
        materiais = [d for d in comparativo.divergencias if d.campo not in cls.IDENTIFICACAO]
        divergencias = sorted(
            materiais, key=lambda d: 0 if d.impacto.startswith("favorece") else 1
        ) or comparativo.divergencias
        partes = [
            f"Foram comparadas {len(comparativo.apolices)} apolices "
            f"({', '.join(comparativo.apolices)}) em {len(comparativo.linhas)} campos "
            f"estruturados, com {len(comparativo.divergencias)} divergencia(s) identificada(s).",
            "",
            "Principais diferencas:",
        ]
        for linha in divergencias[:5]:
            valores = "; ".join(f"{k}: {v}" for k, v in linha.valores.items())
            partes.append(f"- {linha.rotulo} - {valores}. {linha.comentario}".rstrip())

        partes.append("")
        partes.append("Pontos de atencao:")
        for rotulo, itens in comparativo.exclusoes_exclusivas.items():
            if itens:
                partes.append(f"- Exclusoes so em {rotulo}: {'; '.join(itens[:3])}")
        for rotulo, itens in comparativo.coberturas_exclusivas.items():
            if itens:
                partes.append(f"- Coberturas so em {rotulo}: {'; '.join(itens[:3])}")
        partes.append(
            "- Campos nao localizados pela extracao devem ser conferidos no documento original "
            "antes de qualquer decisao."
        )
        return "\n".join(partes)
