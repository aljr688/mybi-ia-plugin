# Personalização por solicitação — versão 0.1.18

## Prioridade, sem estética obrigatória

Pedido explícito > referência indicada > aparência existente quando pedida preservação
> padrão do MyBI > omitir/preservar. Não transformar exemplos ou fixtures em padrões.
Não impor branco, transparência, fonte 26, imagem de fundo nem quantidade de colunas.
Referências não aprovam automaticamente mudanças. Apresente escopo e obtenha aprovação.
Uma cor automática pode ser proposta conforme contraste, mas não aplicada sem aprovação.

## Plano e arquivos de formatação

`formatting` é opcional: `{dashboard:{chave:valor}, components:{ComponentName:{chave:valor}}}`.
Valores são strings; vazio significa não configurado. A lista de chaves aceitas é
validada por mybi_formatting.py. `appearance.titleColor` continua aceito como atalho
para a cor geral; não combine ambos para a mesma propriedade.
`dashboardFile`, opcional no modo livre, define o nome real, por exemplo dashboard4.xml.
Com `--base-xml`, sempre prevalece o nome original desse arquivo.
`componentName`, opcional por item novo, permite identificar precisamente a seção.
Não reutilize identificadores existentes. Se omitido, o gerador aloca nomes únicos.

Seções: [nomeDoXmlSemExtensao] e [nomeDoXmlSemExtensao_ComponentName]. Não presumir N.
Para manter formatação, peça o formatacao.ini e os INIs individuais da aba.
Use `--base-ini formatacao.ini` e, se houver, `--base-format-dir pastaDaAba` em build
e validate. Essa pasta contém os arquivos `<ComponentName>.ini`, sem outros dados.
O ZIP inclui esses arquivos em formatacoes/<nomeDoXml>/<ComponentName>.ini.
Arquivos individuais existentes são preservados; propriedades alteradas também são
sincronizadas no INI geral. Não criar arquivo individual sem necessidade.
Peça conversão para UTF-8 se o INI não puder ser lido; não adivinhe a codificação.
Edição somente de aparência de um XML existente permite `items: []`.

Cor aceita #RRGGBB ou rgb(R, G, B); booleanos usam true/false; tamanhos positivos.
Imagens devem existir na instalação; o pacote não incorpora imagens arbitrárias.
Nunca preencher valores vazios só para completar o arquivo.

### Dashboard e títulos

No bloco da aba: dashboard-color-background; dashboard-title-font-bold,
dashboard-title-font-italic, dashboard-title-font-underline, dashboard-title-font-color,
dashboard-title-font-size, dashboard-title-font-color-background,
dashboard-title-icon-color; dashboard-menu-color, dashboard-menu-icon-color,
dashboard-menu-text-color, dashboard-menu-text-dash-color,
dashboard-menu-left-background-transparency, leftwidth e dashboard-altura.

### Todos os componentes

ativar-configuracao-geral-componente-geral habilita as opções gerais:
component-title-centralizar-geral, component-title-font-bold-geral,
component-title-font-italic-geral, component-title-font-underline-geral,
component-title-font-color-geral, component-title-font-size-geral,
component-title-color-icon-geral, component-title-color-background-geral,
component-aplicar-background-transparency-geral,
component-remover-background-transparency-title-geral e component-color-background-geral.
Somente habilitar opções gerais se o usuário pedir esse escopo. Elas podem prevalecer
sobre opções individuais. Se houver conflito com uma alteração pontual, esclareça
antes de desabilitar a configuração geral; não altere outros componentes silenciosamente.

### Um componente

title-font-center, title-font-bold, title-font-italic, title-font-underline,
title-font-color, title-font-size, title-font-color-background, title-icon-color,
background-transparency, remove-background-transparency-title,
extend-background-color-to-title, color-background, color-marcador-background,
color-moldura-chart, apply-background-image-title, componente-modo-image-background.
As propriedades específicas só têm efeito em componentes compatíveis; não prometer
cor de moldura em um cartão. Modos de imagem além de default exigem contrato confirmado.

### Conteúdo de grades e pivôs

