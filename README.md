# Portfolio — pratzy101.github.io/Portfolio

Personal site for Prathit Shaandilya. Static, no framework, no build step, no dependencies.
Deployed from `main` on GitHub Pages.

**Live:** https://pratzy101.github.io/Portfolio/

---

## Why it's built this way

The site is hand-written HTML, CSS and JavaScript. There is no bundler, no package manager,
and nothing to install — `git clone` and open `index.html`.

That is a deliberate constraint rather than a limitation. A portfolio is a document that has to
keep working untouched for months at a time. A build step is a dependency that rots: a
lockfile ages, a transitive dependency breaks, and a site that was fine in March fails to
build in September. Static files do not have that failure mode.

The trade-off is real and worth naming: there is no templating, so the page chrome — the four
fixed corners, both navigations, the footer, the meta block — is duplicated across all five
pages. Changing a nav link means changing it in five files. That is the price of the
constraint, and it is only affordable because the page count is small and roughly fixed. If
this site ever reaches a dozen pages, the correct move is a build step, not more discipline.

---

## Structure

```
.
├── index.html                        homepage
├── log.html                          build log
├── work/
│   ├── gap-reporting-tool/           case study — written
│   ├── power-platform-suite/         case study — scaffolded, not written
│   └── quadcopter-drones/            case study — scaffolded, not written
├── assets/
│   ├── site.css                      all styles, every page
│   ├── site.js                       shared behaviour, every page
│   ├── og-image.png                  social share card, 1200×630
│   ├── og-image.html                 source for regenerating the above
│   └── Prathit_Shaandilya_Resume.pdf
├── 404.html                          themed, self-contained by design
├── robots.txt
└── sitemap.xml
```

`404.html` keeps its own inline CSS on purpose. If `assets/site.css` ever fails to load, the
error page is the one page that still has to render.

---

## Conventions

**Design tokens.** Every colour and size is a CSS custom property in `:root` at the top of
`assets/site.css`. Nothing downstream hardcodes a hex value. Changing the palette is one
block.

**Module markers.** CSS and JS are divided by `MODULE START` / `MODULE END` comment pairs.
The markers are load-bearing for navigation, not decoration — the stylesheet is ~520 lines.

**Shared vs page-specific JS.** `assets/site.js` holds behaviour every page needs (cursor,
mobile menu, scroll reveal, magnetic buttons). Modules that can only ever run on one page —
active-nav tracking and the GitHub activity feed — stay inline in `index.html`. Shipping them
site-wide would mean four pages parsing code that can never fire.

Each module in `site.js` bails early if the elements it owns are absent. Without that, a
missing element on a subpage throws and every module defined *after* it silently stops
running.

**Layout grid.** The experience timeline, case-study sections, and log entries all use the
same `120px 1fr` grid. That is why the pages read as one system rather than three designs.

---

## Working on it

No install step.

```bash
git clone https://github.com/Pratzy101/Portfolio.git
cd Portfolio
python3 -m http.server 8000
```

Then open `http://localhost:8000`. A plain file open (`file://`) mostly works, but the GitHub
activity fetch behaves differently from that origin, so use the server when touching it.

Deploy is `git push` — GitHub Pages rebuilds from `main` within a minute or two.

---

## Unfinished

- Two case-study pages are scaffolded but not written. They are linked from the homepage and
  marked with visible `.tbd` blocks. Deliberately excluded from `sitemap.xml` until written.
- `assets/og-image.png` was rendered without Space Grotesk available and uses a substitute
  face. `assets/og-image.html` regenerates it brand-exact via a browser screenshot.
- A retrieval-augmented chat over the site's content was scoped and deferred. The corpus is
  around 4,000 tokens against a 200,000-token context window, so retrieval would be
  decoration rather than architecture until there is more here to retrieve.

---

## Analytics

Cloudflare Web Analytics. Cookie-free, no cross-site tracking, nothing stored on the
visitor's device — so no consent banner. The beacon token is public by design; it identifies
the site, not the visitor, and grants no access to the data.
