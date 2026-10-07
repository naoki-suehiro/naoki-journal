#!/usr/bin/env python3
"""Generate a dependency-free static journal. Run from any directory."""
import json
import re
import shutil
from html import escape
from pathlib import Path
from string import Template
from site_config import site_config

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
data = json.loads((ROOT / 'content/journal.json').read_text())
site_url, base_path = site_config(data)
base = Template((ROOT / 'templates/base.html').read_text())
fields = {field['id']: field for field in data['fields']}
stories = data['stories']
seen = set()
for story in stories:
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', story['slug']), 'Invalid slug'
    assert story['slug'] not in seen, 'Duplicate slug'
    seen.add(story['slug'])
    assert story['field'] in fields, 'Unknown category'
    assert story['status'] in ('forthcoming', 'published'), 'Unknown status'
    assert isinstance(story['body'], list), 'Body must be a list of paragraphs'
    if 'translations' in story:
        assert story['defaultLanguage'] == 'ja', 'Bilingual articles start in Japanese'
        assert set(story['translations']) == {'ja', 'en'}, 'Both final copies are required'
        assert all(isinstance(story.get(key), str) and story[key].strip() for key in ('articleTitle', 'subtitle', 'issueLabel'))
        for blocks in story['translations'].values():
            assert isinstance(blocks, list) and blocks, 'Translation must contain body blocks'
            for block in blocks:
                assert block['type'] in ('paragraph', 'heading', 'lead', 'signature'), 'Unknown body block'
                assert block.get('lang') in (None, 'ja', 'en'), 'Invalid block language'
                assert isinstance(block['content'], list) and block['content'], 'Empty block'
                for span in block['content']:
                    assert isinstance(span['text'], str) and span['text'], 'Empty text'
                    assert isinstance(span.get('strong', False), bool), 'Invalid emphasis'
    assert story['status'] != 'published' or story['body'] or story.get('translations'), 'Published stories require body text'
assert len([s for s in stories if s.get('featured')]) == 1
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
e = escape

def photo(story, width=1200):
    return 'https://images.unsplash.com/' + story['image'] + '?auto=format&fit=crop&w=' + str(width) + '&q=85'

def img(story, featured=False):
    sizes = '(max-width: 700px) 100vw, 58vw' if featured else '(max-width: 700px) 45vw, (max-width: 1100px) 45vw, 23vw'
    return f'<img src="{e(photo(story))}" srcset="{e(photo(story,480))} 480w, {e(photo(story,960))} 960w, {e(photo(story,1600))} 1600w" sizes="{sizes}" alt="{e(story["alt"])}" width="1600" height="1100" {"fetchpriority=high" if featured else "loading=lazy"} decoding="async">'

def card(story):
    link = base_path + '/stories/' + story['slug'] + '/'
    return f'<article class="story"><a class="story-image" href="{link}" aria-label="{e(story["title"])}">{img(story)}</a><p class="category">{e(fields[story["field"]]["name"])}</p><h3><a href="{link}">{e(story["title"])}</a></h3><p class="story-status">{"FORTHCOMING" if story["status"] == "forthcoming" else "BY NAOKI SUEHIRO"}</p></article>'

def render_blocks(blocks):
    rendered = []
    for block in blocks:
        tag = 'h2' if block['type'] == 'heading' else 'p'
        block_class = {'lead': 'article-lead', 'signature': 'editorial-signature'}.get(block['type'])
        attrs = f' class="{block_class}"' if block_class else ''
        if block.get('lang'):
            attrs += f' lang="{block["lang"]}"'
        spans = []
        for span in block['content']:
            text = e(span['text']).replace('\n', '<br>')
            spans.append('<strong>' + text + '</strong>' if span.get('strong') else text)
        rendered.append(f'<{tag}{attrs}>' + ''.join(spans) + f'</{tag}>')
    return '\n'.join(rendered)

