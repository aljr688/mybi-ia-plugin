# Geração direta — GPT e Claude 0.1.25

Esta versão não inclui programas, scripts Python, CLI de geração ou validador próprio.
As regras funcionais são idênticas nas duas plataformas. Não instalar dependências.
Use as ferramentas de criação de arquivos que o ambiente já disponibiliza; elas podem
internamente usar código, mas nenhum script precisa ser instalado pelo cliente.
Se não houver ferramenta de anexos/ZIP, entregue o XML como texto com nome/caminho e
explique a limitação. Não invente link de download nem declare um ZIP criado.

## Base e serialização

Leia contrato.md, mybi-plugin-contract/xml-contract.md e os contratos dos componentes
escolhidos. Exemplos sintéticos estão em assets/serializer-reference.xml.md e
mybi-plugin-contract/fixtures/*.xml.md; exemplos de INI em fixtures/*.ini.md.
Esses documentos contêm o conteúdo original em blocos; retire a cerca Markdown ao
criar o arquivo final .xml/.ini. São exemplos de sintaxe, nunca dados reais/aprovações.
Os catálogos JSON podem estar divididos: abra as parts do índice, sem descartar entradas.
O plan.json documenta decisões; não é executável nem substitui o XML.

Com fonte existente, edite a base exportada preservando DataSources, SQL, parâmetros,
ResultSchema, CalculatedFields e todos os elementos não solicitados. Sem base, não
recrie uma fonte existente. No modo livre use fonte nominal CONEXAO_CLIENTE, nunca
credenciais. Inclua os campos físicos e tipos no schema, e vínculos reais de cada item.
Use o XML do exemplo como estrutura; substitua campos e componentes pelos aprovados.
Não suponha que todo componente do catálogo está instalado no cliente.

## Revisão antes da entrega

- Conferir nomes/tipos/agregações contra campos e componentes aprovados.
- Conferir XML bem formado, escapes de atributos/texto e ausência de DTD/entidades.
- Conferir ComponentName únicos; DataSource/DataMember e referências de DataItems,
  CustomMetadata, LayoutTree e INIs devem resolver; preservar IDs anteriores.
- Conferir CustomProperties como elementos filhos e cardinalidade dos bindings.
- Conferir fórmulas/escala percentual, formatos numéricos, datas e conteúdo visual.
- Comparar fonte, consultas e configurações anteriores contra a base, sem executar SQL.
- Não criar AutomaticJavascript nem scripts livres. HtmlTemplate segue html.md;
  grade integrada usa exclusivamente o modelo de html-grid.md.
- ZIP de dashboard contém DashboardWeb/<nome>.xml, formatacao.ini na raiz e somente
  INIs adicionais autorizados. Nunca incluir plan.json, scripts, backups ou bibliotecas.
  Para vários XMLs seguir compatibilidade-v5.md e seções de INI correspondentes.
- Usar caminhos relativos seguros, sem .., caminhos absolutos, links ou duplicatas.
  Não sobrescrever export original. Abrir o ZIP final e conferir entradas se possível.

Declare apenas verificações realizadas. Revisão por modelo e parse XML não equivalem
à antiga validação por recompilação, nem garantem segurança, importação ou aparência.
Recomende teste de importação/renderização em MyBI compatível com dados de teste.
A proteção efetiva também depende da validação de importação e permissões do MyBI;
regras do plugin não são uma barreira de segurança contra usuários maliciosos.
