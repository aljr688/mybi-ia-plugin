"""Explicit INI edits only; no visual defaults and no network access."""
import configparser
import io
import re

DASHBOARD = set('dashboard-color-background dashboard-title-font-bold dashboard-title-font-italic dashboard-title-font-underline dashboard-title-font-color dashboard-title-font-size dashboard-title-font-color-background dashboard-title-icon-color dashboard-menu-color dashboard-menu-icon-color dashboard-menu-text-color dashboard-menu-text-dash-color dashboard-menu-left-background-transparency leftwidth dashboard-altura ativar-configuracao-geral-componente-geral component-title-centralizar-geral component-title-font-bold-geral component-title-font-italic-geral component-title-font-underline-geral component-title-font-color-geral component-title-font-size-geral component-title-color-icon-geral component-title-color-background-geral component-aplicar-background-transparency-geral component-remover-background-transparency-title-geral component-color-background-geral'.split())
COMPONENT = set('title-font-center title-font-bold title-font-italic title-font-underline title-font-color title-font-size title-font-color-background title-icon-color background-transparency remove-background-transparency-title extend-background-color-to-title color-background color-marcador-background color-moldura-chart apply-background-image-title componente-modo-image-background'.split())
for suffix in ('conteudo', 'titulo-tabela'):
    COMPONENT.update('title-font-' + key + '-' + suffix for key in ('bold', 'italic', 'underline', 'color', 'size', 'color-background', 'align'))
DASHBOARD.update({'dashboard-image-background', 'modo-image-background'})
COMPONENT.add('componente-image-background')

def validate_values(values, allowed):
    if not isinstance(values, dict) or set(values) - allowed:
        raise ValueError('Propriedades INI não suportadas')
    for key, value in values.items():
        if not isinstance(value, str) or len(value) > 128 or re.search(r'[\r\n\x00-\x1f;\[\]]', value):
            raise ValueError('Valor INI inválido: ' + key)
        if value == '': continue  # Explicitly unset/inherit, never fill automatically.
        if key in ('dashboard-image-background', 'componente-image-background'):
            if not re.fullmatch(r'(?:\.\./SystemImages/)?[A-Za-z0-9_/-]+\.(?:png|jpg|jpeg|svg|webp)', value) or '..' in value.replace('../SystemImages/', '', 1):
                raise ValueError('Imagem deve ser um caminho relativo aprovado, sem URL externa')
        elif 'color' in key and key != 'extend-background-color-to-title':
            rgb = re.fullmatch(r'rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)', value)
            if not re.fullmatch(r'#[0-9A-Fa-f]{6}', value) and not (rgb and all(int(n) <= 255 for n in rgb.groups())):
                raise ValueError('Cor deve ser #RRGGBB ou rgb(R, G, B): ' + key)
        elif 'size' in key or key in ('leftwidth', 'dashboard-altura'):
            if not re.fullmatch(r'\d+(?:\.\d+)?', value) or float(value) <= 0:
                raise ValueError('Tamanho deve ser positivo: ' + key)
        elif 'align' in key:
            if value not in ('left', 'center', 'right', 'justify'): raise ValueError('Alinhamento inválido')
        elif key in ('componente-modo-image-background', 'modo-image-background'):
            if value not in ('default',): raise ValueError('Modo de imagem exige confirmação no contrato')
        elif value not in ('true', 'false'):
            raise ValueError('Booleano INI deve ser true/false: ' + key)

def validate_formatting(fmt):
    if not isinstance(fmt, dict) or set(fmt) - {'dashboard', 'components'}: raise ValueError('formatting inválido')
    validate_values(fmt.get('dashboard', {}), DASHBOARD)
    components = fmt.get('components', {})
    if not isinstance(components, dict): raise ValueError('formatting.components inválido')
    for name, values in components.items():
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', name): raise ValueError('ComponentName inválido')
        validate_values(values, COMPONENT)

def merge_ini(original, edits):
    """Validate uniqueness, preserve all untouched lines, sections and comments."""
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str
    try: parser.read_string(original)
    except configparser.Error as exc: raise ValueError('INI-base inválido ou ambíguo') from exc
    pending = {section: dict(values) for section, values in edits.items() if values}
    lines, current = [], None
    def remaining():
        if current in pending:
            for key, value in pending.pop(current).items(): lines.append(key + '=' + value + '\n')
    for line in original.splitlines(keepends=True):
        section = re.fullmatch(r'\s*\[([^\]]+)\]\s*', line.strip())
        if section:
            remaining()
            current = section[1]
        key = line.split('=', 1)[0].strip() if '=' in line and not line.lstrip().startswith(('#', ';')) else None
        if current in pending and key in pending[current]:
            line = key + '=' + pending[current].pop(key) + '\n'
        lines.append(line if line.endswith(('\n', '\r')) else line + '\n')
    remaining()
    for section, values in pending.items():
        lines.append('\n[' + section + ']\n')
        lines.extend(key + '=' + value + '\n' for key, value in values.items())
    return ''.join(lines)
