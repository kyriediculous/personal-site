"""Import the owner's archived public RSS posts. Never runs embedded code.

Normal operation is offline. --fetch-assets retrieves only the public images and
code snippets referenced by the archive, then freezes their bytes locally.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import timezone
from email.utils import parsedate_to_datetime
from hashlib import md5, sha256
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen
import argparse
import json
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / 'src' / 'medium'
GISTS = ARCHIVE / 'gists'
IMAGES = ROOT / 'assets' / 'writing'
NS = {'content': 'http://purl.org/rss/1.0/modules/content/'}
SLUGS = {
    'd3f7be6e6f9c': 'the-verifiable-agent',
    '88a1137fdeae': 'ai-agents-smart-contracts',
    '7ebd3680eb7a': 'rollups-are-symbi-idiotic',
    'ca7c797f4c20': 'git-stash',
    'bb0fe9cae64f': 'yield-bearing-stablecoins',
    '46919de23eae': 'livepeer-node',
    '98e425aeaae6': 'go-mongodb-grpc',
    'ba48a7cb306': 'ethparis-hackathon',
    '786d9c18cd9d': 'upgradeable-ethereum-contracts',
    'c415bf1f5cef': 'programmable-incentives',
}
EXCERPTS = {
    'ca7c797f4c20': 'A practical guide to setting changes aside, switching tasks, and returning to work with git stash.',
    'bb0fe9cae64f': 'Exploring the incentives and stability challenges of stablecoins backed by yield-bearing collateral.',
    'ba48a7cb306': 'My first Ethereum hackathon: finding teammates, building a project, and learning along the way.',
    'c415bf1f5cef': 'How programmable incentives could change collaboration, reputation, and the way businesses work.',
}


def source_items():
    return ET.parse(ARCHIVE / 'original-feed.xml').findall('./channel/item')


def source_id(item):
    return item.findtext('guid').rstrip('/').split('/')[-1]


def clean_source(html, title):
    """Remove only publisher scaffolding; preserve the author's article prose."""
    soup = BeautifulSoup(html, 'html.parser')
    for image in soup.find_all('img'):
        if '/_/stat' in image.get('src', ''):
            image.decompose()
    for paragraph in soup.find_all('p'):
        text = paragraph.get_text(' ', strip=True)
        if ('was originally published in' in text and 'on Medium, where people' in text) or text == 'JavaScript is not available.':
            previous = paragraph.find_previous_sibling()
            if previous and previous.name == 'hr':
                previous.decompose()
            paragraph.decompose()
    # Coinmonks appends its channel and unrelated recommendations to this post.
    for block in soup.find_all('blockquote'):
        if block.get_text(' ', strip=True).startswith('Join Coinmonks Telegram Channel'):
            for sibling in list(block.next_siblings):
                sibling.extract()
            block.decompose()
    for frame in soup.find_all('iframe'):
        if 'upscri' in frame.get('src', ''):
            frame.decompose()
    # The RSS sometimes repeats the title as its first body heading.
    first = next((x for x in soup.children if getattr(x, 'name', None)), None)
    normalize = lambda text: re.sub(r'\s+', ' ', text).strip().casefold()
    if first and first.name in ('h3', 'h4') and normalize(first.get_text()) == normalize(title):
        first.decompose()
    return soup


def gist_matches(inventory):
    matches = {}
    for gist in inventory:
        # Medium's embed identifier is the MD5 of its original public URL.
        # Match the URL rather than guessing snippets from surrounding prose.
        for filename, file in gist['files'].items():
            base = gist['html_url']
            variants = [base, base + '.js', base + '/', base.replace('https:', 'http:'),
                        'https://gist.github.com/' + gist['id'],
                        base + '#file-' + filename.lower().replace('.', '-')]
            for url in variants:
                matches[md5(url.encode()).hexdigest()] = {
                    'gist_id': gist['id'], 'filename': filename,
                    'original_embed_url': url, 'raw_url': file['raw_url'],
                    'source_url': base,
                }
    return matches


def fetch(url):
    request = Request(url, headers={'User-Agent': 'Nico-personal-blog-archive/1.0'})
    with urlopen(request, timeout=25) as response:
        return response.read()


def fetch_assets(inventory_path):
    inventory = json.loads(Path(inventory_path).read_text())
    matches = gist_matches(inventory)
    urls = set()
    embeds = {}
    for item in source_items():
        soup = clean_source(item.findtext('content:encoded', namespaces=NS), item.findtext('title'))
        urls.update(image['src'] for image in soup.find_all('img'))
        for frame in soup.find_all('iframe'):
            if frame.get('src'):
                continue
            link = frame.find('a')['href']
            mid = link.split('/')[-2]
            if mid not in matches:
                raise ValueError('No proven source URL for code embed ' + mid)
            embeds[mid] = matches[mid]
    IMAGES.mkdir(parents=True, exist_ok=True)
    GISTS.mkdir(parents=True, exist_ok=True)

    def download_image(url):
        if urlsplit(url).hostname != 'cdn-images-1.medium.com':
            raise ValueError('Unexpected image source ' + url)
        data = fetch(url)
        with Image.open(BytesIO(data)) as image:
            width, height = image.size
            extension = {'JPEG': 'jpg', 'PNG': 'png', 'GIF': 'gif', 'WEBP': 'webp'}[image.format]
            image.verify()
        name = sha256(url.encode()).hexdigest()[:20] + '.' + extension
        (IMAGES / name).write_bytes(data)
        return url, {'path': '/assets/writing/' + name, 'sha256': sha256(data).hexdigest(),
                     'width': width, 'height': height}

    def download_code(pair):
        mid, source = pair
        if urlsplit(source['raw_url']).hostname != 'gist.githubusercontent.com':
            raise ValueError('Unexpected code source')
        data = fetch(source['raw_url'])
        data.decode('utf-8')
        name = mid + '.txt'
        (GISTS / name).write_bytes(data)
        return mid, {**source, 'path': 'gists/' + name, 'sha256': sha256(data).hexdigest(),
                     'match': 'MD5 of exact original embed URL'}

    with ThreadPoolExecutor(max_workers=6) as pool:
        images = dict(pool.map(download_image, sorted(urls)))
        code = dict(pool.map(download_code, sorted(embeds.items())))
    (ARCHIVE / 'assets.json').write_text(json.dumps({'images': images, 'code': code}, indent=2) + '\n')
    print(f'Archived {len(images)} images and {len(code)} exact, URL-matched code snippets.')


