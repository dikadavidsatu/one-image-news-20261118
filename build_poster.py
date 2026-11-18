#!/usr/bin/env python3
"""Render the one-image news poster for Wednesday 18 November 2026.

Dev-time generator: draws entry.png with Pillow and the DejaVu fonts bundled
in fonts/ (loaded by relative path, so the render is identical on any
machine). The graded entrypoint is main.py, which copies the committed
entry.png to the output directory. No randomness, no clock, no network:
re-running this script reproduces entry.png byte for byte.

Layout (1024 x 1024): navy masthead, a hero panel whose drawn illustration
is the Manila -> Shenzhen summit arc, a 2x3 grid of story cards, an
"also today" ticker, and a sources footer.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

W, H = 1024, 1024
NAVY = (11, 31, 51)
NAVY_DEEP = (8, 22, 37)
NAVY_MID = (20, 57, 92)
PAPER = (247, 243, 234)
INK = (18, 18, 18)
GREY = (96, 94, 86)
CARD = (255, 255, 255)
CARD_LINE = (214, 207, 190)
GOLD = (217, 164, 65)
GOLD_LT = (232, 190, 110)
RED = (192, 57, 43)
TEAL = (14, 124, 123)
BLUE = (28, 84, 150)
GREEN = (46, 125, 70)
PURPLE = (98, 70, 140)
MIST = (215, 222, 230)  # light text on navy
PANEL = (10, 26, 43)    # hero art panel


def load(size, bold=False, serif=False):
    name = "DejaVuSerif-Bold.ttf" if serif else (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def measure(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw, text, font, max_w):
    """Greedy word wrap returning lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if measure(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, xy, text, font, fill, tracking=2):
    """Draw text with letter tracking; returns x just past the last glyph."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += measure(draw, ch, font) + tracking
    return x


def vgrad(draw, box, top, bottom):
    """Vertical gradient fill of a rectangle, in fixed 4px bands."""
    x0, y0, x1, y1 = box
    steps = max(1, (y1 - y0) // 4)
    for i in range(steps + 1):
        t = i / steps
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        y = y0 + i * 4
        draw.rectangle([x0, y, x1, min(y + 4, y1)], fill=col)


# ---------------------------------------------------------------- stories
HERO = {
    "kicker": "ASIA  ·  SUMMITS & SECURITY",
    "headline": ["TRUMP'S ASIA", "GAMBIT"],
    "deck": ("Meets Marcos in Manila, then flies to Shenzhen for Xi — "
             "and a first-ever trilateral with Putin."),
    "foot": "MANILA  →  SHENZHEN   ·   APEC   ·   QUAD",
}

CARDS = [
    ("UKRAINE", RED, "Kerch Bridge hit again",
     "Ukraine strikes the Crimea link for a second straight day "
     "as Russia pounds Kyiv's bridges."),
    ("GULF", TEAL, "Hormuz tanker war escalates",
     "Another tanker ablaze off Oman; Iran claims six sunk since "
     "Sunday as a third US carrier arrives."),
    ("MANILA", BLUE, "Streets push back",
     "Nearly 300 arrested in days of anti-Trump protests; marchers "
     "head for Mendiola today."),
    ("TRADE", GOLD, "APEC week opens in Shenzhen",
     "Canada and China extend trade deals as Xi meets Carney; "
     "Baidu's chief warns of an AI bubble."),
    ("BRITAIN", PURPLE, "UK sanctions settler firms",
     "London targets companies in occupied territory in a push "
     "to save the two-state solution."),
    ("WEATHER", GREEN, "Cyclone Akvan bears down",
     "Bay of Bengal storm set to turn severe by Thursday; "
     "India braces for landfall."),
]

TICKER = [
    "Dhoni retires from the IPL",
    "Latvia approves a new cabinet",
    "Knesset picks a new speaker",
]


def draw_hero_art(draw):
    """Stylised Manila -> Shenzhen flight arc on the hero's right half."""
    x0, y0, x1, y1 = 592, 112, 996, 436
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=PANEL,
                           outline=(46, 84, 122), width=1)
    # faint latitude lines
    for yy in (168, 232, 296, 360):
        draw.line([(x0 + 14, yy), (x1 - 14, yy)], fill=(24, 52, 82), width=1)
    # fixed stars
    for sx, sy in [(640, 150), (700, 128), (760, 158), (860, 132),
                   (940, 168), (920, 300), (660, 250), (980, 380)]:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(120, 150, 180))
    # the arc: ellipse centred (790, 290), radii (190, 150), 140deg -> 320deg
    draw.arc([600, 140, 980, 440], start=140, end=320, fill=GOLD, width=4)
    # plane marker at the arc's top (270deg)
    px, py = 790, 140
    draw.polygon([(px, py - 12), (px - 8, py + 8), (px, py + 3),
                  (px + 8, py + 8)], fill=GOLD_LT)
    # endpoints: Manila (140deg) and Shenzhen (320deg)
    manila = (645, 386)
    shenzhen = (935, 194)
    for cx, cy in (manila, shenzhen):
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                     outline=(255, 255, 255), width=2)
    f_small = load(17, bold=True)
    draw.text((shenzhen[0] - 78, shenzhen[1] - 30), "SHENZHEN",
              font=f_small, fill=(255, 255, 255))
    draw.text((manila[0] + 14, manila[1] - 9), "MANILA", font=f_small,
              fill=(255, 255, 255))