title-font-{bold,italic,underline,color,size,color-background,align}-conteudo e
title-font-{bold,italic,underline,color,size,color-background,align}-titulo-tabela.
Cada expansão é uma chave, não grave as chaves com chaves literais. Alinhamentos:
left, center, right, justify. Use os valores pedidos, nunca tamanhos fixos.

## Datas, cálculos e medidas estáveis

Cada item pode ter `dateIntervals:{Data:"MonthYear"}`. Campo deve ser DATETIME e
estar vinculado como dimensão. Valores: None (exata, sem agrupamento), DayMonthYear,
MonthYear, QuarterYear, Year. Pergunte granularidade e apresentação, sem assumir Ano.
Agrupamento não configura uma máscara de exibição personalizada.

Campos físicos aceitam DECIMAL além dos tipos anteriores. Novos cálculos numéricos
aceitam REAL (Double) e DECIMAL (Decimal). A fórmula numérica não vira texto; Decimal
não significa percentual. Fórmulas booleanas/inteiras exigem extensão validada do perfil.
numericFormats decide a apresentação independentemente do tipo; percentuais usam fração.

Medidas do Automático recebem `Name` igual ao campo aprovado e o HTML usa `{Campo}`.
Não depender de sufixos automáticos de agregação. O perfil ainda recusa duas agregações
conflitantes do mesmo campo em um item; não inventar aliases não suportados.
Quantidade de indicadores, colunas, espaçamento, cabeçalho e responsividade devem
acompanhar pedido/referência e legibilidade, não o layout de outro projeto.

## Períodos relativos em filtro novo ou existente

`datePeriods:{ComponentName:{periods:["currentYear","currentMonth","last12Months"],selectedIndex:1}}`
exige DateFilter novo ou DateFilter/RangeFilter no XML-base com esse identificador. Selecionar somente
os períodos pedidos. O índice começa em zero e precisa estar dentro da lista.
Se já há seleção no filtro, confirme a nova seleção antes de substituir a lista.
O gerador preserva os vínculos existentes e grava DateTimePeriods/DateTimePeriod:
currentYear usa StartLimit/FlowDateTimePeriodLimit Offset=1 e EndLimit sem Offset;
currentMonth usa Interval=Month e Offset=1 no início; last12Months usa Month e -12.
Em ambos os períodos mensais o fim usa Month sem Offset. Não calcular datas literais
nem reinterpretar esses offsets como deslocamentos genéricos.

## Componentes, regras condicionais e consultas

Considere DRE pronto para análise gerencial, Pivot para matriz, Grade para detalhe,
ComboBox e filtro de data quando úteis, TabContainer/TabPage para organizar conteúdos.
Consulte componentes-nativos.md para o contrato implementado. Preserve componentes existentes,
ParentContainer, referências, layout, regras condicionais e filtros do XML-base.

A versão 0.1.18 cria Pivot, ComboBox, DateFilter, abas e DRE contábil/gerencial,
com regras de texto/fundo/ícones/escalas/faixas em Grade/Pivot. componentUpdates
adapta propriedades e regras de itens existentes com base no ComponentName real.
Não substitua o componente pronto por Automático ou gráfico genérico sem aprovação.

Preserve SQL funcional, parâmetros e ResultSchema da fonte existente. O plugin não
executa consultas. Se for solicitado aconselhamento SQL, use somente nomes informados,
mudanças mínimas e leitura SELECT; peça detalhes de banco/conector e campos ausentes.
Não gerar comandos destrutivos ou tabelas temporárias como diagnóstico. Uma consulta
proposta não foi validada no ambiente do cliente. Alterações de SQL/schema no XML-base
não são feitas pelo gerador atual; peça a base exportada após validação no MyBI.

## Verificação final

Conferir nomes de XML/componentes, INIs individuais, campos e tipos, nomes de medidas,
granularidades, índices de períodos, formato numérico e preservação do XML-base.
O validador compara a saída com o plano e as mesmas bases e rejeita arquivos extras.
Isso não testa SQL real, semântica financeira ou renderização no ambiente do cliente.
Não publicar automaticamente. Distribuir somente o plugin GPT solicitado.
