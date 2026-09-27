# NAOKI JOURNAL

An independent editorial journal by Naoki Suehiro. Phase 1 / target launch: October 1, 2026.

## Local preview

Python 3.9+ only; no packages, Node.js, CMS or database required.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://localhost:8000. Stop with Ctrl+C. Re-run the build after source changes.

## Files and publishing

- `content/journal.json`: site settings, categories and stories.
- `templates/base.html`: shared document metadata, navigation and footer.
- `scripts/build.py`: HTML generation, home, category and article layouts.
- `scripts/check.py`: generated HTML and internal link checks.
- `assets/style.css`: responsive presentation; system serif/sans fonts.
- `assets/favicon.svg`: journal favicon.
- `dist/`: generated deployment output (ignored by Git).

Upload `dist/` to a static hosting provider supporting directory index pages. Configure its 404 handler to use `404.html`. Connect `naokijournal.com` through that provider's domain/DNS settings and enable HTTPS. Hosting/DNS are not configured by this project. The canonical base URL lives in `content/journal.json`; change it before building if the production domain changes. Restrict indexing of any public staging deployment through hosting settings.

## Adding stories

Add a record under `stories` with a unique lowercase hyphenated `slug`, `title`, existing `field`, `status`, `image` (Unsplash image ID), meaningful `alt`, and `body` (array of plain-text paragraphs). Exactly one story must have `featured: true`. A `forthcoming` story displays an explicit placeholder and is excluded from the sitemap with `noindex, follow`. Set `status: published` only once a nonempty, reviewed body exists. Rebuild. Published body text is HTML-escaped. URLs follow `/stories/{slug}/`; category pages follow `/categories/{field}/`. The four non-featured sample articles populate the home grid; pagination and editorial ordering can be added in Phase 2. Remove obsolete generated files when removing/renaming published routes during deployment.

## Photography and launch readiness

Photos are provisional illustrative images loaded from images.unsplash.com; they do not document Naoki Suehiro's experiences. External image availability requires internet access. There are no external API calls, analytics, embedded widgets, or font downloads. Replace these photos with approved author-owned or licensed local images before launch, adapting the `photo()` helper as needed. Current OGP uses the featured placeholder photo; produce a branded social image in Phase 2. The author's official website link points to https://naokisuehiro.com.

The inaugural story titles are supplied placeholders. No article prose or personal history has been invented. Phase 2 should add reviewed article bodies, publication dates, richer article typography, related articles, final photographs, a branded OGP asset, Article structured data, and production hosting/domain configuration. Review actual browser rendering at desktop/tablet/mobile sizes, image descriptions, keyboard navigation and contrast before launch. Automatic checks do not substitute for visual or screen-reader review.
