# Delivery verification

Reviewed on 12 October 2026 for Cloudflare Pages publication.

The homepage includes applied AI and agent work, two projects, research directly
after Projects, seven career entries, six selected local posts, and an eleven-post
blog index. Projects and every footer use the existing brand logos. Removed
achievement cards and decorative section labels remain absent. Contact uses
LinkedIn and social profiles, with no personal email or phone number.

## Automated checks

Fourteen checks cover:

- Jacobi page prose and text export match the current canonical article; its MP4
  remains identical to the original.
- Every internal page, asset, download, and fragment resolves; IDs are unique and
  each page has one main heading.
- Business backlinks remain followable, and writing/research match the inventory.
- Ten imported articles retain authored prose, original dates, and source credits.
- All 38 imported images and 32 restored snippets match archived bytes; exact gist
  URL hashes establish the original embed mapping.
- Imported pages load no remote media, trackers, active signup forms, or widgets.
- RSS, sitemap, canonical URLs, and social previews use the configured public
  origin and include every article.
- Project/footer logos have accessible link names; section and navigation order
  are Projects, Research, Writing, Experience, Contact.
- Personal email is absent and social contact links work.
- Stylesheet/script URL hashes match the served bytes, preventing stale assets.
- Social metadata resolves to real local images with matching MIME types and
  known dimensions, equivalent Twitter metadata and preserved article covers.
- The served site excludes the résumé PDF, local hosting configuration, and
  repository metadata.

## Browser review

Desktop and 375px/320px layouts were reviewed. Page overflow was absent; wide code
and the benchmark table scroll within their containers. Shared footer logos fit
at 320px. Navigation, original-publication credits, copy-link, and the 24-second
video were verified. Browser logs showed no warnings or errors. The Jacobi video
is user-initiated, and CSS transitions honor reduced-motion preferences.

## Deployment preparation

The canonical article and assets are inside this repository. A clean source-only
checkout can build without a sibling workspace or local hosting metadata.
`build_cloudflare.sh` builds and verifies before Cloudflare uploads `dist/`.
GitHub Actions runs independent build/checks with read-only permissions and pinned
official actions. GitHub no-reply identity is used for commits. Private review
files and local hosting account metadata are ignored by Git. GitHub Pages is not
enabled, and the repository contains no Cloudflare API token.

The site is live at https://nicovergauwen.pages.dev. Cloudflare Pages is connected
to the repository's `main` branch, with framework None, build command
`sh build_cloudflare.sh`, output `dist`, and `SKIP_DEPENDENCY_INSTALL=1` for
Production and Preview. The first production build succeeded on 12 October 2026.

The source is published at https://github.com/kyriediculous/personal-site. The
initial Linux CI build passed all thirteen checks:
https://github.com/kyriediculous/personal-site/actions/runs/38294731015.
A source-only Git export produces the same 71 output files byte for byte as the
reviewed local build. All thirteen local checks pass with the Pages target origin.

## Live verification

All 70 published page/asset/feed URLs match the reviewed local bytes. Six unknown
or source-only routes return HTTP 404 with the site's branded page. The MP4 is
served as `video/mp4` with identical bytes. Cloudflare rejects the default Python
client signature; verification succeeded with browser-style request headers.
Private review evidence stays outside the public repository.

The live homepage was checked on desktop and at a 320px mobile viewport. No page
or footer overflow was present; the keyboard-operated mobile menu and local blog
navigation worked. All article images loaded in the Codex browser. The 24-second
video reached ready state 4, played with advancing time, and reported no media
error. The temporary mobile viewport override was cleared after verification.

## Jacobi voice revision — 12 October 2026

Revised the article using five archived posts from 2018–2021, weighted toward
the author's personal technical tutorials. One independent review covered voice,
cadence, beginner accessibility and fidelity. That draft was 1,311 words;
its benchmark table, citations, captions and media remain unchanged. Rebuilt the
site and passed all thirteen checks, including canonical text/download parity.
The source and preview packages include the revision. The editing references and
reusable voice guidance are in `content/jacobi-forcing/voice-notes.txt`.
This revision is included in the source for the social-preview delivery below.

## Homepage social preview — 12 October 2026

Created a 1200 × 630 JPEG from `src/social-card.html`, using the site's original
portrait, local Host Grotesk font and hero palette. Verified loaded font/image
state before capture, visually reviewed the final card, and checked its actual
dimensions, format and size (67,857 bytes). The source render is excluded from
public output. The normal build uses the checked-in image with no new runtime
or deployment dependency.

The homepage and writing index use this card. Article-specific image paths are
preserved. Open Graph and Twitter tags include the image, description, alt text
and matching MIME; dimensions are included only for the known homepage and
Jacobi covers. The homepage image URL includes a content hash for future updates.

The exact Cloudflare command, `sh build_cloudflare.sh`, builds successfully and
passes all fourteen checks. A new regression checks every page's image URL,
file format, known dimensions and Twitter parity, while the existing custom
origin check covers deployment URL changes. The initial capture's file
extension was corrected to match its native JPEG bytes. One independent review
found no remaining issues. No application layout, dependencies or hosting
configuration changed. Production completion is recorded by the corresponding
main commit's Cloudflare Pages deployment and GitHub checks.

