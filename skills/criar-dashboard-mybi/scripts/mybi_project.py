"""Multi-dashboard packages: independent XMLs and one merged formatting INI."""
import configparser
import io
import zipfile
from pathlib import Path
import mybi_package as pkg


def project_entries(plan, base_ini=None):
    pkg.keys(plan, {'project'}, 'Projeto')
    pkg.keys(plan['project'], {'dashboards'}, 'project')
    dashboards = plan['project'].get('dashboards')
    pkg.require(isinstance(dashboards, list) and 1 <= len(dashboards) <= 20, 'Projeto exige 1..20 dashboards')
    entries, edits, names = {}, {}, set()
    if base_ini:
        pkg.require(Path(base_ini).stat().st_size <= pkg.MAX_SIZE, 'INI excede limite')
    original = Path(base_ini).read_text(encoding='utf-8-sig') if base_ini else ''
    for dash in dashboards:
        pkg.keys(dash, {'plan', 'baseXml', 'baseFormatDir'}, 'Dashboard do projeto')
        child = dash.get('plan')
        pkg.require(isinstance(child, dict) and 'project' not in child, 'Plano de dashboard inválido')
        base = dash.get('baseXml')
        pkg.require(bool(base) == bool(child.get('dataSource', {}).get('existingSource')), 'Cada fonte existente exige seu próprio baseXml')
        entry = pkg.dashboard_entry(base, child)
        pkg.require(entry.casefold() not in names, 'Nome XML duplicado no projeto')
        names.add(entry.casefold())
        entries[entry] = pkg.build_xml(child, base)
        formats = pkg.format_entries(child, base, base_ini, dash.get('baseFormatDir'))
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read_string(formats.pop(pkg.FORMAT_ENTRY).decode('utf-8-sig'))
        stem = Path(entry).stem
        for section in parser.sections():
            if section == stem or section.startswith(stem + '_'):
                pkg.require(section not in edits, 'Seção de formatação duplicada')
                edits[section] = dict(parser[section])
        for name, value in formats.items():
            pkg.require(name.casefold() not in names, 'Arquivo duplicado no projeto')
            names.add(name.casefold()); entries[name] = value
    entries[pkg.FORMAT_ENTRY] = pkg.merge_ini(original, edits).encode('utf-8') if edits else original.encode('utf-8')
    pkg.require(sum(map(len, entries.values())) <= 40_000_000, 'Projeto excede limite total')
    return entries


def validate_project_zip(path, plan, base_ini=None):
    expected = project_entries(plan, base_ini)
    with zipfile.ZipFile(path) as archive:
        pkg.require(archive.namelist() == list(expected), 'Arquivos inesperados, duplicados ou ausentes no projeto')
        for name, value in expected.items():
            info = archive.getinfo(name)
            pkg.require(info.file_size <= pkg.MAX_SIZE and not info.flag_bits & 1, 'Arquivo inválido no projeto')
            pkg.require((info.external_attr >> 16) & 0o170000 != 0o120000, 'Link simbólico proibido')
            actual = archive.read(info)
            if name.endswith('.xml'):
                pkg.require(pkg.canonical(actual) == pkg.canonical(value), 'XML do projeto diverge do plano/base')
            else:
                pkg.require(actual == value, 'Formatação do projeto diverge do plano/base')
    return len(plan['project']['dashboards'])


def build_project_zip(plan, output, base_ini=None):
    entries = project_entries(plan, base_ini)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries.items(): archive.writestr(name, value)
    buffer.seek(0)
    validate_project_zip(buffer, plan, base_ini)
    with Path(output).open('xb') as stream: stream.write(buffer.getvalue())
