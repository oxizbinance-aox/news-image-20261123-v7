#!/usr/bin/env python3
"""News Image 23 November 2026 — v7 broadsheet, drawn from scratch with PIL.

One image, 1024x1024, 46 dated stories, 8 regions, a world map, 2 charts,
a big data strip and a hand-drawn pictogram per lead story.
Deterministic: same input -> byte-identical PNG (no timestamps, no randomness).
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 20  # page margin

PAPER = (247, 243, 232)
INK = (24, 24, 24)
MUTED = (90, 86, 76)
RED = (163, 22, 33)
NAVY = (20, 50, 79)
TEAL = (14, 107, 107)
GOLD = (176, 132, 12)
PANEL = (255, 253, 247)
PANEL_LINE = (200, 192, 172)
MAP_LAND = (232, 223, 200)
MAP_SEA = (214, 228, 235)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- stories
# Each grid story: (number, region, bold head, detail). Heads/details are kept
# short on purpose so every item fits two lines at 11px in a 300px column.
LEADS = [
    ("LEAD 1 · COP31 · ANTALYA", "COP31 collapses — no deal",
     "After a record two days' overtime, 190+ nations fail to agree a pact. "
     "The EU and ~130 parties reject a text with no fossil-fuel mention. "
     "90 nations back electrification; 47 join a methane cut. "
     "First COP collapse since 2009."),
    ("LEAD 2 · LIBYA · MEDITERRANEAN", "Ukraine sinks Russian warship in Libya",
     "Sea drones sink the corvette Merkury at Benghazi; "
     "a second Russian-linked vessel is hit, 10 hurt. "
     "The war reaches the Mediterranean, 1,600 km away."),
    ("LEAD 3 · UKRAINE · KYIV REGION", "Strike on Dymer kills 11",
     "A Russian drone strike partly collapses a five-storey block north of Kyiv. "
     "A boy of 7 is pulled alive after 14 hours, an elderly woman after 22. "
     "Fifteen die across the Kyiv region."),
]

GRID = [
    # Europe
    (4, "EUROPE", "Sparta II ablaze in the Baltic",
     "Russian-linked freighter drifts into Finnish waters."),
    (5, "EUROPE", "Poland: debris was Russian missiles",
     "Fallen objects confirmed cruise missiles; NATO to meet."),
    (6, "EUROPE", "Germany tests suicide drones",
     "First test of loitering munitions, held in Lithuania."),
    (7, "EUROPE", "France–Ukraine build SAMP/T together",
     "Joint production of air defences agreed in Paris."),
    (8, "EUROPE", "Belgium airports shut in strike",
     "Austerity protest grounds flights nationwide."),
    (9, "EUROPE", "NHS trials AI breast screening",
     "World's largest trial; ~700,000 women invited."),
    (10, "EUROPE", "Russia plans nuclear-armed satellite",
     "German media: launch into space planned this year."),
    # Middle East
    (11, "MIDDLE EAST", "Iran vows 'all means' vs US blockade",
     "Two tankers ablaze near Hormuz as tensions spike."),
    (12, "MIDDLE EAST", "Bahrain: Iranian strike wounds two",
     "Two hurt at a civilian site, officials say."),
    # Africa
    (13, "AFRICA", "Khartoum drone strikes hit homes",
     "Strikes destroy houses, damage a UN building."),
    (14, "AFRICA", "Kenya & DR Congo restore ties",
     "Ruto, Tshisekedi agree at Oyo summit; reported Mon."),
    (15, "AFRICA", "Bayelsa boat toll rises to 29",
     "Mourners' boat capsized 20 Nov; Tinubu gives ₦250m."),
    (16, "AFRICA", "S. Africa: coalition deal for Joburg",
     "Metro governments agreed; strict water curbs imposed."),
    (17, "AFRICA", "Libya: eastern forces claim Benghazi port",
     "Claim follows drone strikes on Russian cargo ship."),
    # Asia-Pacific
    (18, "ASIA-PACIFIC", "S. Korea exports top $1 trillion",
     "First time ever; chip exports up 294%."),
    (19, "ASIA-PACIFIC", "Taiwan bans short-selling below close",
     "Stocks swing 1,578 points in a single day."),
    (20, "ASIA-PACIFIC", "KOSPI −3%; China unveils rescue",
     "Beijing's 'three arrows' move to steady markets."),
    (21, "ASIA-PACIFIC", "Banten factory fire: 24 bodies found",
     "Dozens missing; search resumes Monday."),
    (22, "ASIA-PACIFIC", "Indonesia to take 70% of mining take",
     "State claims shares or revenue from miners."),
    (23, "ASIA-PACIFIC", "S. Korea minister quits in AI row",
     "Education chief resigns over exam-cheating scandal."),
    (24, "ASIA-PACIFIC", "Trump, Putin, Xi meet in Shenzhen",
     "Leaders issue a 'Declaration toward Peace'."),
    (25, "ASIA-PACIFIC", "US gives Philippines $2.4bn arms aid",
     "Military financing deepens the Manila alliance."),
    (26, "ASIA-PACIFIC", "Bangladesh: Hasina jailed if she returns",
     "Ex-PM faces arrest from exile in India."),
    # North America
    (27, "NORTH AMERICA", "Democrats win 258 House seats",
     "Largest majority since 1992."),
    (28, "NORTH AMERICA", "The penny ends after 232 years",
     "Common Cents Act signed into law."),
    (29, "NORTH AMERICA", "Delta outage delays 1,600+ flights",
     "Thanksgiving travel begins in chaos."),
    (30, "NORTH AMERICA", "US Army to detonate lead stockpile",
     "Unstable Iowa store blown up despite court order."),
    (31, "NORTH AMERICA", "KPMG Canada hacked",
     "Client tax data stolen in the breach."),
    (32, "NORTH AMERICA", "Two states sue SpaceX over AI safety",
     "Oregon, Virginia challenge Musk on child safety."),
    # Latin America
    (33, "LATIN AMERICA", "Brazil votes on Lula's fiscal bill",
     "Spending curbs; 2027 savings of $0.6–1.9bn."),
    (34, "LATIN AMERICA", "Drones hit police HQ in Cúcuta",
     "Early strike damages homes; no casualty count."),
    (35, "LATIN AMERICA", "Peru: aftershocks after 6.7 quake",
     "Truck driver the only known death from 20 Nov quake."),
    (36, "LATIN AMERICA", "Mexico: CJNG commanders keep falling",
     "Arrests continue after El Mencho's reported death."),
    # Oceania
    (37, "OCEANIA", "Molly Meldrum dies at 83",
     "Australian music icon, host of Countdown, dies Monday."),
    # Global
    (38, "GLOBAL", "Nikkei −5.06%, S&P 500 −3.7%",
     "AI sell-off spreads; gold up 3.14%."),
    (39, "GLOBAL", "Bitcoin ETFs bleed $1.79bn in a week",
     "Third-largest outflow on record."),
    (40, "GLOBAL", "Nvidia revenue more than doubles",
     "Huang board saga deepens."),
    (41, "GLOBAL", "Riemann proof certified in Lean",
     "17m lines checked; the ideas still unexplained."),
    (42, "GLOBAL", "IEEE: energy is AI's key limit to 2030",
     "Power, not chips, constrains AI growth."),
    (43, "GLOBAL", "'Cairn' AI used to hack universities",
     "Research framework turned on East Asian campuses."),
    (44, "GLOBAL", "TfL Oyster site hacked",
     "Data of 265,000 users exposed."),
    (45, "GLOBAL", "Alcaraz beats Zverev in Turin",
     "First ATP Finals title for the Spaniard."),
    (46, "GLOBAL", "GTA VI pre-orders pass 32.5m",
     "Rockstar sequel smashes records."),
]

STRIP = [
    ("258", "Democrats' House seats"),
    ("−5.06%", "Nikkei, Monday"),
    ("$1T", "S. Korea exports"),
    ("11", "killed in Dymer"),
    ("29", "Bayelsa boat toll"),
    ("32.5M", "GTA VI pre-orders"),
]

REGIONS = ["EUROPE", "MIDDLE EAST", "AFRICA", "ASIA-PACIFIC",
           "NORTH AMERICA", "LATIN AMERICA", "OCEANIA", "GLOBAL"]

# ---------------------------------------------------------------- helpers
BOXES = []  # (x0, y0, x1, y1, kind) for the layout validator


def record(x0, y0, x1, y1, kind):
    BOXES.append([round(x0), round(y0), round(x1), round(y1), kind])


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit `width`."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None, max_lines=None):
    """Draw wrapped lines; returns y after the last line. Truncates with … if needed."""
    lh = leading or int(fnt.size * 1.22)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while lines and draw.textlength(last + " …", font=fnt) > 0 and \
                draw.textlength(last, font=fnt) > 0 and len(last) > 3:
            last = last[:-1]
            if draw.textlength(last + " …", font=fnt) <= 320:
                break
        lines[-1] = last.rstrip() + " …"
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        record(x, y, x + draw.textlength(ln, font=fnt), y + fnt.size, "text")
        y += lh
    return y


def rule(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- pictograms
def pic_cop(draw, cx, cy, r):
    """Broken globe: COP31, no deal."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3, fill=(226, 236, 242))
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=NAVY, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 0, 360, fill=NAVY, width=2)
    crack = [(cx - 4, cy - r + 6), (cx + 8, cy - 12), (cx - 6, cy + 2),
             (cx + 10, cy + 14), (cx - 2, cy + r - 4)]
    draw.line(crack, fill=RED, width=3, joint="curve")
    draw.line([(cx - r - 4, cy - r - 4), (cx + r + 4, cy + r + 4)], fill=RED, width=4)
    draw.line([(cx - r - 4, cy + r + 4), (cx + r + 4, cy - r - 4)], fill=RED, width=4)


