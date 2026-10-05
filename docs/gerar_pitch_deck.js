/**
 * Gera o pitch deck do Projeto Final (InsurMinds_Projeto_Final.pptx).
 *
 * Uso: node docs/gerar_pitch_deck.js
 * Saida: Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx
 */

const path = require("path");
const pptxgen = require("pptxgenjs");
// O tema vem de um utilitario externo, disponivel apenas no ambiente onde o deck
// foi produzido. Fora dele o deck e gerado sem essa etapa, em vez de falhar.
let applyTheme = null;
try {
  ({ applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js"));
} catch (erro) {
  console.warn("apply_theme.js indisponivel: deck gerado sem a camada de tema.");
}

const THEME = {
  name: "InsurMinds DO",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1A1D21",
    lt1: "FFFFFF",
    dk2: "36454F",
    lt2: "F2F2F2",
    accent1: "B85042",
    accent2: "A7BEAE",
    accent3: "36454F",
    accent4: "7A8B94",
    accent5: "E7E8D1",
    accent6: "212121",
    hlink: "B85042",
    folHlink: "7A8B94",
  },
};

const SAIDA = path.join(__dirname, "..", "Projeto_Final_Artefatos", "InsurMinds_Projeto_Final.pptx");

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = "Squad 4one";
  pres.company = "InsurMinds - I2A2";
  pres.title = "Plataforma Inteligente para Analise e Comparacao de Apolices D&O";

  const C = pres.SchemeColor;

  // -------------------------------------------------------------- layouts
  pres.defineSlideMaster({
    title: "CAPA",
    background: { color: THEME.colors.dk2 },
    objects: [
      {
        placeholder: {
          options: {
            name: "title",
            type: "title",
            x: 0.9, y: 2.3, w: 11.5, h: 1.9,
            fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left",
          },
          text: "",
        },
      },
      {
        placeholder: {
          options: {
            name: "body",
            type: "body",
            x: 0.9, y: 4.35, w: 11.5, h: 1.6,
            fontSize: 16, color: THEME.colors.accent5, valign: "top",
          },
          text: "",
        },
      },
    ],
  });

  pres.defineSlideMaster({
    title: "CONTEUDO",
    background: { color: C.background1 },
    objects: [
      {
        placeholder: {
          options: {
            name: "title",
            type: "title",
            x: 0.75, y: 0.5, w: 11.8, h: 0.9,
            fontSize: 32, bold: true, color: THEME.colors.dk2, valign: "middle", align: "left",
          },
          text: "",
        },
      },
      {
        text: {
          text: "InsurMinds - Projeto Final | Squad 4one",
          options: {
            x: 0.75, y: 6.95, w: 7, h: 0.3, fontSize: 9,
            color: THEME.colors.accent4, isTextBox: true, margin: 0,
          },
        },
      },
    ],
    slideNumber: { x: 12.4, y: 6.95, fontSize: 9, color: THEME.colors.accent4 },
  });

  pres.defineSlideMaster({
    title: "FECHAMENTO",
    background: { color: THEME.colors.dk2 },
    objects: [
      {
        placeholder: {
          options: {
            name: "title",
            type: "title",
            x: 0.9, y: 0.7, w: 11.5, h: 1.0,
            fontSize: 32, bold: true, color: C.background1, valign: "middle", align: "left",
          },
          text: "",
        },
      },
    ],
  });

  // ------------------------------------------------------------ utilitarios
  const cartao = (slide, { x, y, w, h, titulo, texto, numero }) => {
    slide.addShape(pres.ShapeType.roundRect, {
      x, y, w, h, rectRadius: 0.08,
      fill: { color: THEME.colors.lt2 },
      line: { color: THEME.colors.lt2 },
      objectName: `cartao-${titulo}`,
    });
    if (numero) {
      slide.addShape(pres.ShapeType.ellipse, {
        x: x + 0.3, y: y + 0.28, w: 0.52, h: 0.52,
        fill: { color: THEME.colors.accent1 },
        line: { color: THEME.colors.accent1 },
        objectName: `bola-${titulo}`,
      });
      slide.addText(numero, {
        x: x + 0.3, y: y + 0.28, w: 0.52, h: 0.52,
        fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle",
        isTextBox: true, margin: 0,
      });
    }
    slide.addText(titulo, {
      x: x + (numero ? 0.98 : 0.3), y: y + 0.3, w: w - (numero ? 1.28 : 0.6), h: 0.5,
      fontSize: 15, bold: true, color: THEME.colors.dk2, isTextBox: true, margin: 0,
      valign: "middle",
    });
    slide.addText(texto, {
      x: x + 0.3, y: y + 0.95, w: w - 0.6, h: h - 1.2,
      fontSize: 13, color: THEME.colors.accent3, isTextBox: true, margin: 0,
      lineSpacingMultiple: 1.15,
    });
  };

  const estatistica = (slide, { x, y, w, numero, rotulo }) => {
    slide.addText(numero, {
      x, y, w, h: 1.0, fontSize: 54, bold: true, color: THEME.colors.accent1,
      align: "center", isTextBox: true, margin: 0,
    });
    slide.addText(rotulo, {
      x, y: y + 1.05, w, h: 0.8, fontSize: 13, color: THEME.colors.dk2,
      align: "center", isTextBox: true, margin: 0,
    });
  };

  // ------------------------------------------------------------- 1. capa
  pres.addSection({ title: "Abertura" });
  let s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Abertura" });
  s.addText("Plataforma Inteligente para Análise e Comparação de Apólices D&O", {
    placeholder: "title",
  });
  s.addText(
    [
      { text: "InsurMinds · Projeto Final · Instituto de Inteligência Artificial Aplicada (I2A2)", options: { breakLine: true } },
      { text: "Grupo Squad 4one", options: { bold: true, color: "FFFFFF" } },
    ],
    { placeholder: "body" }
  );
  s.addShape(pres.ShapeType.rect, {
    x: 0.9, y: 2.05, w: 1.4, h: 0.09,
    fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1 },
    objectName: "marca-capa",
  });
  s.addNotes(
    "Apresentamos a plataforma que lê apólices de D&O, estrutura as cláusulas com IA e " +
      "compara documentos de seguradoras diferentes. Projeto final do curso InsurMinds, grupo Squad 4one."
  );

  // -------------------------------------------------------- 2. o problema
  pres.addSection({ title: "Problema" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Problema" });
  s.addText("Comparar duas apólices é trabalho manual de especialista", { placeholder: "title" });
  s.addText(
    "Apólices de D&O são documentos longos, em linguagem jurídica, e cada seguradora organiza as " +
      "mesmas informações de um jeito diferente. Responder \"qual tem maior retroatividade\" exige " +
      "ler os dois documentos inteiros.",
    { x: 0.75, y: 1.5, w: 11.8, h: 0.9, fontSize: 15, color: THEME.colors.accent3, isTextBox: true, margin: 0 }
  );
  estatistica(s, { x: 0.75, y: 2.7, w: 3.6, numero: "4 h", rotulo: "tempo típico de leitura e comparação de duas apólices" });
  estatistica(s, { x: 4.85, y: 2.7, w: 3.6, numero: "30+", rotulo: "cláusulas relevantes espalhadas por seções distintas" });
  estatistica(s, { x: 8.95, y: 2.7, w: 3.6, numero: "0", rotulo: "padronização entre seguradoras para os mesmos campos" });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 5.1, w: 11.8, h: 1.25, rectRadius: 0.08,
    fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, objectName: "consequencia",
  });
  s.addText(
    [
      { text: "A consequência: ", options: { bold: true, color: THEME.colors.accent1 } },
      {
        text: "quem compara às pressas decide pelo prêmio e pelo limite — os campos fáceis de achar — " +
          "e descobre as diferenças de cláusula no momento do sinistro.",
        options: { color: THEME.colors.dk2 },
      },
    ],
    { x: 1.1, y: 5.35, w: 11.1, h: 0.8, fontSize: 15, isTextBox: true, margin: 0, valign: "middle" }
  );
  s.addNotes(
    "O custo não é só tempo: é assimetria de informação. As diferenças que importam estão nas " +
      "cláusulas, e são justamente as mais caras de ler."
  );

  // --------------------------------------------------------- 3. a solução
  pres.addSection({ title: "Solução" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Solução" });
  s.addText("De documento jurídico a quadro comparativo auditável", { placeholder: "title" });
  cartao(s, {
    x: 0.75, y: 1.75, w: 3.85, h: 2.5, numero: "1",
    titulo: "Lê qualquer documento",
    texto: "PDF nativo ou digitalizado. O OCR é acionado página a página, só onde falta texto — e o método usado fica registrado.",
  });
  cartao(s, {
    x: 4.82, y: 1.75, w: 3.85, h: 2.5, numero: "2",
    titulo: "Padroniza com IA",
    texto: "O Gemini devolve JSON aderente a um schema validado, com o trecho do documento que sustenta cada campo extraído.",
  });
  cartao(s, {
    x: 8.9, y: 1.75, w: 3.85, h: 2.5, numero: "3",
    titulo: "Compara e justifica",
    texto: "Quadro campo a campo, cláusulas exclusivas de cada apólice e sumário executivo com os trade-offs.",
  });
  s.addText("O que o usuário recebe", {
    x: 0.75, y: 4.55, w: 11.8, h: 0.4, fontSize: 17, bold: true, color: THEME.colors.dk2,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Quadro comparativo campo a campo, com a direção de cada diferença", options: { bullet: true, breakLine: true } },
      { text: "Lista de coberturas e exclusões presentes em apenas uma das apólices", options: { bullet: true, breakLine: true } },
      { text: "Sumário executivo em linguagem de negócio, e consulta livre sobre os documentos", options: { bullet: true } },
    ],
    { x: 0.95, y: 5.0, w: 11.5, h: 1.6, fontSize: 14, color: THEME.colors.accent3, isTextBox: true, paraSpaceAfter: 6 }
  );
  s.addNotes("Três capacidades: ler, padronizar e comparar. O diferencial está em padronizar documentos heterogêneos.");

  // ------------------------------------------------------ 4. arquitetura
  pres.addSection({ title: "Arquitetura" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Arquitetura" });
  s.addText("Sete agentes, cada um com uma responsabilidade", { placeholder: "title" });
  const agentes = [
    ["1", "Recepção", "Valida formato e integridade"],
    ["2", "Extração", "Texto nativo ou OCR, por página"],
    ["3", "Estruturação", "IA Generativa → JSON validado"],
    ["4", "Armazenamento", "SQLite, com histórico de versões"],
    ["5", "Comparação", "Determinística, campo a campo"],
    ["6", "Relatório", "Sumário executivo com IA"],
    ["7", "Consulta", "Perguntas em linguagem natural"],
  ];
  agentes.forEach(([numero, titulo, descricao], i) => {
    const coluna = i % 4;
    const linha = Math.floor(i / 4);
    const x = 0.75 + coluna * 3.03;
    const y = 1.75 + linha * 2.35;
    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: 2.8, h: 2.0, rectRadius: 0.08,
      fill: { color: linha === 0 ? THEME.colors.lt2 : THEME.colors.accent5 },
      line: { color: linha === 0 ? THEME.colors.lt2 : THEME.colors.accent5 },
      objectName: `agente-${numero}`,
    });
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.25, y: y + 0.25, w: 0.48, h: 0.48,
      fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1 },
      objectName: `num-${numero}`,
    });
    s.addText(numero, {
      x: x + 0.25, y: y + 0.25, w: 0.48, h: 0.48, fontSize: 13, bold: true,
      color: "FFFFFF", align: "center", valign: "middle", isTextBox: true, margin: 0,
    });
    s.addText(titulo, {
      x: x + 0.25, y: y + 0.85, w: 2.3, h: 0.4, fontSize: 15, bold: true,
      color: THEME.colors.dk2, isTextBox: true, margin: 0,
    });
    s.addText(descricao, {
      x: x + 0.25, y: y + 1.25, w: 2.3, h: 0.6, fontSize: 12, color: THEME.colors.accent3,
      isTextBox: true, margin: 0,
    });
  });
  s.addText(
    [
      { text: "Contratos explícitos entre etapas. ", options: { bold: true, color: THEME.colors.dk2 } },
      {
        text: "Cada agente recebe e devolve um tipo Pydantic, então trocar o modelo de linguagem ou " +
          "o motor de OCR não toca em nenhum outro componente.",
        options: { color: THEME.colors.accent3 },
      },
    ],
    { x: 9.84, y: 4.1, w: 2.8, h: 2.0, fontSize: 12.5, isTextBox: true, margin: 0, valign: "middle" }
  );
  s.addNotes("O fluxo segue as sete etapas do enunciado. Cada agente é substituível sem afetar os demais.");

  // ------------------------------------------- 5. decisão arquitetural
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Arquitetura" });
  s.addText("A IA extrai e redige — ela não decide", { placeholder: "title" });
  s.addText(
    "Se o modelo decidisse qual limite é maior ou qual exclusão é exclusiva, duas execuções sobre " +
      "os mesmos documentos poderiam divergir — e nenhuma seria auditável.",
    { x: 0.75, y: 1.5, w: 11.8, h: 0.8, fontSize: 15, color: THEME.colors.accent3, isTextBox: true, margin: 0 }
  );
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 2.5, w: 5.85, h: 3.3, rectRadius: 0.08,
    fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, objectName: "det",
  });
  s.addText("Determinístico", {
    x: 1.1, y: 2.75, w: 5.15, h: 0.45, fontSize: 17, bold: true, color: THEME.colors.dk2,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Comparação numérica entre campos", options: { bullet: true, breakLine: true } },
      { text: "Cláusulas exclusivas por sobreposição de termos", options: { bullet: true, breakLine: true } },
      { text: "Direção do impacto por regra explícita", options: { bullet: true, breakLine: true } },
      { text: "Validação do schema e persistência", options: { bullet: true } },
    ],
    { x: 1.3, y: 3.3, w: 5.0, h: 2.3, fontSize: 13.5, color: THEME.colors.accent3, isTextBox: true, paraSpaceAfter: 8 }
  );
  s.addShape(pres.ShapeType.roundRect, {
    x: 6.9, y: 2.5, w: 5.85, h: 3.3, rectRadius: 0.08,
    fill: { color: THEME.colors.accent5 }, line: { color: THEME.colors.accent5 }, objectName: "gen",
  });
  s.addText("IA Generativa", {
    x: 7.25, y: 2.75, w: 5.15, h: 0.45, fontSize: 17, bold: true, color: THEME.colors.dk2,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Leitura de linguagem jurídica heterogênea", options: { bullet: true, breakLine: true } },
      { text: "Preenchimento do schema, com evidência textual", options: { bullet: true, breakLine: true } },
      { text: "Redação do sumário executivo", options: { bullet: true, breakLine: true } },
      { text: "Resposta a perguntas sobre as fichas", options: { bullet: true } },
    ],
    { x: 7.45, y: 3.3, w: 5.0, h: 2.3, fontSize: 13.5, color: THEME.colors.accent3, isTextBox: true, paraSpaceAfter: 8 }
  );
  s.addNotes(
    "Essa divisão é a decisão central do projeto: o modelo faz o que só ele faz bem, e o que precisa " +
      "ser reproduzível fica em código."
  );

  // ----------------------------------------------------- 6. demonstração
  pres.addSection({ title: "Demonstração" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Demonstração" });
  s.addText("Execução sobre três apólices D&O", { placeholder: "title" });
  s.addText(
    "Documentos fictícios criados para o trabalho, com a estrutura e a terminologia usuais do " +
      "mercado brasileiro. Um deles é gerado sem camada de texto, para exercitar o OCR.",
    { x: 0.75, y: 1.45, w: 11.8, h: 0.7, fontSize: 14, color: THEME.colors.accent3, isTextBox: true, margin: 0 }
  );
  estatistica(s, { x: 0.75, y: 2.35, w: 2.8, numero: "3", rotulo: "apólices processadas, uma delas digitalizada" });
  estatistica(s, { x: 3.75, y: 2.35, w: 2.8, numero: "17", rotulo: "campos estruturados e comparados" });
  estatistica(s, { x: 6.75, y: 2.35, w: 2.8, numero: "12", rotulo: "divergências identificadas" });
  estatistica(s, { x: 9.75, y: 2.35, w: 2.8, numero: "< 1 min", rotulo: "do upload ao quadro comparativo" });
  const linhas = [
    [
      { text: "Campo", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 } } },
      { text: "Aurora", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 } } },
      { text: "Horizonte", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 } } },
      { text: "Meridiano", options: { bold: true, color: "FFFFFF", fill: { color: THEME.colors.dk2 } } },
    ],
    ["Limite máximo de indenização", "R$ 25.000.000", "R$ 20.000.000", "R$ 15.000.000"],
    ["Prêmio total", "R$ 231.800", "R$ 184.500", "R$ 142.000"],
    ["Franquia", "R$ 100.000", "R$ 150.000", "R$ 250.000"],
    ["Retroatividade", "Ilimitada", "01/03/2019", "01/03/2023"],
    ["Prazo suplementar", "72 meses", "36 meses", "24 meses"],
  ];
  s.addTable(linhas, {
    x: 0.75, y: 4.35, w: 11.8, colW: [4.4, 2.46, 2.47, 2.47],
    fontSize: 12.5, color: THEME.colors.accent3, border: { type: "solid", color: "D9D9D9", pt: 0.5 },
    fill: { color: "FFFFFF" }, rowH: 0.33, valign: "middle", margin: 6,
  });
  s.addNotes(
    "Os números vêm de uma execução real: três apólices, 17 campos, 12 divergências. A tabela mostra " +
      "os campos que mais pesam na decisão."
  );

  // -------------------------------------------------- 7. auditabilidade
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Demonstração" });
  s.addText("Cada campo extraído carrega sua evidência", { placeholder: "title" });
  s.addText(
    "O modelo devolve, junto de cada valor, o trecho literal do documento que o sustenta. " +
      "O analista audita a extração sem reler a apólice inteira — e a alucinação fica visível.",
    { x: 0.75, y: 1.5, w: 11.8, h: 0.8, fontSize: 15, color: THEME.colors.accent3, isTextBox: true, margin: 0 }
  );
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 2.5, w: 11.8, h: 1.75, rectRadius: 0.08,
    fill: { color: THEME.colors.lt2 }, line: { color: THEME.colors.lt2 }, objectName: "evidencia",
  });
  s.addText("limite_maximo_indenizacao: 20000000.00", {
    x: 1.1, y: 2.75, w: 11.1, h: 0.4, fontSize: 14, bold: true, fontFace: "Courier New",
    color: THEME.colors.dk2, isTextBox: true, margin: 0,
  });
  s.addText(
    "evidência: \"Limite Máximo de Indenização (LMI): R$ 20.000.000,00 (vinte milhões de reais)\"",
    { x: 1.1, y: 3.2, w: 11.1, h: 0.5, fontSize: 13, italic: true, color: THEME.colors.accent1, isTextBox: true, margin: 0 }
  );
  s.addText("origem: apolice_do_horizonte.pdf · leitura: texto nativo · validado por schema Pydantic", {
    x: 1.1, y: 3.65, w: 11.1, h: 0.4, fontSize: 12, color: THEME.colors.accent4, isTextBox: true, margin: 0,
  });
  cartao(s, {
    x: 0.75, y: 4.55, w: 3.85, h: 1.85,
    titulo: "Saída validada",
    texto: "JSON fora do schema falha na validação em vez de virar dado errado no banco.",
  });
  cartao(s, {
    x: 4.82, y: 4.55, w: 3.85, h: 1.85,
    titulo: "Método registrado",
    texto: "A ficha guarda se veio de texto nativo, de OCR ou da extração heurística.",
  });
  cartao(s, {
    x: 8.9, y: 4.55, w: 3.85, h: 1.85,
    titulo: "Log por execução",
    texto: "Cada etapa registra o que fez, com horário — a execução inteira é reconstituível.",
  });
  s.addNotes("Auditabilidade é requisito, não enfeite: ninguém assume risco com base em extração que não dá para conferir.");

  // ------------------------------------------------------- 8. limitações
  pres.addSection({ title: "Fechamento" });
  s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Fechamento" });
  s.addText("O que ainda não resolve, e para onde vai", { placeholder: "title" });
  s.addText("Limitações conhecidas", {
    x: 0.75, y: 1.6, w: 5.85, h: 0.45, fontSize: 18, bold: true, color: THEME.colors.accent1,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "Documento ruim gera ficha ruim: OCR de baixa qualidade propaga erro", options: { bullet: true, breakLine: true } },
      { text: "Cláusulas são comparadas por termos, não por equivalência jurídica", options: { bullet: true, breakLine: true } },
      { text: "Sem tratamento de endossos, múltiplas moedas ou conversão cambial", options: { bullet: true, breakLine: true } },
      { text: "Sem autenticação nem criptografia: não está pronto para dado real de cliente", options: { bullet: true } },
    ],
    { x: 0.95, y: 2.15, w: 5.5, h: 3.4, fontSize: 13.5, color: THEME.colors.accent3, isTextBox: true, paraSpaceAfter: 10 }
  );
  s.addText("Evolução", {
    x: 6.9, y: 1.6, w: 5.85, h: 0.45, fontSize: 18, bold: true, color: THEME.colors.accent1,
    isTextBox: true, margin: 0,
  });
  s.addText(
    [
      { text: "RAG sobre o texto integral, com citação de página", options: { bullet: true, breakLine: true } },
      { text: "Base de cláusulas padrão para classificar cada redação", options: { bullet: true, breakLine: true } },
      { text: "Comparação entre renovações da mesma apólice", options: { bullet: true, breakLine: true } },
      { text: "Mesmo motor para outros ramos: Cyber, RC Profissional", options: { bullet: true } },
    ],
    { x: 7.1, y: 2.15, w: 5.5, h: 3.4, fontSize: 13.5, color: THEME.colors.accent3, isTextBox: true, paraSpaceAfter: 10 }
  );
  s.addNotes("Reconhecer limites é parte do projeto: o que fica de fora está documentado no relatório técnico.");

  // ------------------------------------------------------ 9. fechamento
  s = pres.addSlide({ masterName: "FECHAMENTO", sectionTitle: "Fechamento" });
  s.addText("Documento jurídico vira decisão comparável", { placeholder: "title" });
  s.addShape(pres.ShapeType.rect, {
    x: 0.9, y: 2.0, w: 1.4, h: 0.09,
    fill: { color: THEME.colors.accent1 }, line: { color: THEME.colors.accent1 },
    objectName: "marca-fim",
  });
  const entregas = [
    ["Protótipo funcional", "Streamlit, sete agentes, OCR e IA Generativa"],
    ["Código aberto", "Repositório público no GitHub, licença MIT"],
    ["Relatório técnico", "Arquitetura, decisões, limitações e evolução"],
  ];
  entregas.forEach(([titulo, descricao], i) => {
    const x = 0.9 + i * 4.0;
    s.addText(titulo, {
      x, y: 2.6, w: 3.6, h: 0.45, fontSize: 17, bold: true, color: "FFFFFF",
      isTextBox: true, margin: 0,
    });
    s.addText(descricao, {
      x, y: 3.1, w: 3.6, h: 0.9, fontSize: 13.5, color: THEME.colors.accent5,
      isTextBox: true, margin: 0,
    });
  });
  s.addText(
    "Horas de leitura comparativa viram um quadro auditável em menos de um minuto.",
    {
      x: 0.9, y: 4.35, w: 11.5, h: 0.6, fontSize: 16, italic: true,
      color: THEME.colors.accent2, isTextBox: true, margin: 0,
    }
  );
  s.addText(
    [
      { text: "Squad 4one", options: { bold: true, color: "FFFFFF", breakLine: true } },
      { text: "github.com/jeancarlosde-lima · InsurMinds · I2A2", options: { color: THEME.colors.accent5 } },
    ],
    { x: 0.9, y: 5.4, w: 11.5, h: 1.0, fontSize: 14, isTextBox: true, margin: 0 }
  );
  s.addNotes("Fechamento: o que entregamos e onde encontrar. Obrigado.");

  await pres.writeFile({ fileName: SAIDA });
  if (applyTheme) {
    await applyTheme(SAIDA, THEME);
  }
  console.log("Deck gerado:", SAIDA);
}

main().catch((erro) => {
  console.error(erro);
  process.exit(1);
});
