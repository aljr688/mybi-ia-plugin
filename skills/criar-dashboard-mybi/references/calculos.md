# Campos calculados no XML

O plano aceita calculatedFields: lista opcional de até 40 objetos {name,type,expression}.
type aceita REAL (Double) ou DECIMAL (Decimal). Os nomes não podem repetir campos da fonte (fields).
Inclua campos calculados na aprovação dos campos; não marque aprovação automaticamente.

Exemplo:
{"name":"PercentualMargem","type":"REAL","expression":"Iif(Sum([ReceitaOperacional]) = 0, 0, Sum([MargemContribuicao]) / Sum([ReceitaOperacional]) * 100)"}

Use bindings de medida {field:"PercentualMargem",summary:"Sum"}. DevExpress detecta
a expressão agregada; Sum é o enum de medida aceito, não se grava SummaryType Auto.
A expressão é calculada no agrupamento da consulta. Não somar ou tirar média desses
resultados novamente em JavaScript para obter um total com outro agrupamento.
Para razão geral use a razão entre somas, não Avg dos percentuais de linha.
O exemplo retorna zero quando o denominador é zero; confirme essa regra com o usuário.
Ele produz escala 0..100: não aplicar formatação Percent nesse exemplo sem ajustar a expressão.
Para novos percentuais formatados, prefira a expressão sem *100, retornando fração:
Iif(Sum([ReceitaOperacional]) = 0, 0, Sum([MargemContribuicao]) / Sum([ReceitaOperacional]))
e numericFormats {"PercentualMargem":{"type":"Percent","precision":2,"scale":1}}.
Se a margem também for calculada, expanda receita menos custo diretamente na razão,
pois este perfil não aceita referência a outro campo calculado. Nunca altere a escala
de um campo físico nem de uma fórmula já aprovada sem apresentar a alteração.

Expressões aceitas: campos numéricos da fonte entre colchetes, números decimais,
parênteses, + - * / %, comparações = != <> < > <= >=, Sum/Avg/Min/Max/Count/CountDistinct
com um argumento, Iif com três, IsNull com dois, Abs com um, Round com dois.
Não aceitar SQL, JavaScript, funções externas, campos não aprovados, referências a
outros calculados, agregações aninhadas ou mistura de valor por linha e agregado.
Campos calculados por linha podem usar uma agregação normal no binding.
Outras funções, tipos e dependências exigem ampliação testada, não alteração improvisada.

Serializar em DataSources/SqlDataSource/CalculatedFields/CalculatedField com atributos
Name, Expression, DataType="Double" ou "Decimal" conforme o tipo, DataMember="Dados". Nos DataItems, DataMember
é o nome do campo calculado. O cliente fornece somente os campos físicos da fonte.
