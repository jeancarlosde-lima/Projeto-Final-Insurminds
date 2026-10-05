"""
Configuracao central do Projeto Final.

Credenciais sao lidas do .env e nunca versionadas (ver .env.example).
"""

from __future__ import annotations

import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
DIR_DADOS = RAIZ / "data"
DIR_EXEMPLOS = DIR_DADOS / "apolices_exemplo"
DIR_SAIDA = RAIZ / "outputs"
DIR_SAIDA.mkdir(exist_ok=True)
BANCO = DIR_DADOS / "apolices.db"

FUSO = ZoneInfo("America/Sao_Paulo")

# --- IA Generativa ---------------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
MODELO_LLM = os.getenv("MODELO_LLM", "gemini-2.5-flash").strip()
TEMPERATURA_LLM = float(os.getenv("TEMPERATURA_LLM", "0.1"))

# Limite de caracteres do documento enviado ao modelo em cada chamada.
MAX_CARACTERES_PROMPT = int(os.getenv("MAX_CARACTERES_PROMPT", "60000"))

# Teto de tokens da resposta. A ficha completa de uma apolice longa passa de 4 mil
# tokens, e modelos com raciocinio interno gastam parte desse orcamento antes de
# responder: sem folga, o JSON volta truncado e a extracao cai para a heuristica.
MAX_TOKENS_SAIDA = int(os.getenv("MAX_TOKENS_SAIDA", "16384"))

# --- OCR -------------------------------------------------------------------
# Usado apenas quando o PDF nao possui camada de texto (documento digitalizado).
OCR_IDIOMA = os.getenv("OCR_IDIOMA", "por")
OCR_DPI = int(os.getenv("OCR_DPI", "200"))
# Minimo de caracteres por pagina para considerar que ha texto nativo.
MIN_CARACTERES_PAGINA = 120

# --- Campos do quadro comparativo -----------------------------------------
# (campo tecnico, rotulo exibido, tipo de comparacao)
#   maior_melhor  -> valor numerico em que mais e melhor (limite de indenizacao)
#   menor_melhor  -> valor numerico em que menos e melhor (franquia, premio)
#   texto         -> comparacao textual simples
CAMPOS_COMPARAVEIS = [
    ("seguradora", "Seguradora", "texto"),
    ("produto", "Produto", "texto"),
    ("numero_apolice", "Numero da apolice", "texto"),
    ("processo_susep", "Processo SUSEP", "texto"),
    ("tomador", "Tomador / Segurado", "texto"),
    ("vigencia_inicio", "Inicio de vigencia", "texto"),
    ("vigencia_fim", "Fim de vigencia", "texto"),
    ("moeda", "Moeda", "texto"),
    ("limite_maximo_indenizacao", "Limite maximo de indenizacao (LMI)", "maior_melhor"),
    ("premio_total", "Premio total", "menor_melhor"),
    ("franquia", "Franquia / participacao obrigatoria", "menor_melhor"),
    ("base_cobertura", "Base de cobertura", "texto"),
    ("data_retroatividade", "Data de retroatividade", "texto"),
    ("prazo_complementar", "Prazo complementar", "texto"),
    ("prazo_suplementar", "Prazo suplementar", "texto"),
    ("ambito_geografico", "Ambito geografico", "texto"),
    ("jurisdicao", "Jurisdicao", "texto"),
]

# Coberturas tipicas de D&O usadas como checklist na extracao e na comparacao.
COBERTURAS_REFERENCIA = [
    "custos de defesa",
    "danos morais",
    "multas e penalidades civis",
    "custos de fianca",
    "responsabilidade da pessoa juridica em valores mobiliarios",
    "reembolso a pessoa juridica",
    "custos de publicidade e gerenciamento de crise",
    "investigacoes e inqueritos",
    "obrigacoes trabalhistas e previdenciarias",
    "ex-administradores e administradores aposentados",
    "conjuges, herdeiros e espolio",
    "despesas de emergencia",
]

NOME_PROJETO = "InsurMinds - Projeto Final"
GRUPO = "Squad 4one"
