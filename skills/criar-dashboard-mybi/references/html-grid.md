# Modelo fixo de grade HtmlTemplate

Este trecho é conteúdo de referência para o XML gerado, não um programa para executar no chat.
Use somente para htmlGrid aprovado. Acrescente `<div class="mybi-template-grid"></div>`
seguido do trecho em `<script>` dentro do HTML serializado. Ative AllowScripts apenas nesse caso.
Substitua __SPECS__ por JSON de objetos {source: campo aprovado, title: título com escape HTML,
mode: display ou raw}; escape <, > e & como sequências Unicode no JSON. Nunca interpole
código fornecido pelo usuário. Substitua __HEIGHT__ por `options.height = N;` com inteiro
100..2000 aprovado, ou por texto vazio. Preserve todo o resto do código. Faça escape XML
no HTML final, sem alterar o JavaScript. Campos devem existir nos bindings.

```javascript
(function () {
  var script = document.currentScript;
  var content = script && script.closest('.ht-content');
  var container = script && script.previousElementSibling;
  if (!content || !container) return;
  if (typeof Tabulator === 'undefined') {
    container.textContent = 'Grade indisponível nesta instalação.';
    return;
  }
  var specs = __SPECS__;
  var dataset = content.__htData || [];
  var rows = dataset.map(function (row) {
    var result = {};
    specs.forEach(function (spec, index) {
      var values = row[spec.mode] || {};
      result['c' + index] = Object.prototype.hasOwnProperty.call(values, spec.source) ? values[spec.source] : null;
    });
    return result;
  });
  var columns = specs.map(function (spec, index) {
    return {title: spec.title, field: 'c' + index, formatter: 'plaintext'};
  });
  var options = {data: rows, columns: columns, layout: 'fitColumns', placeholder: 'Sem dados'};
  __HEIGHT__
  new Tabulator(container, options);
})();
```
