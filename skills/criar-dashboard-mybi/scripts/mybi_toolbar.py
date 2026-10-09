"""Typed properties for verified runtime CustomItems. No application actions."""
import math
import re
import xml.etree.ElementTree as ET


def apply_properties(node, item, contract):
    props = item.get('customProperties', {})
    allowed = contract.get('properties', {})
    if not isinstance(props, dict) or set(props) - set(allowed):
        raise ValueError('Propriedade não verificada para ' + item['component'])
    if not props: return
    group = node.find('CustomProperties')
    if group is None: group = ET.SubElement(node, 'CustomProperties')
    for key, value in props.items():
        rule = allowed[key]
        valid = {'string': type(value) is str, 'boolean': type(value) is bool,
                 'number': type(value) in (int, float) and math.isfinite(value) if type(value) in (int, float) else False}
        if not valid[rule['type']]: raise ValueError('Tipo inválido: ' + key)
        if 'enum' in rule and not any(type(value) is type(v) and value == v for v in rule['enum']):
            raise ValueError('Opção inválida: ' + key)
        if rule['type'] == 'number':
            if ('min' in rule and value < rule['min']) or ('max' in rule and value > rule['max']):
                raise ValueError('Valor fora dos limites: ' + key)
        if isinstance(value, str):
            if len(value) > 10000 or re.search(r'[\x00-\x1f\ud800-\udfff\ufffe\uffff<>]|javascript:|https?://', value, re.I):
                raise ValueError('Texto ativo/externo ou inválido: ' + key)
            if rule.get('format') == 'color' and not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                raise ValueError('Cor deve ser #RRGGBB: ' + key)
        old = group.find(key)
        if old is not None: group.remove(old)
        ET.SubElement(group, key).text = str(value).lower() if type(value) is bool else str(value)