def pic_ship(draw, x0, y0, x1, y1):
    """Warship hit by sea drones: the Merkury sinking."""
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    draw.polygon([(x0 + 8, cy + 6), (x1 - 8, cy + 6), (x1 - 26, cy + 18),
                  (x0 + 22, cy + 18)], fill=NAVY)
    draw.rectangle([cx - 22, cy - 8, cx + 6, cy + 6], fill=NAVY)
    draw.line([(cx - 8, cy - 8), (cx - 8, cy - 22)], fill=NAVY, width=3)
    draw.line([(cx - 8, cy - 22), (cx + 10, cy - 16)], fill=RED, width=3)
    for wx in (x0 + 4, cx - 10, cx + 18, x1 - 12):
        draw.arc([wx, cy + 20, wx + 22, cy + 30], 180, 360, fill=TEAL, width=2)
    for dx, dy in ((x0 + 30, y0 + 4), (x1 - 46, y0 + 10), (cx + 26, y0 + 2)):
        draw.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=RED)
        draw.line([(dx, dy + 3), (dx - 6, dy + 14)], fill=RED, width=1)
    draw.line([(cx + 14, cy + 2), (cx + 30, cy - 12)], fill=RED, width=2)
    draw.ellipse([cx + 26, cy - 16, cx + 34, cy - 8], outline=RED, width=2)


