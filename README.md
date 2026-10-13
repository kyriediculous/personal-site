# Nico Vergauwen’s personal site

Personal site and blog for applied AI, agents, and distributed infrastructure.
Source: [kyriediculous/personal-site](https://github.com/kyriediculous/personal-site).
Public site: [nicovergauwen.pages.dev](https://nicovergauwen.pages.dev/).

The site is static HTML, CSS, and JavaScript, built with Python. It contains the
project portfolio, research, career history, ten locally archived Medium articles,
and the Jacobi Forcing article with its motion graphic.

## Run locally

```sh
python3 build.py
python3 serve.py
```

Open [127.0.0.1:4173](http://127.0.0.1:4173/). The preview binds only to loopback.
Python 3 is sufficient to build and serve the site. No npm packages are required.

To run the delivery checks:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m unittest discover -s tests -v
```

## Deploy with Cloudflare Pages

Connect the `kyriediculous/personal-site` GitHub repository through Cloudflare
Pages' Git integration. Limit the GitHub app installation to this repository.
Use these settings:

- Project name: `nicovergauwen`.
- Production branch: `main`.
- Framework preset: None.
- Build command: `sh build_cloudflare.sh`.
- Build output directory: `dist`.
- Root directory: repository root (leave blank).
- Environment variable: `SKIP_DEPENDENCY_INSTALL=1`.
- Python: `.python-version` selects Python 3.12.

Cloudflare runs the build and all delivery checks before uploading only `dist/`.
A failed check stops deployment. Pushes to `main` rebuild production; other
branches receive previews. GitHub Actions runs the same checks independently on
pushes and pull requests. Official actions are pinned to commit SHAs, and the
workflow needs only read access. GitHub Pages is not enabled.

`src/site.json` contains the public HTTPS origin used for canonical URLs, social
previews, RSS, and the sitemap. Cloudflare assigned `nicovergauwen.pages.dev`.
A future custom domain requires updating the origin and adding that domain in
Cloudflare Pages.

Styles, scripts, and the embedded Jacobi MP4 and poster carry content hashes in
their URLs to avoid stale browser assets after an update. Git integration needs
no API token in this repository or GitHub Actions. This static site needs no
Pages Functions or paid services.

## Edit the site

- `src/content.json`: projects, career history, and selected writing.
- `build.py`: page templates and static output.
- `src/site.css` and `src/site.js`: styles, navigation, and copy-link behavior.
- `src/site.json`: public site origin.
- `content/jacobi-forcing/`: canonical article text, diagram, cover, and video.
- `src/medium/posts.json` and `src/medium/*/article.html`: imported articles.
- `assets/`: fonts, portrait, brand logos, and archived article images.

The repository is self-contained. The Jacobi page and its text download match
the current canonical article. The 12 October 2026 voice revision uses the
author’s archived 2018–2021 writing; `content/jacobi-forcing/voice-notes.txt`
records the references and editing guidance. `DESIGN_MEMORY.md` records owner
feedback, including the correction toward a technical audience and a mechanism-first
opening. Native browser controls handle the silent motion graphic. Its current
source is a 30-second technical promo opening with “What if LLMs could generate
multiple tokens at once?” A token tile becomes a parallel block, then the
mechanism and training explanation lead to an illustrative multi-token commit
and the scoped benchmark payoff. The clip closes on the article's actual URL.
Article prose is unchanged by this video cut. The final 30-second, 900-frame
silent H.264 export passes complete decoding and encoded-frame review; browser
playback advances without a media error. Canonical and site media copies match,
and the exact Cloudflare build passes all 15 acceptance tests. Production deployment and
publication-ZIP verification are recorded separately in the delivery evidence.

## Social link previews

The homepage and writing index use `assets/social/nico-vergauwen-og.jpg`, a
1200 × 630 JPEG based on the homepage hero. It uses the original portrait,
Host Grotesk font and site colors. Individual articles retain their own covers.
The build emits public Open Graph and Twitter image URLs, descriptive alt text,
MIME types, and dimensions for the homepage and Jacobi covers. A content hash
on the homepage image URL changes when its bytes change.

`src/social-card.html` is the editable card source. To update the image, serve
this file with `/assets/` resolving to the site's assets, render at exactly
1200 × 630, wait for the local font and portrait to finish loading, and capture
a JPEG to the asset path above. Inspect the image before rebuilding. The
checked-in JPEG is copied by the normal build; Cloudflare needs no browser,
image generator, external asset service or additional build dependencies.
The source preview page is not included in the public site.

## Imported articles

Homepage writing links and the blog index lead to full local posts. Each imported
article includes its original date and an original-publication link inside it.
All ten full entries available in the author’s public RSS feed on 12 October 2026
are archived; older posts absent from that feed are not claimed as included.

Authored prose, lists, captions, commands, and images are preserved. Medium
tracking pixels, RSS syndication footers, unrelated Coinmonks recommendations,
and Upscribe signup embeds are removed. X and YouTube widgets become ordinary
links. Original historical claims and code remain dated to their publication.

The 28 Go snippets and four Solidity snippets are restored as escaped local code.
Medium embed IDs were matched to the MD5 of their exact original public gist URLs.
Raw revisions and SHA-256 hashes are recorded in `src/medium/assets.json`. Article
code is displayed as text and never executed by the importer or site.

To regenerate prepared bodies from the frozen sources without network access:

```sh
python3 import_medium.py
python3 build.py
```

The optional importer flag `--fetch-assets /path/to/public-gist-inventory.json`
explicitly refreshes public image and gist bytes. Normal builds are offline.

## Content and privacy

Career facts and the portrait come from the owner-supplied résumé, supplemented
by the owner’s corrections. The original PDF, personal email, telephone number,
local review screenshots, and hosting account metadata are excluded from the
published site and repository. Contact uses LinkedIn and social profiles.

TensorCommitments authorship and NeurIPS acceptance were verified with the paper
and research lab. Its current post-training extension using lattice-based
commitments is described as ongoing work, focused on performance and post-quantum
security. VIC-HTN is omitted until a public link is available.

Colors, Host Grotesk typography, and the grokked brand lockup follow the owner’s
existing grokked.ai codebase. Kollekt’s SVG is reused unchanged. Brand assets are
local, and fonts retain their included SIL Open Font License. Business links to
kollekt.now and grokked.ai remain ordinary followable links. The site has no
analytics, third-party runtime media, cookie scripts, or signup forms.

`sources.json` records provenance. `ACCEPTANCE.md` records delivery verification.


The latest Jacobi cover and 30-second motion graphic use the site’s house style.
The cover explains serial generation versus grouped parallel guesses, including
refinement and verification. The video uses the existing Host Grotesk font and
semantic mint/sky token states. Its editable source, `frame.md` brand spec and
encoder preflight are in the publication package’s motion project.
