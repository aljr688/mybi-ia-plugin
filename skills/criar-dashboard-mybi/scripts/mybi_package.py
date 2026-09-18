"""Offline MyBI package compiler. Python stdlib only; never connects to MyBI or AI."""
from __future__ import annotations
import argparse
import copy
import io
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CATALOG = json.loads((BASE / 'references/catalog.json').read_text(encoding='utf-8'))
TYPES = {'TEXT', 'INTEGER', 'REAL', 'DATETIME', 'BOOLEAN'}
SUMMARIES = {'Sum', 'Count', 'CountDistinct', 'Avg', 'Min', 'Max'}
ENTRY = 'DashboardWeb/dashboard1.xml'
FORMAT_ENTRY = 'formatacao.ini'
MAX_SIZE = 2_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, label, maximum=200):
    require(isinstance(value, str) and 0 < len(value.strip()) <= maximum, label + ': texto inválido')
    require(not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]', value), label + ': caractere XML inválido')
    return value


def keys(obj, allowed, label):
    require(isinstance(obj, dict), label + ': objeto esperado')
    require(not set(obj) - set(allowed), label + ': propriedades não suportadas: ' + str(set(obj) - set(allowed)))


def unique_json(pairs):
    result = {}
    for key, val in pairs:
        require(key not in result, 'Chave JSON duplicada: ' + key)
        result[key] = val
    return result


def load_plan(path):
    require(Path(path).stat().st_size <= MAX_SIZE, 'Plano excede 2 MB')
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_json)


def check_javascript(code):
    text(code, 'javascript', 100_000)
    inspected = code.replace('http://www.w3.org/2000/svg', '').replace('http://www.w3.org/1999/xlink', '')
    require(not re.search(r'\b(fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|eval|Function|import|require|process|insight|opener|postMessage|location|localStorage|sessionStorage|indexedDB|globalThis|window|self|parent|top|constructor|prototype|__proto__|cookie)\b|https?://|<script|\bon\w+\s*=|\.(?:submit|requestSubmit)\s*\(', inspected),
            'JavaScript contém recurso proibido ou exige revisão para este perfil offline')
    require(not re.search(r'\bfunction\s+render\s*\(', code), 'Envie o corpo de render, não a função completa')
    node = shutil.which('node')
    require(node is not None, 'Node.js necessário para validar sintaxe de Dashboard HTML; não validado')
    result = subprocess.run([node, '--check'], input='function render(root, rows, fields) {\n' + code + '\n}',
                            text=True, capture_output=True, timeout=20, encoding='utf-8')
    require(result.returncode == 0, 'Sintaxe JavaScript inválida: ' + result.stderr[:1200])


class SafeMarkup(HTMLParser):
    allowed = {'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'section', 'header', 'footer',
               'main', 'article', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'strong',
               'em', 'b', 'i', 'small', 'br', 'ul', 'ol', 'li'}

    def handle_starttag(self, tag, attrs):
        require(tag in self.allowed, 'Tag HTML não permitida: ' + tag)
        for name, value in attrs:
            require(name in {'class', 'id', 'style', 'title', 'colspan', 'rowspan'}, 'Atributo HTML não permitido: ' + name)
            require(not re.search(r'url\s*\(|@import|expression\s*\(|https?://|javascript:', value or '', re.I), 'Recurso externo/ativo no HTML')

    def handle_endtag(self, tag):
        require(tag in self.allowed, 'Tag HTML não permitida: ' + tag)

    def handle_decl(self, decl):
        raise ValueError('Declarações HTML não permitidas')


