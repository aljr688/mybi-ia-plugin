"""Explicit native contracts, verified with the local dashboard serializer; no IO."""
import math
import re
import xml.etree.ElementTree as ET

def check(ok, message):
    if not ok: raise ValueError(message)

def obj(value, allowed):
    check(isinstance(value, dict) and not set(value) - set(allowed), 'Propriedades nativas inválidas')

def el(parent, tag, **attrs):
    check(all(not re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]',str(v)) for v in attrs.values()),'Caractere XML inválido')
    return ET.SubElement(parent, tag, {k: str(v).lower() if type(v) is bool else str(v) for k,v in attrs.items()})

def binding(kind, array=True): return {'type': kind, 'array': array}

EXTENSIONS = {
    'pivot': {'xml':'Pivot', 'bindings':{'rows':binding('Dimension'), 'columns':binding('Dimension'), 'measures':binding('Measure')}, 'required':['measures']},
    'comboBox': {'xml':'ComboBox', 'bindings':{'dimensions':binding('Dimension')}, 'required':['dimensions']},
    'dateFilter': {'xml':'DateFilter', 'bindings':{'dimension':binding('Dimension', False)}, 'required':['dimension']},
    'DREContabil': {'xml':'CustomItem', 'bindings':{**{n:binding('Dimension',False) for n in ['Codigo','Conta','TipoLinha']}, **{n:binding('Measure',False) for n in ['ValorAtual','ValorAnterior','Ordem']}}, 'required':['Codigo','Conta','ValorAtual']},
    'DREVendas': {'xml':'CustomItem', 'bindings':{**{n:binding('Dimension',False) for n in ['Data','PromoProduto']}, 'DimensoesGrupo':binding('Dimension'), **{n:binding('Measure',False) for n in ['Vendas','CMV','ImpostosValor','InadimpValor','DespesasAdmValor','MetaMesValor','PromoQuantidade','PromoValorUnitario']}}, 'required':['Data','Vendas']},
}
PIVOT_BOOL = {'ShowColumnGrandTotals','ShowRowGrandTotals','ShowColumnTotals','ShowRowTotals','AutoExpandColumnGroups','AutoExpandRowGroups'}
COMBO_BOOL = {'ShowAllValue','EnableSearch'}
DRE_PROPS = {
    'DREContabil': {'MostrarAnaliseVertical':bool,'MostrarComparativo':bool,'MostrarKPIs':bool,'CodigoReceitaBase':str,'TituloRelatorio':str},
    'DREVendas': {'CMVPercentDefault':float,'ImpostosPercent':float,'InadimpPercent':float,'DespesasAdmDefault':float,'DiasNoMes':float,'ShowCards':bool,'ShowPizza':bool},
}

def color(value):
    check(isinstance(value,str) and re.fullmatch('#[0-9a-fA-F]{6}',value), 'Cor explícita deve ser #RRGGBB')
    return int(value[1:],16) - 16777216

def style(parent, config):
    obj(config, {'background','foreground','icon'})
    check(bool(config), 'Estilo condicional vazio')
    if 'icon' in config:
        check(len(config)==1 and config['icon'] in {'IndicatorGreenCheck','IndicatorRedCross','IndicatorYellowExclamation'}, 'Ícone não suportado ou estilo misturado')
        el(parent,'IconSettings',IconType=config['icon'])
    else:
        attrs={'AppearanceType':'Custom'}
        for key, dest in [('background','BackColor'),('foreground','ForeColor')]:
            if key in config: attrs[dest]=color(config[key])
        el(parent,'AppearanceSettings',**attrs)

def value(parent, tag, v):
    check(type(v) in {str,int,float} and (not isinstance(v,float) or math.isfinite(v)), 'Valor condicional inválido')
    check(not isinstance(v,str) or 0<len(v)<=500, 'Texto condicional inválido')
    el(parent,tag,Type='System.String' if isinstance(v,str) else 'System.Decimal',Value=v)

def apply_rules(node, rules, ids):
    check(isinstance(rules,list) and len(rules)<=30, 'Até 30 regras por componente')
    check(not rules or node.tag in {'Grid','Pivot'}, 'Regras nativas exigem Grade ou Pivot')
    if not rules: return
    group=el(node,'FormatRules'); used=set()
    for r in rules:
        obj(r, {'name','field','kind','condition','value','value2','expression','style','applyToRow','ranges','valueType'})
        name=r.get('name'); check(isinstance(name,str) and 0<len(name)<=128 and name not in used,'Nome de regra inválido/duplicado'); used.add(name)
        check(r.get('field') in ids,'Regra exige campo vinculado')
        attrs={'Name':name,'DataItem':ids[r['field']]}
        if 'applyToRow' in r:
            check(node.tag=='Grid' and type(r['applyToRow']) is bool,'applyToRow exige Grade/booleano')
            attrs['ApplyToRow']=r['applyToRow']
        rule=el(group,node.tag+'ItemFormatRule',**attrs)
        kind=r.get('kind')
        if kind=='value':
            check(not set(r)&{'expression','ranges','valueType'},'Propriedades incompatíveis com regra value')
            op=r.get('condition')
            check(op in {'Greater','GreaterOrEqual','Less','LessOrEqual','Equal','NotEqual','Between','NotBetween','BetweenOrEqual','NotBetweenOrEqual','ContainsText'},'Comparação não suportada')
            cond=el(rule,'FormatConditionValue',Condition=op)
            style(cond,r.get('style')); value(cond,'Value1',r.get('value'))
            if 'Between' in op: value(cond,'Value2',r.get('value2'))
            else: check('value2' not in r,'value2 somente em intervalo')
        elif kind=='expression':
            check(not set(r)&{'condition','value','value2','ranges','valueType'},'Propriedades incompatíveis com expressão')
            expression=r.get('expression')
            check(isinstance(expression,str) and 0<len(expression)<=2000,'Expressão inválida')
            # Restricted Criteria comparison grammar, never execute/eval expressions.
            pattern=r"\s*\[([^\[\]]+)\]\s*(?:>=|<=|<>|!=|=|>|<)\s*(?:-?\d+(?:\.\d+)?|'(?:[^']|'')*')\s*"
            match=re.fullmatch(pattern,expression)
            check(match is not None and match[1] in ids,'Expressão exige comparação simples de campo vinculado com número/texto')
            cond=el(rule,'FormatConditionExpression',Expression=expression); style(cond,r.get('style'))
        elif kind in {'ranges','gradient'}:
            check(not set(r)&{'condition','value','value2','expression','style'},'Propriedades incompatíveis com escala/faixas')
            ranges=r.get('ranges'); vt=r.get('valueType')
            check(vt in {'Number','Percent'} and isinstance(ranges,list) and 2<=len(ranges)<=10,'Faixas exigem tipo e 2..10 limites')
            cond=el(rule,'FormatConditionRangeGradient' if kind=='gradient' else 'FormatConditionRangeSet',ValueType=vt)
            entries=el(el(cond,'RangeSet'),'Ranges'); previous=-math.inf
            for index, entry in enumerate(ranges):
                obj(entry,{'value','style'}); v=entry.get('value')
                check(type(v) in {int,float} and math.isfinite(v) and v>previous,'Limites devem ser numéricos crescentes')
                check(vt!='Percent' or 0<=v<=100,'Percentual fora de 0..100'); previous=v
                info=el(entries,'RangeInfo'); value(info,'Value',v)
                if kind=='ranges' or index in {0,len(ranges)-1}:
                    if kind=='gradient': check(set(entry.get('style',{}))=={'background'},'Escala exige cor de fundo nas extremidades')
                    style(info,entry.get('style'))
                else: check('style' not in entry,'Escala interpola estilos intermediários')
        else: raise ValueError('Tipo de regra não suportado')
        if node.tag=='Pivot': el(rule,'PivotItemFormatRuleLevel')

def decorate(node, item, ids):
    options=item.get('options',{}); component=item['component']
    allowed=PIVOT_BOOL|{'LayoutType','RowTotalsPosition','ColumnTotalsPosition'} if component=='pivot' else COMBO_BOOL|{'ComboBoxType'} if component=='comboBox' else set()
    obj(options,allowed)
    for key,v in options.items():
        if key in PIVOT_BOOL|COMBO_BOOL: check(type(v) is bool,'Opção exige booleano')
        elif key=='LayoutType': check(v in {'Compact','Tabular'},'LayoutType inválido')
        elif key=='RowTotalsPosition': check(v in {'Top','Bottom'},'RowTotalsPosition inválido')
        elif key=='ColumnTotalsPosition': check(v in {'Near','Far'},'ColumnTotalsPosition inválido')
        else: check(v in {'Standard','Checked'},'ComboBoxType inválido')
        if component=='pivot': el(node,key).text=str(v).lower() if type(v)is bool else v
        else: node.set(key,str(v).lower() if type(v)is bool else v)
    interaction=item.get('interactivity',{})
    obj(interaction, {'IgnoreMasterFilters'} if component in {'pivot','dateFilter'} else {'IgnoreMasterFilters','MasterFilterMode'} if component=='grid' else set())
    if interaction:
        for k,v in interaction.items():
            check(type(v)is bool if k=='IgnoreMasterFilters' else v in {'None','Single','Multiple'},'Interação inválida')
        el(node,'InteractivityOptions',**interaction)
    sort=item.get('sort',{}); obj(sort, ids)
    dimensions={d.get('DataMember'):d for d in node.findall('DataItems/Dimension')}
    for field,order in sort.items():
        check(field in dimensions and order in {'Ascending','Descending'},'Ordenação exige dimensão e direção')
        dimensions[field].set('SortOrder',order)
    totals=item.get('totals',{}); obj(totals,ids)
    check(not totals or component=='grid','totals exige Grade')
    for field, choices in totals.items():
        check(isinstance(choices,list) and len(choices)<=6 and all(isinstance(c,str) for c in choices) and len(set(choices))==len(choices),'Lista de totais inválida')
        check(all(c in {'Auto','Count','Min','Max','Avg','Sum'} for c in choices),'Total não suportado')
        columns=[c for c in node.findall('GridColumns/*') if any(d.get('DefaultId')==ids[field] for d in c if d.tag in {'Dimension','Measure'})]
        check(len(columns)==1,'Total exige coluna não ambígua')
        column=columns[0]
        check(column.tag=='GridMeasureColumn' or all(c=='Count' for c in choices),'Dimensão permite somente total Count')
        for old in column.findall('Totals'):column.remove(old)
        if choices:
            group=el(column,'Totals')
            for choice in choices:el(group,'Total',Type=choice)
    props=item.get('customProperties',{})
    types={**DRE_PROPS.get(component,{}), **({n:str for n in ['PrimaryColor','NegativeColor','PositiveColor']} if component in DRE_PROPS else {})}
    obj(props,types)
    if props:
        group=el(node,'CustomProperties')
        for k,v in props.items():
            expected=types[k]
            check(type(v)is expected if expected!=float else type(v) in {int,float} and math.isfinite(v),'Propriedade DRE inválida')
            if k.endswith('Color'): color(v)
            if k=='DiasNoMes': check(1<=v<=31 and int(v)==v,'DiasNoMes deve ser 1..31')
            if expected==str: check(len(v)<=500 and not re.search(r'[\x00-\x1f]',v),'Texto DRE inválido')
            el(group,k).text=str(v).lower() if type(v)is bool else str(v)
    apply_rules(node,item.get('rules',[]),ids)

def tabs(root, layout, configs, item_configs, names):
    check(isinstance(configs,list) and len(configs)<=10,'Até 10 grupos de abas')
    used={n.get('ComponentName') for n in root.iter() if n.get('ComponentName')}; pages={}
    def identity(config):
        obj(config,{'componentName','title','pages'} if 'pages' in config else {'componentName','title'})
        name=config.get('componentName'); title=config.get('title')
        check(isinstance(name,str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',name) and name not in used,'ID de aba duplicado/inválido')
        check(isinstance(title,str) and 0<len(title)<=200,'Título de aba inválido'); used.add(name)
        return name,title
    for config in configs:
        name,title=identity(config); group=el(root.find('Items'),'TabContainer',ComponentName=name,Name=title)
        pn=el(group,'Pages'); ln=el(layout,'LayoutTabContainer',DashboardItem=name,Weight=100)
        entries=config.get('pages'); check(isinstance(entries,list) and 1<=len(entries)<=20,'Grupo exige 1..20 abas')
        for page in entries:
            p,t=identity(page); el(pn,'Page',ComponentName=p,Name=t); pages[p]=el(ln,'LayoutTabPage',DashboardItem=p)
    for config,name in zip(item_configs,names):
        if 'parentContainer' not in config: continue
        parent=config['parentContainer']; check(parent in pages,'Aba pai inexistente no plano')
        node=next(n for n in root.find('Items') if n.get('ComponentName')==name); node.set('ParentContainer',parent)
        for group in list(layout.iter()):
            for child in list(group):
                if child.tag=='LayoutItem' and child.get('DashboardItem')==name: group.remove(child)
        el(pages[parent],'LayoutItem',DashboardItem=name,Weight=100)
    for name,page in pages.items(): check(len(page)>0,'Aba vazia: '+name)
    for group in list(layout):
        if group.tag=='LayoutGroup' and len(group)==0: layout.remove(group)

def update_existing(root, updates, approved):
    check(isinstance(updates,dict) and len(updates)<=40,'componentUpdates inválido')
    mapping={'Pivot':'pivot','Grid':'grid','ComboBox':'comboBox','DateFilter':'dateFilter'}
    for name, config in updates.items():
        obj(config,{'options','interactivity','sort','customProperties','rules','totals'})
        matches=[n for n in root.findall('Items/*') if n.get('ComponentName')==name]
        check(len(matches)==1,'Componente existente não encontrado: '+str(name)); node=matches[0]
        component=mapping.get(node.tag,node.get('CustomItemType'))
        check(component in {*mapping.values(),*DRE_PROPS},'Atualização nativa não suportada para este componente')
        fields=node.findall('DataItems/*'); ids={n.get('DataMember'):n.get('DefaultId') for n in fields}
        check(len(ids)==len(fields) and all(ids.values()),'Campos repetidos ou IDs ausentes; exporte componente sem ambiguidade')
        ids={field:uid for field,uid in ids.items() if field in approved}
        # Only explicitly requested parts are changed; unrelated XML is untouched.
        if 'rules' in config:
            old=node.find('FormatRules')
            if old is not None: node.remove(old)
        for key in config.get('options',{}):
            for old in node.findall(key):node.remove(old)
        old_interaction=node.find('InteractivityOptions')
        old_properties=node.find('CustomProperties')
        decorate(node,{'component':component,**config},ids)
        if config.get('interactivity') and old_interaction is not None:
            added=node.findall('InteractivityOptions')[-1]
            old_interaction.attrib.update(added.attrib);node.remove(added)
        if config.get('customProperties') and old_properties is not None:
            added=node.findall('CustomProperties')[-1]
            for child in list(added):
                for old in old_properties.findall(child.tag):old_properties.remove(old)
                old_properties.append(child)
            node.remove(added)
