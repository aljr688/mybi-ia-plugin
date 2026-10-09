# Toolbar: contratos compartilhados e modelos prontos — 0.1.20

## Escolha primeiro o componente existente

Quando o pedido corresponder a um modelo pronto (Fluxo de Caixa, WMS, Monitor CRM,
estoque, hospitalar, representantes etc.), procure esse modelo em catalog.json.
Não recrie com Automático/JavaScript nem substitua por gráficos genéricos sem aprovação.
O motor comum não torna modelos intercambiáveis: cada nome tem bindings e propriedades
próprios. Preserve identificadores técnicos apenas no plano/XML, nunca na proposta.

O catálogo contém tipos nativos e modelos de comercial, financeiro, contábil,
hospitalar, representantes, público, crédito, veículos, seguradoras, indústria,
postos, hotéis, logística, educação, patrimônio público, restaurantes, inventário,
assistência técnica, eleições, RH, projetos, jurídico, agro e supermercados.
`toolbar-inventory.json` relaciona TODOS os construtores registrados, inclusive
integrações ocultas e itens manuais. Não confundir registrado com visível na toolbar.

Pesquise `displayName`, nome técnico e grupo; use sinônimos antes de concluir ausência.
Busca local: `python scripts/mybi_catalog.py "fluxo de caixa" --detail`.
Sem --detail retorna índice compacto; sem consulta lista os não ocultos. Use
--include-hidden somente para consultar integrações/itens ocultos. Busca tolera acentos
e espaços. Os identificadores retornados são internos, não títulos para o cliente.
Exemplos: Fluxo de Caixa → FluxoCaixa; demais IDs devem ser consultados, não adivinhados.
Integrações ocultas permanecem para compatibilidade: não prometer que aparecem na toolbar.

## Contrato comum dos modelos JavaScript

São `CustomItem` com `CustomItemType` exato. O plugin gera vínculos/XML e não copia
o código do motor: a extensão precisa existir na versão MyBI instalada no destino.
Em `bindings`, cada propriedade usa uma lista: dimensão = nomes de campos;
medida = objetos `{ "field": "Valor", "summary": "Sum" }`.
`array:false` admite até um elemento; `array:true` admite vários. Não invente campos.
Consulte o label para o significado de cada vínculo.

`required` registra mínimos conhecidos pelo gerador. Lista vazia NÃO prova que o
modelo funciona com qualquer campo: metadados de muitos motores não declaram
obrigatoriedade. Aprovar os campos necessários ao objetivo e explicar recursos sem
dados; não vincular um campo arbitrário só para passar no validador.
Datas exigem granularidade explícita. Agregação deve respeitar o significado do campo.

`customProperties` aceita somente propriedades de `properties` no catálogo: tipos
boolean/string/number, enums e limites exatos. `runtimeDefault` é informativo;
nunca copiá-lo automaticamente para o plano como preferência do cliente.
Propriedades que executam código, URLs/consultas e credenciais foram excluídas do
contrato genérico: explicar quando exigem configuração manual específica.

`toolbar-inventory.json` contém as seções originais de opções por componente.
Isso permite orientar o usuário, mas somente `catalog.json.properties` é autorizado
para geração genérica. Não tratar toda opção documentada como serializável.

## Fluxo de Caixa pronto

Bindings mínimos: Data (data), Tipo (Entrada/Saída), ValorRealizado (medida).
Opcionais conforme objetivo: Categoria/plano de contas, ValorProjetado, SaldoInicial,
Situacao, Cliente, Referencia, Descricao, ColunasGrid (várias dimensões).
Não preencher projetado/saldo inicial com valores inventados. Confirmar emissão,
vencimento ou quitação, granularidade diária/mensal e agregação das medidas.
Uma coluna de saldo repetida pode exigir Max em vez de Sum: confirmar a semântica.
SaldoInicial não integra o card legado de Saldo Acumulado.
Opções incluem layout, cartões, gráfico, rosquinha, lançamentos e suas colunas.
Ative recursos opcionais apenas com dados e finalidade aprovados.

## Nativos básicos adicionados

| Tipo interno | Vínculos |
| --- | --- |
| chart | arguments (dimensões), measures; barras simples |
| pie | arguments, measures; pizza |
| treemap | arguments, measures |
| scatterChart | x e y (uma medida cada), arguments opcionais |
| gauge | actual (uma medida), target opcional |
| listBox | dimensions |
| rangeFilter | argument (uma dimensão), measures; série linha |

Identificadores seguem chartDashboardItem1, chartDashboardItem2 etc., continuando
a sequência existente. Nome descritivo pertence a title. Outras propriedades não
listadas não são implicitamente suportadas. Imagem/texto estático, agrupadores e
mapas nativos com arquivos externos requerem contratos próprios; não improvisar XML.

## Recursos manuais e verificação

Itens sem vínculos de dados (chat/apresentação IA, parâmetros e central de arquivos)
são mapeados no inventário como manual-configuration. Não simular conexão, upload,
consulta, autenticação, cobrança ou execução de IA a partir de um ZIP offline.
Página Web também exige configuração manual de destino externo explicitamente
aprovado: não gerar a URL padrão com dados do cliente. Mapas online podem depender
de serviços externos configurados no MyBI; explicar essa dependência antes da aprovação.
O teste estrutural cobre os contratos e a preservação de vínculos pelo serializador;
não atesta cálculo financeiro, dados reais, aparência ou versão instalada no cliente.