def validate_formula(expression, fields):
    """Parse a deliberately small numeric Criteria subset; never eval user text.

    Returns True for aggregate formulas. Reject mixed row/aggregate operands.
    Calculations may reference source fields only, making cycles impossible.
    """
    text(expression, 'expression', 4000)
    token = re.compile(r'\s*(\[[^\[\]]+\]|\d+(?:\.\d+)?|[A-Za-z]+|<=|>=|<>|!=|[()+*/%,=<>-])')
    tokens, offset = [], 0
    while offset < len(expression.rstrip()):
        match = token.match(expression, offset)
        require(match is not None, 'Token não suportado na fórmula')
        tokens.append(match.group(1)); offset = match.end()
    require(len(tokens) <= 512, 'Fórmula muito complexa')
    pos = 0
    aggregates = {'sum', 'avg', 'min', 'max', 'count', 'countdistinct'}
    arities = {'iif': 3, 'isnull': 2, 'abs': 1, 'round': 2}
    def peek(): return tokens[pos] if pos < len(tokens) else ''
    def take(expected=None):
        nonlocal pos
        value = peek()
        require(value != '' and (expected is None or value == expected), 'Sintaxe inválida na fórmula')
        pos += 1
        return value
    def expr(depth=0, minimum=0):
        require(depth < 40, 'Fórmula muito profunda')
        value = take()
        if value in {'+', '-'}:
            modes = expr(depth + 1, 4)
        elif value == '(':
            modes = expr(depth + 1); take(')')
        elif value.startswith('['):
            name = value[1:-1]
            require(fields.get(name) in {'INTEGER', 'REAL'}, 'Fórmula exige campo numérico da fonte: ' + name)
            modes = {'row'}
        elif re.fullmatch(r'\d+(?:\.\d+)?', value):
            modes = set()
        else:
            fn = value.lower()
            require(fn in aggregates or fn in arities, 'Função não suportada: ' + value)
            take('('); args = [expr(depth + 1)]
            while peek() == ',':
                take(','); args.append(expr(depth + 1))
            take(')')
            require(len(args) == (1 if fn in aggregates else arities[fn]), 'Quantidade de argumentos inválida: ' + value)
            modes = set().union(*args)
            if fn in aggregates:
                require('aggregate' not in modes, 'Agregações aninhadas não suportadas')
                modes = {'aggregate'}
        precedence = {'=': 1, '!=': 1, '<>': 1, '<': 1, '>': 1, '<=': 1, '>=': 1, '+': 2, '-': 2, '*': 3, '/': 3, '%': 3}
        while peek() in precedence and precedence[peek()] >= minimum:
            op = take(); modes |= expr(depth + 1, precedence[op] + 1)
        return modes
    modes = expr()
    require(pos == len(tokens), 'Conteúdo extra na fórmula')
    require(modes != {'row', 'aggregate'}, 'Não misture campos por linha e agregados na fórmula')
    return 'aggregate' in modes


