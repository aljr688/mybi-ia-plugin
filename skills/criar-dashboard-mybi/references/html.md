# Automático (Template HTML) — V5

Identificador exato HtmlTemplate. HTML/CSS e placeholders de campos vinculados.
Não gerar DashboardAutomatico nem AutomaticJavascript, mesmo no catálogo histórico.
Não somar médias, percentuais nem acumulados repetidos como valores aditivos.

Sem scripts livres, CDN, APIs, rede ou dados fictícios. Ícones podem usar CSS local.
Para interações fora do contrato, explicar a limitação e compor componentes nativos.

Reproduzir hierarquia/layout da referência, adaptando indicadores aos campos aprovados.
Não copiar dados fictícios nem marcas de fornecedores; não preencher ausência com
zero. Planejar cards legíveis sem overflow que esconda valores.

`HtmlTemplate` permite HTML/CSS com placeholders `{Campo}` e grade integrada.
As medidas recebem Name igual ao campo; use esse nome estável sem sufixos de agregação.
Layout, quantidade de cards e estilos seguem o pedido e a referência aprovada.
O gerador aceita somente placeholders de campos vinculados, sem `{Campo:raw}`.
Sem htmlGrid, AllowScripts permanece false; RowMode first e RenderMode single.
Não embutir scripts livres no campo html.
Para vários gráficos e interações, compor com gráficos/filtros nativos suportados.

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

Antes de gerar, descrever os elementos internos do Template e os componentes nativos
separadamente. Não montar gráficos com JavaScript livre dentro do Template.
Somente o script fixo htmlGrid passa por `node --check`, sem executar seu corpo.
A qualidade visual deve ser revisada separadamente; sintaxe não prova renderização.
