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
cadence, beginner accessibility and fidelity. The article is now 1,311 words;
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