def validate_plan(plan):
    keys(plan, {'title', 'fieldsApproved', 'componentsApproved', 'fields', 'calculatedFields', 'items', 'mode', 'appearance', 'numericFormats', 'dataSource'}, 'Plano')
    data_source = plan.get('dataSource', {})
    keys(data_source, {'name', 'componentName', 'connectionName', 'dataMember', 'tableName', 'existingSource'}, 'Fonte de dados')
    existing_source = data_source.get('existingSource', False)
    require(type(existing_source) is bool, 'Fonte de dados.existingSource deve ser booleano')
    if data_source:
        text(data_source.get('name'), 'Fonte de dados.name', 128)
        text(data_source.get('componentName'), 'Fonte de dados.componentName', 128)
        text(data_source.get('dataMember'), 'Fonte de dados.dataMember', 128)
        if not existing_source:
            text(data_source.get('tableName'), 'Fonte de dados.tableName', 256)
    for key, default in {'name': 'Dados', 'componentName': 'sqlDataSource1', 'connectionName': 'CONEXAO_CLIENTE', 'dataMember': 'Dados'}.items():
        text(data_source.get(key, default), 'Fonte de dados.' + key, 128)
    appearance = plan.get('appearance', {})
    keys(appearance, {'titleColor'}, 'Aparência')
    require(re.fullmatch(r'#[0-9a-fA-F]{6}', appearance.get('titleColor', '#FFFFFF')) is not None, 'Cor do título deve ser hexadecimal #RRGGBB')
    require(plan.get('mode', 'components') in {'components', 'html'}, 'Modo inválido')
    text(plan.get('title'), 'title')
    require(plan.get('fieldsApproved') is True, 'Campos precisam de aprovação')
    require(plan.get('componentsApproved') is True, 'Componentes precisam de aprovação')
    fields = plan.get('fields')
    require(isinstance(fields, list) and 1 <= len(fields) <= 100, 'Esperados 1..100 campos')
    field_types = {}
    for f in fields:
        keys(f, {'name', 'type', 'calculated'}, 'Campo')
        name = text(f.get('name'), 'Campo.name', 128)
        require(name.casefold() not in {n.casefold() for n in field_types}, 'Campo duplicado: ' + name)
        require(f.get('type') in TYPES, 'Tipo de campo inválido')
        require(type(f.get('calculated', False)) is bool, 'Campo.calculated deve ser booleano')
        field_types[name] = f['type']
    calculations = plan.get('calculatedFields', [])
    require(isinstance(calculations, list) and len(calculations) <= 40, 'Esperados até 40 cálculos')
    require(not existing_source or not calculations, 'Fonte existente não pode ser sobrescrita com calculatedFields; crie o cálculo no MyBI e copie novamente os campos')
    source_types = dict(field_types)
    aggregate_fields = set()
    for calc in calculations:
        keys(calc, {'name', 'type', 'expression'}, 'CalculatedField')
        name = text(calc.get('name'), 'CalculatedField.name', 128)
        require(name.casefold() not in {n.casefold() for n in field_types}, 'Campo duplicado: ' + name)
        require(calc.get('type') == 'REAL', 'Campo calculado deve ser REAL neste perfil')
        if validate_formula(calc.get('expression'), source_types): aggregate_fields.add(name)
        field_types[name] = 'REAL'
    formats = plan.get('numericFormats', {})
    require(isinstance(formats, dict), 'numericFormats deve ser objeto por campo')
    for name, fmt in formats.items():
        require(field_types.get(name) in {'INTEGER', 'REAL'}, 'Formato exige campo numérico aprovado: ' + name)
        keys(fmt, {'type', 'precision', 'scale'}, 'Formato ' + name)
        require(fmt.get('type') in {'Number', 'Currency', 'Percent'}, 'Tipo de formato inválido')
        precision = fmt.get('precision', 2)
        require(type(precision) is int and 0 <= precision <= 8, 'Precisão deve ser inteiro entre 0 e 8')
        if fmt['type'] == 'Percent':
            require(type(fmt.get('scale')) is int and fmt['scale'] == 1, 'Percent exige scale 1: 0.677 representa 67.7%; não use valor já multiplicado por 100')
        else:
            require('scale' not in fmt, 'scale só é permitido em Percent')
    items = plan.get('items')
    require(isinstance(items, list) and 1 <= len(items) <= 40, 'Esperados 1..40 componentes')
    for item in items:
        keys(item, {'component', 'title', 'bindings', 'javascript', 'html', 'css'}, 'Componente')
        component = item.get('component')
        require(component in CATALOG, 'Componente não suportado: ' + str(component))
        require(component not in {'DashboardAutomatico', 'HtmlTemplate'} or plan.get('mode') == 'html', 'HTML exige modo html explicitamente aprovado; padrão são componentes separados')
        text(item.get('title'), 'Componente.title')
        spec = binding_spec(component)
        bindings = item.get('bindings')
        keys(bindings, spec, 'Bindings ' + component)
        count = 0
        roles = {}
        for prop, values in bindings.items():
            require(isinstance(values, list), prop + ': lista esperada')
            require(len(values) <= (100 if spec[prop]['array'] else 1), prop + ': cardinalidade inválida')
            local = []
            for val in values:
                if spec[prop]['type'] == 'Dimension':
                    name = text(val, 'Dimensão', 128)
                    role = ('Dimension', '')
                else:
                    keys(val, {'field', 'summary'}, 'Medida')
                    name = text(val.get('field'), 'Medida.field', 128)
                    require(val.get('summary') in SUMMARIES, 'Agregação inválida')
                    role = ('Measure', val['summary'])
                    if val['summary'] not in {'Count', 'CountDistinct'}:
                        require(field_types.get(name) in {'INTEGER', 'REAL'}, 'Agregação exige campo numérico: ' + name)
                require(name in field_types, 'Campo não aprovado: ' + name)
                if name in aggregate_fields:
                    require(role == ('Measure', 'Sum'), 'Cálculo agregado usa medida Sum; a agregação está na expressão: ' + name)
                require(name not in local, 'Campo duplicado no binding: ' + name)
                require(name not in roles or roles[name] == role, 'Papéis/agregações conflitantes no mesmo item: ' + name)
                roles[name] = role
                local.append(name)
                count += 1
        require(count > 0, 'Componente sem campos')
        if component == 'card':
            require(bindings.get('measures'), 'Card exige medida')
        elif component not in {'grid', 'HtmlTemplate', 'DashboardAutomatico', 'tabulatorGridItem'}:
            for prop in spec:
                if prop.lower() not in {'series'}:
                    require(bindings.get(prop), 'Binding obrigatório ausente: ' + component + '.' + prop)
        if component == 'DashboardAutomatico':
            require('html' not in item and 'css' not in item, 'Dashboard HTML usa javascript, não html/css separados')
            check_javascript(item.get('javascript'))
        elif component == 'HtmlTemplate':
            require('javascript' not in item, 'HtmlTemplate não executa JavaScript')
            html = text(item.get('html'), 'html', 100_000)
            css = item.get('css', '')
            require(isinstance(css, str) and len(css) <= 50_000, 'CSS inválido')
            text(css or ' ', 'css', 50_000) if css.strip() else None
            require(not re.search(r'url\s*\(|@import|expression\s*\(|https?://|javascript:|</?script', css, re.I), 'CSS contém recurso externo/ativo')
            SafeMarkup(convert_charrefs=True).feed(html)
            for placeholder in re.findall(r'\{([^{}]+)\}', html):
                require(placeholder in roles, 'Placeholder não vinculado (ou raw): ' + placeholder)
        else:
            require(not {'javascript', 'html', 'css'} & item.keys(), 'Código só é aceito em componentes HTML')
    return field_types


