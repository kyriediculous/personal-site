"""Build the personal site locally. This script never publishes or pushes."""
from pathlib import Path
from html import escape
from hashlib import sha256
from datetime import date, datetime
from email.utils import format_datetime
import json
import mimetypes
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
PUBLICATION = ROOT / 'content' / 'jacobi-forcing'
JACOBI_TITLE = 'What if LLMs could generate multiple tokens at once?'
JACOBI_DESCRIPTION = 'How Jacobi Forcing trains autoregressive models for parallel decoding, with measured speedups and accuracy tradeoffs.'
CONTENT = json.loads((ROOT / 'src' / 'content.json').read_text())
MEDIUM = ROOT / 'src' / 'medium'
POSTS = json.loads((MEDIUM / 'posts.json').read_text())
POST_URLS = {p['original_url']: p['url'] for p in POSTS}
ASSET_VERSIONS = {name: sha256((ROOT/'src'/name).read_bytes()).hexdigest()[:12] for name in ('site.css','site.js')}
SOCIAL_IMAGE = '/assets/social/nico-vergauwen-og.jpg'
SOCIAL_IMAGE_ALT = 'Nico Vergauwen giving a presentation beside the headline Applied AI, Agents & Distributed Infrastructure, on a dark teal background with mint and yellow accents.'
ORIGIN = json.loads((ROOT / 'src' / 'site.json').read_text()).get('origin')
if ORIGIN is not None:
    if not re.fullmatch(r'https://[^/\s]+', ORIGIN):
        raise ValueError('Set origin to the real HTTPS site origin, without a path or trailing slash.')

def external(url, label, cls=''):
    return f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener" class="{cls}">{escape(label)}</a>'

def local_post(url, label):
    return f'<a href="{POST_URLS[url]}">{escape(label)}</a>'

def brand_link(url, name, cls=''):
    if name == 'grokked.ai':
        logo = '<span class="grokked-lockup"><img src="/assets/brands/grokked-mark.svg" width="29" height="29" alt=""><span>grokked</span></span>'
    elif name == 'kollekt.now':
        logo = '<img class="kollekt-logo" src="/assets/brands/kollekt-logo.svg" width="230" height="62" alt="kollekt.now">'
    elif name == 'GitHub':
        logo = '<img class="github-logo" src="/assets/brands/github.svg" width="32" height="32" alt="GitHub">'
    else:
        raise ValueError('Missing brand asset for ' + name)
    return f'<a href="{escape(url,quote=True)}" target="_blank" rel="noopener" class="brand-link {cls}" aria-label="{escape(name,quote=True)}" title="{escape(name,quote=True)}">{logo}</a>'

def navigation():
    return '''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="shell nav-row">
<a class="brand" href="/">Nico Vergauwen</a>
<button class="menu-toggle" type="button" aria-controls="site-navigation" aria-expanded="false">Menu</button>
<nav class="nav-links" id="site-navigation" aria-label="Main navigation">
<a href="/#projects">Projects</a><a href="/#research">Research</a><a href="/blog/">Writing</a><a href="/#experience">Experience</a><a href="/#contact">Contact</a>
</nav></div></header>'''

def footer():
    return f'''<footer class="shell site-footer"><p>© 2026 Nico Vergauwen</p>
<div class="site-footer-links">{brand_link('https://kollekt.now','kollekt.now')}{brand_link('https://grokked.ai','grokked.ai')}{brand_link(CONTENT['github'],'GitHub')}</div></footer>'''

def document(title, description, content, structured=None, image=SOCIAL_IMAGE, path='/', image_alt=None, image_size=None):
    schema = '' if structured is None else '<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('</','<\\/')+'</script>'
    canonical = '' if not ORIGIN else f'<link rel="canonical" href="{ORIGIN}{path}"><meta property="og:url" content="{ORIGIN}{path}">'
    image_type = mimetypes.guess_type(image)[0]
    if image == SOCIAL_IMAGE:
        image_alt = image_alt or SOCIAL_IMAGE_ALT
        image_size = (1200, 630)
        version = sha256((ROOT/image.lstrip('/')).read_bytes()).hexdigest()[:12]
        image += '?v=' + version
    image_alt = image_alt or ('Cover image for ' + title)
    image_url = escape(ORIGIN + image if ORIGIN else image, quote=True)
    image_meta = '' if not image_type else f'<meta property="og:image:type" content="{image_type}">'
    if image_size:
        image_meta += f'<meta property="og:image:width" content="{image_size[0]}"><meta property="og:image:height" content="{image_size[1]}">'
    feed = '' if not ORIGIN else '<link rel="alternate" type="application/rss+xml" title="Nico Vergauwen’s writing" href="/feed.xml">'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}">
