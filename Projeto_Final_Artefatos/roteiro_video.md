# Roteiro do vídeo — InsurMinds_Projeto_Final.mp4

**Duração máxima: 5 minutos.** O enunciado pede quatro coisas no vídeo: o problema abordado, a
arquitetura da solução, o funcionamento da aplicação e os principais resultados. O roteiro
abaixo cobre as quatro, com folga de 15 segundos.

**Antes de gravar:** rode `streamlit run app.py`, clique em *Carregar apólices de exemplo* e
deixe o resultado já processado na tela. Gravar o processamento ao vivo gasta tempo precioso —
mostre o resultado e cite que levou menos de um minuto.

**Ferramenta:** OBS Studio ou a gravação de tela do próprio Windows (Win+G). Grave em 1080p,
com o navegador em tela cheia e o zoom em 110% para o texto ficar legível.

---

## 0:00 – 0:35 · O problema (slide 2 do deck)

> Comparar duas apólices de D&O é trabalho manual de especialista. São documentos longos, em
> linguagem jurídica, e cada seguradora organiza as mesmas informações de um jeito diferente.
> Para responder uma pergunta simples — qual tem maior retroatividade, qual exclui danos morais —
> o analista precisa ler os dois documentos inteiros. O custo não é só o tempo: quem compara às
> pressas decide pelo prêmio e pelo limite, que são os campos fáceis de achar, e descobre as
> diferenças de cláusula no momento do sinistro.

## 0:35 – 1:20 · A arquitetura (slides 4 e 5)

> A solução é um fluxo de sete agentes, cada um com uma responsabilidade: recepção, extração,
> estruturação, armazenamento, comparação, relatório e consulta.
>
> A decisão central do projeto está aqui: a IA extrai e redige, mas não decide. Qual limite é
> maior, qual exclusão existe só em uma apólice — isso é aritmética sobre a ficha estruturada e
> está em código determinístico. Se o modelo decidisse, duas execuções poderiam divergir e
> nenhuma seria auditável. O LLM faz o que só ele faz bem: ler linguagem jurídica heterogênea e
> devolver campos padronizados.

## 1:20 – 3:30 · A aplicação funcionando (tela do Streamlit)

Percorra as abas na ordem, narrando:

**Aba 2 — Extração** (20s)
> Três apólices processadas. Repare na coluna Método: duas foram lidas por texto nativo e uma
> por OCR — essa terceira é um PDF digitalizado, sem camada de texto. A decisão de acionar o OCR
> é tomada página a página, porque apólices reais misturam páginas digitais com anexos
> escaneados.

**Aba 3 — Ficha estruturada** (40s) — abra uma apólice e depois *Evidências da extração*
> Esta é a ficha padronizada: limite máximo de indenização, franquia, base de cobertura,
> retroatividade, coberturas, exclusões. E aqui está o ponto que torna a solução utilizável: cada
> campo carrega a evidência, o trecho literal do documento que sustenta aquele valor. O analista
> confere a extração sem reler a apólice inteira — e se o modelo alucinar, isso fica visível.

**Aba 4 — Armazenamento** (15s)
> As fichas vão para um banco SQLite. Dá para consultar por campo, em SQL — por exemplo, ordenar
> as apólices por limite de indenização.

**Aba 5 — Comparação** (40s)
> O quadro comparativo, campo a campo. O sistema aponta a direção de cada diferença: aqui, a
> Aurora oferece dez milhões a mais de limite que a Meridiano; a Meridiano tem o menor prêmio.
> Abaixo, as cláusulas que existem em apenas uma das apólices — e é aí que mora o risco: a
> Meridiano exclui danos morais, que as outras duas cobrem. E o sumário executivo, escrito pela
> IA a partir das divergências já apuradas.

**Aba 6 — Consulta** (25s) — faça uma pergunta ao vivo
> Dá para perguntar em linguagem natural. "Alguma delas exclui danos morais?" A resposta usa as
> fichas estruturadas, não o PDF bruto, e cita de qual apólice veio cada informação.

## 3:30 – 4:15 · Resultados (slide 6)

> Três apólices, sendo uma digitalizada. Dezessete campos estruturados e comparados, doze
> divergências identificadas, do upload ao quadro comparativo em menos de um minuto. O trabalho
> que levaria horas de leitura vira uma tabela auditável — com a evidência de cada campo e o log
> completo da execução.

## 4:15 – 4:45 · Limitações e fechamento (slides 8 e 9)

> O protótipo tem limites conhecidos, e eles estão documentados: documento digitalizado ruim gera
> ficha ruim; as cláusulas são comparadas por termos, não por equivalência jurídica; e não há
> autenticação nem criptografia, então não está pronto para dado real de cliente.
>
> O que entregamos: protótipo funcional, código aberto sob licença MIT no GitHub e relatório
> técnico com a arquitetura e as decisões. Squad 4one, InsurMinds, I2A2. Obrigado.

---

## Checklist antes de exportar

- [ ] Arquivo nomeado exatamente `InsurMinds_Projeto_Final.mp4`
- [ ] Duração igual ou inferior a 5 minutos
- [ ] Áudio audível, sem ruído de fundo
- [ ] Nenhuma chave de API visível na tela (cuidado ao mostrar o `.env` ou o terminal)
- [ ] Vídeo depositado em `Projeto_Final_Artefatos/` no repositório