def binding_spec(component):
    if component in {'card', 'grid'}:
        return {'dimensions': {'type': 'Dimension', 'array': True}, 'measures': {'type': 'Measure', 'array': True}}
    return CATALOG[component]['bindings']


def element(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})


def parse_base_xml(base_xml):
    require(base_xml is not None, 'Fonte existente exige o XML atual do dashboard (--base-xml) para preservar DataSources, SQL/procedure, parâmetros e cálculos')
    if isinstance(base_xml, (str, Path)):
        path = Path(base_xml)
        require(path.stat().st_size <= MAX_SIZE, 'XML-base excede 2 MB')
        base_xml = path.read_bytes()
    require(isinstance(base_xml, bytes), 'XML-base inválido')
    require(len(base_xml) <= MAX_SIZE, 'XML-base excede 2 MB')
    require(not re.search(br'<!DOCTYPE|<!ENTITY', base_xml, re.I), 'DTD/entidades proibidas no XML-base')
    root = ET.fromstring(base_xml)
    require(root.tag == 'Dashboard', 'XML-base deve ter raiz Dashboard')
    return root


def component_names(plan, base_root=None):
    used = set() if base_root is None else {node.get('ComponentName') for node in base_root.iter() if node.get('ComponentName')}
    result = []
    for index, item in enumerate(plan['items'], 1):
        tag = CATALOG[item['component']]['xml']
        prefix = {'Card': 'cardDashboardItem', 'Grid': 'gridDashboardItem', 'CustomItem': 'customItemDashboardItem'}[tag]
        number = index
        name = prefix + str(number)
        while name in used:
            number += 1
            name = prefix + str(number)
        used.add(name)
        result.append(name)
    return result


