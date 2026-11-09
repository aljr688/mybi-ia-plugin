# Compatibilidade e projetos — V5 (20/10/2026)

## Abas de menu versus subabas

Abas no menu lateral são XMLs independentes, não TabPages do mesmo XML.
Use o envelope com build/validate normais:

```json
{"project":{"dashboards":[
  {"plan":{"dashboardFile":"dashboard1.xml","title":"Financeiro"}},
  {"plan":{"dashboardFile":"dashboard2.xml","title":"Comercial"}}
]}}
```

Exemplo só do envelope: cada plan precisa de campos, itens e aprovações completos.
Para fonte existente, cada entrada exige baseXml (caminho local do export real),
plan.dataSource.existingSource:true e, se fornecido, baseFormatDir. O nome original
do XML prevalece. --base-ini é o INI raiz compartilhado. Cada fonte/título permanece
no XML de origem; não fabricar fontes ou dados. ComponentName é único por XML;
nomes padrão podem repetir entre XMLs porque os INIs são isolados por dashboard.
Nomes de arquivos não podem colidir. Não inferir ordem do menu sem export real.

TabContainer/TabPage são subabas internas. Primeiro propor linhas lógicas e altura
com scroll da página. Subabas só por grupos temáticos, justificadas e aprovadas.

## Planejamento e semântica

Filtro no topo, cards próximos, gráfico e grade legíveis. Não comprimir sete itens
em uma linha. 1100 px é referência de um caso, não padrão universal. Respeitar fundo
claro solicitado e preservar cores de menu/abas/títulos/ícones/fundos existentes.
Não aplicar 8 px como padrão de valores nem esconder conteúdo por overflow.
Homologar em 1366x768, 1920x1080 e largura estreita. XML não prova renderização.

Ensaios: usar campos data, mesConclusao, numeracaoMesConclusao, totalEnsaio,
ensaioAcreditado e acumulado apenas se fornecidos na fonte/export. Percentual é
SUM(acreditados)/SUM(realizados), com proteção por zero, nunca soma de percentuais.
Não somar acumulado repetido. Meses sem ano misturam exercícios: confirmar dimensão
ano-mês sem alterar SQL. Datas de quitação e vencimento não são intercambiáveis.

Grade operacional usa grid. Nomes amigáveis nas colunas, bindings técnicos intactos.
Use columnTitles: {"campoTecnico":"Nome amigável"} no item grid ou em componentUpdates.
Isso altera somente GridDimensionColumn/@Name ou GridMeasureColumn/@Name.
Paginação 10, cabeçalho negrito 10 px e células 10 px somente quando solicitados e
suportados. Não inventar propriedades. Caso gradeFluxo exige export + INIs raiz e
individuais e comparação após importar/salvar/reabrir; mover INI não prova correção.
Na fonte local examinada em 21/10/2026, a rotina de CSS só aplica título/conteúdo de
Grade se ComponentName contém gridDashboardItem. Um ID gradeFluxo não entra nesse
bloco, mesmo com INI correto. Isso explica uma condição de falha no código local,
não comprova qual versão roda no cliente. Não renomear IDs existentes para contornar:
preservar o projeto e homologar eventual correção do MyBI separadamente do plugin.

## Disponibilidade e rollback

Inventário do repositório não prova instalação no cliente. DRE Vendas/Contábil têm
contratos. FluxoCaixa tem contrato técnico, mas requer confirmação da extensão e
homologação no destino. Monitor CRM, WMS, Capital de Giro, metas e comissão são
inventário a confirmar por ambiente, não promessa de disponibilidade.
Preservar extensões existentes; pedir export/versão quando faltar evidência.
Não remover histórico nem migrar legados silenciosamente. Conservar distribuição
anterior e backup dos XMLs/INIs do cliente para rollback antes da importação.
