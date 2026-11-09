"""V5 compatibility: preserve legacy panels, never generate new ones."""
import re
import unicodedata

BANNED_NEW_TYPES = {'DashboardAutomatico'}


def route_intent(intent):
    value = ''.join(c for c in unicodedata.normalize('NFKD', intent.lower()) if not unicodedata.combining(c))
    visual = bool(re.search(r'html|css|javascript|\bjs\b|\bcards?\b|cartao|cartoes|kpi|painel web|indicadores com icones', value))
    return {'htmlComponent': 'HtmlTemplate' if visual else None,
            'arbitraryJavaScript': False, 'composeNativeComponents': True}


def guard_plan(plan):
    if not isinstance(plan.get('items', []), list) or any(not isinstance(i, dict) for i in plan.get('items', [])):
        raise ValueError('Items deve ser uma lista de objetos.')
    for item in plan.get('items', []):
        if item.get('component') in BANNED_NEW_TYPES:
            raise ValueError('Componente incompatível para novos itens. Use Automático (Template HTML) e componentes MyBI suportados.')
        if 'javascript' in item or 'AutomaticJavascript' in item.get('customProperties', {}):
            raise ValueError('Template HTML não executa JavaScript livre; use HTML/CSS ou htmlGrid fixo.')
    if plan.get('intent') and route_intent(plan['intent'])['htmlComponent']:
        if not any(i.get('component') == 'HtmlTemplate' for i in plan.get('items', [])):
            raise ValueError('Pedido HTML/cards exige Automático (Template HTML) para o conteúdo visual.')


def guard_xml(root, base=None):
    def signature(node):
        return (node.tag, sorted(node.attrib.items()), (node.text or '') if len(node) == 0 else (node.text or '').strip(), tuple(signature(c) for c in node))
    legacy = {n.get('ComponentName'): signature(n) for n in base.findall('Items/*')
              if n.get('CustomItemType') in BANNED_NEW_TYPES or n.find('.//AutomaticJavascript') is not None} if base is not None else {}
    seen = set()
    for node in root.findall('Items/*'):
        if node.get('CustomItemType') in BANNED_NEW_TYPES or node.find('.//AutomaticJavascript') is not None:
            name = node.get('ComponentName')
            if name not in legacy or signature(node) != legacy[name] or name in seen:
                raise ValueError('XML contém componente personalizado incompatível novo ou legado alterado.')
            seen.add(name)
    if seen != set(legacy):
        raise ValueError('Componente legado removido sem migração explícita.')
