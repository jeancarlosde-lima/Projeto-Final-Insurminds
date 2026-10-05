"""
Agente 5 - Comparacao entre apolices.

Responsabilidade unica: produzir o quadro comparativo campo a campo e apontar
onde as apolices divergem.

A comparacao e DETERMINISTICA. Nenhum LLM decide qual apolice tem o maior
limite ou qual exclusao esta presente em uma e ausente na outra - isso e
aritmetica e teoria de conjuntos sobre a ficha estruturada. O modelo so entra
depois, no agente de relatorio, para escrever o resumo executivo a partir das
diferencas ja apuradas.

A direcao do impacto segue regras simples e explicitas:
  - LMI e sublimites: mais e melhor para o segurado;
  - franquia e premio: menos e melhor;
  - coberturas presentes em uma e ausentes na outra: favorecem quem as tem;
  - exclusoes exclusivas: pesam contra quem as traz.
Essa leitura e uma referencia de analise, nao um parecer juridico - o relatorio
deixa isso explicito.
"""

from __future__ import annotations

from datetime import datetime

from src import config
from src.models import ApoliceEstruturada, Comparativo, LinhaComparativo


def formatar(valor, campo: str = "") -> str:
    if valor is None or valor == "":
        return "nao informado"
    if isinstance(valor, float):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(valor)


class AgenteComparacao:
    nome = "AgenteComparacao"

    def __init__(self, logger=None) -> None:
        self.log = logger or (lambda _m: None)

    def executar(self, fichas: list[ApoliceEstruturada]) -> Comparativo:
        if len(fichas) < 2:
            raise ValueError("a comparacao exige pelo menos duas apolices")

        rotulos = self._rotulos(fichas)
        comparativo = Comparativo(
            gerado_em=datetime.now(tz=config.FUSO), apolices=list(rotulos.values())
        )

        for campo, rotulo_campo, tipo in config.CAMPOS_COMPARAVEIS:
            valores: dict[str, str] = {}
            brutos: dict[str, object] = {}
            for ficha in fichas:
                bruto = getattr(ficha, campo, None)
                if hasattr(bruto, "value"):
                    bruto = bruto.value
                brutos[rotulos[id(ficha)]] = bruto
                valores[rotulos[id(ficha)]] = formatar(bruto, campo)

            distintos = {v for v in valores.values()}
            divergente = len(distintos) > 1
            impacto, comentario = self._avaliar(tipo, brutos)

            comparativo.linhas.append(
                LinhaComparativo(
                    campo=campo,
                    rotulo=rotulo_campo,
                    valores=valores,
                    divergente=divergente,
                    impacto=impacto if divergente else "neutro",
                    comentario=comentario if divergente else "",
                )
            )

        # coberturas e exclusoes: conjuntos exclusivos de cada apolice
        for ficha in fichas:
            rotulo = rotulos[id(ficha)]
            outras_cob: set[str] = set()
            outras_exc: set[str] = set()
            for outra in fichas:
                if outra is ficha:
                    continue
                outras_cob |= outra.nomes_coberturas()
                outras_exc |= {e.strip().lower() for e in outra.exclusoes}

            exclusivas_cob = [
                c.nome for c in ficha.coberturas
                if c.incluida and not self._parecido(c.nome, outras_cob)
            ]
            exclusivas_exc = [
                e for e in ficha.exclusoes if not self._parecido(e, outras_exc)
            ]
            comparativo.coberturas_exclusivas[rotulo] = exclusivas_cob
            comparativo.exclusoes_exclusivas[rotulo] = exclusivas_exc

        self.log(
            f"[{self.nome}] {len(fichas)} apolices comparadas: "
            f"{len(comparativo.divergencias)} divergencia(s) em {len(comparativo.linhas)} campos"
        )
        return comparativo

    # -- apoio -------------------------------------------------------------
    @staticmethod
    def _rotulos(fichas: list[ApoliceEstruturada]) -> dict[int, str]:
        usados: dict[str, int] = {}
        mapa: dict[int, str] = {}
        for ficha in fichas:
            base = ficha.seguradora or ficha.arquivo
            usados[base] = usados.get(base, 0) + 1
            mapa[id(ficha)] = base if usados[base] == 1 else f"{base} ({usados[base]})"
        return mapa

    @staticmethod
    def _parecido(termo: str, conjunto: set[str]) -> bool:
        """Compara clausulas por sobreposicao de palavras significativas."""
        alvo = {p for p in termo.lower().split() if len(p) > 4}
        if not alvo:
            return termo.lower() in conjunto
        for item in conjunto:
            outras = {p for p in item.split() if len(p) > 4}
            if not outras:
                continue
            intersecao = alvo & outras
            if len(intersecao) / max(1, min(len(alvo), len(outras))) >= 0.6:
                return True
        return False

    def _avaliar(self, tipo: str, brutos: dict[str, object]) -> tuple[str, str]:
        numericos = {k: v for k, v in brutos.items() if isinstance(v, (int, float))}
        if tipo == "maior_melhor" and len(numericos) >= 2:
            vencedor = max(numericos, key=lambda k: numericos[k])
            perdedor = min(numericos, key=lambda k: numericos[k])
            if numericos[vencedor] != numericos[perdedor]:
                diferenca = numericos[vencedor] - numericos[perdedor]
                return (
                    f"favorece: {vencedor}",
                    f"{vencedor} oferece {formatar(diferenca)} a mais que {perdedor}.",
                )
        if tipo == "menor_melhor" and len(numericos) >= 2:
            vencedor = min(numericos, key=lambda k: numericos[k])
            perdedor = max(numericos, key=lambda k: numericos[k])
            if numericos[vencedor] != numericos[perdedor]:
                diferenca = numericos[perdedor] - numericos[vencedor]
                return (
                    f"favorece: {vencedor}",
                    f"{vencedor} e {formatar(diferenca)} menor que {perdedor}.",
                )
        if any(v in (None, "") for v in brutos.values()):
            return "atencao", "Campo nao localizado em pelo menos uma das apolices."
        return "atencao", "Condicoes diferentes entre as apolices."
