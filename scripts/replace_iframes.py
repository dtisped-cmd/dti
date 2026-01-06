#!/usr/bin/env python3
from bs4 import BeautifulSoup
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
TARGET_FILES = [
    os.path.join(ROOT, 'content', 'body.html'),
    os.path.join(ROOT, 'content', 'body_clean.html'),
    os.path.join(ROOT, 'original.html'),
]

PLACEHOLDER_TMPL = ('<div class="iframe-placeholder">'
                   '<p>تم استبدال عنصر مضمّن (iframe). <a href="{src}" target="_blank">فتح المصدر الأصلي</a></p>'
                   '<pre class="small">{attrs}</pre>'
                   '</div>')

def fmt_attrs(tag):
    return ' '.join(f'{k}="{v}"' for k,v in tag.attrs.items())

def process_file(path):
    if not os.path.exists(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    changed = False
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src','')
        attrs = fmt_attrs(iframe)
        placeholder = BeautifulSoup(PLACEHOLDER_TMPL.format(src=src, attrs=attrs), 'html.parser')
        iframe.replace_with(placeholder)
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    return changed

def main():
    any_changed = False
    for p in TARGET_FILES:
        if process_file(p):
            print('Processed', p)
            any_changed = True
    if not any_changed:
        print('No iframes found or no files updated')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
