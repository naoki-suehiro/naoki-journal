"""Check generated internal links, metadata, headings and image alternatives."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree
from site_config import site_config

ROOT = Path(__file__).resolve().parents[1] / 'dist'
data = json.loads((ROOT.parent / 'content/journal.json').read_text())
base_url, base_path = site_config(data)

def local_file(url_path):
    assert url_path.startswith(base_path + '/'), f'URL outside base path: {url_path}'
    return ROOT / url_path[len(base_path):].lstrip('/')

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.meta = set(), [], {}
        self.h1 = 0
        self.canonical = False
        self.elements = {}
        self.resources = []
        self.html_lang = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, 'Duplicate ID'
            self.ids.add(a['id'])
            self.elements[a['id']] = a
        if tag == 'html': self.html_lang = a.get('lang')
        if tag == 'script': self.resources.append(a.get('src', ''))
        if tag == 'link' and a.get('rel') in ('stylesheet', 'icon'): self.resources.append(a['href'])
        if tag == 'h1': self.h1 += 1
        if tag == 'img':
            assert a.get('alt') and a.get('width') and a.get('height'), 'Image needs alt and dimensions'
            self.resources.append(a['src'])
            self.resources.extend(item.strip().split()[0] for item in a.get('srcset', '').split(',') if item.strip())
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')

docs = {}
for path in ROOT.rglob('*.html'):
    doc = Document()
    doc.feed(path.read_text())
    assert doc.h1 == 1, str(path) + ': expected one h1'
    route = path.relative_to(ROOT).as_posix()
    route = route[:-10] if route.endswith('index.html') else '404/'
    assert doc.canonical == base_url + '/' + route
    assert doc.meta['og:url'] == doc.canonical
    for key in ('description', 'viewport', 'og:title', 'og:image', 'robots'):
        assert doc.meta.get(key), key
    docs[path.resolve()] = doc
for path, doc in docs.items():
    for resource in doc.resources:
        if urlsplit(resource).scheme or urlsplit(resource).netloc: continue
        assert local_file(resource).is_file(), f'Missing resource: {resource}'
    for link in doc.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        dest = local_file(url.path) if url.path else path
        if dest.is_dir(): dest = dest / 'index.html'
        assert dest.exists(), f'Broken link: {link} in {path}'
        if url.fragment: assert url.fragment in docs[dest.resolve()].ids, f'Missing anchor: {link}'

data = json.loads((ROOT.parent / 'content/journal.json').read_text())
sitemap = ElementTree.parse(ROOT / 'sitemap.xml')
urls = [node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
expected_urls = {base_url + '/'} | {base_url + '/categories/' + field['id'] + '/' for field in data['fields']}
expected_urls |= {base_url + '/stories/' + story['slug'] + '/' for story in data['stories'] if story['status'] == 'published'}
assert len(urls) == len(set(urls)) and set(urls) == expected_urls, 'Unexpected sitemap URLs'
assert (ROOT / 'robots.txt').read_text() == 'User-agent: *\nAllow: /\nSitemap: ' + base_url + '/sitemap.xml\n'
assert (ROOT / '404.html').read_bytes() == (ROOT / '404/index.html').read_bytes()
assert docs[(ROOT / '404.html').resolve()].meta['robots'] == 'noindex, follow'
assert (ROOT / 'assets/favicon.svg').is_file()
for story in data['stories']:
    path = (ROOT / 'stories' / story['slug'] / 'index.html').resolve()
    doc = docs[path]
    published = story['status'] == 'published'
    assert doc.meta['robots'] == ('index, follow' if published else 'noindex, follow')
    assert doc.meta['og:type'] == ('article' if published else 'website')
    assert doc.canonical == base_url + '/stories/' + story['slug'] + '/'
    assert doc.meta['og:url'] == doc.canonical
    assert doc.meta['twitter:card'] == 'summary_large_image'
    if 'translations' not in story:
        continue
    assert doc.html_lang == 'ja'
    assert doc.canonical == base_url + '/stories/' + story['slug'] + '/'
    for language in ('ja', 'en'):
        panel = doc.elements['article-' + language]
        button = doc.elements['language-' + language]
        assert panel['lang'] == language
        assert ('hidden' in panel) == (language != story['defaultLanguage'])
        assert button['type'] == 'button'
        assert button['aria-controls'] == panel['id']
        assert button['aria-pressed'] == ('true' if language == story['defaultLanguage'] else 'false')
    if story['status'] == 'forthcoming':
        assert doc.meta['robots'] == 'noindex, follow'
        assert doc.canonical not in (ROOT / 'sitemap.xml').read_text()
    print('PASS: bilingual language markup, no-JS initial state, controls and canonical:', story['slug'])
print(f'PASS: publication metadata, sitemap ({len(urls)} URLs), robots.txt, 404 and favicon.')
print(f'PASS: {len(docs)} HTML files; internal links, anchors, H1, metadata, image alt and dimensions.')
