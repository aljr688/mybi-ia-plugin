# Dashboard HTML

Nome visível Dashboard HTML, CustomItemType exato `DashboardAutomatico`.
Contrato: corpo de `render(root, rows, fields)` em `javascript`, sem declarar/chamar render.
`rows` contém objetos por nome de campo, já agregados pelas dimensões do componente.
`fields` contém a ordem dos campos vinculados. As medidas usam a agregação aprovada.
Não somar médias/percentuais de grupos distintos como se fossem valores aditivos.

Usar JS puro, DOM, SVG e CSS local. Sem bibliotecas, CDN ou rede. `root` é o ponto de
montagem; criar elementos com document.createElement/createElementNS e valores com
textContent. Nunca interpretar dados como HTML/código. Não usar innerHTML para valores.
Não usar eval, Function, import, fetch, cookies, storage, navegação, parent/top/opener,
postMessage, formulários ou SQL. Não chamar insight: essa ação do MyBI pode consumir
IA do servidor e está fora deste fluxo sem acessarIA.

Reproduzir hierarquia/layout da referência, adaptando indicadores aos campos aprovados.
Não copiar dados fictícios nem marcas de fornecedores. Mesmo rows vazio, montar todos
os cards e áreas de gráficos aprovados, com travessão e mensagens locais; não retornar
antes de construir a estrutura nem preencher ausência com zero.

`HtmlTemplate` é alternativa estática para HTML/CSS com placeholders `{Campo}`.
As medidas recebem Name igual ao campo; use esse nome estável sem sufixos de agregação.
Layout, quantidade de cards e estilos seguem o pedido e a referência aprovada.
O gerador aceita somente placeholders de campos vinculados, sem `{Campo:raw}`.
AllowScripts é sempre false; RowMode first e RenderMode single. Não embutir scripts.
Se for preciso vários gráficos e interações locais, preferir DashboardAutomatico.

Antes de gerar, descrever ao usuário os elementos internos. Um CustomItem com 6 KPIs
e 3 gráficos tem 9 elementos visuais, embora tenha apenas um item no XML.
O script verifica sintaxe com `node --check` sem executar o corpo. A qualidade visual
deve ser revisada separadamente; não confundir sintaxe válida com reprodução fiel.
