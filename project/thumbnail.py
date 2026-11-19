# -*- coding: utf-8 -*-
"""YouTube thumbnail in the reference channel's format: split panel,
left = angry baby 'AGE 0', right = dramatic grown-up version with a 2-word tag."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import skia
from gfx import G, W, H, PAL, OUTLINE, C, text, text_w, new_surface
from characters import Person, CAST, anger_mark
from scenes_bg import *
from timeline import ROOT

CH = {k: Person(v) for k, v in CAST().items()}
LABELS = {"en": ("AGE 0", "LOCKED UP"), "tr": ("YAŞ 0", "HAPİSTE"), "de": ("ALTER 0", "WEGGESPERRT")}

def thumb(lang="en"):
    s = new_surface(); g = G(s.getCanvas()); t = 1.3
    split = [(0, 0), (930, 0), (800, H), (0, H)]
    right = [(930, 0), (W, 0), (W, H), (800, H)]
    # ---------- left: baby in Liberty City apartment
    g.c.save(); g.c.clipPath(G.poly_p(split), doAntiAlias=True)
    wall(g, "#e9d8b8", 800, stripes=(40, "#ffffff")); floor(g, 800, "#a8744a")
    window(g, 90, 130, 300, 250, view_lc_night, t, curtains="#c46a6a")
    crib(g, 470, 1000, 640, 340)
    CH["lucia_baby"].draw(g, 470, 950, 860, t, face={"brows": "angry", "mouth": "frown"}, blink_seed=1.0)
    crib_front(g, 470, 1080, 700, 230)
    anger_mark(g, 690, 300, 70, 0.0)
    g.c.restore()
    # ---------- right: grown-up Lucia, Vice City sunset behind prison bars
    g.c.save(); g.c.clipPath(G.poly_p(right), doAntiAlias=True)
    sky(g, "#ff6b6b", "#ffd6a0", mid="#ff9a6c", h=H)
    sun(g, 1760, 470, 220, "#fff1b8", bg="#ffb37a")
    skyline_vice(g, 760, t, scale=1.1)
    palm(g, 900, 1100, 1.6, t, sil="#3a2552"); palm(g, 1880, 1100, 1.5, t, sil="#3a2552", flip=True)
    g.rect_fill(0, 0, W, H, "#2a1030", 0.18)
    from realistic import Adult, ADULTS
    from atmo import vignette as vg, grain as gr, glow_at
    glow_at(g, 1400, 380, 600, "#ffb070", 0.35)
    Adult(ADULTS()["lucia_prison"], 3).draw(g, 1420, 300 + 7 * 330, 7.5 * 330, t, pose="cross",
                                             face={"brows": "angry", "mouth": "smirk"}, look=-0.15, blink_seed=2.0)
    for xx in (850, 1090, 1830):
        g.rrect(xx, -20, 44, H + 40, 22, "#3b3f55")
        g.line(xx + 12, 0, xx + 12, H, color="#7a8090", w=5)
    g.c.restore()
    # divider
    g.c.drawPath(G.poly_p([(930, 0), (800, H)], close=False), P_stroke("#fbf7f0", 22))
    g.c.drawPath(G.poly_p([(930, 0), (800, H)], close=False), P_stroke(OUTLINE, 8))
    l1, l2 = LABELS[lang]
    fn = "display_tr" if lang == "tr" else "display"
    text(g, l1, 430, 175, 170, fill="#ffffff", ow=26, name=fn)
    sz = 150 if len(l2) <= 9 else 120
    text(g, l2, 1400, 180, sz, fill="#ff5a3c", ow=24, rot=-4, name=fn)
    out = os.path.join(ROOT, "build", f"thumbnail_{lang}.png")
    img = s.makeImageSnapshot()
    img.save(out)
    # YouTube size 1280x720
    from PIL import Image
    Image.open(out).convert("RGB").resize((1280, 720), Image.LANCZOS).save(out.replace(".png", ".jpg"), quality=92)
    return out

if __name__ == "__main__":
    for l in (sys.argv[1:] or ["en", "tr", "de"]):
        print(thumb(l))
