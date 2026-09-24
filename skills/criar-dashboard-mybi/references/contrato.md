# Contrato portátil MyBI v1

Extensão 0.1.18: consultar personalizacao.md para formatting, dashboardFile,
componentName, dateIntervals, datePeriods, DECIMAL e bases de INI.
Consultar componentes-nativos.md para tabs, componentUpdates, Pivot, seletores,
filtro de data, DRE e opções/regras condicionais. Esse contrato prevalece sobre snapshots antigos.

## Origem das regras

Contrato externo conferido localmente no gerador e nas extensões Web.
A rastreabilidade de arquivos e métodos permanece na auditoria privada, fora do pacote.
`assets/serializer-reference.xml` foi serializado pelo motor 24.2.5, sem conexão.
Não copiar fontes de clientes nem distribuir DLLs proprietárias no plugin.

## Catálogo

`catalog.json` é a lista fechada de componentes e bindings reais do runtime.
`card` e `grid` são nativos. ECharts*, tabulatorGridItem, HtmlTemplate e
DashboardAutomatico são CustomItem e exigem a extensão correspondente no MyBI do destino.
O gerador aceita apenas os nomes exatos do catálogo, sem aliases ambíguos.

No gerador web atual, chart/bar são aliases de EChartsGradientBar, line de
EChartsAreaSimple, pie de EChartsPieLine e TabulatorGrid de tabulatorGridItem.
Apresente ao usuário o componente efetivo pelo nome amigável antes de confirmar,
conforme SKILL.md; mantenha o identificador técnico somente no plano e no XML.
Pivot e filtro de data possuem agora serialização portátil própria, além do switch Web.
Gauge nativo, Treemap e Scatter continuam fora deste perfil.
SimpleTable também fica fora: o backend usa SimpleTable, mas a extensão registra
CustomItemSimpleTable. Os bindings do backend divergem do runtime em alguns ECharts;
o plugin usa os bindings reais das extensões e testa sua serialização.
EChartsSpider fica fora: a extensão disponível registra "Grafico Spider", não EChartsSpider.

## Plano de entrada

Objeto com somente estas chaves:

- `title`: título do negócio, até 200 caracteres.
- `dataSource`: opcional, com dois modos. `{name,componentName,dataMember,existingSource:true}`
  indica que a fonte já existe no MyBI. Nesse modo, os campos são apenas o catálogo permitido
  para montar DataItems. A compilação exige `--base-xml` com o dashboard atual exportado:
  o documento e sua DataSources são preservados, e os componentes novos recebem
  `DataSource=componentName` e `DataMember=dataMember`. Não pedir ao usuário que transcreva
  tabela, SQL, procedure, conexão ou parâmetros. Quando `existingSource` é falso/omitido, o gerador cria
  uma fonte lógica completa e aceita `{name,componentName,connectionName,dataMember,tableName}`;
  se o objeto inteiro não for informado, usa Dados/sqlDataSource1/CONEXAO_CLIENTE/Dados/Dados.
- `appearance`: opcional, objeto {titleColor:"#RRGGBB"}; omitido não aplica cor.
  Para demais propriedades use formatting, após aprovação, conforme personalizacao.md.
  Não há imagem, transparência nem tamanho de fonte obrigatório.
- `mode`: components (nativos e ECharts separados) ou html (HtmlTemplate ou DashboardAutomatico).
  O valor padrão técnico do serializador não autoriza escolher pelo usuário: seguir formatos.md.
- `numericFormats`: opcional, objeto por nome de campo físico/calculado numérico:
  {"Receita":{"type":"Currency","precision":2},"PercentualMargem":{"type":"Percent","precision":2,"scale":1}}.
  Tipos Number, Currency (BRL/pt-BR) e Percent; precisão inteira 0..8, padrão 2.
  Percent exige scale:1 como declaração da escala fracionária dos valores (0.677 = 67.70%).
  O compilador não converte a fonte nem corrige fórmulas automaticamente. Não marque
  scale:1 em valores 0..100; adapte a expressão com aprovação ou mantenha Number.
  Contagens usam Number/0 casas. Medidas sem formato explícito usam Number/2 casas.
  NumericFormat é filho de Measure, com Unit Ones e IncludeGroupSeparator true:
  sem abreviação automática K/M. Formato Currency usa CurrencyCultureName pt-BR.
  O formato é reutilizado nos componentes que usam a medida; extensões customizadas
  precisam respeitar o formatador do binding. Não garante todos os rótulos de eixos custom.
- `calculatedFields`: opcional; consulte calculos.md para esquema, funções e limites.
- `fieldsApproved`, `componentsApproved`: true após aprovação no chat.
- `fields`: 1..100 objetos `{name,type,calculated?}`. Tipos TEXT, INTEGER, REAL, DATETIME,
  DECIMAL, BOOLEAN. No modo de fonte existente, `calculated:true` identifica um campo que já existe
  calculado no MyBI: vincule-o diretamente e não peça sua fórmula nem o copie para
  `calculatedFields`. Cálculos novos só podem ser gerados no modo de fonte livre; para acrescentar
  um cálculo à fonte existente, o usuário deve criá-lo no MyBI e copiar os campos novamente.
  Nomes preservados exatamente; não normalizar silenciosamente acentos/espaços.