## Jacobi technical correction — 12 October 2026

The owner rejected the novice title and canned chatbot opening. The article is
now “Jacobi Forcing: Training for Parallel Decoding” and 952 words. It starts
with the gap between parallel predictions and accepted tokens, assumes readers
know the serial generation bottleneck, and explains the training contribution.
The benchmark table, primary citations, captions and motion graphic are
unchanged. One independent editorial review found no accuracy or flow issues.
The owner feedback and practical rules are recorded in `DESIGN_MEMORY.md`.

The corrected cover is a 1733 × 907 PNG, with a new asset filename for social
previews. Homepage OG artwork remains unchanged. The title is synchronized
across the article, homepage card, blog index, feed, JSON-LD and social tags.
The canonical HTML/text and downloads agree. The exact Cloudflare build command
passes all fourteen checks; the parity check now also covers title surfaces.
Desktop and 375px mobile render checks confirm the heading, cover and opening
fit. No rejected title or canned opening remains in public output. Source and
preview ZIPs are rebuilt at delivery; production completion is verified through
the main commit's Cloudflare/GitHub checks and live-to-local byte comparison.

## Earlier marketing motion revision — superseded 12 October 2026

Replaced the 24-second illustration with a 30-second technical promo. The
3.97× result is visible immediately with benchmark/model scope and pass@1
tradeoff. The mechanism uses one synchronous update and a distinct accepted
prefix; a training sequence leads into proportional ablation bars and an
article CTA. The article prose, table, links, captions and cover are unchanged.

One independent editorial/technical review approved the composition and sampled
frames. Strict motion-project checks pass with zero warnings/errors: 15 layout
times, 300 seeked motion states and 52 contrast checks. The final H.264/yuv420p
export is 1920 × 1080, 30 fps, exactly 30 seconds/900 frames and silent. All frames
decode; encoded opening, mechanism, training, comparison and CTA frames were
visually reviewed. A brief entrance flash found in the first export was fixed,
then affected checks and rendering repeated.

The poster is an encoded frame from the final video. Browser playback reports
30 seconds, advancing time, readyState 4 and no error. MP4 and poster URLs now
carry content hashes; a new regression verifies those hashes and source/served
byte equality. The Cloudflare build passes all fifteen site tests. Source and
publication ZIPs are refreshed at delivery. Live publication is confirmed by
the deployment commit's Cloudflare/GitHub checks and public-file byte comparison.


## Owner-premise motion revision — 12 October 2026

The owner rejected the benchmark-first opening and the proposed slowdown angle.
The current 30-second cut starts on frame one with “What if LLMs could generate
multiple tokens at once?” One token fans into simultaneous predictions; the
same draft becomes training material. A separate illustrative pass commits four
tokens together and leaves two provisional. This visibly answers the opening
before the scoped benchmark evidence. Article prose and research values are unchanged.

One independent reviewer checked the hook, motion continuity, technical semantics,
new acceptance payoff and reading holds. Strict checks pass with zero errors,
warnings or informational findings: 18 layout timestamps, 300 motion states and
45 contrast checks. The final silent H.264/yuv420p MP4 is 1920×1080, 30 fps,
30 seconds and 900 frames. Every encoded frame decodes; opening, transition,
mechanism, training, payoff, evidence and outro frames were visually inspected.
Browser playback has duration 30, readyState 4, advancing time and no error.

The poster is the final MP4 frame at 2.5 seconds, showing the full opening question
and parallel block. Root and site media match. The exact Cloudflare build passes
all 15 site checks, including content-hash URLs and served-byte equality. Current
publication verification is recorded in `.qa/jacobi-hook-verification.json`;
ZIP integrity and member-byte checks are completed at delivery.


## 12 October 2026 — same hook in article title and cover

The article title and cover headline are now “What if LLMs could generate
multiple tokens at once?” The new 1733 × 908 PNG retains the cream, charcoal
and blue token artwork. A fresh cover URL avoids reusing the cached social
image. Homepage feature, blog listing, RSS, JSON-LD, OG/Twitter metadata and
copy-ready text share the title; the previous cover is excluded from dist.
The article body, benchmark data, video and homepage OG image are preserved.

The exact Cloudflare build passes all 15 existing acceptance tests. Desktop
and 390-pixel article views were visually checked, along with the homepage
feature and thumbnail legibility. One independent review found no issues.
Root/site canonical files and built image bytes match. Build output and
deployment evidence for this delivery are kept locally under
`.qa/jacobi-title-cover-*`.


## 13 October 2026 — intro baseline restored

Only the lead paragraph changes: standard token-by-token autoregressive
decoding establishes the baseline, Jacobi decoding introduces parallel block
prediction, and Jacobi Forcing supplies the training contribution. The
remaining article HTML and all media are identical to the previous delivery.
Both canonical copies and text exports match. One independent editorial and
technical review approved the lead; all 15 Cloudflare build checks pass.
Delivery evidence is kept locally under `.qa/jacobi-intro-*`.