def build_xml(plan, base_xml=None):
    validate_plan(plan)
    data_source = {'name': 'Dados', 'componentName': 'sqlDataSource1',
                   'connectionName': 'CONEXAO_CLIENTE', 'dataMember': 'Dados',
                   'tableName': 'Dados', 'existingSource': False}
    data_source.update(plan.get('dataSource', {}))
    source_name = data_source['name']
    source_component = data_source['componentName']
    connection_name = data_source['connectionName']
    data_member = data_source['dataMember']
    table_name = data_source['tableName']
    existing_source = data_source['existingSource']
    base_root = parse_base_xml(base_xml) if existing_source else None
    require(existing_source or base_xml is None, 'XML-base só é aceito com dataSource.existingSource=true')
    if existing_source:
        root = base_root
        sources = [node for node in root.findall('DataSources/SqlDataSource')
                   if node.get('Name') == source_name and node.get('ComponentName') == source_component]
        require(len(sources) == 1, 'XML-base não contém exatamente a SqlDataSource Name=' + source_name + ' e ComponentName=' + source_component)
        members = [query for query in sources[0].findall('Query') if query.get('Name') == data_member]
        require(len(members) == 1, 'XML-base não contém a query/procedure DataMember=' + data_member + ' na fonte ' + source_component)
        # A edição preserva o título e seus demais atributos/conteúdo da base.
    else:
        root = ET.Element('Dashboard', CurrencyCulture='pt-BR')
        element(root, 'Title', Text=plan['title'])
        reference = ET.parse(BASE / 'assets/serializer-reference.xml').getroot()
        root.append(copy.deepcopy(reference.find('DataSources')))
        source = root.find('DataSources/SqlDataSource')
        source.set('Name', source_name)
        source.set('ComponentName', source_component)
        source.find('Connection').set('Name', connection_name)
        query = source.find('Query')
        query.set('Name', data_member)
        query.find('Tables/Table').set('Name', table_name)
        columns = query.find('Columns')
        columns.clear()
        schema = ET.Element('ResultSchema')
        view = element(element(schema, 'DataSet', Name=data_member), 'View', Name=data_member)
        schema_types = {'TEXT': 'String', 'INTEGER': 'Int64', 'REAL': 'Double', 'DATETIME': 'DateTime', 'BOOLEAN': 'Boolean'}
        for field in plan['fields']:
            if not field.get('calculated', False):
                element(columns, 'Column', Table=table_name, Name=field['name'])
            element(view, 'Field', Name=field['name'], Type=schema_types[field['type']])
        source.insert(list(source).index(source.find('ConnectionOptions')), schema)
        if plan.get('calculatedFields'):
            calculated = element(source, 'CalculatedFields')
            for calc in plan['calculatedFields']:
                element(calculated, 'CalculatedField', Name=calc['name'], Expression=calc['expression'], DataMember=data_member, DataType='Double')
    items = root.find('Items')
    if items is None:
        items = element(root, 'Items')
    layout_tree = root.find('LayoutTree')
    if layout_tree is None:
        layout_tree = element(root, 'LayoutTree')
    layout = ET.Element('LayoutGroup', Orientation='Vertical', Weight='100')
    if existing_source and len(layout_tree):
        if len(layout_tree) == 1 and layout_tree[0].tag == 'LayoutGroup':
            layout_tree[0].append(layout)
        else:
            previous = list(layout_tree)
            for child in previous:
                layout_tree.remove(child)
            wrapper = element(layout_tree, 'LayoutGroup', Orientation='Vertical', Weight='100')
            for child in previous:
                wrapper.append(child)
            wrapper.append(layout)
    else:
        layout_tree.append(layout)
    names = component_names(plan, base_root)
    row = None
    for index, item in enumerate(plan['items'], 1):
        component = item['component']
        tag = CATALOG[component]['xml']
        name = names[index - 1]
        node = element(items, tag, ComponentName=name, Name=item['title'], DataSource=source_component, DataMember=data_member)
        if tag == 'CustomItem':
            node.set('CustomItemType', component)
        bindings = item['bindings']
        spec = binding_spec(component)
        data_items = element(node, 'DataItems')
        ids = {}
        refs = {}
        for prop, values in bindings.items():
            refs[prop] = []
            for value in values:
                kind = spec[prop]['type']
                field = value if kind == 'Dimension' else value['field']
                if field not in ids:
                    uid = 'DataItem' + str(len(ids))
                    ids[field] = uid
                    di = element(data_items, kind, DataMember=field, DefaultId=uid)
                    if kind == 'Measure':
                        di.set('SummaryType', value['summary'])
                        # Counts are numbers even if the underlying field is money/a ratio.
                        fmt = plan.get('numericFormats', {}).get(field, {})
                        if value['summary'] in {'Count', 'CountDistinct'}:
                            fmt = {'type': 'Number', 'precision': 0}
                        attrs = dict(FormatType=fmt.get('type', 'Number'), Precision=fmt.get('precision', 2), Unit='Ones', IncludeGroupSeparator='true')
                        if attrs['FormatType'] == 'Currency':
                            attrs['CurrencyCultureName'] = 'pt-BR'
                        element(di, 'NumericFormat', **attrs)
                refs[prop].append(ids[field])
        if component == 'card':
            if refs.get('dimensions'):
                series = element(node, 'SeriesDimensions')
                for uid in refs['dimensions']:
                    element(series, 'SeriesDimension', DefaultId=uid)
            for uid in refs['measures']:
                element(element(node, 'Card'), 'ActualValue', DefaultId=uid)
        elif component == 'grid':
            cols = element(node, 'GridColumns')
            for prop, uids in refs.items():
                kind = spec[prop]['type']
                for uid in uids:
                    element(element(cols, 'Grid' + kind + 'Column', WidthType='Weight'), kind, DefaultId=uid)
            element(node, 'GridOptions')
            element(node, 'ColumnFilterOptions')
        else:
            metadata = element(node, 'CustomMetadata')
            for prop, uids in refs.items():
                if not uids:
                    continue
                if spec[prop]['array']:
                    parent = element(metadata, prop)
                    for n, uid in enumerate(uids, 1):
                        element(parent, 'Item' + str(n), ItemType=spec[prop]['type'], DefaultId=uid)
                else:
                    element(metadata, prop, ItemType=spec[prop]['type'], DefaultId=uids[0])
            if component in {'DashboardAutomatico', 'HtmlTemplate'}:
                properties = ET.Element('CustomProperties')
                node.insert(0, properties)
                if component == 'DashboardAutomatico':
                    element(properties, 'AutomaticJavascript').text = item['javascript']
                    element(properties, 'AutomaticFields').text = json.dumps(list(ids), ensure_ascii=False)
                else:
                    for key, value in {'HtmlTemplate': item['html'], 'CssStyles': item.get('css', ''),
                                       'RowMode': 'first', 'RenderMode': 'single', 'AllowScripts': 'false',
                                       'EmptyValueText': 'Sem dados', 'ScrollOverflow': 'true'}.items():
                        element(properties, key).text = value
            else:
                # Mirror the web generator's slice table and coloring references.
                slices = ET.Element('SliceTables')
                node.insert(1, slices)
                table = element(slices, 'SliceTable', Name='SliceTable1')
                for kind in ('Dimension', 'Measure'):
                    group = element(table, kind + 's')
                    for di in data_items:
                        if di.tag == kind:
                            element(group, kind, DefaultId=di.get('DefaultId'))
        if component == 'DashboardAutomatico':
            html_row = element(layout, 'LayoutGroup', Orientation='Horizontal', Weight='100')
            element(html_row, 'LayoutItem', DashboardItem=name, Weight='100')
            row = None
        else:
            if row is None or len(row) == 2:
                row = element(layout, 'LayoutGroup', Orientation='Horizontal', Weight='100')
            element(row, 'LayoutItem', DashboardItem=name, Weight='50')
    ET.indent(root, space='  ')
    result = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    require(len(result) <= MAX_SIZE, 'XML excede 2 MB')
    return result


