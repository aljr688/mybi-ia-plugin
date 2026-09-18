# Escolha do formato

Quando o formato estiver ausente, pergunte antes de gerar ou aprovar componentes:

“Como você quer montar o dashboard?
1. Componentes separados DevExpress + ECharts.
2. HTMLTemplate, com layout HTML/CSS personalizado.
3. Painel integrado em JavaScript, com toda a tela em um componente.
4. Componentes prontos do MyBI, como os modelos por segmento e IAComercial
   (DRE, Segmentação de Clientes etc.).
Qual opção prefere? Pode responder pelo nome ou número.”

Restaurantes e postos são exemplos de segmento, não uma autorização automática para
usar JavaScript. Se “JS fechado” significar um modelo já existente, confirme qual
modelo; não o recrie silenciosamente como JavaScript gerado. Se o usuário pedir uma
combinação, descreva os componentes de cada formato e obtenha aprovação dessa composição.

## Representação e limites atuais

- DevExpress/ECharts: `mode: components`, componentes exatos do catálogo.
- HTMLTemplate: `mode: html`, `component: HtmlTemplate`; HTML/CSS e placeholders,
  sem scripts, conforme html.md. Não confundir com DashboardAutomatico.
- JavaScript integrado gerado: `mode: html`, `component: DashboardAutomatico`;
  corpo de render(root, rows, fields), conforme html.md. O código fica no XML;
  não entregar um arquivo JS solto que o importador não instala.
- Modelos prontos e IAComercial: exigem o CustomItemType e bindings reais da extensão
  instalada no MyBI. A extensão continua sendo fornecida pelo MyBI, não pelo ZIP.
  Use somente tipos existentes em catalog.json. Se DRE, Segmentação ou outro modelo
  não estiver no catálogo, explique a limitação e pare a geração desse componente.
  Peça o contrato/exportação ou a atualização do catálogo; não invente bindings,
  propriedades, cálculos financeiros ou nomes de tipos para contornar o validador.

Uma solicitação de “DRE” pode indicar uma análise ou o componente pronto DRE Vendas /
DRE Contábil. Esclareça qual quando não estiver explícito. Nunca alegue paridade total
com o assistente web: o catálogo portátil ainda precisa ser ampliado e validado para
os componentes prontos de segmentos e IAComercial.

Na proposta, indique formato, componente real, campos, agregações, comportamento
interno e disponibilidade no MyBI do destino. Mantenha as aprovações de campos,
componentes e aparência e a preservação do XML-base.
