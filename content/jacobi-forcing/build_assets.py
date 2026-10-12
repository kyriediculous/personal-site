"""Render the original explanatory SVG and export the canonical article as text.

Run: python3 content/jacobi-forcing/build_assets.py
The AI-generated cover is a separate, preserved source asset.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

def render_png(svg):
    """Render our own simple SVG with Pillow, without a native Cairo dependency."""
    scale = 2
    canvas = Image.new("RGB", (1600 * scale, 1150 * scale), "#f7f5ef")
    draw = ImageDraw.Draw(canvas)
    for element in ET.fromstring(svg):
        tag = element.tag.rsplit("}", 1)[-1]
        attrs = element.attrib
        def number(key, default=0):
            return float(attrs.get(key, default)) * scale
        if tag == "rect":
            x, y, w, h = (number(key) for key in ("x", "y", "width", "height"))
            draw.rounded_rectangle((x, y, x + w, y + h), radius=number("rx"),
                                   fill=attrs.get("fill"), outline=attrs.get("stroke"),
                                   width=max(1, int(number("stroke-width", 1))))
        elif tag == "line":
            draw.line([(number("x1"), number("y1")), (number("x2"), number("y2"))],
                      fill=attrs.get("stroke", "#252523"), width=max(1, int(number("stroke-width", 1))))
        elif tag == "text":
            bold = int(attrs.get("font-weight", 400)) >= 600
            size = int(number("font-size", 28))
            font_paths = [
                ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
                 else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
            ]
            for font_path, index in font_paths:
                if Path(font_path).is_file():
                    font = ImageFont.truetype(font_path, size=size, index=index)
                    break
            else:
                raise RuntimeError("A Helvetica or DejaVu Sans font is required to render the diagram.")
            anchor = "ms" if attrs.get("text-anchor") == "middle" else "ls"
            pos = (number("x"), number("y"))
            bounds = draw.textbbox(pos, element.text or "", font=font, anchor=anchor)
            if min(bounds[:2]) < 0 or bounds[2] > canvas.width or bounds[3] > canvas.height:
                raise ValueError(f"Diagram text exceeds its canvas: {element.text}")
            draw.text(pos, element.text or "", fill=attrs.get("fill", "#252523"),
                      font=font, anchor=anchor)
    canvas.resize((1600, 1150), Image.Resampling.LANCZOS).save(ASSETS / "jacobi-forcing-refinement.png")

def text(x, y, value, size=28, fill="#252523", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{fill}">{escape(value)}</text>')

def render_diagram():
    ink, muted, blue, paper = "#252523", "#74746c", "#315ad4", "#f7f5ef"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1150" viewBox="0 0 1600 1150">',
             '<title>Jacobi Forcing improves several guesses together</title>',
             '<desc>A made-up sentence improves through several rounds. Some later words match the finished sentence while earlier words are still changing. Words stand in for tokens.</desc>',
             f'<rect width="1600" height="1150" fill="{paper}"/>',
             text(96, 78, "JACOBI FORCING / AI EXPLAINED", 22, muted, 600),
             text(96, 154, "Improve several guesses at once.", 66, ink, 700),
             text(96, 211, "Some words can fall into place while others are still changing.", 30, muted),
             f'<rect x="96" y="253" width="24" height="24" rx="5" fill="{blue}"/>',
             text(134, 273, "Matches the finished sentence", 25, ink),
             '<rect x="575" y="253" width="24" height="24" rx="5" fill="#e5e3dc" stroke="#cccac3"/>',
             text(613, 273, "Still needs to change", 25, ink)]
    final = ["The", "cat", "sat", "on", "the", "mat"]
    rows = [
        ("First guesses", ["A", "dog", "ran", "near", "a", "tree"]),
        ("Try again", ["The", "dog", "ran", "on", "a", "mat"]),
        ("Improve again", ["The", "cat", "sat", "on", "a", "mat"]),
        ("Final answer", final),
    ]
    for row, (label, tokens) in enumerate(rows):
        y = 353 + row * 130
        parts.append(text(96, y + 53, label, 27, ink, 600))
        for col, token in enumerate(tokens):
            x = 405 + col * 179
            is_match = token == final[col]
            fill = blue if is_match else "#e5e3dc"
            stroke = blue if is_match else "#d4d2ca"
            parts.append(f'<rect x="{x}" y="{y}" width="155" height="88" rx="10" fill="{fill}" stroke="{stroke}"/>')
            parts.append(text(x + 77.5, y + 56, token, 34, "#ffffff" if is_match else muted, 500, "middle"))
        if row < len(rows) - 1:
            parts.append(f'<line x1="285" y1="{y + 79}" x2="285" y2="{y + 122}" stroke="#a4a39b" stroke-width="2"/>')
            parts.append(f'<line x1="278" y1="{y + 113}" x2="285" y2="{y + 122}" stroke="#a4a39b" stroke-width="2"/>')
            parts.append(f'<line x1="292" y1="{y + 113}" x2="285" y2="{y + 122}" stroke="#a4a39b" stroke-width="2"/>')
    parts.extend([
        '<line x1="96" y1="906" x2="1504" y2="906" stroke="#cfcdc5"/>',
        text(96, 964, "Several guesses can improve during the same round.", 37, ink, 600),
        text(96, 1014, "The system still checks and finalizes the text from left to right.", 30, muted),
        text(96, 1090, "A MADE-UP EXAMPLE. WORDS STAND IN FOR TOKENS.", 20, muted, 500),
        '</svg>',
    ])
    svg = "\n".join(parts)
    (ASSETS / "jacobi-forcing-refinement.svg").write_text(svg)
    render_png(svg)

class ArticleText(HTMLParser):
    """Export only article text, retaining citations and readable table rows."""
    def __init__(self):
        super().__init__()
        self.in_article = False
        self.out = []
        self.link = None
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self.in_article = True
        if not self.in_article:
            return
        if tag == "p" and attrs.get("class") == "eyebrow":
            self.skip += 1
        if self.skip:
            return
        if tag == "a":
            self.link = attrs.get("href")
    def handle_endtag(self, tag):
        if not self.in_article:
            return
        if tag == "p" and self.skip:
            self.skip -= 1
            return
        if self.skip:
            return
        if tag == "a" and self.link:
            self.out.append(f" ({self.link})")
            self.link = None
        if tag in ("th", "td"):
            self.out.append(" | ")
        elif tag == "tr":
            self.out.append("\n")
        elif tag in ("p", "h1", "h2", "h3", "figcaption", "table"):
            self.out.append("\n\n")
        if tag == "article":
            self.in_article = False
    def handle_data(self, data):
        if self.in_article and not self.skip:
            value = re.sub(r"\s+", " ", data)
            if value.strip():
                self.out.append(value)

def export_text():
    parser = ArticleText()
    parser.feed((ROOT / "article.html").read_text())
    value = "".join(parser.out)
    value = re.sub(r"\s*\|\s*\n", "\n", value)
    value = re.sub(r" +\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value).strip() + "\n"
    (ROOT / "article.txt").write_text(value)
    words = len(re.findall(r"\b[\w’'-]+\b", re.sub(r"https?://\S+", "", value)))
    print(f"Article exported: {words} words; diagram rendered: 1600 × 1150")

if __name__ == "__main__":
    render_diagram()
    export_text()