def pic_block(draw, x0, y0, x1, y1):
    """Apartment block, partly collapsed: Dymer."""
    bw, bh = 54, 58
    bx, by = x0 + 12, y0 + 6
    draw.rectangle([bx, by, bx + bw, by + bh], outline=NAVY, width=3, fill=(226, 236, 242))
    for r in range(4):
        for c in range(3):
            wx, wy = bx + 7 + c * 16, by + 7 + r * 13
            draw.rectangle([wx, wy, wx + 9, wy + 8], outline=NAVY, width=1, fill=(255, 255, 255))
    # collapsed corner: jagged rubble
    rubble = [(bx + bw, by + 18), (bx + bw + 22, by + 26), (bx + bw + 12, by + 40),
              (bx + bw + 24, by + 52), (bx + bw, by + bh), (bx + bw, by + 18)]
    draw.polygon(rubble, fill=(190, 186, 172), outline=RED, width=2)
    draw.line([(bx + bw + 2, by + 22), (bx + bw + 18, by + 34)], fill=RED, width=2)
    # rescue heart
    hx, hy = x1 - 34, y1 - 26
    draw.ellipse([hx - 8, hy - 6, hx + 1, hy + 3], fill=RED)
    draw.ellipse([hx - 1, hy - 6, hx + 8, hy + 3], fill=RED)
    draw.polygon([(hx - 8, hy - 1), (hx + 8, hy - 1), (hx, hy + 10)], fill=RED)
    draw.text((x1 - 44, y1 - 12), "11", font=font(SANS_B, 13), fill=RED)


