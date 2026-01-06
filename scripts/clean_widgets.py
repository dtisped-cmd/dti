#!/usr/bin/env python3
from bs4 import BeautifulSoup
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
SOURCE = os.path.join(ROOT, 'content', 'body.html')
CLEAN = os.path.join(ROOT, 'content', 'body_clean.html')

def main():
    if not os.path.exists(SOURCE):
        print('source body.html not found')
        return 1
    with open(SOURCE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # remove script and iframe tags
    for tag in soup.find_all(['script', 'iframe']):
        tag.decompose()

    # remove inline event handlers to reduce external behavior
    for el in soup.find_all(True):
        attrs = dict(el.attrs)
        for a in list(attrs.keys()):
            if a.startswith('on'):
                del el.attrs[a]

    # write cleaned output
    with open(CLEAN, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print('Wrote cleaned body to', CLEAN)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