def canonical(xml):
    require(len(xml) <= MAX_SIZE, 'XML excede limite')
    require(not re.search(br'<!DOCTYPE|<!ENTITY', xml, re.I), 'DTD/entidades proibidas')
    node = ET.fromstring(xml)
    def normalized(n):
        # Leaf content (JS/HTML/labels) is significant; indentation between nodes is not.
        return (n.tag, sorted(n.attrib.items()), (n.text or '') if len(n) == 0 else (n.text or '').strip(),
                tuple(normalized(child) for child in n))
    return normalized(node)


def dashboard_entry(base_xml=None):
    if isinstance(base_xml, (str, Path)):
        name = Path(base_xml).name
        require(name.lower().endswith('.xml') and not re.search(r'[\\/\r\n\[\]:]', name), 'Nome do XML-base inválido')
        return 'DashboardWeb/' + name
    return ENTRY


def build_format(plan, base_xml=None):
    # MyBI prefixes /images/; this fixed relative URL resolves to /SystemImages/back.png.
    color = plan.get('appearance', {}).get('titleColor', '#FFFFFF')
    result = ('[dashboard1]\r\n'
            'dashboard-image-background=../SystemImages/back.png\r\n'
            'modo-image-background=default\r\n'
            'ativar-configuracao-geral-componente-geral=true\r\n'
            'component-aplicar-background-transparency-geral=true\r\n'
            'component-remover-background-transparency-title-geral=false\r\n'
            'component-title-font-color-geral=' + color + '\r\n')
    base_root = parse_base_xml(base_xml) if plan.get('dataSource', {}).get('existingSource', False) else None
    names = component_names(plan, base_root)
    for index, item in enumerate(plan['items'], 1):
        if item['component'] == 'card':
            result += ('\r\n[dashboard1_' + names[index - 1] + ']\r\n'
                       'background-transparency=true\r\n'
                       'remove-background-transparency-title=false\r\n'
                       'title-font-size-conteudo=26\r\n')
    dashboard_name = Path(dashboard_entry(base_xml)).stem
    result = result.replace('[dashboard1]', '[' + dashboard_name + ']').replace('[dashboard1_', '[' + dashboard_name + '_')
    return result.encode('utf-8')


