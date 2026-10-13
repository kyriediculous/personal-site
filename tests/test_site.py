"""Delivery checks for content preservation, local links, and public-page scope."""
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urljoin, unquote
import json
from hashlib import sha256, md5
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
CANONICAL = ROOT / 'content' / 'jacobi-forcing'

class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.ids=[]; self.h1=0; self.anchors=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='a': self.anchors.append(a)
        for key in ('href','src','poster'):
            if a.get(key): self.refs.append(a[key])

def parse(path):
    d=Document(); d.feed(path.read_text()); return d

def exported_article(html):
    spec=importlib.util.spec_from_file_location('canonical_assets',CANONICAL/'build_assets.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    parser=module.ArticleText();parser.feed(html)
    value=''.join(parser.out)
    value=re.sub(r'\s*\|\s*\n','\n',value)
    value=re.sub(r' +\n','\n',value)
    return re.sub(r'\n{3,}','\n\n',value).strip()+'\n'

class SiteAcceptance(unittest.TestCase):
    def test_canonical_article_and_download_stay_identical(self):
        self.assertEqual(exported_article((DIST/'blog/jacobi-forcing/index.html').read_text()),(CANONICAL/'article.txt').read_text())
        self.assertEqual((DIST/'blog/jacobi-forcing/article.txt').read_bytes(),(CANONICAL/'article.txt').read_bytes())
        self.assertEqual((DIST/'blog/jacobi-forcing/assets/jacobi-forcing-motion.mp4').read_bytes(),(CANONICAL/'assets/jacobi-forcing-motion.mp4').read_bytes())
        canonical=BeautifulSoup((CANONICAL/'article.html').read_text(),'html.parser')
        title=canonical.title.get_text()
        article=BeautifulSoup((DIST/'blog/jacobi-forcing/index.html').read_text(),'html.parser')
        self.assertEqual(article.h1.get_text(),title)
        self.assertEqual(article.select_one('meta[property="og:title"]')['content'],title+' | Nico Vergauwen')
        self.assertEqual(json.loads(article.select_one('script[type="application/ld+json"]').string)['headline'],title)
        for route in ('index.html','blog/index.html'):
            page=BeautifulSoup((DIST/route).read_text(),'html.parser')
            titles=[a.get_text() for a in page.select('h2 a[href="/blog/jacobi-forcing/"],h3 a[href="/blog/jacobi-forcing/"]')]
            self.assertEqual(titles,[title])
        if (DIST/'feed.xml').exists():
            item=next(i for i in ET.parse(DIST/'feed.xml').findall('./channel/item') if i.findtext('link').endswith('/blog/jacobi-forcing/'))
            self.assertEqual(item.findtext('title'),title)


    def test_every_internal_reference_and_fragment_resolves(self):
        for page in DIST.rglob('*.html'):
            doc=parse(page); base='/'+str(page.relative_to(DIST))
            self.assertEqual(doc.h1,1,str(page))
            self.assertEqual(len(doc.ids),len(set(doc.ids)),str(page))
            for ref in doc.refs:
                url=urlsplit(urljoin('http://local.test'+base,ref))
                if url.scheme not in ('http','https') or url.hostname!='local.test': continue
                resolved=DIST/unquote(url.path.lstrip('/'))
                if url.path.endswith('/'): resolved=resolved/'index.html'
                self.assertTrue(resolved.is_file(),f'{page}: {ref}')
                if url.fragment: self.assertIn(url.fragment,parse(resolved).ids,f'{page}: {ref}')

    def test_business_backlinks_are_real_followable_links(self):
        home=parse(DIST/'index.html')
        for url in ('https://kollekt.now','https://grokked.ai'):
            links=[a for a in home.anchors if a.get('href')==url]
            self.assertGreaterEqual(len(links),2,url)
            self.assertTrue(all('nofollow' not in a.get('rel','') for a in links))

    def test_project_and_footer_brands_and_research_order(self):
        home=BeautifulSoup((DIST/'index.html').read_text(),'html.parser')
        sections=[section.get('id') for section in home.select('main > section') if section.get('id')]
        self.assertEqual(sections[:3],['projects','research','writing'])
        nav=[a.get_text() for a in home.select('#site-navigation a')]
        self.assertEqual(nav[:3],['Projects','Research','Writing'])
        for project in home.select('#projects .project'):
            self.assertTrue(project.select_one('h3 a img'))
            self.assertTrue(project.select_one('h3 a').get('aria-label'))
        research=home.select_one('#research').get_text(' ',strip=True)
        for phrase in ('currently extending','post-training','lattice-based commitments','post-quantum security'):
            self.assertIn(phrase,research)
        for page in DIST.rglob('*.html'):
            soup=BeautifulSoup(page.read_text(),'html.parser')
            brands=soup.select('.site-footer-links a')
            self.assertEqual(len(brands),3)
            for brand in brands:
                self.assertTrue(brand.find('img'),str(page))
                self.assertTrue(brand.get('aria-label'),str(page))

    def test_personal_email_is_absent_and_social_contact_works(self):
        self.assertNotIn('email',json.loads((ROOT/'src/content.json').read_text()))
        for page in DIST.rglob('*.html'):
            self.assertNotRegex(page.read_text(),r'[\w.+-]+@gmail\.com')
        home=BeautifulSoup((DIST/'index.html').read_text(),'html.parser')
        contact=home.select_one('#contact')
        self.assertFalse(contact.select('a[href^="mailto:"]'))
        content=json.loads((ROOT/'src/content.json').read_text())
        self.assertEqual(contact.select_one('a.button')['href'],content['linkedin'])
        self.assertTrue(contact.select_one('a[href="'+content['x']+'"]'))

    def test_built_style_and_script_versions_match_their_served_bytes(self):
        for page in DIST.rglob('*.html'):
            soup=BeautifulSoup(page.read_text(),'html.parser')
            for name,reference in [('site.css',soup.select_one('link[rel="stylesheet"]')['href']),('site.js',soup.select_one('script[src]')['src'])]:
                expected=sha256((DIST/'assets'/name).read_bytes()).hexdigest()[:12]
                self.assertEqual(reference,'/assets/'+name+'?v='+expected)

    def test_jacobi_video_and_poster_versions_match_their_served_bytes(self):
        article_dir=DIST/'blog/jacobi-forcing'
        soup=BeautifulSoup((article_dir/'index.html').read_text(),'html.parser')
        video=soup.select_one('article video')
        self.assertIsNotNone(video)
        source=video.select_one('source[type="video/mp4"]')
        self.assertIsNotNone(source)
        for name,reference in [('jacobi-forcing-motion.mp4',source['src']),
                               ('jacobi-forcing-motion-poster.png',video['poster'])]:
            with self.subTest(asset=name):
                served=(article_dir/'assets'/name).read_bytes()
                self.assertEqual(served,(CANONICAL/'assets'/name).read_bytes())
                expected=sha256(served).hexdigest()[:12]
                self.assertEqual(reference,'assets/'+name+'?v='+expected)

    def test_research_and_curated_writing_inventory(self):
        home=(DIST/'index.html').read_text()
        content=json.loads((ROOT/'src/content.json').read_text())
        self.assertIn('https://arxiv.org/abs/2602.12630',home)
        self.assertIn('Accepted at NeurIPS 2026',home)
        self.assertNotIn('VIC-HTN',home)
        imported=json.loads((ROOT/'src/medium/posts.json').read_text())
        local={p['original_url']:p['url'] for p in imported}
        for p in content['posts']:
            self.assertIn(local[p['url']],home)
            self.assertNotIn(p['url'],home)
        self.assertEqual(len(content['experience']),7)

    def test_imported_inventory_is_complete_and_attributes_originals(self):
        imported=json.loads((ROOT/'src/medium/posts.json').read_text())
        self.assertEqual(len(imported),10)
        index=parse(DIST/'blog/index.html')
        blog_links=[a['href'] for a in index.anchors if a.get('href','').startswith('/blog/') and a['href']!='/blog/']
        self.assertEqual(len(blog_links),11)
        self.assertEqual(set(blog_links),{'/blog/jacobi-forcing/',*(p['url'] for p in imported)})
        for post in imported:
            soup=BeautifulSoup((DIST/post['url'].lstrip('/')/'index.html').read_text(),'html.parser')
            self.assertEqual(soup.h1.get_text(),post['title'])
            self.assertEqual(soup.select_one('.article-byline time')['datetime'],post['date'])
            self.assertEqual(soup.select_one('article .publication-note a')['href'],post['original_url'])
            schema=json.loads(soup.select_one('script[type="application/ld+json"]').string)
            self.assertEqual(schema['@type'],'BlogPosting')
            self.assertEqual(schema['isBasedOn'],post['original_url'])
            self.assertEqual(soup.select_one('meta[property="og:type"]')['content'],'article')

    def test_author_prose_is_preserved_and_every_embed_is_recovered(self):
        imported=json.loads((ROOT/'src/medium/posts.json').read_text())
        normalize=lambda text:re.sub(r'\s+',' ',text).strip()
        for post in imported:
            original=BeautifulSoup((ROOT/'src/medium'/f"{post['id']}.original.html").read_text(),'html.parser')
            page=BeautifulSoup((DIST/post['url'].lstrip('/')/'index.html').read_text(),'html.parser')
            body=page.select_one('.imported-body')
            actual=normalize(body.get_text(' ',strip=True))
            # Original authored paragraphs, headings, lists, quotes and captions
            # must still appear in sequence. Exempt only identifiable publisher
            # additions, RSS boilerplate, and the repeated article title.
            promo=original.find('blockquote',string=lambda s:s and s.startswith('Join Coinmonks Telegram Channel'))
            if not promo:
                promo=next((b for b in original.find_all('blockquote') if b.get_text(' ',strip=True).startswith('Join Coinmonks Telegram Channel')),None)
            if promo:
                for sibling in list(promo.next_siblings): sibling.extract()
                promo.decompose()
            for frame in original.find_all('iframe'): frame.decompose()
            position=0
            for block in original.find_all(['p','h3','h4','li','figcaption']):
                if block.find_parent(['li','p']): continue
                text=normalize(block.get_text(' ',strip=True))
                if not text or ('was originally published in' in text and 'on Medium, where people' in text) or text=='JavaScript is not available.': continue
                if text.casefold()==normalize(post['title']).casefold(): continue
                match=actual.find(text,position)
                self.assertGreaterEqual(match,0,f"{post['slug']}: missing or reordered original text {text[:100]}")
                position=match+len(text)
            self.assertEqual(len(body.select('[data-code-source]')),post['code_count'])
            self.assertEqual(len(body.find_all('img')),post['image_count'])
        self.assertEqual(sum(p['code_count'] for p in imported),32)
        self.assertEqual(sum(p['image_count'] for p in imported),38)

    def test_archived_images_and_code_match_their_exact_sources(self):
        ledger=json.loads((ROOT/'src/medium/assets.json').read_text())
        for image in ledger['images'].values():
            for base in (ROOT,DIST):
                self.assertEqual(sha256((base/image['path'].lstrip('/')).read_bytes()).hexdigest(),image['sha256'])
        recovered={}
        for path in (DIST/'blog').rglob('index.html'):
            soup=BeautifulSoup(path.read_text(),'html.parser')
            for code in soup.select('[data-code-source]'): recovered[code['data-code-source']]=code.get_text()
        for mid,source in ledger['code'].items():
            data=(ROOT/'src/medium'/source['path']).read_bytes()
            self.assertEqual(md5(source['original_embed_url'].encode()).hexdigest(),mid)
            self.assertEqual(sha256(data).hexdigest(),source['sha256'])
            self.assertEqual(recovered[mid],data.decode('utf-8'))

    def test_imported_posts_load_no_third_party_media_or_tracking(self):
        for path in (DIST/'blog').rglob('index.html'):
            soup=BeautifulSoup(path.read_text(),'html.parser')
            self.assertFalse(soup.select('iframe, object, embed, form'))
            self.assertNotIn('medium.com/_/stat',str(soup))
            for media in soup.select('[src], [poster], [srcset]'):
                for key in ('src','poster','srcset'):
                    if media.has_attr(key): self.assertFalse(urlsplit(media[key]).netloc,f'{path}: remote media')
            for element in soup.find_all(True):
                self.assertFalse(any(k.lower().startswith('on') for k in element.attrs))
            for anchor in soup.find_all('a',href=True):
                self.assertIn(urlsplit(anchor['href']).scheme,('','http','https','mailto'))

    def test_future_feed_sitemap_and_canonicals_cover_all_local_articles(self):
        spec=importlib.util.spec_from_file_location('site_build',ROOT/'build.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        origin='https://example.com'
        with TemporaryDirectory() as folder, patch.object(builder,'DIST',Path(folder)), patch.object(builder,'ORIGIN',origin), redirect_stdout(StringIO()):
            builder.build()
            pages=builder.all_posts()
            feed=ET.parse(Path(folder)/'feed.xml').findall('./channel/item')
            self.assertEqual(len(feed),11)
            self.assertEqual([item.findtext('link') for item in feed],[origin+p['url'] for p in pages])
            self.assertEqual([item.findtext('title') for item in feed],[p['title'] for p in pages])
            sitemap=ET.parse(Path(folder)/'sitemap.xml')
            locations=[node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            self.assertEqual(set(locations),{origin+'/',origin+'/blog/',*(origin+p['url'] for p in pages)})
            for post in pages:
                soup=BeautifulSoup((Path(folder)/post['url'].lstrip('/')/'index.html').read_text(),'html.parser')
                self.assertEqual(soup.select_one('link[rel="canonical"]')['href'],origin+post['url'])
                self.assertTrue(soup.select_one('meta[property="og:image"]')['content'].startswith(origin+'/'))
                self.assertEqual(soup.select_one('meta[name="twitter:image"]')['content'],soup.select_one('meta[property="og:image"]')['content'])
        configured=json.loads((ROOT/'src/site.json').read_text())['origin']
        self.assertEqual((DIST/'sitemap.xml').exists(),bool(configured))
        self.assertEqual((DIST/'feed.xml').exists(),bool(configured))
        if configured:
            home=BeautifulSoup((DIST/'index.html').read_text(),'html.parser')
            self.assertEqual(home.select_one('link[rel="canonical"]')['href'],configured+'/')
            links=[node.text for node in ET.parse(DIST/'feed.xml').findall('./channel/item/link')]
            self.assertEqual(links,[configured+p['url'] for p in builder.all_posts()])

    def test_social_cards_resolve_and_preserve_article_covers(self):
        origin=json.loads((ROOT/'src/site.json').read_text())['origin'] or ''
        card='/assets/social/nico-vergauwen-og.jpg'
        posts=json.loads((ROOT/'src/medium/posts.json').read_text())
        expected={'/':card,'/blog/':card,'/404.html':card,
                  '/blog/jacobi-forcing/':'/blog/jacobi-forcing/assets/jacobi-forcing-cover-house.png',
                  **{p['url']:p['image'] for p in posts}}
        for route,image_path in expected.items():
            page=DIST/route.lstrip('/')
            if route.endswith('/'): page=page/'index.html'
            soup=BeautifulSoup(page.read_text(),'html.parser')
            get=lambda selector:soup.select_one(selector)['content']
            image_url=get('meta[property="og:image"]')
            self.assertEqual(len(soup.select('meta[property="og:image"]')),1)
            self.assertEqual(image_url.split('?',1)[0],origin+image_path)
            self.assertEqual(get('meta[name="twitter:card"]'),'summary_large_image')
            self.assertEqual(get('meta[name="twitter:image"]'),image_url)
            self.assertEqual(get('meta[name="twitter:title"]'),get('meta[property="og:title"]'))
            self.assertEqual(get('meta[name="twitter:description"]'),get('meta[property="og:description"]'))
            self.assertTrue(get('meta[property="og:image:alt"]').strip())
            self.assertEqual(get('meta[name="twitter:image:alt"]'),get('meta[property="og:image:alt"]'))
            asset=DIST/image_path.lstrip('/')
            with Image.open(asset) as image:
                self.assertEqual(get('meta[property="og:image:type"]'),Image.MIME[image.format])
                if image_path==card:
                    self.assertEqual(image.size,(1200,630))
                    self.assertEqual(image.format,'JPEG')
                    self.assertEqual(get('meta[property="og:image:width"]'),'1200')
                    self.assertEqual(get('meta[property="og:image:height"]'),'630')
                    self.assertLess(asset.stat().st_size,1_000_000)
                    self.assertIn('Nico Vergauwen',get('meta[property="og:image:alt"]'))
                    self.assertIn('Applied AI',get('meta[property="og:image:alt"]'))
                    self.assertEqual(urlsplit(image_url).query,'v='+sha256(asset.read_bytes()).hexdigest()[:12])
                if soup.select_one('meta[property="og:image:width"]'):
                    self.assertEqual((int(get('meta[property="og:image:width"]')),int(get('meta[property="og:image:height"]'))),image.size)
                image.verify()
        self.assertEqual((DIST/card.lstrip('/')).read_bytes(),(ROOT/card.lstrip('/')).read_bytes())
        self.assertFalse((DIST/'social-card-preview.html').exists())

    def test_no_decorative_labels_or_unrequested_private_files(self):
        for page in DIST.rglob('*.html'):
            doc=parse(page)
            self.assertFalse(any(a.get('href','').startswith('tel:') for a in doc.anchors))
            self.assertNotIn('class="eyebrow"',page.read_text())
        diagram=ET.parse(CANONICAL/'assets/jacobi-forcing-refinement.svg')
        visible=' '.join(node.text or '' for node in diagram.iter() if node.tag.rsplit('}',1)[-1]=='text')
        self.assertNotRegex(visible.lower(),r'illustration|made.up example|words stand in for tokens|ai explained')
        article=BeautifulSoup((DIST/'blog/jacobi-forcing/index.html').read_text(),'html.parser')
        for caption in article.select('figcaption'):
            self.assertNotRegex(caption.get_text().lower(),r'not a measured model run|a made.up example|words standing in for tokens')
        self.assertFalse(list(DIST.rglob('*Resume*.pdf')))
        self.assertFalse(any(p.name in ('security-reports','.git','.openai') for p in DIST.rglob('*')))

if __name__=='__main__': unittest.main()