<meta name="theme-color" content="#0b1b20"><meta property="og:type" content="{'article' if structured and structured.get('@type') == 'BlogPosting' else 'website'}">
<meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}">
<meta property="og:site_name" content="Nico Vergauwen">
<meta property="og:image" content="{image_url}">{image_meta}<meta property="og:image:alt" content="{escape(image_alt,quote=True)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}">
<meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="{escape(image_alt,quote=True)}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/host-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSIONS['site.css']}">{canonical}{feed}
{schema}<script src="/assets/site.js?v={ASSET_VERSIONS['site.js']}" defer></script></head><body>{navigation()}{content}{footer()}</body></html>'''

def homepage():
    projects=''.join(f'<article class="project {p["color"]}"><h3>{brand_link(p["url"],p["name"],"project-brand")}</h3><p>{escape(p["description"])}</p>{external(p["url"],"Visit "+p["name"],"project-link")}</article>' for p in CONTENT['projects'])
    posts=''.join(f'<article class="post"><h3>{local_post(p["url"],p["title"])}</h3><p>{escape(p["description"])}</p><time datetime="{p["date"]}">{date.fromisoformat(p["date"]).strftime("%B %Y")}</time></article>' for p in CONTENT['posts'])
    work=[]
    for x in CONTENT['experience']:
        heading=external(x['url'],x['company']) if x.get('url') else escape(x['company'])
        links='<p class="work-links">'+''.join(external(l['url'],l['label']) for l in x.get('links',[]))+'</p>' if x.get('links') else ''
        work.append(f'<article class="work"><div><h3>{heading}</h3><p class="role">{escape(x["role"])}</p><p class="dates">{escape(x["dates"])}</p></div><div><p class="description">{escape(x["text"])}</p>{links}</div></article>')
    body=f'''<main id="main">
<section class="shell hero" aria-labelledby="intro-title"><div class="hero-panel">
<div><h1 id="intro-title">Applied AI, Agents &amp; Distributed Infrastructure</h1>
<p>Hi, I’m <strong>Nico</strong>. A technical founder building AI products for businesses, agent systems, and the infrastructure behind them.</p>
<div class="hero-actions"><a class="button" href="#experience">What I’ve built</a><a class="button secondary" href="#writing">Read my writing</a></div></div>
<div class="portrait-field"><img src="/assets/nico-vergauwen.png" width="500" height="500" alt="Nico Vergauwen giving a presentation" fetchpriority="high"></div>
</div></section>
<section class="shell section" id="projects" aria-labelledby="projects-title"><h2 class="section-title" id="projects-title">Projects</h2><div class="projects-grid">{projects}</div></section>
<section class="shell section" id="research" aria-labelledby="research-title"><h2 class="section-title" id="research-title">Research</h2>
<article class="research"><div><h3>Tensor<wbr>Commitments: A Lightweight Verifiable Inference for Language Models</h3><p>I co-authored this work on checking that a remote language model ran as intended, without running the whole model again on the verifier’s machine.</p>
<p>I’m currently extending TensorCommitments to verifiable post-training using lattice-based commitments, with a focus on performance and post-quantum security.</p>
<div class="research-links">{external('https://arxiv.org/abs/2602.12630','Read the paper')}{external('https://github.com/NeurIPS26TC/TensorCommitment','Explore the code')}{external('https://utaustin-swarmlab.github.io/2026/10/04/TensorCommitments.html','Research explanation')}</div></div>
<div class="research-side"><p class="acceptance">Accepted at NeurIPS 2026</p><p>Co-authored with researchers from UT Austin, Georgia Tech, and McGill.</p></div></article></section>
<section class="shell section" id="writing" aria-labelledby="writing-title"><h2 class="section-title" id="writing-title">Writing</h2>
<article class="feature"><a class="feature-image" href="/blog/jacobi-forcing/" aria-label="Read {JACOBI_TITLE}"><img src="/blog/jacobi-forcing/assets/jacobi-forcing-cover-hook.png" width="1733" height="908" alt="{JACOBI_TITLE}" loading="lazy"></a>
<div><h3><a href="/blog/jacobi-forcing/">{JACOBI_TITLE}</a></h3><p>Training on imperfect decoding trajectories improves parallel token acceptance. A look at the mechanism, measured speedups, and accuracy tradeoffs.</p><a class="button" href="/blog/jacobi-forcing/">Read the article</a></div></article>
<div class="post-grid">{posts}</div><p class="more-writing"><a href="/blog/">Browse all writing</a></p></section>
<section class="shell section" id="experience" aria-labelledby="experience-title"><h2 class="section-title" id="experience-title">What I’ve built</h2><div class="work-list">{''.join(work)}</div></section>
<section class="shell section" aria-labelledby="about-title"><h2 class="section-title" id="about-title">About me</h2><div class="about-grid"><div>
<p>My work spans applied AI products, agent systems, distributed compute, and protocols. I like working across the whole stack: the model, the runtime, the infrastructure, and the product people actually use.</p>
<p>My work ranges from early protocol engineering at Livepeer and founding Tenderize to agent compilers, memory systems, private personal AI, and distributed inference and post-training.</p>
<p>I’m based in Belgium and have worked remotely with teams in New York, San Francisco, and worldwide since 2019. I speak Dutch and English, with conversational French.</p></div>
<aside class="about-aside"><h3>Education and awards</h3><p>B.Sc. in Applied Computer Science from Karel de Grote University of Applied Sciences, and a postgraduate certificate in Blockchain from Howest.</p><p style="margin-top:20px">Prize-winning projects at ETHParis 2019, ETHBerlin Zwei 2019, and the 2024 DMCC × Bybit hackathon, plus the Emakina Group Silver Innovation Award.</p></aside></div></section>
<section class="shell contact-panel" id="contact" aria-labelledby="contact-title"><h2 id="contact-title">Let’s talk.</h2><p>If you’re building applied AI products, agent systems, or distributed compute, I’d like to hear what you’re working on.</p>{external(CONTENT['linkedin'],'Message me on LinkedIn','button')}
<div class="social-links">{external(CONTENT['github'],'GitHub')}{external(CONTENT['x'],'X')}{external(CONTENT['medium'],'Medium')}</div></section>
</main>'''
    person={'@context':'https://schema.org','@type':'Person','name':CONTENT['name'],'jobTitle':'Technical Founder','description':'Applied AI products, agent systems, and distributed infrastructure','sameAs':[CONTENT[k] for k in ('github','x','medium','linkedin')]}
    return document('Nico Vergauwen | Applied AI, Agents & Distributed Infrastructure','Technical founder building applied AI products, agent systems, and distributed infrastructure. Projects, research, and writing.',body,person)

def articlepage():
    canonical=(PUBLICATION/'article.html').read_text()
    article=re.search(r'<article>.*?</article>',canonical,re.S).group()
    article=re.sub(r'\s*<p class="eyebrow">.*?</p>','',article)
    # Replacing the video or poster must also change its browser cache key.
    for name in ('jacobi-forcing-motion.mp4','jacobi-forcing-motion-poster.png'):
        version=sha256((PUBLICATION/'assets'/name).read_bytes()).hexdigest()[:12]
        article=article.replace(f'"assets/{name}"',f'"assets/{name}?v={version}"')
    # Article prose stays canonical; only chrome, styling and media URLs change.
    body='''<main id="main" class="shell"><div class="reading-nav"><a href="/blog/">Back to writing</a></div><div class="article-container">'''+article+'''
