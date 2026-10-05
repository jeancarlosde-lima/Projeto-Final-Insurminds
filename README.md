# InsurMinds — Projeto Final
## Plataforma Inteligente para Análise e Comparação de Apólices D&O

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?logo=googlegemini&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C?logo=langchain&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-persist%C3%AAncia-003B57?logo=sqlite&logoColor=white)
![OCR](https://img.shields.io/badge/OCR-Tesseract%20por-5C3EE8)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-3DA639)

Protótipo funcional (MVP) que recebe apólices de Responsabilidade Civil de Administradores
(D&O) em **PDF ou imagem**, extrai o conteúdo com **OCR quando necessário**, identifica e
estrutura as cláusulas com **IA Generativa**, armazena tudo em **banco relacional** e produz um
**quadro comparativo auditável** entre as apólices, com sumário executivo e consulta em
linguagem natural.

> Grupo **Squad 4one** — Curso InsurMinds, Instituto de Inteligência Artificial Aplicada (I2A2).

**Entregáveis:** [relatório técnico (PDF)](docs/InsurMinds_Projeto_Final_Relatorio_Tecnico.pdf) ·
[pitch deck (PPTX)](Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx) ·
[roteiro do vídeo](Projeto_Final_Artefatos/roteiro_video.md)

---

## Arquitetura

Sete agentes especializados, um por etapa do fluxo previsto no desafio:

```
 PDF / imagem
      │
      ▼
 ┌─────────────────────┐  valida formato, tamanho e integridade
 │ 1. AgenteRecepcao   │
 └─────────────────────┘
 ┌─────────────────────┐  pdfplumber lê o texto nativo; Tesseract entra
 │ 2. AgenteExtracao   │  página a página, só onde falta texto
 └─────────────────────┘
 ┌─────────────────────┐  Gemini devolve JSON aderente a um schema,
 │ 3. AgenteEstruturacao│ com a evidência textual de cada campo
 └─────────────────────┘
 ┌─────────────────────┐  SQLite: campos escalares em SQL, listas em JSON,
 │ 4. AgenteArmazenamento│ histórico de versões por reprocessamento
 └─────────────────────┘
 ┌─────────────────────┐  quadro campo a campo, cláusulas exclusivas,
 │ 5. AgenteComparacao │  direção do impacto — tudo determinístico
 └─────────────────────┘
 ┌─────────────────────┐  sumário executivo escrito a partir das
 │ 6. AgenteRelatorio  │  divergências já apuradas
 └─────────────────────┘
 ┌─────────────────────┐  perguntas em linguagem natural sobre as fichas,
 │ 7. AgenteConsulta   │  com citação da apólice de origem
 └─────────────────────┘
```

**Decisão central do projeto: a IA extrai e redige, mas não decide.** Qual limite é maior, qual
exclusão existe só em uma apólice, qual diferença favorece quem — tudo isso é aritmética e
teoria de conjuntos sobre a ficha estruturada, implementado em código determinístico. Se o
modelo decidisse, duas execuções sobre os mesmos documentos poderiam divergir e nenhuma seria
auditável. O LLM faz o que só ele faz bem: ler linguagem jurídica heterogênea e devolver campos
padronizados.

### Ficha estruturada

Os 17 campos comparados: seguradora, produto, número da apólice, processo SUSEP, tomador,
início e fim de vigência, moeda, limite máximo de indenização, prêmio, franquia, base de
cobertura (claims made / ocorrência), retroatividade, prazos complementar e suplementar, âmbito
geográfico e jurisdição — além das listas de coberturas, sublimites, exclusões e cláusulas
particulares.

Cada campo preenchido carrega a **evidência**: o trecho literal do documento que sustenta o
valor. É o que permite auditar a extração sem reler a apólice inteira.

---

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.11 a 3.13 (validado no 3.13) |
| Leitura de documentos | pdfplumber, pdf2image, Pillow |
| OCR | Tesseract (`pytesseract`), idioma `por` |
| IA Generativa | Google Gemini (`gemini-2.5-flash`) via LangChain |
| Contratos de dados | Pydantic v2 |
| Persistência | SQLite |
| Interface | Streamlit |
| Relatórios | ReportLab (PDF), python-pptx / pptxgenjs (deck) |
| Configuração | python-dotenv (`.env` fora do versionamento) |

---

## Instalação

```bash
git clone https://github.com/jeancarlosde-lima/Projeto-Final-Insurminds.git
cd Projeto-Final-Insurminds

python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux / macOS

pip install -r requirements.txt
```

**OCR (opcional, mas necessário para apólices digitalizadas).** Instale o Tesseract e o pacote
de idioma português:

- Windows: instalador em https://github.com/UB-Mannheim/tesseract/wiki (marque *Portuguese* na
  seleção de idiomas) e adicione a pasta de instalação ao PATH.
