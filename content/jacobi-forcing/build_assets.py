"""Render the original explanatory SVG and export the canonical article as text.

Run: python3 content/jacobi-forcing/build_assets.py
The AI-generated cover is a separate, preserved source asset.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import re
import base64
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONT = ASSETS / "fonts" / "host-grotesk.ttf"
INK, PAPER, WHITE = "#201f1e", "#f5f4ef", "#fbfbf9"
MINT, SKY, LILAC, SUN = "#c6f1e9", "#70c4e1", "#c0b7f9", "#ffc757"

def render_png(svg, destination):
    """Render our own simple SVG with Pillow, without a native Cairo dependency."""
    scale = 2
    root = ET.fromstring(svg)
    width, height = int(root.attrib["width"]), int(root.attrib["height"])
    canvas = Image.new("RGB", (width * scale, height * scale), PAPER)
    draw = ImageDraw.Draw(canvas)
    fonts = {}
    for element in root:
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
            size = int(number("font-size", 28))
            weight = int(attrs.get("font-weight", 400))
            key = size, weight
            if key not in fonts:
                fonts[key] = ImageFont.truetype(str(FONT), size=size)
                fonts[key].set_variation_by_axes([weight])
            font = fonts[key]
            anchor = "ms" if attrs.get("text-anchor") == "middle" else "ls"
            pos = (number("x"), number("y"))
            bounds = draw.textbbox(pos, element.text or "", font=font, anchor=anchor)
            if min(bounds[:2]) < 0 or bounds[2] > canvas.width or bounds[3] > canvas.height:
                raise ValueError(f"Diagram text exceeds its canvas: {element.text}")
            draw.text(pos, element.text or "", fill=attrs.get("fill", "#252523"),
                      font=font, anchor=anchor)
    canvas.resize((width, height), Image.Resampling.LANCZOS).save(destination)

def text(x, y, value, size=28, fill=INK, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Host Grotesk, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{fill}">{escape(value)}</text>')

def rect(x, y, width, height, fill, radius=16, stroke=None, stroke_width=1):
    border = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ""
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{fill}"{border}/>')

def line(x1, y1, x2, y2, width=3):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{INK}" stroke-width="{width}"/>')

def check(x, y, size=18):
    # A shape cue distinguishes matching tokens without relying on colour alone.
    return [line(x, y + size*.5, x + size*.35, y + size*.85),
            line(x + size*.35, y + size*.85, x + size, y)]

def render_diagram(mobile=False):
    width, height = (800, 1120) if mobile else (1600, 900)
    font_data = base64.b64encode(FONT.read_bytes()).decode("ascii")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
             '<title id="title">Parallel token refinement</title>',
             '<desc id="description">An invented sentence changes from A dog ran near a tree to The cat sat on the mat over four rounds. Mint tokens with checks match the final output; white tokens still need to change. A match at a later position is not automatically accepted. Words stand in for tokens.</desc>',
             f'<defs><style>@font-face{{font-family:"Host Grotesk";src:url(data:font/ttf;base64,{font_data}) format("truetype");font-weight:300 800;}}</style></defs>',
             rect(0, 0, width, height, PAPER, 0)]
    if mobile:
        parts += [text(40, 100, "Parallel token", 64), text(40, 164, "refinement", 64)]
        legend_y, legend_size, legend_x = 220, 32, 40
    else:
        parts += [text(64, 126, "Parallel token refinement", 80)]
        legend_y, legend_size, legend_x = 209, 32, 64
    parts.append(rect(legend_x, legend_y - 26, 32, 32, MINT, 8, INK, 2))
    parts += check(legend_x + 7, legend_y - 18, 18)
    parts.append(text(legend_x + 48, legend_y, "Matches final output", legend_size))
    second_x, second_y = (40, 274) if mobile else (500, legend_y)
    parts += [rect(second_x, second_y - 26, 32, 32, WHITE, 8, INK),
              text(second_x + 48, second_y, "Still changing", legend_size)]
    final = ["The", "cat", "sat", "on", "the", "mat"]
    rows = [
        ("Initial guesses", ["A", "dog", "ran", "near", "a", "tree"]),
        ("Pass 1", ["The", "dog", "ran", "on", "a", "mat"]),
        ("Pass 2", ["The", "cat", "sat", "on", "a", "mat"]),
        ("Final output", final),
    ]
    # Pass colours follow the site's project-card palette. Token states remain
    # constant across every band: mint plus a check is a match, white is a guess.
    bands = SKY, LILAC, SUN, MINT
    for row, (label, tokens) in enumerate(rows):
        if mobile:
            y, band_height, card_x = 322 + row*190, 166, 24
            parts += [rect(card_x, y, 752, band_height, bands[row], 24),
                      text(48, y + 48, label, 34, weight=500)]
            token_x, token_y, token_width, stride, font_size = 48, y + 69, 104, 120, 42
        else:
            y, band_height, card_x = 280 + row*146, 124, 64
            parts += [rect(card_x, y, 1472, band_height, bands[row], 28),
                      text(96, y + 76, label, 36, weight=500)]
            token_x, token_y, token_width, stride, font_size = 390, y + 18, 160, 180, 46
        for col, token in enumerate(tokens):
            x = token_x + col*stride
            is_match = token == final[col]
            parts.append(rect(x, token_y, token_width, 88, MINT if is_match else WHITE,
                              16, INK, 2 if is_match else 1))
            parts.append(text(x + token_width/2, token_y + 61, token, font_size,
                              weight=400, anchor="middle"))
            if is_match:
                parts += check(x + token_width - 25, token_y + 10, 14)
        if row < len(rows) - 1:
            arrow_x = 72 if mobile else 200
            arrow_y = y + band_height + 3
            parts += [line(arrow_x, arrow_y, arrow_x, arrow_y + 16, 2),
                      line(arrow_x - 5, arrow_y + 11, arrow_x, arrow_y + 16, 2),
                      line(arrow_x + 5, arrow_y + 11, arrow_x, arrow_y + 16, 2)]
    parts.append('</svg>')
    svg = "\n".join(parts)
    name = "jacobi-forcing-refinement" + ("-mobile" if mobile else "")
    (ASSETS / f"{name}.svg").write_text(svg)
    render_png(svg, ASSETS / f"{name}.png")

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
    print(f"Article exported: {words} words")

if __name__ == "__main__":
    render_diagram()
    render_diagram(mobile=True)
    export_text()
