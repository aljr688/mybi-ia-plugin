"""Generate a fixed, local grid snippet; never accept arbitrary template scripts."""
import html
import json
import re
import shutil
import subprocess

def require(ok, message):
    if not ok: raise ValueError(message)

def grid_markup(config, fields):
    require(isinstance(config, dict) and not set(config)-{'columns','height'}, 'htmlGrid: propriedades inválidas')
    columns=config.get('columns')
    require(isinstance(columns,list) and 1<=len(columns)<=100, 'htmlGrid exige 1..100 colunas')
    names=set(); specs=[]
    for column in columns:
        require(isinstance(column,dict) and not set(column)-{'field','title','value'}, 'Coluna da grade inválida')
        field=column.get('field'); title=column.get('title',field)
        require(isinstance(field,str) and field in fields and field not in names, 'Grade exige campo vinculado único: '+str(field))
        require(isinstance(title,str) and 0<len(title)<=200 and not re.search(r'[\x00-\x1f\ud800-\udfff\ufffe\uffff]',title),'Título de coluna inválido')
        mode=column.get('value','display'); require(mode in {'display','raw'},'Valor da coluna deve ser display ou raw')
        names.add(field); specs.append({'source':field,'title':html.escape(title),'mode':mode})
    height=config.get('height')
    require(height is None or type(height)is int and 100<=height<=2000,'Altura da grade deve ser 100..2000 pixels')
    encoded=json.dumps(specs,ensure_ascii=True).replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')
    script=r'''(function () {
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
})();'''.replace('__HEIGHT__','options.height = '+str(height)+';' if height is not None else '').replace('__SPECS__',encoded)
    node=shutil.which('node'); require(node is not None,'Node.js necessário para validar a grade Automático')
    result=subprocess.run([node,'--check'],input=script,text=True,capture_output=True,encoding='utf-8',timeout=20)
    require(result.returncode==0,'Sintaxe da grade inválida: '+result.stderr[:500])
    return '<div class="mybi-template-grid"></div>\n<script>\n'+script+'\n</script>'