def validate_zip(path, plan, base_xml=None):
    expected = build_xml(plan, base_xml)
    with zipfile.ZipFile(path) as archive:
        require(archive.namelist() == [dashboard_entry(base_xml), FORMAT_ENTRY], 'ZIP deve conter o XML com nome original e formatacao.ini somente')
        fmt = archive.getinfo(FORMAT_ENTRY)
        require(not fmt.flag_bits & 1 and fmt.file_size <= 4096, 'INI inválido')
        require((fmt.external_attr >> 16) & 0o170000 != 0o120000, 'Link simbólico proibido')
        require(archive.read(fmt) == build_format(plan, base_xml), 'INI diverge da aparência aprovada')
        info = archive.getinfo(dashboard_entry(base_xml))
        require(not info.flag_bits & 1, 'ZIP criptografado não suportado')
        require(info.file_size <= MAX_SIZE, 'Arquivo descompactado excede limite')
        require((info.external_attr >> 16) & 0o170000 != 0o120000, 'Link simbólico proibido')
        actual = archive.read(info)
        require(canonical(actual) == canonical(expected), 'XML diverge do plano aprovado/contrato do gerador')
    return len(plan['items'])


def build_zip(plan, output, base_xml=None):
    xml = build_xml(plan, base_xml)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        entry = zipfile.ZipInfo(dashboard_entry(base_xml), date_time=(2026, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(entry, xml)
        archive.writestr(FORMAT_ENTRY, build_format(plan, base_xml))
    # Validate entirely before creating any destination file; do not overwrite user files.
    buffer.seek(0)
    validate_zip(buffer, plan, base_xml)
    with Path(output).open('xb') as stream:
        stream.write(buffer.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    build = sub.add_parser('build')
    build.add_argument('plan'); build.add_argument('output')
    build.add_argument('--base-xml')
    validate = sub.add_parser('validate')
    validate.add_argument('zip'); validate.add_argument('--plan', required=True)
    validate.add_argument('--base-xml')
    args = parser.parse_args()
    try:
        plan = load_plan(args.plan)
        if args.command == 'build':
            build_zip(plan, args.output, args.base_xml)
        else:
            validate_zip(args.zip, plan, args.base_xml)
        print('OK: pacote estruturalmente validado; conexão do cliente não acessada.')
    except (ValueError, OSError, ET.ParseError, zipfile.BadZipFile, subprocess.TimeoutExpired) as ex:
        print('ERRO: ' + str(ex), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
