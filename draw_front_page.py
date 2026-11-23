#!/usr/bin/env python3
"""Draw the front page of The Monday Herald, 23 November 2026. (v2)

Dev-time renderer (Pillow). Produces entry.png (1024x1024, under 1 MiB).
The submitted entrypoint main.py only copies this image to the output
directory, because the grader sandbox runs with the standard library only.
Deterministic: no timestamps, no randomness, no network.

Layout (1024x1024): masthead, lead story with globe panel, then two
columns of stories with side icons, a numbers box, a ticker and a footer.
Every text block is wrapped to its column width and its height is checked
against its zone; the script fails loudly if anything overflows.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (158, 27, 27)
GRAY = (90, 83, 72)
PANEL = (233, 226, 207)
PANEL_LINE = (120, 110, 92)
BLUE = (111, 143, 163)
DARK_BLUE = (46, 74, 90)
ORANGE = (217, 106, 30)
YELLOW = (232, 169, 28)
SMOKE = (154, 147, 138)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines; return the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_font(draw, text, path, start, width):
    """Largest font size <= start whose text fits `width`."""
    size = start
    while size > 10:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= width:
            return fnt
        size -= 2
    return font(path, 10)


def star_points(cx, cy, r_out, r_in, n=5):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_globe(draw, cx, cy, r):
    """A cracked globe: circle, latitude/longitude arcs, red crack."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE,
                 outline=DARK_BLUE, width=4)
    for dy, w in ((-r * 0.55, 0.83), (0, 1.0), (r * 0.55, 0.83)):
        draw.arc([cx - r * w, cy + dy - r * 0.28, cx + r * w,
                  cy + dy + r * 0.28], 0, 360, fill=DARK_BLUE, width=2)
    for w in (0.45, 0.8):
        draw.arc([cx - r * w, cy - r, cx + r * w, cy + r], 0, 360,
                 fill=DARK_BLUE, width=2)
    crack = [(cx - r * 0.55, cy - r * 0.85), (cx - r * 0.2, cy - r * 0.45),
             (cx - r * 0.45, cy - r * 0.1), (cx - r * 0.05, cy + r * 0.2),
             (cx - r * 0.3, cy + r * 0.5), (cx + r * 0.1, cy + r * 0.8)]
    draw.line(crack, fill=RED, width=5, joint="curve")


