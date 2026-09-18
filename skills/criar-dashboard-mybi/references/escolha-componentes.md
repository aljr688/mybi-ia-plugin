# Entender o pedido e escolher o componente

Separe conceito visual, implementação e campos necessários. Não diga que o MyBI não
possui um recurso porque o usuário utilizou um sinônimo ou porque o gerador portátil
ainda não suporta uma implementação. O catálogo é do gerador, não de todo o produto.

| Termos do usuário | Interpretação / decisão |
|---|---|
| velocímetro, medidor, gauge, ponteiro | Medida contra escala; considerar `Grafico Gauge` (extensão DevExtreme instalada no MyBI). Perguntar medida, unidade, mínimo, máximo e eventual meta. Gauge nativo DevExpress existe no produto, mas não é serializado neste perfil. Não inventar EChartsGauge. |
| indicador circular, progresso circular | Pode ser gauge com ponteiro, anel de progresso ou rosca de composição. Perguntar se mostra avanço rumo à meta ou participação de categorias. Não substituir por pizza automaticamente. |
| grade, grid, tabela, listagem | Propor `grid` DevExpress para tabela padrão integrada. Considerar `tabulatorGridItem` quando o usuário pedir explicitamente Tabulator ou seus recursos específicos; confirmar que a extensão está instalada. Não prometer edição, links ou exportação que este pacote não configura. |
| pizza, setores, participação | `EChartsPieLine`; rosca/múltiplos níveis pode corresponder a `EChartsNestedPie`, após confirmar o objetivo. |
| evolução, tendência, série temporal | `EChartsAreaSimple` e campo de data/tempo, não gráfico de categorias sem ordem. |
| ranking, barras, comparação | `EChartsGradientBar` ou `EChartsHorizontalBar`, conforme orientação e rótulos. |
| cascata, waterfall | `EChartsWaterfall2`; confirmar valores aditivos e significado do saldo. |
| cartão, KPI, totalizador | `card`; percentual exige escala e agregação aprovadas. |
| DRE, segmentação, restaurante, posto | Análise/modelo de negócio, não uma biblioteca gráfica. Confirmar modelo pronto versus painel personalizado; seguir formatos.md. |

Uma preferência explícita por DevExpress, ECharts, Tabulator ou modelo pronto deve
ser respeitada. Quando houver alternativas, proponha a compatível com o objetivo,
explique brevemente a diferença e obtenha aprovação. Se faltar formato geral,
pergunte conforme formatos.md; pode reunir as dúvidas numa só mensagem.

Antes de rejeitar: normalizar mentalmente acentos, singular/plural e termos em inglês;
consultar esta referência e catalog.json; distinguir ausência de suporte no pacote
de inexistência no MyBI. Não selecionar um item apenas por semelhança de nome.

`Grafico Gauge` usa `argumentValue` como medida; a extensão padrão usa escala 0–100
e indicador circular. Este perfil ainda não serializa propriedades de escala/meta:
se o usuário precisar de outra escala, explique que exige configuração no MyBI ou
ampliação validada do gerador, em vez de entregar uma escala incorreta.

Casos de verificação: “velocímetro de atingimento 0–100” deve encontrar gauge;
“indicador circular” exige esclarecer intenção; “grade Dev” deve usar grid;
“Tabulator” não deve virar grid silenciosamente; “ECharts gauge” não autoriza inventar
tipo; “DRE pronto” não deve virar gráfico genérico; campos ausentes não são inventados.
