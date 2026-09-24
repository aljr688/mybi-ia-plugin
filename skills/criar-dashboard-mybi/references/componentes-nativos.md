# Componentes e regras — contrato 0.1.18

Leia junto de personalizacao.md. As chaves abaixo são internas; na conversa use
Matriz, Grade, Seletor, Filtro de data, Abas e DRE. Não exiba marcas de fornecedores.
Contrato obtido por serialização e reabertura no motor local 24.2.5, sem banco.

## Componentes adicionais

Todos usam items, bindings com listas e os mesmos campos aprovados. Medida continua
{field,summary}; dimensão é nome literal. Não substituir componentes prontos por
Automático sem aprovação. Todos aceitam componentName explícito e parentContainer.

- pivot: rows e columns são dimensões opcionais; measures é obrigatório.
  options: ShowColumnGrandTotals, ShowRowGrandTotals, ShowColumnTotals, ShowRowTotals,
  AutoExpandColumnGroups, AutoExpandRowGroups (booleanos); LayoutType Compact/Tabular.
  RowTotalsPosition Top/Bottom e ColumnTotalsPosition Near/Far.
- comboBox: dimensions obrigatório; options ComboBoxType Standard/Checked,
  EnableSearch e ShowAllValue booleanos.
- dateFilter: dimension obrigatório, exatamente um campo DATETIME; dateIntervals
  precisa registrar a granularidade escolhida. datePeriods funciona também em filtros
  novos, apontando para componentName explícito; não aplicar períodos não pedidos.
- DREContabil: Codigo e Conta dimensões; ValorAtual medida, todos obrigatórios.
  Opcionais: ValorAnterior e Ordem medidas, TipoLinha dimensão.
- DREVendas: Data dimensão DATETIME e Vendas medida obrigatórias. CMV, ImpostosValor,
  InadimpValor, DespesasAdmValor, MetaMesValor, PromoQuantidade e PromoValorUnitario
  medidas opcionais; PromoProduto dimensão opcional; DimensoesGrupo lista de dimensões.

Todas as dimensões de data exigem dateIntervals. Pergunte data exata, dia, ano/mês,
trimestre/ano ou ano; não assuma agrupamento anual. Na DRE gerencial confirme ainda
a compatibilidade dessa granularidade com a análise mensal pedida.

## Opções DRE, somente se solicitadas

customProperties da contábil: MostrarAnaliseVertical, MostrarComparativo, MostrarKPIs
(booleanos), CodigoReceitaBase e TituloRelatorio (texto).
Da gerencial: CMVPercentDefault, ImpostosPercent, InadimpPercent, DespesasAdmDefault,
DiasNoMes (números; dias inteiro 1..31), ShowCards e ShowPizza (booleanos).
Ambas: PrimaryColor, NegativeColor, PositiveColor em #RRGGBB.
Omitir propriedades não solicitadas; nunca inventar percentuais, metas ou custos.
InadimpValor é percentual apesar do nome: confirmar unidade no contexto do runtime.
Essas extensões devem estar instaladas no MyBI do destino. Podem mostrar demonstração
quando não recebem dados: não apresentar esses números como dados reais nem como teste
da consulta. Verificar após importação com a fonte real do cliente.

## Ordenação e interação

sort: {"Categoria":"Descending"} ou Ascending, somente dimensões vinculadas.
Grade aceita totals:{"Receita":["Sum","Avg"]}; opções Auto, Count, Min, Max, Avg, Sum.
Para dimensões, somente Count. [] remove os totais daquela coluna explicitamente.
Totalizadores não são agregações da fonte: confirme ambos separadamente.
interactivity em Pivot/Filtro de data: IgnoreMasterFilters booleano.
Em Grade: IgnoreMasterFilters e MasterFilterMode None/Single/Multiple.
Não escolher isolamento ou filtro mestre sem confirmar o comportamento desejado.

## Abas

No plano, tabs é uma lista de grupos:

```json
{"tabs":[{"componentName":"abas","title":"Análises","pages":[
  {"componentName":"resumo","title":"Resumo"},
  {"componentName":"detalhes","title":"Detalhes"}
]}]}
```

Cada item que deve aparecer dentro de uma aba usa parentContainer:"resumo" ou
"detalhes". Cada página precisa ter pelo menos um item. Identificadores únicos em
todo o dashboard; não é o título visual. O gerador cria TabContainer, Pages/Page,
ParentContainer e LayoutTabContainer/LayoutTabPage consistentes. Itens sem pai ficam
fora do grupo. As abas novas são acrescentadas; abas existentes são preservadas.
Não transferir itens existentes entre abas silenciosamente.

## Formatação condicional nativa

rules é lista por item Grade/Pivot, no máximo 30. Cada regra exige name único, field
vinculado e kind. As cores/condições vêm do pedido ou referência, nunca de padrão fixo.
style aceita background e/ou foreground #RRGGBB, ou apenas icon:
IndicatorGreenCheck, IndicatorRedCross, IndicatorYellowExclamation.
applyToRow booleano é exclusivo da Grade.

- kind:value: condition Greater, GreaterOrEqual, Less, LessOrEqual, Equal, NotEqual,
  Between, NotBetween, BetweenOrEqual, NotBetweenOrEqual ou ContainsText. value
  numérico/texto; intervalos exigem value2. Texto/status usa Equal/ContainsText.
- kind:expression: expression é comparação simples de campo vinculado com número
  ou texto entre aspas simples, como `[Atraso] > 0` ou `[Status] = 'Vencido'`.
  Expressões compostas/funções não pertencem ao subconjunto validado; não fingir suporte.
- kind:ranges: valueType Number/Percent; ranges contém 2..10 objetos {value,style}
  com limites crescentes. Permite faixas coloridas ou ícones.
- kind:gradient: mesma estrutura de limites; style com background obrigatório
  apenas na primeira e última faixa; as intermediárias não recebem style.

```json
{"rules":[{"name":"Atrasados","field":"Atraso","kind":"value",
"condition":"Greater","value":0,"applyToRow":true,
"style":{"background":"#FFF0D0","foreground":"#802000"}}]}
```

As cores acima são somente exemplo, não regra de estilo. Confirme fronteiras das
faixas e se limites são valores absolutos ou percentuais. Atraso exige campo real
ou cálculo aprovado; não inventar datas/SQL para sustentar a regra.

## Atualizar componente existente

Com existingSource:true e --base-xml, componentUpdates mapeia ComponentName real para
options, interactivity, sort, totals, customProperties e/ou rules. Exemplo:

```json
{"componentUpdates":{"matrizReal":{"options":{"ShowRowTotals":false}}}}
```

items pode ser [] para alteração pontual. Somente propriedades fornecidas mudam;
consulta, DataSources, layout e demais itens permanecem. rules, quando fornecido,
substitui a lista inteira daquele componente: ler as regras atuais e confirmar o
conjunto final, incluindo todas as que devem permanecer; [] remove todas explicitamente.
Se o componente possui o mesmo campo vinculado várias vezes, a atualização é recusada
por ambiguidade. Não renomear ou substituir identificadores para contornar essa proteção.

## Limites e validação

Inclui testes estruturais, reabertura e reserialização local de exemplares. Isso não
equivale a teste visual no navegador nem validação contábil/SQL. Gerar ZIP e validá-lo
com o mesmo plano e bases. Não publicar nem acessar cliente automaticamente.
Demais modelos de segmentos, outros gauges, expressões avançadas e alterações de SQL
continuam exigindo contrato específico; isso não limita os recursos já implementados.