# ---------------------------------------------------------------- header + strip
def draw_header(draw):
    draw.text((M, 12), "THE WORLD IN ONE PAGE", font=font(SERIF_B, 40), fill=INK)
    record(M, 12, M + draw.textlength("THE WORLD IN ONE PAGE", font=font(SERIF_B, 40)), 52, "text")
    right = "46 STORIES · 8 REGIONS"
    rf = font(SANS_B, 19)
    draw.text((W - M - draw.textlength(right, font=rf), 18), right, font=rf, fill=RED)
    record(W - M - draw.textlength(right, font=rf), 18, W - M, 37, "text")
    sub = "Monday 23 November 2026 — the day's world news, one broadsheet"
    sf = font(SANS, 15)
    draw.text((M, 58), sub, font=sf, fill=MUTED)
    record(M, 58, M + draw.textlength(sub, font=sf), 73, "text")
    rule(draw, M, 88, W - M, 3)


def draw_strip(draw):
    y0, y1 = 96, 142
    draw.rectangle([M, y0, W - M, y1], fill=NAVY)
    cw = (W - 2 * M) / len(STRIP)
    nf, lf = font(SANS_B, 23), font(SANS, 10)
    for i, (num, label) in enumerate(STRIP):
        cx = M + cw * i
        nw = draw.textlength(num, font=nf)
        draw.text((cx + (cw - nw) / 2, y0 + 4), num, font=nf, fill=(255, 255, 255))
        lw = draw.textlength(label, font=lf)
        draw.text((cx + (cw - lw) / 2, y0 + 30), label, font=lf, fill=(200, 214, 228))
        if i:
            draw.line([(cx, y0 + 6), (cx, y1 - 6)], fill=(70, 100, 130), width=1)


# ---------------------------------------------------------------- leads
def draw_leads(draw):
    y0, y1 = 148, 330
    pw, gap = 322, 8
    pics = [pic_cop, pic_ship, pic_block]
    for i, (kicker, head, body) in enumerate(LEADS):
        x0 = M + i * (pw + gap)
        x1 = x0 + pw
        draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=PANEL_LINE, width=1)
        draw.rectangle([x0, y0, x1, y0 + 4], fill=RED)
        kf = font(SANS_B, 10)
        draw.text((x0 + 10, y0 + 10), kicker, font=kf, fill=RED)
        record(x0 + 10, y0 + 10, x0 + 10 + draw.textlength(kicker, font=kf), y0 + 20, "text")
        # pictogram band
        draw.rectangle([x0 + 1, y0 + 28, x1 - 1, y0 + 88], fill=(238, 234, 222))
        cx = x0 + 52
        if i == 0:
            pic_cop(draw, cx, y0 + 58, 26)
        elif i == 1:
            pic_ship(draw, x0 + 14, y0 + 32, x0 + 118, y0 + 86)
        else:
            pic_block(draw, x0 + 8, y0 + 28, x0 + 118, y0 + 88)
        tag = ["NO DEAL", "SUNK AT BENGHAZI", "RESCUED ALIVE"][i]
        tf = font(SANS_B, 12)
        draw.text((x0 + 126, y0 + 50), tag, font=tf, fill=NAVY)
        record(x0 + 126, y0 + 50, x0 + 126 + draw.textlength(tag, font=tf), y0 + 62, "text")
        hf = font(SANS_B, 16)
        lines = wrap(draw, head, hf, pw - 20)
        y = text_block(draw, x0 + 10, y0 + 94, lines, hf, leading=18, max_lines=2)
        bf = font(SANS, 11)
        blines = wrap(draw, body, bf, pw - 20)
        end_y = text_block(draw, x0 + 10, y + 3, blines, bf, leading=13, max_lines=5)
        assert end_y <= y1 + 2, f"lead {i} overflow: end_y={end_y} > {y1}"