def draw_factory(draw, x, y, w, h):
    """Factory silhouette with flames and smoke, inside (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    base = y + h
    draw.rectangle([x + 10, base - 34, x + 44, base], fill=(70, 66, 60))
    draw.rectangle([x + 48, base - 46, x + 78, base], fill=(52, 50, 46))
    draw.rectangle([x + 62, base - 62, x + 70, base - 44], fill=(52, 50, 46))
    for sx, sy, sr in ((x + 66, base - 68, 6), (x + 74, base - 78, 8),
                       (x + 82, base - 70, 5)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
    for fx in (x + 16, x + 54):
        draw.polygon([(fx, base - 34), (fx + 8, base - 52),
                      (fx + 16, base - 34)], fill=ORANGE)
        draw.polygon([(fx + 4, base - 34), (fx + 8, base - 46),
                      (fx + 12, base - 34)], fill=YELLOW)


def draw_ship(draw, x, y, w, h):
    """Cargo ship with smoke plume on wavy sea, inside (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    base = y + h - 18
    for sx, sy, sr in ((x + w - 30, y + 12, 8), (x + w - 20, y + 6, 10)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
    for i, c in enumerate((RED, DARK_BLUE, (90, 110, 60))):
        cx = x + 14 + i * 24
        draw.rectangle([cx, base - 24, cx + 21, base - 8], fill=c,
                       outline=INK, width=1)
    draw.polygon([(x + 8, base - 8), (x + w - 8, base - 8),
                  (x + w - 20, base + 8), (x + 20, base + 8)],
                 fill=(52, 50, 46))
    draw.rectangle([x + w - 24, base - 26, x + w - 13, base - 8],
                   fill=(70, 66, 60))
    for wy in (base + 13,):
        pts = []
        for px in range(x + 6, x + w - 6, 10):
            pts.append((px, wy + (3 if (px // 10) % 2 else -3)))
        draw.line(pts, fill=DARK_BLUE, width=2)


def draw_badge(draw, x, y, w, h):
    """Police star badge, inside (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    cx, cy = x + w // 2, y + h // 2
    draw.polygon(star_points(cx, cy, 30, 12), fill=YELLOW,
                 outline=(120, 90, 10), width=2)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                 outline=INK, width=1)


def draw_missiles(draw, x, y, w, h):
    """Underground tunnel mouth with two missiles, inside (x, y, w, h)."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # ground line and tunnel: dark floor band with an arched opening
    draw.line([(x + 8, y + h - 8), (x + w - 8, y + h - 8)], fill=INK, width=2)
    draw.pieslice([x + 14, y + h - 54, x + w - 14, y + h - 4], 180, 360,
                  fill=(60, 56, 50))
    draw.rectangle([x + 14, y + h - 30, x + w - 14, y + h - 8], fill=(60, 56, 50))
    # two missiles rising from the tunnel, thicker with clear red tips
    for mx, tilt in ((x + w // 2 - 28, -6), (x + w // 2 + 14, 4)):
        top = y + 8 + tilt
        draw.rectangle([mx, top + 13, mx + 11, y + h - 30], fill=(205, 205, 205),
                       outline=INK, width=1)
        draw.polygon([(mx, top + 13), (mx + 5, top), (mx + 11, top + 13)],
                     fill=RED)


def draw_block(draw, x, y, w, h):
    """Apartment block with a collapsed corner and rubble, inside box."""
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    bx, by = x + 12, y + 8
    bw, bh = w - 24, h - 20
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(150, 138, 120),
                   outline=INK, width=2)
    # window grid, 4 cols x 3 rows, sized to the block
    cols, rows = 4, 3
    cw, ch = bw // cols, bh // rows
    for r in range(rows):
        for c in range(cols):
            wx = bx + 6 + c * cw + 3
            wy = by + 6 + r * ch + 3
            draw.rectangle([wx, wy, wx + cw - 9, wy + ch - 9],
                           fill=(40, 44, 52))
    # collapsed corner: jagged notch cut from the block's right edge
    cut = [(bx + bw, by + bh // 3), (bx + bw - 16, by + bh // 3 + 8),
           (bx + bw - 6, by + bh // 3 + 16), (bx + bw - 18, by + bh // 2 + 6),
           (bx + bw, by + bh // 2 + 14)]
    draw.polygon(cut, fill=PANEL)
    draw.line(cut, fill=INK, width=2)
    # rubble at the base
    for rx, rs in ((bx + bw - 22, 6), (bx + bw - 10, 8), (bx + bw - 32, 5)):
        draw.polygon([(rx - rs, by + bh), (rx, by + bh - rs),
                      (rx + rs, by + bh)], fill=(110, 102, 88))
    # smoke above the notch
    draw.ellipse([bx + bw - 26, by - 4, bx + bw - 12, by + 10], fill=SMOKE)


def story_cell(draw, x, y, w, icon_fn, kicker, headline, body_text):
    """Side-icon story cell. Returns the y just below the cell."""
    icon_w, icon_h = 96, 80
    tx = x + icon_w + 12
    tw = w - icon_w - 12
    icon_fn(draw, x, y + 4, icon_w, icon_h)
    d_kick = font(SANS_B, 14)
    d_head = font(SERIF_B, 21)
    d_body = font(SERIF, 14)
    cy = y
    draw.text((tx, cy), kicker, font=d_kick, fill=RED)
    cy += 17
    hlines = wrap(draw, headline, d_head, tw)
    cy = text_block(draw, tx, cy, hlines, d_head, fill=INK, leading=25)
    blines = wrap(draw, body_text, d_body, tw)
    cy = text_block(draw, tx, cy + 3, blines, d_body, fill=INK, leading=17)
    return cy


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 32  # margin

    # ---- top dateline bar ----
    d.line([(M, 14), (W - M, 14)], fill=INK, width=2)
    d.text((M, 22), "MONDAY, 23 NOVEMBER 2026", font=font(SANS_B, 19), fill=INK)
    right = "THE WORLD IN ONE PAGE"
    d.text((W - M - d.textlength(right, font=font(SANS, 17)), 23), right,
           font=font(SANS, 17), fill=GRAY)
    d.line([(M, 48), (W - M, 48)], fill=INK, width=1)

    # ---- masthead ----
    mast = fit_font(d, "The Monday Herald", SERIF_B, 88, W - 2 * M)
    mw = d.textlength("The Monday Herald", font=mast)
    d.text(((W - mw) / 2, 56), "The Monday Herald", font=mast, fill=INK)
    d.line([(M, 150), (W - M, 150)], fill=INK, width=3)
    d.line([(M, 156), (W - M, 156)], fill=INK, width=1)
    tag = "Six stories that defined the day — from Antalya to Guasave"
    tf = font(SERIF, 20)
    d.text(((W - d.textlength(tag, font=tf)) / 2, 166), tag, font=tf, fill=GRAY)

    # ---- lead story: COP31 ----
    LX, LW = M, 588
    RX, RW = 640, W - M - 640
    d.text((LX, 200), "CLIMATE · ANTALYA", font=font(SANS_B, 20), fill=RED)
    head = ["COP31 COLLAPSES", "WITHOUT A DEAL"]
    hf = font(SERIF_B, 50)
    y = 224
    for line in head:
        d.text((LX, y), line, font=hf, fill=INK)
        y += 58
    deck = "The EU and its allies refuse a pact that never names fossil fuels."
    y = text_block(d, LX, y + 6, wrap(d, deck, font(SERIF, 20), LW),
                   font(SERIF, 20), fill=INK, leading=25)
    body = ("After two weeks in Antalya, COP31 ended on Sunday with no "
            "deal.")
    y = text_block(d, LX, y + 8, wrap(d, body, font(SERIF, 16), LW),
                   font(SERIF, 16), fill=INK, leading=21)
    assert y <= 456, f"lead text overflows: ends {y}"

    # lead illustration panel: cracked globe
    d.rectangle([RX, 200, RX + RW, 448], fill=PANEL, outline=PANEL_LINE,
                width=2)
    draw_globe(d, RX + RW // 2, 200 + 108, 72)
    cap = "The Antalya Pact fell apart over two words: fossil fuels."
    text_block(d, RX + 16, 200 + 196,
               wrap(d, cap, font(SERIF, 17), RW - 32), font(SERIF, 17),
               fill=GRAY, leading=21)

    d.line([(M, 462), (W - M, 462)], fill=INK, width=2)

    # ---- story columns ----
    COL_W = 464
    y_left, y_right = 478, 478
    y_left = story_cell(d, M, y_left, COL_W, draw_factory,
                        "INDONESIA · CIKANDE",
                        "50 MISSING AFTER JAVA FACTORY FIRE",
                        "Seven body bags were recovered and about 50 workers "
                        "were unaccounted for after fire tore through a "
                        "candy factory in Cikande, Banten.")
    y_left += 14
    y_left = story_cell(d, M, y_left, COL_W, draw_ship,
                        "BALTIC SEA",
                        "RUSSIAN SHIP STILL SMOULDERING OFF FINLAND",
                        "The Sparta II, hit by drones in the Gulf of "
                        "Finland on Saturday, was still smouldering on "
                        "Sunday as three nations' crews fought the fire.")
    y_right = story_cell(d, M + 496, y_right, COL_W, draw_badge,
                         "MEXICO · SINALOA",
                         "FBI FUGITIVE “EL CHAPO ISIDRO” SEIZED",
                         "Mexican troops captured Fausto Isidro Meza Flores, "
                         "one of the FBI’s ten most wanted, in Guasave on "
                         "Friday. Eleven died in the gunfight.")
    y_right += 10
    y_right = story_cell(d, M + 496, y_right, COL_W, draw_missiles,
                         "MIDDLE EAST",
                         "IRAN SHOWS OFF ITS “MISSILE CITY”",
                         "Iran unveiled a launcher firing two liquid-fuel "
                         "missiles at once from an underground base, as "
                         "three tankers were hit near the Strait of Hormuz.")
    y_right += 10
    y_right = story_cell(d, M + 496, y_right, COL_W, draw_block,
                         "UKRAINE · KYIV REGION",
                         "14 MISSING AFTER DRONE HITS KYIV FLATS",
                         "Part of a five-storey block in Dymer, north of "
                         "Kyiv, collapsed after a Russian drone strike on "
                         "Sunday, Kyiv officials said. Nine were "
                         "evacuated.")
    assert max(y_left, y_right) <= 886, (
        f"story columns overflow: left {y_left}, right {y_right}")

    # ---- numbers box, bottom of the left column ----
    box_y = y_left + 8
    d.rectangle([M, box_y, M + COL_W, box_y + 108], fill=PANEL,
                outline=PANEL_LINE, width=2)
    d.text((M + 14, box_y + 6), "THE DAY IN NUMBERS", font=font(SANS_B, 15),
           fill=RED)
    stats = [("50", "workers missing in the Cikande factory fire"),
             ("16", "crew evacuated from the burning Sparta II"),
             ("720", "India’s record Test total in Wellington"),
             ("186", "drones fired at Ukraine overnight")]
    sy = box_y + 28
    for num, label in stats:
        d.text((M + 14, sy), num, font=font(SERIF_B, 18), fill=INK)
        d.text((M + 64, sy + 2), label, font=font(SERIF, 15), fill=INK)
        sy += 19
    assert box_y + 108 <= 886, "numbers box overflows"

    # ---- ticker ----
    ty = 898
    d.rectangle([0, ty, W, ty + 56], fill=INK)
    tick = ("ALSO TODAY   •   NATO council meets in Brussels over the "
            "Russian incursion into Polish airspace   •   Seoul’s education "
            "minister quits over AI exam cheating   •   India post a record "
            "720 in Wellington; New Zealand 119 for 2 at stumps")
    tf2 = font(SANS, 16)
    tlines = wrap(d, tick, tf2, W - 2 * M)
    assert len(tlines) <= 2, f"ticker wraps to {len(tlines)} lines"
    text_block(d, M, ty + 8, tlines, tf2, fill=(240, 236, 224), leading=20)

    # ---- footer ----
    foot = "The Monday Herald  ·  Monday 23 November 2026  ·  The world in one page"
    ff = font(SANS, 14)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 970), foot, font=ff,
           fill=GRAY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