<p class="article-byline">By Nico Vergauwen. Published 11 October 2026.</p>
<div class="article-tools"><button class="button" type="button" data-copy-link>Copy link</button><a href="article.txt" download>Download article text</a><p class="copy-status" role="status" aria-live="polite"></p></div>
<section class="article-end"><h2>More on AI and agents</h2><a href="/blog/the-verifiable-agent/">Read The Verifiable Agent</a></section></div></main>'''
    schema={'@context':'https://schema.org','@type':'BlogPosting','headline':JACOBI_TITLE,'datePublished':'2026-10-11','author':{'@type':'Person','name':CONTENT['name']},'description':'How Jacobi Forcing trains language models for parallel guesses, with measured speed and quality results.'}
    return document(JACOBI_TITLE+' | Nico Vergauwen',JACOBI_DESCRIPTION,body,schema,'/blog/jacobi-forcing/assets/jacobi-forcing-cover-hook.png','/blog/jacobi-forcing/',image_alt='What if LLMs could generate multiple tokens at once? Rows of charcoal and blue token tiles converge below the question.',image_size=(1733,908))

def all_posts():
    jacobi = {'title': JACOBI_TITLE, 'url': '/blog/jacobi-forcing/',
              'date': '2026-10-11', 'published_at': '2026-10-11T12:00:00+00:00',
              'description': JACOBI_DESCRIPTION}
    return sorted([jacobi, *POSTS], key=lambda p: p['published_at'], reverse=True)

def blogpage():
    posts = ''.join(f'''<article class="post"><h2><a href="{p['url']}">{escape(p['title'])}</a></h2>