# ---------------------------------------------------------------- map
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
           (-75, 72), (-60, 60), (-55, 47), (-65, 45), (-75, 35), (-80, 25),
           (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
           (-140, 60), (-165, 60)],
    "SA": [(-80, 10), (-72, 12), (-60, 8), (-50, 5), (-35, -6), (-35, -15),
           (-40, -25), (-48, -28), (-58, -35), (-65, -40), (-70, -52), (-73, -50),
           (-73, -35), (-70, -20), (-80, -5), (-81, 0)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
           (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (40, 68), (45, 68),
           (40, 55), (35, 50), (30, 46), (28, 41), (23, 36), (19, 40), (12, 44),
           (3, 43), (-2, 37)],
    "AF": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
           (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35),
           (15, -30), (12, -18), (9, -2), (9, 4), (-8, 5), (-15, 11)],
    "AS": [(40, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72), (160, 70),
           (178, 66), (170, 60), (160, 55), (145, 45), (140, 40), (130, 35),
           (122, 30), (115, 22), (108, 12), (100, 8), (95, 15), (90, 22), (80, 13),
           (75, 8), (70, 20), (60, 25), (55, 27), (48, 30), (43, 38), (40, 45),
           (35, 42)],
    "OC": [(113, -22), (114, -30), (115, -35), (125, -32), (132, -32), (137, -35),
           (142, -38), (147, -39), (150, -37), (153, -27), (150, -22), (146, -19),
           (142, -11), (136, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
}

# (lon, lat, label or None)
HOTSPOTS = [
    (30.7, 36.9, None), (20.1, 32.1, "Benghazi"), (30.5, 50.4, "Kyiv"),
    (23.0, 59.5, None), (-0.1, 51.5, None), (32.5, 15.6, "Khartoum"),
    (6.3, 4.9, None), (28.0, -26.2, "Joburg"), (127.0, 37.5, "Seoul"),
    (121.5, 25.0, "Taipei"), (106.2, -6.1, None), (114.0, 22.5, None),
    (-47.9, -15.8, "Brasília"), (-72.5, 7.9, None), (-77.0, -12.0, "Lima"),
    (-99.1, 19.4, None), (145.0, -37.8, "Melbourne"), (121.0, 14.6, None),
]


def draw_map(draw):
    x0, y0, x1, y1 = M, 336, 490, 542
    draw.rectangle([x0, y0, x1, y1], fill=MAP_SEA, outline=PANEL_LINE, width=1)
    tf = font(SANS_B, 11)
    draw.text((x0 + 10, y0 + 8), "THE WORLD — MONDAY'S HOTSPOTS", font=tf, fill=NAVY)
    record(x0 + 10, y0 + 8, x0 + 10 + draw.textlength("THE WORLD — MONDAY'S HOTSPOTS", font=tf), y0 + 19, "text")
    px0, py0, px1, py1 = x0 + 8, y0 + 28, x1 - 8, y1 - 8

    def proj(lon, lat):
        x = px0 + (lon + 170) / 360 * (px1 - px0)
        y = py0 + (84 - lat) / 142 * (py1 - py0)
        return (x, y)

    for pts in CONTINENTS.values():
        draw.polygon([proj(lo, la) for lo, la in pts], fill=MAP_LAND, outline=NAVY)
    lf = font(SANS, 9)
    for lon, lat, label in HOTSPOTS:
        x, y = proj(lon, lat)
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=RED, outline=(255, 255, 255), width=1)
        if label:
            tw = draw.textlength(label, font=lf)
            tx = min(max(x + 6, px0), px1 - tw)
            ty = min(max(y - 12, py0), py1 - 10)
            draw.text((tx, ty), label, font=lf, fill=INK)
            record(tx, ty, tx + tw, ty + 9, "text")


