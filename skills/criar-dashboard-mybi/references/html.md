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

`HtmlTemplate` permite HTML/CSS com placeholders `{Campo}` e grade integrada.
As medidas recebem Name igual ao campo; use esse nome estável sem sufixos de agregação.
Layout, quantidade de cards e estilos seguem o pedido e a referência aprovada.
O gerador aceita somente placeholders de campos vinculados, sem `{Campo:raw}`.
Sem htmlGrid, AllowScripts permanece false; RowMode first e RenderMode single.
Não embutir scripts livres no campo html.
Se for preciso vários gráficos e interações locais, preferir DashboardAutomatico.

## Grade dentro do Automático — versão 0.1.19

O componente tem a opção Adicionar Grid. O plugin a reproduz com htmlGrid no item:

```json
"htmlGrid": {
  "columns": [
    {"field":"Cliente","title":"Cliente"},
    {"field":"Receita","title":"Receita","value":"display"}
  ],
  "height": 350
}
```

columns exige 1..100 campos vinculados, sem duplicatas. title é opcional (usa o campo).
value é display (padrão, respeita o texto formatado do binding) ou raw (valor bruto).
height é opcional, inteiro 100..2000 pixels; só definir conforme layout solicitado.
O conteúdo de html é preservado e a grade é acrescentada ao final. Para somente grade,
usar um contêiner vazio no html, como `<div></div>`. Pode estilizar .mybi-template-grid
via css. Não impor fontes, cores, altura ou cards de exemplo.

O compilador gera um script fixo usando a biblioteca de grade já instalada no MyBI,
content.__htData e as colunas aprovadas, e ativa AllowScripts somente nesse caso.
Não há CDN, download, API, script arbitrário, eval ou conexão adicional.
Título e células são tratados como texto; nomes com pontos/espaços não viram caminhos.
Requer Node.js no ambiente de geração para verificar sintaxe.

IMPORTANTE: RowMode=first limita os placeholders do cabeçalho, NÃO a grade. Ela recebe
todas as linhas de __htData, mesmo com RenderMode=single. Não mudar para repeat para
gerar a tabela: isso duplicaria a grade. Não afirmar que o MyBI não oferece o recurso,
nem pedir XML de exemplo para este caso já coberto pelo contrato.
Todas as linhas significa todas as linhas RECEBIDAS pelo componente, respeitando
filtros/agregações da fonte, não necessariamente cada registro físico da consulta.
Medidas continuam usando Name estável e a agregação aprovada, inclusive Sum/Max.
Se a biblioteca estiver ausente, o snippet informa indisponibilidade, sem buscar rede.
Validar visualmente na instalação do cliente; o gerador não testa consultas reais.

Antes de gerar, descrever ao usuário os elementos internos. Um CustomItem com 6 KPIs
e 3 gráficos tem 9 elementos visuais, embora tenha apenas um item no XML.
O script verifica sintaxe com `node --check` sem executar o corpo. A qualidade visual
deve ser revisada separadamente; não confundir sintaxe válida com reprodução fiel.
