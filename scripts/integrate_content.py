#!/usr/bin/env python3
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(__file__))
SITE_JSON = os.path.join(ROOT, 'content', 'site_content.json')
INDEX_HTML = os.path.join(ROOT, 'index.html')

def build_fragment(data):
    parts = []
    parts.append('<section id="imported" class="section">')
    parts.append('  <div class="container">')
    parts.append('    <h3>المحتوى المستورد من الموقع الأصلي</h3>')
    # Add metadata
    title = data.get('title')
    if title:
        parts.append(f'    <p class="muted">عنوان المصدر: {title}</p>')

    # Insert headings and paragraphs in order
    headings = data.get('headings', [])
    paragraphs = data.get('paragraphs', [])

    if headings:
        parts.append('    <div class="import-headings">')
        for h in headings:
            tag = h.get('tag','h2')
            text = h.get('text','').strip()
            if not text: continue
            # normalize heading levels to h3/h4 for page
            if tag.lower() == 'h1':
                parts.append(f'      <h3>{text}</h3>')
            else:
                parts.append(f'      <h4>{text}</h4>')
        parts.append('    </div>')

    if paragraphs:
        parts.append('    <div class="import-paragraphs">')
        for p in paragraphs:
            txt = p.strip()
            if not txt: continue
            parts.append(f'      <p>{txt}</p>')
        parts.append('    </div>')

    images = data.get('images', [])
    if images:
        parts.append('    <div class="import-images">')
        for im in images:
            local = im.get('local') or im.get('original')
            if not local: continue
            parts.append(f'      <figure><img src="{local}" alt="Imported image"><figcaption>{os.path.basename(local)}</figcaption></figure>')
        parts.append('    </div>')

    parts.append('  </div>')
    parts.append('</section>')
    return '\n'.join(parts)


def main():
    if not os.path.exists(SITE_JSON):
        print('site_content.json not found at', SITE_JSON)
        return 1

    with open(SITE_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fragment = build_fragment(data)

    # Backup index.html
    if os.path.exists(INDEX_HTML):
        bak = INDEX_HTML + '.bak'
        if not os.path.exists(bak):
            shutil.copyfile(INDEX_HTML, bak)

        html = open(INDEX_HTML, 'r', encoding='utf-8').read()
        # Insert the fragment before the closing </main>
        if '</main>' in html:
            new_html = html.replace('</main>', fragment + '\n\n    </main>', 1)
        else:
            # fallback: append before footer
            if '</body>' in html:
                new_html = html.replace('</body>', fragment + '\n\n</body>', 1)
            else:
                print('Could not find insertion point in index.html')
                return 1

        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(new_html)

        print('Integrated content into', INDEX_HTML)
        return 0
    else:
        print('index.html not found')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