# ---------------------------------------------------------------- charts
def draw_chart_rout(draw):
    x0, y0, x1, y1 = 498, 336, 1004, 436
    draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=PANEL_LINE, width=1)
    tf = font(SANS_B, 11)
    draw.text((x0 + 10, y0 + 8), "MONDAY'S ROUT — % CHANGE", font=tf, fill=NAVY)
    record(x0 + 10, y0 + 8, x0 + 10 + draw.textlength("MONDAY'S ROUT — % CHANGE", font=tf), y0 + 19, "text")
    rows = [("Taiwan (wk)", -17.5), ("Nasdaq (wk)", -10.0), ("Nikkei", -5.06),
            ("S&P 500", -3.7), ("KOSPI", -3.0), ("Euro Stoxx", 0.94), ("Gold", 3.14)]
    lf, vf = font(SANS, 10), font(SANS_B, 10)
    bx0, bx1 = x0 + 96, x1 - 52
    zero = bx0 + (bx1 - bx0) * 0.5
    top, rh = y0 + 26, 10
    for i, (name, val) in enumerate(rows):
        ry = top + i * rh
        draw.text((x0 + 10, ry - 1), name, font=lf, fill=INK)
        record(x0 + 10, ry - 1, x0 + 10 + draw.textlength(name, font=lf), ry + 9, "text")
        w = abs(val) / 17.5 * (bx1 - zero)
        col = RED if val < 0 else TEAL
        if val < 0:
            draw.rectangle([zero - w, ry, zero, ry + 7], fill=col)
        else:
            draw.rectangle([zero, ry, zero + w, ry + 7], fill=col)
        vs = f"{val:+.2f}".rstrip("0").rstrip(".") if val != int(val) else f"{val:+.0f}"
        if w > 60:
            # long bar: value inside it, white, right-aligned at the zero line
            vw = draw.textlength(vs, font=vf)
            vx = zero - vw - 4 if val < 0 else zero + 4
            draw.text((vx, ry - 1), vs, font=vf, fill=(255, 255, 255))
            record(vx, ry - 1, vx + vw, ry + 9, "text")
        else:
            vx = zero - w - 34 if val < 0 else zero + w + 4
            vx = max(bx0, min(vx, x1 - 40))
            draw.text((vx, ry - 1), vs, font=vf, fill=col)
            record(vx, ry - 1, vx + draw.textlength(vs, font=vf), ry + 9, "text")
    draw.line([(zero, top - 2), (zero, top + 7 * rh - 2)], fill=MUTED, width=1)


def draw_chart_taiex(draw):
    x0, y0, x1, y1 = 498, 442, 1004, 542
    draw.rectangle([x0, y0, x1, y1], fill=PANEL, outline=PANEL_LINE, width=1)
    tf = font(SANS_B, 11)
    draw.text((x0 + 10, y0 + 8), "TAIEX — MONDAY, POINTS", font=tf, fill=NAVY)
    record(x0 + 10, y0 + 8, x0 + 10 + draw.textlength("TAIEX — MONDAY, POINTS", font=tf), y0 + 19, "text")
    pts = [("Fri close", 36033), ("Early low", 35442), ("High", 37021), ("Close", 36000)]
    px0, px1 = x0 + 46, x1 - 56
    py0, py1 = y0 + 30, y1 - 22
    lo, hi = 35300, 37200

    def P(i, v):
        x = px0 + i * (px1 - px0) / 3
        y = py1 - (v - lo) / (hi - lo) * (py1 - py0)
        return (x, y)

    for gy in (36000, 37000):
        gyv = py1 - (gy - lo) / (hi - lo) * (py1 - py0)
        draw.line([(px0, gyv), (px1, gyv)], fill=(220, 216, 204), width=1)
        gf = font(SANS, 8)
        draw.text((x0 + 6, gyv - 4), f"{gy:,}", font=gf, fill=MUTED)
    xy = [P(i, v) for i, (_, v) in enumerate(pts)]
    draw.line(xy, fill=RED, width=3, joint="curve")
    lf, vf = font(SANS, 9), font(SANS_B, 9)
    for (label, v), (x, y) in zip(pts, xy):
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=RED, outline=(255, 255, 255), width=1)
        vs = f"{v:,}"
        vw = draw.textlength(vs, font=vf)
        tx = min(max(x - vw / 2, px0), px1 - vw)
        ty = y - 16 if v in (37021, 35442) else y + 6
        draw.text((tx, ty), vs, font=vf, fill=INK)
        record(tx, ty, tx + vw, ty + 9, "text")
        lw = draw.textlength(label, font=lf)
        lx = min(max(x - lw / 2, px0), px1 - lw)
        draw.text((lx, y1 - 18), label, font=lf, fill=MUTED)
        record(lx, y1 - 18, lx + lw, y1 - 9, "text")
    nf = font(SANS, 9)
    note = "1,578-pt swing — 13th largest ever"
    draw.text((x1 - 10 - draw.textlength(note, font=nf), y0 + 8), note, font=nf, fill=MUTED)