def bilingual_article(story):
    bodies = []
    for language in ('ja', 'en'):
        hidden = '' if language == story['defaultLanguage'] else ' hidden'
        note = '<p>Originally written in Japanese.</p>' if language == 'en' else ''
        bodies.append(f'''<section id="article-{language}" class="article-body" lang="{language}" aria-label="{'日本語本文' if language == 'ja' else 'English article'}"{hidden}>
{render_blocks(story['translations'][language])}
<footer class="article-colophon" lang="en">{note}<p>NAOKI JOURNAL · {e(story['issueLabel'])}</p></footer>
</section>''')
    return f'''<article class="article-page bilingual-article" data-bilingual-article>
<header class="article-heading" lang="en">
<p class="category">{e(story['issueLabel'])} · {e(fields[story['field']]['name'])}</p>
<h1>{e(story['articleTitle'])}</h1>
<p class="article-subtitle">{e(story['subtitle'])}</p>
</header>
<div class="language-switch" role="group" aria-label="本文の言語 / Article language" hidden>
<button type="button" id="language-ja" lang="ja" aria-pressed="true" aria-controls="article-ja" data-language="ja">日本語</button>
<span aria-hidden="true">｜</span>
<button type="button" id="language-en" lang="en" aria-pressed="false" aria-controls="article-en" data-language="en">ENGLISH</button>
</div>
<div class="article-image" lang="en">{img(story,True)}</div>
{''.join(bodies)}
<a class="text-link article-back" lang="en" href="{base_path}/">← BACK TO THE JOURNAL</a>
</article>'''

pages = []
def page(path, title, content, description=None, noindex=False, story=None, bilingual=False):
    target = OUT / path / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    canonical = site_url + '/' + (path + '/' if path else '')
    image_story = story or next(s for s in stories if s.get('featured'))
    article_assets = f'\n<link rel="stylesheet" href="{base_path}/assets/article.css">\n<script src="{base_path}/assets/article-language.js" defer></script>' if bilingual else ''
    rendered = base.substitute(title=e(title), description=e(description or data['description']), canonical=e(canonical), content=content, robots='noindex, follow' if noindex else 'index, follow', og_type='article' if story and story['status'] == 'published' else 'website', og_image=e(photo(image_story,1600)), og_alt=e(image_story['alt']), document_lang='ja' if bilingual else 'en', og_locale='ja_JP' if bilingual else 'en_US', chrome_lang=' lang="en"' if bilingual else '', article_assets=article_assets, base_path=e(base_path))
    target.write_text(rendered)
    if not noindex:
        pages.append(canonical)

