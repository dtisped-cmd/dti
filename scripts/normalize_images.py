#!/usr/bin/env python3
import os
import json
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(ROOT, 'assets')
FILES_TO_UPDATE = [
    os.path.join(ROOT, 'content', 'site_content.json'),
    os.path.join(ROOT, 'content', 'body.html'),
    os.path.join(ROOT, 'index.html'),
    os.path.join(ROOT, 'original.html'),
    os.path.join(ROOT, 'original_view.html'),
]

def find_images():
    if not os.path.isdir(ASSETS):
        return []
    exts = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
    files = [f for f in os.listdir(ASSETS) if f.lower().endswith(exts)]
    return sorted(files)

def make_name(i, orig):
    base, ext = os.path.splitext(orig)
    return f'img-{i}{ext}'

def update_references(mapping):
    for path in FILES_TO_UPDATE:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()
        for old, new in mapping.items():
            txt = txt.replace(old, new)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)

def update_json_site_content(mapping):
    p = os.path.join(ROOT, 'content', 'site_content.json')
    if not os.path.exists(p):
        return
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    changed = False
    for img in data.get('images', []):
        local = img.get('local')
        if not local: continue
        b = os.path.basename(local)
        if b in mapping:
            img['local'] = os.path.join('assets', mapping[b])
            changed = True
    if changed:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    imgs = find_images()
    if not imgs:
        print('No images found in assets/')
        return 0
    mapping = {}
    for i, name in enumerate(imgs, start=1):
        new = make_name(i, name)
        old_path = os.path.join(ASSETS, name)
        new_path = os.path.join(ASSETS, new)
        if os.path.exists(new_path):
            # avoid clobbering
            continue
        os.rename(old_path, new_path)
        mapping[name] = new
    if mapping:
        # update references across files
        update_references(mapping)
        update_json_site_content(mapping)
        print('Renamed images and updated references:')
        for k,v in mapping.items():
            print(f'  {k} -> {v}')
    else:
        print('No renames performed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