# ---------------------------------------------------------------- grid
COLUMNS = [
    [("EUROPE", [4, 5, 6, 7, 8, 9, 10]),
     ("MIDDLE EAST", [11, 12]),
     ("AFRICA", [13, 14, 15, 16, 17])],
    [("ASIA-PACIFIC", [18, 19, 20, 21, 22, 23, 24, 25, 26]),
     ("NORTH AMERICA", [27, 28, 29, 30, 31, 32])],
    [("LATIN AMERICA", [33, 34, 35, 36]),
     ("OCEANIA", [37]),
     ("GLOBAL", [38, 39, 40, 41, 42, 43, 44, 45, 46])],
]

BY_NUM = {n: (r, h, d) for n, r, h, d in GRID}


def fit_one_line(draw, text, fnt, width):
    """Truncate with an ellipsis so the text fits on one line."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while len(text) > 4 and draw.textlength(text + " …", font=fnt) > width:
        text = text[:-1]
    return text.rstrip() + " …"


def draw_grid(draw):
    y_top, y_bot = 548, 996
    col_w, gap = 322, 8
    hf = font(SANS_B, 11)
    bf, df = font(SANS_B, 11), font(SANS, 10)
    nf = font(SANS_B, 9)
    for ci, groups in enumerate(COLUMNS):
        x0 = M + ci * (col_w + gap)
        y = y_top
        for region, nums in groups:
            draw.text((x0, y), region, font=hf, fill=NAVY)
            record(x0, y, x0 + draw.textlength(region, font=hf), y + 11, "text")
            rule(draw, x0, y + 14, x0 + col_w, 1, fill=NAVY)
            y += 18
            for n in nums:
                _, head, detail = BY_NUM[n]
                # number chip
                draw.rectangle([x0, y + 1, x0 + 15, y + 15], fill=RED)
                ns = str(n)
                draw.text((x0 + (15 - draw.textlength(ns, font=nf)) / 2, y + 2),
                          ns, font=nf, fill=(255, 255, 255))
                tx = x0 + 20
                tw = col_w - 20
                hline = fit_one_line(draw, head, bf, tw)
                dline = fit_one_line(draw, detail, df, tw)
                draw.text((tx, y), hline, font=bf, fill=INK)
                record(tx, y, tx + draw.textlength(hline, font=bf), y + 11, "text")
                draw.text((tx, y + 13), dline, font=df, fill=(60, 58, 52))
                record(tx, y + 13, tx + draw.textlength(dline, font=df), y + 23, "text")
                y += 27
        assert y <= y_bot, f"column {ci} overflow: y={y} > {y_bot}"


# ---------------------------------------------------------------- footer + build
def draw_footer(draw):
    ff = font(SANS, 9)
    l1 = ("Sources: One Turn, BBC, France 24, Reuters, Yonhap, CNA, SCMP, FT, "
          "Just Security, Rio Times, Afripoli, UBStandard and the wires they cite.")
    l2 = "Every story happened, or was first reported, on Monday 23 November 2026."
    draw.text((M, 1000), l1, font=ff, fill=MUTED)
    record(M, 1000, M + draw.textlength(l1, font=ff), 1009, "text")
    draw.text((M, 1011), l2, font=ff, fill=MUTED)
    record(M, 1011, M + draw.textlength(l2, font=ff), 1020, "text")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_strip(draw)
    draw_leads(draw)
    draw_map(draw)
    draw_chart_rout(draw)
    draw_chart_taiex(draw)
    draw_grid(draw)
    draw_footer(draw)
    return img


def main():
    import hashlib
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    boxes_path = "/tmp/ni23v7_boxes.json"
    with open(boxes_path, "w") as f:
        json.dump({"boxes": BOXES, "stories": 3 + len(GRID),
                   "regions": REGIONS, "size": [W, H]}, f)
    print(f"stories={3 + len(GRID)} regions={len(REGIONS)} "
          f"size={len(data)} sha256={hashlib.sha256(data).hexdigest()}")
    print(f"boxes={len(BOXES)} -> {boxes_path}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
