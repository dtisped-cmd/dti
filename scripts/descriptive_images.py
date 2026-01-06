#!/usr/bin/env python3
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(ROOT, 'assets')
SITE_JSON = os.path.join(ROOT, 'content', 'site_content.json')
FILES_TO_UPDATE = [
    os.path.join(ROOT, 'content', 'site_content.json'),
    os.path.join(ROOT, 'content', 'body.html'),
    os.path.join(ROOT, 'content', 'body_clean.html'),
    os.path.join(ROOT, 'index.html'),
    os.path.join(ROOT, 'original.html'),
    os.path.join(ROOT, 'original_view.html'),
]

def slugify(text):
    text = text.strip()
    # replace spaces with dashes
    text = re.sub(r'\s+', '-', text)
    # keep Arabic letters, Latin letters, numbers, dashes
    text = re.sub(r'[^\u0600-\u06FFa-zA-Z0-9\-]', '', text)
    # collapse multiple dashes
    text = re.sub(r'-{2,}', '-', text)
    if not text:
        text = 'untitled'
    return text

def main():
    if not os.path.exists(SITE_JSON):
        print('site_content.json not found; run scraper first')
        return 1

    with open(SITE_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    images = data.get('images', [])
    headings = [h.get('text','') for h in data.get('headings',[])]
    title = data.get('title','')

    mapping = {}
    for i, img in enumerate(images, start=1):
        local = img.get('local')
        if not local: continue
        basename = os.path.basename(local)
        src_path = os.path.join(ASSETS, basename)
        if not os.path.exists(src_path):
            # maybe already renamed
            continue

        # choose a descriptive name: prefer heading with same index-1, then title
        desc = ''
        if i-1 < len(headings) and headings[i-1].strip():
            desc = headings[i-1]
        elif title:
            desc = title
        else:
            desc = f'image-{i}'

        slug = slugify(desc)
        ext = os.path.splitext(basename)[1]
        new_name = f'{slug}{ext}'
        new_path = os.path.join(ASSETS, new_name)
        # avoid collision
        if os.path.exists(new_path):
            new_name = f'{slug}-{i}{ext}'
            new_path = os.path.join(ASSETS, new_name)

        os.rename(src_path, new_path)
        mapping[basename] = new_name
        # update data entry
        img['local'] = os.path.join('assets', new_name)

    # write updated site_content.json
    with open(SITE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # update references in files
    for path in FILES_TO_UPDATE:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()
        for old, new in mapping.items():
            txt = txt.replace(old, new)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(txt)

    if mapping:
        print('Renamed images:')
        for k,v in mapping.items():
            print(f'  {k} -> {v}')
    else:
        print('No images renamed')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