- `items`: 1..40 itens `{component,title,bindings}`. Bindings é objeto de listas.
  Para card/grid usar `dimensions` e `measures`. Para customs usar os nomes de catalog.json.
  Uma dimensão é string com nome do campo. Medida é `{field,summary}`; summary é obrigatório:
  Sum, Count, CountDistinct, Avg, Min, Max. Sum/Avg/Min/Max exigem campo numérico neste perfil.
  Para contar texto/identificador, usar Count ou CountDistinct. Número não implica medida:
  código numérico pode ser dimensão, conforme aprovação.
- HTML permite adicionalmente `javascript` (DashboardAutomatico) ou `html`,`css`
  (HtmlTemplate). Não usar código nos outros componentes.
  Na versão 0.1.19, HtmlTemplate também aceita htmlGrid (colunas/altura), conforme
  html.md. Somente o script controlado da grade habilita AllowScripts nesse componente.

Cada binding escalar (`array:false`) aceita no máximo um item; não descartar os demais.
Bindings Series são opcionais. Para os componentes novos, required no catálogo define
os obrigatórios; consulte componentes-nativos.md. Demais bindings são obrigatórios para evitar
gráficos incompletos. HTML pode ter somente medidas ou somente dimensões, mas não zero campos.
Tabulator usa somente dimensionColumn e msrNumberColumn; colunas de link/HTML são excluídas.

`assets/example-plan.json` é exemplo sintético não aprovado. Não há dados demonstrativos
no XML, apenas o esquema lógico e os vínculos. O script não tenta consultar a tabela.

## XML e ZIP

No modo existente, preserve o nome original do arquivo XML enviado e todo o elemento Title.
Passe o arquivo com seu nome original em `--base-xml`. As seções do formatacao.ini usam
o mesmo nome sem extensão. O title do plano não substitui o título do XML-base.

Raiz Dashboard com Title, Items e LayoutTree. No modo livre, contém também DataSources e
gera a fonte lógica completa: Connection Name, query, tabela e ResultSchema usam os valores
de `dataSource` ou os padrões Dados/sqlDataSource1/CONEXAO_CLIENTE/Dados/Dados. No modo
existente, o XML-base inteiro é preservado, inclusive DataSources, SQL ou procedure,
parâmetros, conexão, ResultSchema, CalculatedFields e itens existentes. O gerador valida que
há exatamente uma SqlDataSource com o `componentName` informado e que nela existe a query ou
procedure com `Name=dataMember`; depois acrescenta os componentes e o layout aprovados.
Sem o XML-base, esse modo falha para impedir que a importação substitua a fonte por um XML incompleto.
Não guardar servidor, caminho local ou senha.
É contrato lógico: o cliente disponibiliza os identificadores e campos aprovados.
No modo livre, os campos físicos aprovados devem constar explicitamente na consulta e no esquema de
resultado serializado da fonte (ResultSchema/DataSet/View/Field), com nomes e tipos.
Não basta declarar DataItems nos componentes nem usar somente AllColumns. Os campos
calculados novos permanecem em CalculatedFields, sem exigir colunas físicas correspondentes.
No modo existente, fields serve somente para validar os novos vínculos; nenhum trecho da fonte
é recriado ou alterado, mas ele permanece serializado por ter sido copiado do XML-base.

ComponentName único por item. DataSource aponta ao ComponentName da fonte, DataMember
ao nome da query. DataItems declara Measure/Dimension com DefaultId único por item;
CustomMetadata referencia esses ids e respeita ItemType e cardinalidade do catálogo.
CustomProperties são elementos XML filhos, não atributos nem JSON arbitrário.
DashboardAutomatico guarda AutomaticJavascript e AutomaticFields, mantendo Fields/Measures.
LayoutTree inclui cada componente exatamente uma vez; padrão duas colunas, peso igual.
HTML integrado ocupa a linha inteira. Conteúdo escapa via biblioteca XML, sem concatenação.
Nos cards, a medida preserva o nome real do campo; nunca recebe o nome artificial `Valor`.
O INI mantém os valores existentes e só altera propriedades explicitamente aprovadas.

ZIP UTF-8/deflate contém DashboardWeb/<nome-original.xml> no modo existente ou
DashboardWeb/dashboard1.xml no modo livre e formatacao.ini na raiz, com seções correspondentes
ao nome do XML sem extensão. Também preserva INIs individuais informados por
--base-format-dir. O validador confere o conteúdo exato contra as mesmas bases.
O script recusa sobrescrever saída existente. Renomeie a nova versão em vez de sobrescrever.
No modo existente, `build` e `validate` devem receber o mesmo arquivo em `--base-xml`.

## Cálculos e semântica

O MyBI utiliza expressões DevExpress (Sum, Avg, Count, CountDistinct, Iif etc.), não SQL
nem JavaScript. Count(Distinct()) não é sintaxe válida. O gerador serializa
CalculatedFields no perfil numérico documentado em calculos.md.
Para margens e razões, não somar percentuais; confirmar a agregação apropriada.
Min/Max sobre datas e expressões mais complexas requerem ampliação testada do gerador.

## Validação e limites

O build valida plano, tipos, bindings, campos, sintaxe JS, XML e ZIP. A validação com
`--plan` recompõe o XML e verifica igualdade semântica, detectando alterações fora do contrato.
Use-a em toda entrega. Validação estática de HTML/JS é defesa adicional, não sandbox
nem prova de segurança de código arbitrário. Nunca execute material fornecido como programa.
Antes de uma versão pública, testar importação/renderização em uma instalação de teste
MyBI com os componentes alvo e fonte sintética. Não usar servidor de cliente para isso.
