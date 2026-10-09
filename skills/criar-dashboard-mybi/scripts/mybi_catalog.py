"""Search component contracts locally, without loading the whole catalog into chat."""
import argparse
import json
import unicodedata
from pathlib import Path
from mybi_references import load_reference


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c) and c.isalnum())


def search(query, detail=False, include_hidden=False):
    ref=Path(__file__).resolve().parents[1]/'references'
    catalog=load_reference(ref/'catalog.json')
    inventory=load_reference(ref/'toolbar-inventory.json')
    entries={entry['name']:entry for entry in inventory['captured'].values()}
    result=[]; term=normalized(query)
    for name in sorted(set(catalog)|set(entries)):
        contract=catalog.get(name); entry=entries.get(name,{})
        if not include_hidden and entry.get('visibility') == 'hidden-by-runtime': continue
        title=(contract or {}).get('displayName',entry.get('displayName',name))
        group=(contract or {}).get('group',entry.get('group',''))
        if term and not any(term in normalized(s) for s in (name,title,group)): continue
        item={'component':name,'displayName':title,'group':group,
              'generation':'contract' if contract else 'manual-configuration',
              'visibility':entry.get('visibility','native')}
        if detail: item.update({'contract':contract,'optionsPanel':entry.get('options',[])})
        result.append(item)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?',default=''); parser.add_argument('--detail',action='store_true')
    parser.add_argument('--include-hidden',action='store_true')
    args=parser.parse_args(); print(json.dumps(search(args.query,args.detail,args.include_hidden),ensure_ascii=False,indent=2))