- Linux: `sudo apt install tesseract-ocr tesseract-ocr-por poppler-utils`
- macOS: `brew install tesseract tesseract-lang poppler`

Sem Tesseract a plataforma continua funcionando: documentos com texto nativo são lidos
normalmente e os digitalizados são reportados como não processados, em vez de falharem em
silêncio.

**Credenciais:**

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Linux / macOS
```

Informe a `GOOGLE_API_KEY` (Google AI Studio). Sem a chave a extração cai para um modo
heurístico por rótulos e seções — menos preciso, mas suficiente para demonstrar o fluxo offline.
O modo efetivamente usado fica registrado em cada ficha, no campo `extraido_por`.

---

## Execução

**Interface web (recomendada para a demonstração):**

```bash
python data/gerar_apolices_exemplo.py   # cria as apólices fictícias de teste
streamlit run app.py
```

A interface abre em `http://localhost:8501`, com uma aba por etapa: extração, ficha
estruturada, banco de dados, comparação, consulta em linguagem natural e log de execução.

**Linha de comando:**

```bash
python main.py                              # usa as apólices de exemplo
python main.py caminho/a.pdf caminho/b.pdf  # seus próprios documentos
python main.py --sem-llm                    # extração heurística, offline
python main.py --sem-ocr                    # ignora páginas digitalizadas
```

**Regerar os artefatos:**

```bash
python docs/gerar_relatorio.py --com-llm    # relatório técnico em PDF
node docs/gerar_pitch_deck.js               # pitch deck .pptx
```

---

## Dados utilizados

As três apólices em `data/apolices_exemplo/` são **fictícias**, geradas pelo script
`data/gerar_apolices_exemplo.py` especificamente para este trabalho. A redação segue a estrutura
e a terminologia usuais de condições particulares de D&O no mercado brasileiro, mas nomes de
seguradora, números de apólice, valores e processos SUSEP não correspondem a nenhum produto
real. Uma delas é gerada **sem camada de texto**, simulando um documento digitalizado, para
exercitar o caminho de OCR.

A plataforma aceita igualmente documentos públicos reais — modelos de apólice publicados por
seguradoras ou material da SUSEP.

---

## Estrutura do projeto

```
Projeto-Final-Insurminds/
├── app.py                        interface Streamlit
├── main.py                       execução por linha de comando
├── requirements.txt
├── .env.example                  modelo de configuração, sem segredos
├── data/
│   ├── gerar_apolices_exemplo.py gerador das apólices fictícias
│   └── apolices_exemplo/         3 PDFs (uma delas digitalizada)
├── docs/
│   ├── gerar_relatorio.py        gera o relatório a partir de uma execução real
│   ├── gerar_pitch_deck.js       gera o pitch deck
│   └── InsurMinds_Projeto_Final_Relatorio_Tecnico.pdf
├── Projeto_Final_Artefatos/
│   ├── InsurMinds_Projeto_Final.pptx
│   ├── InsurMinds_Projeto_Final.mp4
│   └── roteiro_video.md
├── outputs/                      comparativos exportados
└── src/
    ├── config.py                 campos comparáveis, parâmetros, credenciais
    ├── models.py                 ficha da apólice e quadro comparativo (Pydantic)
    ├── orquestrador.py           encadeamento dos agentes
    └── agentes/
        ├── recepcao.py  extracao.py  estruturacao.py  armazenamento.py
        └── comparacao.py  relatorio.py  consulta.py
```

---

## Limitações conhecidas

- A qualidade da extração depende da qualidade do documento: digitalização ruim gera ficha ruim.
- O extrator heurístico (sem chave de API) funciona bem em documentos rotulados e mal em texto
  corrido jurídico — é contingência, não alternativa equivalente ao modelo.
- A comparação de cláusulas usa sobreposição de termos, não equivalência jurídica: redações
  diferentes com o mesmo efeito legal podem aparecer como divergentes.
- A leitura de impacto segue regras simples (mais limite é melhor, menos franquia é melhor) e
  não substitui parecer técnico ou jurídico.
- Sem tratamento de endossos, apólices em múltiplos arquivos ou moedas diferentes.
- Sem autenticação, controle de acesso ou criptografia em repouso — não está pronto para dados
  reais de clientes.

---

## Integrantes — Squad 4one

| Nome | Papel |
|------|-------|
| Daiane Cristina de Oliveira Brito | Representante do grupo |
| Jean Carlos Oliveira de Lima | Desenvolvimento |
| Simone Teixeira da Silva | Integrante |
| Carolinne Vieira Costa | Integrante |
| Aline Cristina Goya | Integrante |

---

## Licença

Este projeto está licenciado sob a **licença MIT**. Veja o arquivo [LICENSE](LICENSE).
