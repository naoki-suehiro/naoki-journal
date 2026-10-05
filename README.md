# NAOKI JOURNAL

An independent editorial journal by Naoki Suehiro. Phase 3: local launch preparation for October 1, 2026.

## Current release scope

ISSUE 001, “Japanese Language Is Not a Skill. It Is Infrastructure.”, is the only published article in the local build. The other four stories remain forthcoming. Local publication status controls generated metadata; it does not deploy the site or make it publicly accessible.

## Build, check and preview

Python 3.9+ and its standard library are sufficient. No packages, Node.js, CMS or database are required.

```sh
python3 scripts/build.py
python3 scripts/check.py
git diff --check
python3 -m http.server 8001 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8001/. Stop the server with Ctrl+C. Rebuild after source changes and reload the browser. The check script validates internal links, anchors, headings, image alternatives, resources, language controls, article publication metadata, sitemap membership, robots.txt, favicon and generated 404 files. Also review desktop/mobile rendering, keyboard operation and both language selections in a browser.

## Source files and generated output

- `content/journal.json`: site settings, categories, story metadata and approved copy.
- `templates/base.html`: shared document metadata, navigation and footer.
- `scripts/build.py`: home, category and article HTML generation.
- `scripts/check.py`: validation of generated output.
- `assets/style.css`: shared Phase 1 presentation.
- `assets/article.css`: bilingual article typography and responsive layout.
- `assets/article-language.js`: language switching only; loaded only by bilingual articles.
- `assets/favicon.svg`: journal favicon.
- `dist/`: generated output, ignored by Git. Edit sources, not this directory. The build copies assets and generates HTML, robots.txt and sitemap.xml. It does not remove obsolete routes; use a fresh build directory when preparing a deployment after route removal or renaming.

## ISSUE 001 bilingual article

The single URL is `/stories/language-as-infrastructure/`. Both approved copies are statically rendered into the HTML. `translations.ja` and `translations.en` contain ordered blocks (`paragraph`, `heading`, `lead`, `signature`), with text spans and optional `strong` emphasis. `articleTitle`, `subtitle`, `issueLabel` and `defaultLanguage` describe the article presentation. Keep the listing `title` aligned with the approved article title.

Japanese is displayed initially. The 日本語 / ENGLISH buttons switch body visibility without navigation, URL changes or storage. Buttons expose their selection and controlled panel through ARIA, with visible keyboard focus. Each body has its own language attribute. JavaScript is used only for this switch. If JavaScript is disabled or fails to load, the Japanese copy remains readable and inactive language controls stay hidden. BACK TO THE JOURNAL returns to `/`.

## Published and forthcoming stories

Every story needs a unique lowercase hyphenated `slug`, `title`, valid `field`, `status`, Unsplash `image` ID, meaningful `alt` and a `body` list. Exactly one story has `featured: true`. Bilingual stories additionally use the fields described above. Text is HTML-escaped during generation.

- `published`: requires body text or validated bilingual copy, generates `index, follow`, `og:type=article` and a sitemap entry. The home feature CTA becomes READ THE STORY.
- `forthcoming`: generates `noindex, follow` and is excluded from the sitemap. Unwritten stories display a FORTHCOMING notice. Their placeholder titles and photos are retained. A completed bilingual draft can also stay forthcoming while showing its copy locally.

The current sitemap contains six URLs: HOME, four category pages and ISSUE 001. The other four articles remain accessible as forthcoming pages but are not indexing targets. robots.txt allows crawling and points to the sitemap; per-page metadata controls article indexing.

## Metadata and photography

The canonical site URL is `https://naoki-suehiro.github.io/naoki-journal`, configured in `content/journal.json` and overridable with `JOURNAL_SITE_URL`. ISSUE 001 uses its approved English title and subtitle for title/description and OGP, `ja_JP` for its initial OGP locale, and a summary-large-image Twitter card. Language switching does not change metadata or canonical.

All current photos remain the existing illustrative Unsplash images, loaded from images.unsplash.com. They do not document the author's experiences and require an internet connection. ISSUE 001 keeps its existing photo, including for OGP. Replacement with photography from actual teaching is a separate phase. No dedicated OGP artwork, Article structured data or publication-date field is included in this release. There are no analytics, embedded widgets or font downloads. Existing author website links are retained.

## Deployment is a separate operation

Build and check only prepare and validate files. The repository now has a GitHub Pages deployment workflow; pushing main triggers it. DNS and custom-domain configuration remain separate tasks.

After local review, freeze the approved release in Git. Then, only as a separately authorized operation, configure a dedicated journal repository/hosting environment and deploy the output from that revision. Keep any preview private; avoid connecting a push-triggered production deployment before release is approved. Host `dist/` with directory-index support, HTTPS, the journal's own domain and a custom 404 handler that serves `404.html` with HTTP status 404. Python's local server does not automatically use the custom 404 page for missing routes; inspect `/404.html` locally and verify the actual fallback on the selected host.

Before public release, confirm metadata, six sitemap URLs, robots.txt, image availability and the complete reading path. Production hosting, domain ownership and DNS must be verified separately. The author's official site is outside this project's editing and deployment scope.

## GitHub Pages project paths

The existing `.github/workflows/main.yml` builds and deploys on pushes to `main`. Its build job sets `JOURNAL_BASE_PATH=/naoki-journal` and `JOURNAL_SITE_URL=https://naoki-suehiro.github.io/naoki-journal` for both build and check. All internal links, CSS, JavaScript and favicon paths include the mount prefix. External photos and external website links are unchanged. Canonical, OGP URL, sitemap and the sitemap reference in robots.txt use the full site URL.

For the existing root-based local preview, use the ordinary build/check commands above with these environment variables unset. To reproduce the Pages mount locally:

```sh
JOURNAL_BASE_PATH=/naoki-journal python3 scripts/build.py
JOURNAL_BASE_PATH=/naoki-journal python3 scripts/check.py
mkdir -p /tmp/naoki-journal-preview
ln -sfn "$PWD/dist" /tmp/naoki-journal-preview/naoki-journal
python3 -m http.server 8003 --bind 127.0.0.1 --directory /tmp/naoki-journal-preview
```

Open http://127.0.0.1:8003/naoki-journal/. Run `python3 scripts/test_paths.py` to test both mount configurations in temporary directories, including a regression test that rejects a broken root-relative asset URL. For a future custom-domain deployment, change the workflow site URL and base path together (empty base path for a domain root).

`404.html` uses mount-prefixed assets and HOME links, so they also work when Pages serves it for an unknown nested URL. The language buttons only change visibility; they do not construct URLs. The generated project-level robots.txt contains the correct sitemap URL, but crawlers look for robots.txt at the host root, not `/naoki-journal/robots.txt`. This project does not alter the host-root site; forthcoming articles retain their own noindex metadata.