<p>{escape(p['description'])}</p><time datetime="{p['date']}">{date.fromisoformat(p['date']).strftime('%B %Y')}</time></article>''' for p in all_posts())
    body = f'''<main id="main" class="shell blog-index"><h1>Writing</h1><p class="section-intro">AI systems, distributed infrastructure, and what I learn while building.</p><div class="post-grid">{posts}</div></main>'''
    return document('Writing | Nico Vergauwen', 'Articles on AI, agents, distributed infrastructure, and software engineering by Nico Vergauwen.', body, path='/blog/')

def imported_articlepage(post):
    article = (MEDIUM / post['slug'] / 'article.html').read_text()
    published = date.fromisoformat(post['date']).strftime('%-d %B %Y')
    body = f'''<main id="main" class="shell"><div class="reading-nav"><a href="/blog/">Back to writing</a></div><div class="article-container">
<article><header><h1>{escape(post['title'])}</h1><p class="article-byline">By Nico Vergauwen. <time datetime="{post['date']}">{published}</time>.</p></header>
<div class="body imported-body">{article}</div>
<p class="publication-note">Originally published on {external(post['original_url'],post['publication'])} on {published}.</p></article>
<div class="article-tools"><button class="button" type="button" data-copy-link>Copy link</button><a href="/blog/">Browse all writing</a><p class="copy-status" role="status" aria-live="polite"></p></div>
</div></main>'''
    schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': post['title'],
              'datePublished': post['published_at'], 'author': {'@type': 'Person', 'name': CONTENT['name']},
              'description': post['description'], 'isBasedOn': post['original_url']}
    return document(post['title'] + ' | Nico Vergauwen',post['description'],body,schema,post['image'],post['url'])

def build():
    DIST.mkdir(exist_ok=True)
    assets=DIST/'assets'; assets.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',assets,dirs_exist_ok=True)
    for name in ('site.css','site.js'): shutil.copy2(ROOT/'src'/name,assets/name)
    (assets/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#ffc757"/><text x="32" y="43" text-anchor="middle" font-family="Arial,sans-serif" font-size="32" fill="#0b1b20">NV</text></svg>')
    blog=DIST/'blog'/'jacobi-forcing'; blog.mkdir(parents=True,exist_ok=True)
    shutil.copytree(PUBLICATION/'assets',blog/'assets',dirs_exist_ok=True)
    # Exclude superseded covers from incremental builds.
    for obsolete in ('jacobi-forcing-cover.png', 'jacobi-forcing-cover-beginner.png', 'jacobi-forcing-cover-parallel.png'):
        (blog/'assets'/obsolete).unlink(missing_ok=True)
    shutil.copy2(PUBLICATION/'article.txt',blog/'article.txt')
    (DIST/'index.html').write_text(homepage())
    (blog/'index.html').write_text(articlepage())
    (DIST/'blog'/'index.html').write_text(blogpage())
    for post in POSTS:
        destination = DIST / 'blog' / post['slug']
        destination.mkdir(exist_ok=True)
        (destination / 'index.html').write_text(imported_articlepage(post))
    (DIST/'404.html').write_text(document('Page not found | Nico Vergauwen','Find Nico Vergauwen’s projects, research, and writing.','<main id="main" class="shell not-found"><h1>This page isn’t here.</h1><p>You can find my projects, research, and writing on the homepage.</p><p><a class="button" href="/">Back home</a></p></main>'))
    # Public SEO/feed URLs are emitted only after a real origin is configured.
    (DIST/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {ORIGIN}/sitemap.xml\n' if ORIGIN else ''))
    for filename in ('feed.xml','sitemap.xml'): (DIST/filename).unlink(missing_ok=True)
    if ORIGIN:
        rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
        for tag,value in [('title','Nico Vergauwen'),('link',ORIGIN+'/'),('description','Writing on AI systems and distributed infrastructure')]: ET.SubElement(channel,tag).text=value
        for post in all_posts():
            item=ET.SubElement(channel,'item')
            for tag,value in [('title',post['title']),('link',ORIGIN+post['url']),('guid',ORIGIN+post['url']),('pubDate',format_datetime(datetime.fromisoformat(post['published_at']), usegmt=True)),('description',post['description'])]: ET.SubElement(item,tag).text=value
        ET.indent(rss); (DIST/'feed.xml').write_text(ET.tostring(rss,encoding='unicode',xml_declaration=True))
        sitemap=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        for path in ['/', '/blog/', *(p['url'] for p in all_posts())]:
            node=ET.SubElement(sitemap,'url'); ET.SubElement(node,'loc').text=ORIGIN+path
        ET.indent(sitemap); (DIST/'sitemap.xml').write_text(ET.tostring(sitemap,encoding='unicode',xml_declaration=True))
    print(f'Built homepage, blog index, {len(POSTS)+1} full articles, video, static assets, and 404 locally. No publication performed.')

if __name__=='__main__': build()
