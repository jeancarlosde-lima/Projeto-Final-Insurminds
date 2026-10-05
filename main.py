"""
Execucao do fluxo completo pela linha de comando.

Exemplos:
    python main.py                                   # usa as apolices de exemplo
    python main.py caminho/a.pdf caminho/b.pdf       # usa seus proprios documentos
    python main.py --sem-llm                         # extracao heuristica, sem IA
    python main.py --sem-ocr                         # ignora paginas digitalizadas
"""

from __future__ import annotations

import argparse
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src import config
from src.agentes.comparacao import formatar
from src.orquestrador import processar


def main() -> None:
    parser = argparse.ArgumentParser(
        description="InsurMinds - Projeto Final: analise e comparacao de apolices D&O"
    )
    parser.add_argument("arquivos", nargs="*", help="PDFs ou imagens das apolices")
    parser.add_argument("--sem-llm", action="store_true", help="usa a extracao heuristica")
    parser.add_argument("--sem-ocr", action="store_true", help="desativa o OCR")
    argumentos = parser.parse_args()

    caminhos = argumentos.arquivos or sorted(str(p) for p in config.DIR_EXEMPLOS.glob("*.pdf"))
    if not caminhos:
        print("Nenhum documento informado e nenhuma apolice de exemplo encontrada.")
        print("Gere os exemplos com: python data/gerar_apolices_exemplo.py")
        return

    resultado = processar(
        caminhos, usar_llm=not argumentos.sem_llm, permitir_ocr=not argumentos.sem_ocr
    )

    print("\n".join(resultado.log))
    print("\n" + "=" * 80)
    print(f"Extracao: {resultado.modo_ia}")
    print(f"Apolices processadas: {len(resultado.fichas)}")
    print("=" * 80)

    for ficha in resultado.fichas:
        print(f"\n--- {ficha.rotulo} ({ficha.arquivo}) ---")
        print(f"  leitura ........... {ficha.metodo_leitura}, {ficha.paginas} pagina(s)")
        print(f"  LMI ............... {formatar(ficha.limite_maximo_indenizacao)}")
        print(f"  premio ............ {formatar(ficha.premio_total)}")
        print(f"  franquia .......... {formatar(ficha.franquia)}")
        print(f"  base .............. {ficha.base_cobertura.value}")
        print(f"  retroatividade .... {ficha.data_retroatividade}")
        print(f"  coberturas ........ {len(ficha.coberturas)}")
        print(f"  exclusoes ......... {len(ficha.exclusoes)}")

    comparativo = resultado.comparativo
    if comparativo:
        print("\n" + "=" * 80)
        print(f"QUADRO COMPARATIVO - {len(comparativo.divergencias)} divergencia(s)")
        print("=" * 80)
        for linha in comparativo.divergencias:
            print(f"\n{linha.rotulo}  [{linha.impacto}]")
            for apolice, valor in linha.valores.items():
                print(f"    {apolice}: {valor}")
            if linha.comentario:
                print(f"    > {linha.comentario}")

        print("\n" + "=" * 80)
        print(f"SUMARIO EXECUTIVO ({comparativo.gerado_sumario_por})")
        print("=" * 80)
        print(comparativo.sumario_executivo)


if __name__ == "__main__":
    main()
