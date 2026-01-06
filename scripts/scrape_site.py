#!/usr/bin/env python3
import os
import sys
import json
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    print('missing-deps')
    sys.exit(2)


def safe_filename(url):
    p = urlparse(url)
    name = os.path.basename(p.path) or 'image'
    name = name.split('?')[0]
    if not os.path.splitext(name)[1]:
        name += '.png'
    return name


def download_file(session, src, outdir):
    try:
        r = session.get(src, timeout=15)
        r.raise_for_status()
    except Exception as e:
        return None
    fname = safe_filename(src)
    path = os.path.join(outdir, fname)
    with open(path, 'wb') as f:
        f.write(r.content)
    return path


def main():
    if len(sys.argv) < 2:
        print('usage: scrape_site.py <url>')
        sys.exit(1)
    url = sys.argv[1]
    work = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(work, 'assets')
    content_dir = os.path.join(work, 'content')
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(content_dir, exist_ok=True)

    session = requests.Session()
    resp = session.get(url, headers={'User-Agent': 'dti-scraper/1.0'}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # extract basic metadata
    data = {}
    data['url'] = url
    data['title'] = (soup.title.string.strip() if soup.title and soup.title.string else '')
    desc = soup.find('meta', attrs={'name':'description'})
    data['description'] = desc['content'].strip() if desc and desc.get('content') else ''

    # collect headings and paragraphs
    data['headings'] = []
    for h in soup.find_all(['h1','h2','h3']):
        text = h.get_text(separator=' ', strip=True)
        if text:
            data['headings'].append({'tag':h.name, 'text': text})

    data['paragraphs'] = []
    for p in soup.find_all('p'):
        t = p.get_text(separator=' ', strip=True)
        if t:
            data['paragraphs'].append(t)

    # download images and rewrite srcs in a copy of body
    images = []
    body = soup.body
    if body:
        for img in body.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            full = urljoin(url, src)
            local = download_file(session, full, assets_dir)
            if local:
                images.append({'original': full, 'local': os.path.relpath(local, work)})
                img['src'] = os.path.relpath(local, work)

    data['images'] = images

    # save body HTML fragment
    body_html = str(body) if body else ''
    with open(os.path.join(content_dir, 'body.html'), 'w', encoding='utf-8') as f:
        f.write(body_html)

    # save json summary
    with open(os.path.join(content_dir, 'site_content.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('ok')


if __name__ == '__main__':
    main()