def safe_url(url):
    return urlsplit(url).scheme.lower() in ('http', 'https', 'mailto') or url.startswith(('/', '#'))


def import_posts():
    ledger = json.loads((ARCHIVE / 'assets.json').read_text())
    selected = {p['url']: p for p in json.loads((ROOT / 'src' / 'content.json').read_text())['posts']}
    items = source_items()
    local_urls = {item.findtext('link').split('?')[0]: '/blog/' + SLUGS[source_id(item)] + '/' for item in items}
    posts = []
    for item in items:
        post_id = source_id(item)
        title = item.findtext('title')
        url = item.findtext('link').split('?')[0]
        soup = clean_source(item.findtext('content:encoded', namespaces=NS), title)
        # Freeze all code as escaped text, including '<' and HTML-like strings.
        for frame in soup.find_all('iframe'):
            src = frame.get('src', '')
            figure = soup.new_tag('figure', attrs={'class': 'code-example' if not src else 'linked-embed'})
            caption = soup.new_tag('figcaption')
            if not src:
                mid = frame.find('a')['href'].split('/')[-2]
                code = ledger['code'][mid]
                pre = soup.new_tag('pre')
                block = soup.new_tag('code', attrs={'data-code-source': mid})
                block.string = (ARCHIVE / code['path']).read_text()
                pre.append(block)
                figure.append(pre)
                href, label = code['source_url'], code['filename'] + ' — original code'
            else:
                query = parse_qs(urlsplit(src).query)
                href = query['url'][0].replace('http://www.youtube.com', 'https://www.youtube.com')
                label = 'Watch the original video on YouTube' if 'youtube.com' in href else 'View the original post on X'
            a = soup.new_tag('a', href=href)
            a.string = label
            caption.append(a)
            figure.append(caption)
            frame.replace_with(figure)
        for image in soup.find_all('img'):
            asset = ledger['images'][image['src']]
            image.attrs = {key: image[key] for key in ('alt',) if image.has_attr(key)}
            image['src'] = asset['path']
            image['width'], image['height'] = asset['width'], asset['height']
            image['loading'], image['decoding'] = 'lazy', 'async'
            if not image.get('alt'):
                caption = image.find_next_sibling('figcaption')
                image['alt'] = caption.get_text(' ', strip=True) if caption else 'Illustration from ' + title
        for tag in list(soup.find_all(True)):
            if tag.name in ('script', 'style', 'object', 'embed', 'form', 'input', 'button'):
                tag.decompose()
                continue
            if tag.name == 'h3':
                tag.name = 'h2'
            elif tag.name == 'h4':
                tag.name = 'h3'
            allowed = {'href', 'src', 'alt', 'width', 'height', 'loading', 'decoding',
                       'data-code-source', 'class'}
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
            if tag.name == 'a':
                href = tag.get('href', '')
                if not safe_url(href):
                    tag.unwrap()
                    continue
                key = href.split('?')[0]
                if key in local_urls:
                    tag['href'] = local_urls[key]
                elif urlsplit(href).scheme in ('http', 'https'):
                    tag['rel'], tag['target'] = 'noopener', '_blank'
        for pre in soup.find_all('pre'):
            pre['tabindex'] = '0'
            pre['aria-label'] = 'Code example, scroll horizontally if needed'
        dt = parsedate_to_datetime(item.findtext('pubDate')).astimezone(timezone.utc)
        source = 'ITNEXT' if 'itnext.io' in url else ('Coinmonks on Medium' if '/coinmonks/' in url else ('HackerNoon on Medium' if '/hackernoon/' in url else 'Medium'))
        body = str(soup)
        folder = ARCHIVE / SLUGS[post_id]
        folder.mkdir(exist_ok=True)
        (folder / 'article.html').write_text(body)
        description = selected[url]['description'] if url in selected else EXCERPTS[post_id]
        images = soup.find_all('img')
        posts.append({'id': post_id, 'slug': SLUGS[post_id], 'title': title, 'url': local_urls[url],
                      'original_url': url, 'publication': source, 'date': dt.date().isoformat(),
                      'published_at': dt.isoformat(), 'description': description,
                      'image': images[0]['src'] if images else '/assets/nico-vergauwen.png',
                      'code_count': len(soup.select('[data-code-source]')),
                      'image_count': len(images), 'body_sha256': sha256(body.encode()).hexdigest()})
    (ARCHIVE / 'posts.json').write_text(json.dumps(posts, indent=2, ensure_ascii=False) + '\n')
    print(f'Imported {len(posts)} complete local posts; normal builds need no network.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-assets', metavar='PUBLIC_GIST_INVENTORY_JSON')
    args = parser.parse_args()
    if args.fetch_assets:
        fetch_assets(args.fetch_assets)
    import_posts()