featured = next(s for s in stories if s.get('featured'))
featured_published = featured['status'] == 'published'
featured_action = 'READ THE STORY' if featured_published else 'FORTHCOMING STORY'
featured_label = ('Read the story: ' if featured_published else 'Explore the forthcoming story: ') + featured['title']
latest = ''.join(card(s) for s in stories if not s.get('featured'))
field_links = ''.join(f'<a class="field" href="{base_path}/categories/{f["id"]}/"><span class="field-number">{i:02}</span><h3>{e(f["name"])}</h3><p>{e(f["topics"])}</p><span class="field-arrow" aria-hidden="true">↗</span></a>' for i,f in enumerate(data['fields'],1))
content = f'''
<section class="hero wrap" aria-labelledby="journal-title">
<div class="hero-top"><p class="eyebrow">AN INDEPENDENT JOURNAL</p><p class="eyebrow">EST. 2026 · JAPAN & BEYOND</p></div>
<h1 id="journal-title">NAOKI JOURNAL</h1>
<div class="hero-bottom"><p class="hero-description">Thoughts on Education, Work,<br>Life, and the World.</p><p class="hero-copy">Experience becomes philosophy<br>when we give it words.</p></div>
</section>
<section class="featured wrap" aria-labelledby="featured-title"><a class="featured-image" href="{base_path}/stories/{featured['slug']}/" aria-label="{e(featured_label)}">{img(featured,True)}</a><div class="featured-content"><p class="eyebrow issue">ISSUE 001 / OCTOBER 2026</p><div><p class="category">GLOBAL WORKFORCE</p><h2 id="featured-title"><a href="{base_path}/stories/{featured['slug']}/">{e(featured['title'])}</a></h2><p class="byline">BY NAOKI SUEHIRO</p></div><a class="text-link" href="{base_path}/stories/{featured['slug']}/">{featured_action} <span aria-hidden="true">↗</span></a></div></section>
<section class="section wrap" id="stories" aria-labelledby="stories-title"><div class="section-heading"><h2 class="section-label" id="stories-title">FORTHCOMING</h2></div><div class="story-grid">{latest}</div></section>
<section class="section fields wrap" id="fields" aria-labelledby="fields-title"><div class="section-heading"><h2 class="section-label" id="fields-title">EXPLORE BY FIELD</h2><p>Four fields. One unfolding perspective.</p></div>{field_links}</section>
<section class="statement" aria-labelledby="statement-title"><div class="wrap statement-inner"><p class="section-label">THE JOURNAL STATEMENT</p><div><h2 id="statement-title">We live first.<br>Then we find the words.</h2><p>Experience becomes a question.<br>A question becomes an idea.<br>And sometimes, an idea becomes a philosophy.</p><p class="closing">NAOKI JOURNAL exists to preserve that journey.</p></div></div></section>
<section class="author wrap" id="about" aria-labelledby="author-title"><p class="section-label">ABOUT THE AUTHOR</p><div class="author-content"><div><h2 id="author-title">NAOKI SUEHIRO</h2><p class="author-roles">Educator.<br>Global Workforce Architect.<br>Writer.</p></div><div class="author-bio"><p>NAOKI JOURNAL is an independent journal by Naoki Suehiro — a collection of thoughts, questions, experiences, and stories about education, work, people, resilience, Japan, and Asia.</p><a class="text-link" href="https://naokisuehiro.com">VISIT NAOKI SUEHIRO <span aria-hidden="true">→</span></a></div></div></section>'''
interview = f'''<section class="interview wrap" aria-labelledby="interview-title">
<div class="interview-copy"><p class="eyebrow">INTERVIEW 001 / OCTOBER 2026</p><h2 id="interview-title">Starting Again</h2><p lang="ja">もう一度、歩み出す。</p><p class="interview-caption">NAOKI SUEHIRO · ENGLISH AUDIO<br><span lang="ja">日英字幕付き</span> / JAPANESE &amp; ENGLISH SUBTITLES</p></div>
<a class="interview-play" href="{base_path}/assets/NAOKI_Interview_001_Bilingual.mp4" data-interview-open aria-label="Watch the interview / インタビューを見る"><img src="{base_path}/assets/interview-001-poster.jpg" alt="Naoki Suehiro speaking in Interview 001" width="1280" height="720" loading="lazy"><span class="interview-play-label"><span aria-hidden="true">▶</span> WATCH THE INTERVIEW <span lang="ja">インタビューを見る</span></span></a>
</section>
<dialog class="interview-dialog" aria-labelledby="interview-dialog-title"><div class="interview-dialog-heading"><h2 id="interview-dialog-title">Starting Again · Interview 001</h2><button type="button" data-interview-close aria-label="Close video / 動画を閉じる">CLOSE ×</button></div><video controls playsinline preload="none" poster="{base_path}/assets/interview-001-poster.jpg"><source src="{base_path}/assets/NAOKI_Interview_001_Bilingual.mp4" type="video/mp4"><a href="{base_path}/assets/NAOKI_Interview_001_Bilingual.mp4">Watch the interview</a></video></dialog>
<script src="{base_path}/assets/interview.js" defer></script>'''
content = content.replace('<section class="featured wrap"', interview + '<section class="featured wrap"', 1)
page('', 'NAOKI JOURNAL — Experience becomes philosophy', content)
for story in stories:
    forthcoming = story['status'] == 'forthcoming'
    if 'translations' in story:
        page('stories/' + story['slug'], story['articleTitle'] + ' — NAOKI JOURNAL', bilingual_article(story), description=story['subtitle'], noindex=forthcoming, story=story, bilingual=True)
        continue
    body = '<aside class="notice"><p class="eyebrow">FORTHCOMING</p><p>This story is being prepared for NAOKI JOURNAL.</p><p lang="ja">この記事は現在準備中です。掲載タイトル・写真は仮のものです。</p></aside>' if forthcoming else ''.join('<p>' + e(p) + '</p>' for p in story['body'])
    article = f'<article class="article-page"><a class="text-link" href="{base_path}/#stories">← BACK TO THE JOURNAL</a><p class="category" style="margin-top:40px">{e(fields[story["field"]]["name"])}</p><h1>{e(story["title"])}</h1><p class="eyebrow">BY NAOKI SUEHIRO</p><div class="article-image">{img(story,True)}</div>{body}</article>'
    page('stories/' + story['slug'], story['title'] + ' — NAOKI JOURNAL', article, noindex=forthcoming, story=story)
for field in data['fields']:
    listing = ''.join(card(s) for s in stories if s['field'] == field['id'])
    page('categories/' + field['id'], field['name'] + ' — NAOKI JOURNAL', f'<section class="archive section wrap"><h1 class="archive-title">{e(field["name"])}</h1><p class="archive-intro">{e(field["topics"])}</p><div class="story-grid">{listing}</div></section>')
page('404', 'Page not found — NAOKI JOURNAL', f'<section class="article-page"><p class="eyebrow">404</p><h1>A page yet to be found.</h1><p>The page you’re looking for isn’t here.</p><a class="text-link" href="{base_path}/">RETURN TO THE JOURNAL →</a></section>', noindex=True)
shutil.copyfile(OUT / '404/index.html', OUT / '404.html')
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + site_url + '/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + e(url) + '</loc></url>' for url in pages) + '</urlset>\n')
print('Built 11 pages, 404.html, assets, robots.txt and sitemap.xml in dist/')
