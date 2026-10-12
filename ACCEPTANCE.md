# Delivery verification

Reviewed on 12 October 2026 for Cloudflare Pages publication.

The homepage includes applied AI and agent work, two projects, research directly
after Projects, seven career entries, six selected local posts, and an eleven-post
blog index. Projects and every footer use the existing brand logos. Removed
achievement cards and decorative section labels remain absent. Contact uses
LinkedIn and social profiles, with no personal email or phone number.

## Automated checks

Thirteen checks cover:

- Canonical Jacobi prose, text export, and MP4 remain identical to their originals.
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

The configured target origin is https://nicovergauwen.pages.dev. Cloudflare account
sign-in, GitHub integration, hostname confirmation, and live verification are
pending. Preparation checks do not establish that the site is live.

The source is published at https://github.com/kyriediculous/personal-site. The
initial Linux CI build passed all thirteen checks:
https://github.com/kyriediculous/personal-site/actions/runs/38294731015.
A source-only Git export produces the same 71 output files byte for byte as the
reviewed local build. All thirteen local checks pass with the Pages target origin.
