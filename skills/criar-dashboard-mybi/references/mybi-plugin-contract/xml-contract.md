# XML — perfil portátil

Dashboard contém Title, DataSources, Items e LayoutTree. Item referencia
DataSource por ComponentName e DataMember pelo nome da consulta existente.
DataItems define Dimension/Measure com DataMember e DefaultId. Measure usa SummaryType.
Bindings de CustomMetadata apontam para DefaultId com ItemType Dimension ou Measure.
Coleções usam Item1, Item2 etc. LayoutItem aponta DashboardItem para ComponentName.
CustomProperties contém elementos filhos, não atributos arbitrários.
NumericFormat informa FormatType, Precision, Unit=Ones e IncludeGroupSeparator=true;
moeda usa CurrencyCultureName=pt-BR. Percent recebe fração, não valor multiplicado por 100.
O perfil não oferece filtros, parâmetros novos, paletas nem regras condicionais novas.
Preservar os existentes no XML-base. Datas: perguntar dia/horário, ano-mês ou ano;
formatação não equivale a agrupamento. Não inventar DateTimeGroupInterval no plano.
Para detalhes operacionais, consultar ../contrato.md e ../calculos.md.
