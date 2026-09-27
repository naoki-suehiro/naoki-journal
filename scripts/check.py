"""Check generated internal links, metadata, headings and image alternatives."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'dist'
class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.meta = set(), [], {}
        self.h1 = 0
        self.canonical = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'img': assert a.get('alt') and a.get('width') and a.get('height'), 'Image needs alt and dimensions'
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = True

docs = {}
for path in ROOT.rglob('*.html'):
    doc = Document()
    doc.feed(path.read_text())
    assert doc.h1 == 1, str(path) + ': expected one h1'
    assert doc.canonical
    for key in ('description', 'viewport', 'og:title', 'og:image', 'robots'):
        assert doc.meta.get(key), key
    docs[path.resolve()] = doc
for path, doc in docs.items():
    for link in doc.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        dest = ROOT / url.path.lstrip('/') if url.path else path
        if dest.is_dir(): dest = dest / 'index.html'
        assert dest.exists(), f'Broken link: {link} in {path}'
        if url.fragment: assert url.fragment in docs[dest.resolve()].ids, f'Missing anchor: {link}'
print(f'PASS: {len(docs)} HTML files; internal links, anchors, H1, metadata, image alt and dimensions.')