def draw_card(draw, x, y, w, h, tag, colour, headline, summary):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=CARD,
                           outline=CARD_LINE, width=1)
    draw.rectangle([x, y + 8, x + 6, y + h - 8], fill=colour)
    tx = x + 20
    f_tag = load(15, bold=True)
    draw.text((tx, y + 12), tag, font=f_tag, fill=colour)
    f_head = load(24, bold=True)
    lines = wrap_text(draw, headline, f_head, w - 40)
    ly = y + 36
    for line in lines[:2]:
        draw.text((tx, ly), line, font=f_head, fill=INK)
        ly += 29
    f_body = load(17)
    blines = wrap_text(draw, summary, f_body, w - 40)
    by = ly + 4
    for line in blines[:2]:
        draw.text((tx, by), line, font=f_body, fill=GREY)
        by += 22


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 92], fill=NAVY)
    tracked(d, (28, 22), "THE WORLD IN ONE IMAGE", load(30, bold=True),
            (255, 255, 255), tracking=2)
    d.text((28, 60), "One day's world news, in a single picture",
           font=load(16), fill=MIST)
    chip = "WEDNESDAY  ·  18 NOVEMBER 2026"
    f_chip = load(19, bold=True)
    cw = measure(d, chip, f_chip) + 28
    d.rounded_rectangle([W - 28 - cw, 26, W - 28, 26 + 40], radius=6,
                        fill=RED)
    d.text((W - 28 - cw + 14, 35), chip, font=f_chip, fill=(255, 255, 255))
    d.rectangle([0, 92, W, 96], fill=GOLD)

    # ---- hero
    vgrad(d, (0, 96, W, 452), NAVY, NAVY_MID)
    d.text((28, 116), HERO["kicker"], font=load(19, bold=True), fill=GOLD_LT)
    f_hero = load(66, serif=True)
    hy = 148
    for line in HERO["headline"]:
        d.text((28, hy), line, font=f_hero, fill=(255, 255, 255))
        hy += 74
    f_deck = load(22)
    for i, line in enumerate(wrap_text(d, HERO["deck"], f_deck, 520)):
        d.text((28, 306 + i * 29), line, font=f_deck, fill=MIST)
    d.rectangle([28, 392, 88, 396], fill=GOLD)
    d.text((28, 406), HERO["foot"], font=load(17, bold=True), fill=GOLD_LT)
    draw_hero_art(d)

    # ---- grid header
    f_grid = load(20, bold=True)
    d.text((28, 466), "THE REST OF THE DAY", font=f_grid, fill=NAVY)
    rule_x = 28 + measure(d, "THE REST OF THE DAY", f_grid) + 16
    d.line([(rule_x, 478), (996, 478)], fill=CARD_LINE, width=2)

    # ---- story cards, 2 x 3
    cw_, ch_, gap = 468, 132, 14
    for i, (tag, colour, head, summ) in enumerate(CARDS):
        cx = 28 + (i % 2) * (cw_ + gap)
        cy = 490 + (i // 2) * (ch_ + gap)
        draw_card(d, cx, cy, cw_, ch_, tag, colour, head, summ)

    # ---- ticker
    d.rectangle([0, 926, W, 968], fill=NAVY)
    d.text((28, 938), "ALSO TODAY", font=load(16, bold=True), fill=GOLD_LT)
    tx = 28 + measure(d, "ALSO TODAY", load(16, bold=True)) + 22
    f_tick = load(16)
    for item in TICKER:
        d.text((tx, 938), item, font=f_tick, fill=(255, 255, 255))
        tx += measure(d, item, f_tick) + 18
        d.ellipse([tx - 9, 946, tx - 3, 952], fill=GOLD)
        tx += 10

    # ---- footer
    d.text((28, 982),
           "Sources: Reuters · AP · The Guardian · Al Jazeera · UKMTO · IMD",
           font=load(13), fill=GREY)
    d.text((W - 28 - measure(d, "ONE IMAGE · ONE DAY", load(13, bold=True)),
            982), "ONE IMAGE · ONE DAY", font=load(13, bold=True), fill=GREY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    return out


if __name__ == "__main__":
    path = build()
    print("wrote", path, os.path.getsize(path), "bytes")
