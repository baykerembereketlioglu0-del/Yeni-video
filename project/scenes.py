# -*- coding: utf-8 -*-
"""One draw function per shot. Each receives (g, x) where x is a Ctx with:
   x.t (seconds into shot), x.d (shot length), x.cue(name) -> seconds,
   x.talking(who) -> bool, x.pop(name, dur), x.after(name)."""
import math, random
import skia
from gfx import (G, W, H, PAL, OUTLINE, C, P_fill, P_stroke, shade, tint, mix, clamp, lerp,
                 ease_io, ease_out, ease_in, ease_back, pop, fade, wob, text, text_w)
from characters import Person, CAST, anger_mark, sweat_drop, draw_prop
from scenes_bg import *

CH = {k: Person(v) for k, v in CAST().items()}
SCENES = {}

def scene(fn):
    SCENES[fn.__name__] = fn
    return fn

# ------------------------------------------------------------------ helpers
def cam(g, x, z0=1.0, z1=1.07, fx=W / 2, fy=H / 2, dx=0.0, dy=0.0, shake=None):
    k = ease_io(x.t / max(x.d, 0.01))
    z = lerp(z0, z1, k)
    sx = sy = 0.0
    if shake:
        for (t0, dur, amp) in shake:
            if t0 <= x.t < t0 + dur:
                f = 1 - (x.t - t0) / dur
                sx += math.sin(x.t * 90) * amp * f; sy += math.cos(x.t * 77) * amp * f
    g.tr(fx + dx * k + sx, fy + dy * k + sy); g.sc(z); g.tr(-fx, -fy)

def pop_text(g, s, x, y, size, k, fill="#ffffff", rot=0, outline=OUTLINE):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    text(g, s, 0, size * 0.35, size, fill=fill, rot=rot, outline=outline)
    g.restore()

def remember_tag(g, x, y, k, label="REMEMBER THIS", t=0.0):
    """Recurring callback marker: yellow sticky note."""
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k); g.rot(-6 + math.sin(t * 2) * 1.5)
    w = text_w(label, 46) + 60
    g.rrect(-w / 2 + 6, -34 + 8, w, 72, 10, "#1a1020", outline=None, a=0.25)
    g.rrect(-w / 2, -34, w, 72, 10, "#ffd84d")
    g.rrect(-24, -50, 48, 26, 4, "#ff8fab", w=g.lw * 0.6)
    text(g, label, 0, 16, 46, fill=PAL["red"], outline=None, shadow=False)
    g.restore()

def label_tag(g, s, x, y, k, fill="#fbf7f0", col="#2b2233", size=42, rot=-3):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k); g.rot(rot)
    w = text_w(s, size) + 50
    g.rrect(-w / 2, -size * 0.85, w, size * 1.6, 14, col)
    text(g, s, 0, size * 0.32, size, fill=fill, outline=None, shadow=False)
    g.restore()

def stamp(g, s, x, y, k, size=90, col=PAL["red"], rot=-10):
    if k <= 0: return
    sc = lerp(2.2, 1.0, ease_out(k)) if k < 1 else 1.0
    g.save(); g.tr(x, y); g.sc(sc); g.rot(rot)
    w = text_w(s, size) + 70
    g.alpha(clamp(k * 3))
    g.rrect(-w / 2, -size * 0.85, w, size * 1.55, 16, None, outline=col, w=12)
    text(g, s, 0, size * 0.35, size, fill=col, outline=None, shadow=False)
    g.restore(); g.restore()

def sparkles(g, x, y, t, r=120, n=6, col="#fff1a8", seed=1):
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0.4, 1.0) * r
        k = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
        sx, sy = x + math.cos(a) * d, y + math.sin(a) * d
        s = 14 * k + 4
        q = skia.Path(); q.moveTo(sx, sy - s); q.quadTo(sx, sy, sx + s, sy); q.quadTo(sx, sy, sx, sy + s)
        q.quadTo(sx, sy, sx - s, sy); q.quadTo(sx, sy, sx, sy - s); q.close()
        g.fillp(q, col, 0.9)

def cloud(g, x, y, s, col="#9aa0ad", rain=False, t=0.0, k=1.0):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(s * k)
    if rain:
        for i in range(7):
            ph = (t * 1.8 + i * 0.37) % 1.0
            xx = -70 + i * 23; yy = 30 + ph * 120
            g.line(xx, yy, xx - 6, yy + 22, color="#6fb6ff", w=6, a=1 - ph)
    g.smooth([(-100, 20), (-110, -20), (-60, -50), (-20, -80), (40, -70), (80, -40), (110, -10), (100, 25)], col)
    g.restore()

def lightbulb(g, x, y, k, t=0.0):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    g.glow(0, -10, 110, "#fff1a8", 0.6)
    g.circle(0, -10, 45, "#fff1a8")
    g.rrect(-22, 28, 44, 30, 8, "#9aa0ad")
    g.restore()

def chess_knight(g, x, y, s, k=1.0):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(s * k)
    q = skia.Path()
    q.moveTo(-40, 60); q.lineTo(40, 60); q.lineTo(30, 20); q.cubicTo(45, -20, 35, -60, 0, -75)
    q.cubicTo(-20, -82, -35, -70, -40, -55); q.lineTo(-60, -25); q.lineTo(-48, -12); q.lineTo(-20, -25)
    q.cubicTo(-30, 0, -40, 15, -30, 20); q.close()
    g.shape(q, "#fbf7f0")
    g.circle(-10, -50, 6, "#2b2233", outline=None)
    g.rrect(-55, 55, 110, 24, 8, "#fbf7f0")
    g.restore()

def mugshot_wall(g):
    wall(g, "#cfd4dc", 1080)
    for i, y in enumerate(range(140, 1000, 60)):
        g.line(0, y, W, y, color="#9aa3b1", w=3)
        if i % 2 == 0:
            text(g, "%d'" % (7 - i // 2) if i // 2 < 7 else "", 60, y + 12, 34, fill="#6a7180", outline=None, shadow=False)

def cell_bg(g, t, night=False):
    wl = "#9aa0ad" if not night else "#4a4f66"
    wall(g, wl, 860)
    for row in range(0, 860, 70):     # brick-like blocks
        off = 0 if (row // 70) % 2 == 0 else 80
        for col in range(-off, W, 160):
            g.rrect(col + 4, row + 4, 152, 62, 6, mix(wl, "#ffffff", 0.08), outline=None)
    floor(g, 860, "#6e7381" if not night else "#3a3d50")
    window(g, 1380, 150, 220, 170, view_moon if night else view_prison, t, frame="#7a8494")
    bars(g, 1380, 150, 220, 170, 4, "#4d5260", t, wdt=12)

def apartment_lc(g, t, night=True):
    wall(g, "#e9d8b8", 820, wainscot="#d7bf98", stripes=(40, "#ffffff"))
    floor(g, 820, "#a8744a")
    for i in range(0, W, 140):
        g.line(i, 820, i - 80, H, color="#8f6038", w=3)
    window(g, 1250, 150, 420, 330, view_lc_night if night else view_lc_day, t, curtains="#c46a6a")

def gym_bg(g, t):
    wall(g, "#3f4a6b", 800, stripes=(60, "#2f3956"))
    floor(g, 800, "#7a5236")
    for i, (x, col) in enumerate(((260, PAL["red"]), (620, PAL["gold"]), (1500, PAL["teal"]))):
        g.save(); g.tr(x, 260); g.rot(-4 + i * 4)
        g.rrect(-100, -130, 200, 260, 8, "#fbf7f0")
        g.rrect(-80, -110, 160, 150, 6, col)
        text(g, ["FIGHT", "TRAIN", "WIN"][i], 0, 105, 54, fill="#2b2233", outline=None, shadow=False)
        g.restore()
    for k in range(3):
        g.line(0, 600 + k * 45, W, 600 + k * 45, color=PAL["red"], w=10, a=0.9)

# ================================================================== PROLOGUE
@scene
def hook_prison(g, x):
    cam(g, x, 1.0, 1.12, fy=480)
    cell_bg(g, x.t)
    k_fam = pop(x.t, x.cue("family"), 0.4)
    if k_fam > 0:
        g.save(); g.tr(560, 330); g.sc(k_fam); g.rot(-5)
        g.rrect(-110, -90, 220, 180, 8, "#fbf7f0")
        g.rrect(-90, -70, 180, 130, 6, "#f6c27a")
        for i, (xx, sz, col) in enumerate(((-48, 30, PAL["skin_mom"]), (0, 22, PAL["skin_lucia"]), (48, 32, PAL["skin_dad"]))):
            g.rrect(xx - sz * 0.8, 20, sz * 1.6, 60, 10, ["#c46aa0", "#e2483d", "#e2483d"][i], w=g.lw * 0.5)
            g.circle(xx, 10, sz, col, w=g.lw * 0.6)
            q = skia.Path(); q.moveTo(xx - sz, 6); q.cubicTo(xx - sz, 10 - sz * 1.4, xx + sz, 10 - sz * 1.4, xx + sz, 6); q.close()
            g.shape(q, PAL["hair_dark"], w=g.lw * 0.5)
            for e in (-1, 1):
                g.fillp(G.circle_p(xx + e * sz * 0.35, 14, sz * 0.12), "#2a1d22")
            g.line(xx - sz * 0.2, 26, xx + sz * 0.2, 26, w=g.lw * 0.4)
        g.restore()
        heart(g, 680, 230, 30 * k_fam)
    CH["lucia_prison"].draw(g, 960, 980, 640, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"},
                            anger=x.t > 1.0, look=-0.1)
    # bars slide shut in front
    k = ease_out(x.t / 0.7)
    g.save(); g.tr(lerp(W, 0, k), 0)
    bars(g, 380, 60, 1160, 1060, 9, "#4d5260", x.t, wdt=26)
    g.restore()
    vignette(g, 0.45)

@scene
def hook_gate(g, x):
    cam(g, x, 1.0, 1.05)
    sky(g, "#7cc6f0", "#d6eefa", h=700)
    sun(g, 1650, 160, 70, "#fff1b8")
    g.rect_fill(0, 640, W, 440, "#c9b98a")
    g.rect_fill(0, 640, W, 30, "#a99a6e")
    # fence + gate (gate slides open)
    for i in range(0, W, 70):
        g.line(i, 300, i, 650, color="#7a8494", w=8)
    g.line(0, 310, W, 310, color="#7a8494", w=10); g.line(0, 640, W, 640, color="#7a8494", w=10)
    for i in range(0, W, 46):
        g.circle(i, 290, 14, None, outline="#5e6270", w=4)
    gk = ease_io(x.t / 1.2)
    g.rect_fill(560 + gk * 380, 300, 380, 345, "#5e6270", 0.25)
    for i in range(6):
        g.line(560 + gk * 380 + i * 70, 300, 560 + gk * 380 + i * 70, 645, color="#4d5260", w=12)
    car(g, 1530, 1000, 1.2, "#d63d3d", x.t)
    CH["jason"].draw(g, 1180, 1000, 560, x.t, pose="wave_r" if x.t > x.cue("car") else "hips",
                     face={"mouth": "smile", "brows": "raised"}, look=-0.5)
    wk = clamp((x.t - 0.6) / 2.5)
    CH["lucia"].draw(g, lerp(700, 820, wk), lerp(900, 1000, wk), lerp(470, 560, wk), x.t, pose="relaxed",
                     face={"brows": "skeptical", "mouth": "flat"}, look=0.5, walk=1.0 if wk < 1 else 0)
    clover(g, 520, 260, 50 * pop(x.t, 0.8), x.t)

@scene
def hook_chase(g, x):
    cam(g, x, 1.05, 1.0, shake=[(0, x.d, 3)])
    sky(g, "#141230", "#3b2a6a", h=700)
    stars(g, x.t, 50, h=380)
    g.save(); g.tr(-(x.t * 120) % 400, 0)
    skyline_vice(g, 640, x.t, sunset=False, scale=0.9)
    g.restore()
    g.rect_fill(0, 640, W, 440, "#2b2a3a")
    for i in range(-1, 12):
        xx = (i * 260 - x.t * 1400) % (W + 260) - 130
        g.rrect(xx, 850, 130, 16, 6, "#ffd166", outline=None)
    speed_lines(g, x.t, a=0.25, y0=640, y1=1060)
    police_car(g, 420, 1010, 0.85, x.t, driving=True)
    car(g, 1250, 1010, 0.95, "#d63d3d", x.t, driving=True, lights=True)
    helicopter(g, 1500 - x.t * 40, 170, 0.8, x.t)
    k = pop(x.t, x.cue("state"), 0.5)
    label_tag(g, "LEONIDA", 960, 220, k, fill="#ffd166", size=80)

@scene
def baby(g, x):
    cam(g, x, 1.0, 1.1, fx=840, fy=560)
    apartment_lc(g, x.t)
    crib(g, 840, 900, 520, 260)
    gum = x.t > x.cue("teeth")
    CH["lucia_baby"].draw(g, 840, 860, 520, x.t, face={"brows": "angry", "mouth": "gummy" if gum else "frown"},
                          anger=True)
    crib_front(g, 840, 960, 560, 190)
    for i, (name, fn, xx) in enumerate((("record", icon_record, 330), ("gun", icon_gun, 690), ("teeth", icon_tooth, 1050))):
        k = pop(x.t, x.cue(name), 0.4)
        if k > 0:
            badge_icon(g, xx, 230 if i != 1 else 200, 95, k, lambda g, f=fn: f(g, 0, 0, 0.9))
            no_sign(g, xx, 230 if i != 1 else 200, 92, pop(x.t, x.cue(name) + 0.25, 0.3))

@scene
def mom(g, x):
    cam(g, x, 1.0, 1.08, fx=700, fy=500)
    apartment_lc(g, x.t, night=False)
    CH["mom"].draw(g, 700, 1000, 620, x.t, pose="hold_front", face={"mouth": "smile", "eyes": "open"},
                   look=0.15)
    CH["lucia_baby"].draw(g, 700, 790, 230, x.t, face={"brows": "angry", "mouth": "frown"})
    k = ease_back(clamp((x.t - x.cue("dream")) / 0.6))
    dream_bubble(g, 1220, 360, 600, 420, k, lambda g, cx, cy, w, h: good_life_content(g, cx, cy, w, h, x.t),
                 x.t, tail=(-330, 260))
    remember_tag(g, 1240, 640, pop(x.t, x.cue("remember")), "REMEMBER THIS", x.t)

@scene
def dad_gloves(g, x):
    cam(g, x, 1.0, 1.06)
    gym_bg(g, x.t)
    k = x.t > x.cue("gloves")
    CH["dad"].draw(g, 1240, 1010, 700, x.t, pose="hold_front" if not k else "guard",
                   face={"mouth": "grin" if k else "smile", "brows": "raised" if k else "neutral"}, look=-0.45,
                   held="gloves" if k else None)
    CH["lucia_toddler"].draw(g, 700, 1010, 470, x.t, pose="guard" if k else "idle",
                             face={"brows": "angry" if k else "neutral", "mouth": "frown" if k else "o"},
                             held="gloves" if k else None, look=0.4, anger=k)
    if k: sparkles(g, 700, 760, x.t, 160, seed=4)

@scene
def guard(g, x):
    cam(g, x, 1.0, 1.06, fy=600)
    gym_bg(g, x.t)
    hit = x.t > x.cue("w3")
    CH["lucia_toddler"].draw(g, 960, 1230, 880, x.t, pose="punch_r" if (hit and x.t < x.cue("w3") + 0.6) else "guard",
                             face={"brows": "angry", "mouth": "frown"}, held="gloves", anger=True)
    pop_text(g, "HANDS UP", 400, 330, 100, pop(x.t, x.cue("w1")), fill="#ffd166", rot=-6)
    pop_text(g, "CHIN DOWN", 1500, 330, 100, pop(x.t, x.cue("w2")), fill="#ffd166", rot=5)
    pop_text(g, "HIT BACK!", 420, 640, 120, pop(x.t, x.cue("w3")), fill=PAL["red"], rot=-4)
    remember_tag(g, 1490, 640, pop(x.t, x.cue("remember")), "REMEMBER THIS", x.t)

@scene
def school(g, x):
    cam(g, x, 1.0, 1.06)
    sky(g, "#8fd0f0", "#d9eef9", h=560)
    g.rrect(-20, 230, W + 40, 360, 0, "#e8b07a")
    for i in range(6):
        window(g, 80 + i * 320, 300, 200, 150, view_prison, x.t)
    text(g, "LIBERTY ELEMENTARY", 960, 230, 64, fill="#fbf7f0")
    g.rect_fill(0, 590, W, 490, "#9aa0ad")
    for i in range(0, W, 120):
        g.line(i, 590, i - 40, H, color="#8a909c", w=3)
    tc, oc = x.cue("try"), x.cue("once")
    beaten = x.t > oc + 0.35
    if x.t > tc - 0.2:
        bx = lerp(1900, 1300, ease_out((x.t - tc + 0.2) / 0.6))
        if beaten:
            bx = 1300 + (x.t - oc - 0.35) * 420
        CH["bully"].draw(g, bx, 1030, 640, x.t, pose="hips" if not beaten else "facepalm",
                         face={"brows": "angry" if not beaten else "sad", "mouth": "grin" if not beaten else "frown"},
                         look=-0.5, flip=beaten, walk=1.0 if beaten else 0, sweat=beaten)
    CH["lucia_kid"].draw(g, 760, 1030, 560, x.t, pose="cross" if not (oc <= x.t < oc + 0.6) else "punch_r",
                         face={"brows": "determined", "mouth": "smirk" if beaten else "flat"}, look=0.3)
    pow_burst(g, 1040, 520, 150, pop(x.t, oc) * (1 - clamp((x.t - oc - 0.6) / 0.3)), "POW!")

@scene
def gym(g, x):
    cam(g, x, 1.0, 1.08, shake=[(x.cue("back"), 0.35, 10)])
    gym_bg(g, x.t)
    hit_t = x.cue("back")
    ph = (x.t * 2.2) % 1
    punch = ph < 0.35 or (hit_t <= x.t < hit_t + 0.5)
    ang = math.sin(x.t * 2.2 * 2 * math.pi) * 6
    if x.t > hit_t:
        ang = 22 * math.exp(-(x.t - hit_t) * 1.5) * math.cos((x.t - hit_t) * 6)
    punching_bag(g, 1300, 420, ang)
    CH["lucia_preteen"].draw(g, 960, 1020, 600, x.t, pose="punch_r" if punch else "guard",
                             face={"brows": "angry", "mouth": "frown"}, held="gloves", look=0.6)
    pow_burst(g, 1260, 360, 150, pop(x.t, hit_t) * (1 - clamp((x.t - hit_t - 0.7) / 0.3)), "WHAM!")

# ================================================================== I · THE GOOD LIFE
@scene
def move_map(g, x):
    cam(g, x, 1.0, 1.12, fx=900, fy=560, dy=-60)
    k = clamp(lerp(0.0, 1.0, (x.t - 0.4) / max(0.5, x.cue("leonida") - 0.2)))
    leonida_map(g, ease_io(k), x.t)
    label_tag(g, "WAY SOUTH", 1380, 520, pop(x.t, x.cue("south")), fill="#ffd166", size=60)

@scene
def vice_skyline(g, x):
    cam(g, x, 1.0, 1.06, fx=960, fy=500)
    sky(g, "#ff7b6b", "#ffd6a0", mid="#ffa36c", h=720)
    sun(g, 960, 520, 230, "#fff1b8", bg="#ffb37a")
    ocean(g, 640, 160, "#ff9a8b", "#c65a8a", x.t)
    skyline_vice(g, 660, x.t, scale=1.0)
    palm(g, 120, 900, 1.3, x.t); palm(g, 1800, 900, 1.2, x.t, flip=True)
    g.rect_fill(0, 790, W, 300, "#f3d9a0"); g.line(0, 790, W, 790, w=g.lw)
    # pool + gator
    g.rrect(1240, 860, 560, 170, 30, "#5fd3e8")
    gk = pop(x.t, x.cue("gator"), 0.5)
    if gk > 0:
        g.c.save(); g.c.clipPath(G.rrect_p(1240, 700, 560, 330, 30), doAntiAlias=True)
        alligator(g, 1520, 960 - 60 * gk, 1.2, x.t, mouth=0.4 + 0.3 * math.sin(x.t * 3), sunglasses=True, flip=True)
        g.c.restore()
    g.rrect(1240, 860, 560, 170, 30, None)
    fin = x.t > x.cue("finally")
    CH["mom"].draw(g, 560, 1040, 560, x.t, pose="relaxed" if not fin else "hands_up",
                   face={"mouth": "grin" if fin else "smile", "eyes": "happy" if fin else "open"}, look=0.2)
    CH["lucia_teen"].draw(g, 860, 1040, 520, x.t, pose="hips", face={"mouth": "smile", "brows": "neutral"}, look=-0.2)
    fk = pop(x.t, x.cue("film"), 0.4)
    if fk > 0:
        g.save(); g.tr(260, 470); g.sc(fk); g.rot(-8)
        g.circle(40, 210, 34, PAL["skin_light"])
        phone_frame(g, -60, -110, 170, 300, live=False)
        g.rrect(-60, -110, 170, 300, 18, "#ff8a5c", outline=None)
        g.save(); g.sc(0.25); palm(g, 100, 600, 1.0, x.t, sil="#5b3b7a"); g.restore()
        g.circle(-30, -80, 10, "#ff3b5c", outline=None, a=0.5 + 0.5 * math.sin(x.t * 6))
        text(g, "REC", 10, -70, 28, fill="#ffffff", outline=None, shadow=False, name="ui")
        g.restore()
    if fin: sparkles(g, 600, 600, x.t, 220, 8, seed=6)

@scene
def bills(g, x):
    cam(g, x, 1.0, 1.08, fy=600)
    wall(g, "#b9a37f", 800, stripes=(50, "#a48f6c"))
    floor(g, 800, "#6e5a44")
    tr_t = x.cue("trouble")
    def view(g2, w, h, t):
        g2.vgrad(0, 0, w, h, [(0, "#1d1b3a"), (1, "#3a2a5a")])
        g2.save(); g2.sc(0.55); skyline_lc(g2, h / 0.55 + 10, t, True, width=w / 0.55); g2.restore()
        if t > tr_t:
            blink = (t * 3) % 1 < 0.5
            g2.glow(w * (0.25 if blink else 0.75), h * 0.8, w * 0.7, "#ff3b3b" if blink else "#3b6bff", 0.75)
    window(g, 1350, 170, 360, 280, view, x.t)
    table(g, 760, 760, 760, legs=230)
    mk = pop(x.t, x.cue("money"), 0.4)
    rnd = random.Random(4)
    for i in range(7):
        if mk <= 0: break
        g.save(); g.tr(560 + i * 60, 720 - (i % 3) * 8); g.rot(rnd.uniform(-14, 14)); g.sc(mk)
        g.rrect(-60, -40, 120, 80, 4, "#fbf7f0", w=g.lw * 0.7)
        text(g, "DUE", 0, 12, 34, fill=PAL["red"], outline=None, shadow=False)
        g.restore()
    CH["mom"].draw(g, 600, 900, 600, x.t, pose="chin", face={"brows": "sad", "mouth": "frown"},
                   look=0.2, legs_hidden=True)
    g.rrect(400, 770, 720, 240, 8, "#8f6038")
    g.rrect(380, 734, 760, 40, 8, "#a8744a")
    for i in range(4 if mk > 0 else 0):
        g.save(); g.tr(520 + i * 110, 730); g.rot(-8 + i * 6); g.sc(mk)
        g.rrect(-55, -36, 110, 72, 4, "#fbf7f0", w=g.lw * 0.7)
        text(g, "$0" if i == 1 else "DUE", 0, 12, 32, fill=PAL["red"], outline=None, shadow=False)
        g.restore()
    girl = x.t > x.cue("girl")
    CH["lucia_teen"].draw(g, 1380, 1030, 580, x.t, pose="cross", face={"brows": "angry" if girl else "sad", "mouth": "frown"},
                          look=-0.4, anger=girl)

# ================================================================== II · FIGHTING FOR FAMILY
@scene
def fight_night(g, x):
    hit = x.cue("w3")
    cam(g, x, 1.0, 1.1, fx=800, shake=[(hit, 0.4, 14)])
    sky(g, "#120f26", "#2b1d4a", h=H)
    for row in range(0, 900, 60):
        off = 0 if (row // 60) % 2 == 0 else 70
        for col in range(-off, W, 140):
            g.rrect(col + 3, row + 3, 134, 54, 5, "#3a2a4a", outline="#24182e", w=3)
    g.glow(500, 120, 500, "#ffcf7a", 0.35)
    g.rrect(470, 80, 60, 40, 8, "#fff1b8")
    floor(g, 900, "#22202e")
    # shadowy figures (darkened with a src-atop layer)
    back = x.t > hit
    g.c.saveLayer(None, None)
    for i, (fx_, s_) in enumerate(((1350, 600), (1600, 640))):
        off = (x.t - hit) * 700 if back else 0
        CH["grifter2" if i else "grifter1"].draw(g, fx_ + off * (1 + i * 0.3), 1000, s_, x.t, pose="hips",
                                                  face={"brows": "angry", "mouth": "grin"}, look=-0.6,
                                                  tilt=20 if back else 0)
    dk = skia.Paint(Color=C("#120a1a", 0.6)); dk.setBlendMode(skia.BlendMode.kSrcATop)
    g.c.drawRect(skia.Rect.MakeWH(W, H), dk)
    g.c.restore()
    CH["lucia_night"].draw(g, 760, 1000, 640, x.t, pose="punch_r" if (hit <= x.t < hit + 0.6) else "guard",
                           face={"brows": "angry", "mouth": "frown"}, look=0.6, anger=x.t > x.cue("w1"))
    pop_text(g, "HANDS UP", 380, 260, 96, pop(x.t, x.cue("w1")), fill="#ffd166", rot=-6)
    pop_text(g, "CHIN DOWN", 960, 170, 96, pop(x.t, x.cue("w2")), fill="#ffd166", rot=4)
    pop_text(g, "HIT BACK!", 1420, 300, 120, pop(x.t, hit), fill=PAL["red"], rot=-4)
    pow_burst(g, 1150, 540, 160, pop(x.t, hit) * (1 - clamp((x.t - hit - 0.7) / 0.3)), "POW!")
    vignette(g, 0.5)

@scene
def arrest(g, x):
    cam(g, x, 1.0, 1.08)
    sky(g, "#120f26", "#2b1d4a", h=H)
    skyline_vice(g, 640, x.t, sunset=False)
    g.rect_fill(0, 640, W, 440, "#2b2a3a")
    blink = (x.t * 3) % 1 < 0.5
    g.rect_fill(0, 0, W, H, "#ff3b3b" if blink else "#3b6bff", 0.18)
    police_car(g, 1300, 960, 1.0, x.t)
    CH["guard"].draw(g, 1060, 1000, 560, x.t, pose="hips", face={"brows": "angry", "mouth": "flat"}, look=-0.5)
    CH["lucia_night"].draw(g, 700, 1000, 600, x.t, pose="behind", face={"brows": "angry", "mouth": "frown"},
                           look=-0.2, anger=True)
    stamp(g, "LEONIDA PENITENTIARY", 960, 320, clamp((x.t - x.cue("sign")) / 0.25), size=86)

# ================================================================== III · BAD LUCK
@scene
def cell(g, x):
    cam(g, x, 1.0, 1.1, fy=520)
    if x.t < x.cue("number"):
        cell_bg(g, x.t)
        grey = clamp((x.t - x.cue("walls")) / 0.4)
        g.rect_fill(0, 0, W, 860, "#7a7f8c", 0.25 * grey)
        CH["lucia_prison"].draw(g, 960, 1000, 620, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"})
    else:
        mugshot_wall(g)
        k = pop(x.t, x.cue("number"), 0.35)
        CH["lucia_prison"].draw(g, 960, 1120, 760, x.t, pose="hold_front", face={"brows": "angry", "mouth": "frown"})
        g.save(); g.tr(960, 880); g.sc(k)
        g.rrect(-230, -80, 460, 160, 10, "#2b2233")
        text(g, "LP-0419", 0, 26, 92, fill="#fbf7f0", outline=None, shadow=False)
        g.restore()
        g.glow(960, 300, 600, "#ffffff", 0.35 * (1 - clamp((x.t - x.cue("number")) / 0.3)))

@scene
def interview(g, x):
    cam(g, x, 1.0, 1.06)
    wall(g, "#8f96a3", 760)
    floor(g, 760, "#5e6270")
    g.glow(960, 80, 700, "#fff6d8", 0.35)
    g.line(960, 0, 960, 80, w=g.lw)
    g.poly([(880, 80), (1040, 80), (1000, 40), (920, 40)], "#4d5260")
    shrug = x.t > x.cue("shrug")
    CH["lucia_prison"].draw(g, 560, 1050, 640, x.t, pose="shrug" if shrug and x.t < x.cue("remember") else "cross",
                            face={"brows": "skeptical" if shrug else "angry", "mouth": "smirk" if shrug else "frown"},
                            look=0.5, talk=x.talking("lucia"), legs_hidden=True)
    CH["officer"].draw(g, 1360, 1050, 640, x.t, pose="hold_front", face={"brows": "neutral", "mouth": "flat"},
                       look=-0.5, talk=x.talking("officer"), legs_hidden=True)
    table(g, 960, 860, 1300, legs=300)
    g.rrect(360, 856, 1200, 230, 6, "#4d5260")
    g.save(); g.tr(1220, 820); g.rot(4)
    g.rrect(-90, -10, 180, 26, 4, "#e9c58a", w=g.lw * 0.7)
    g.restore()
    remember_tag(g, 600, 300, pop(x.t, x.cue("remember")), "REMEMBER THIS", x.t)

@scene
def workout(g, x):
    cam(g, x, 1.0, 1.06, fy=560)
    cell_bg(g, x.t)
    marks = int(clamp(x.t / x.d) * 24) + 3
    for i in range(marks):
        gx = 220 + (i // 5) * 70 + (i % 5) * 12
        if i % 5 == 4:
            g.line(gx - 52, 330, gx + 4, 290, color="#2b2233", w=5)
        else:
            g.line(gx, 280, gx, 340, color="#2b2233", w=5)
    bunk(g, 1250, 860, 560)
    th, sm = x.cue("think"), x.cue("smart")
    if x.t < th:
        ph = (x.t * 2.4) % 1
        CH["lucia_prison"].draw(g, 880, 1000, 620, x.t, pose="punch_r" if ph < 0.4 else "guard",
                                face={"brows": "angry", "mouth": "frown"}, look=0.4)
    else:
        CH["lucia_prison"].draw(g, 1250, 812, 600, x.t, pose="chin", face={"brows": "determined", "mouth": "flat"},
                                look=-0.3, sit=True)
        lightbulb(g, 1080, 380, pop(x.t, th + 0.3))
        chess_knight(g, 640, 560, 2.0, pop(x.t, sm))
        pop_text(g, "SMART MOVES ONLY", 640, 860, 84, pop(x.t, sm + 0.2), fill="#ffd166", rot=-4)

@scene
def photo(g, x):
    cam(g, x, 1.0, 1.1, fx=900, fy=560)
    cell_bg(g, x.t, night=True)
    g.glow(1490, 250, 600, "#cfe0ff", 0.2)
    bunk(g, 900, 860, 620, col="#4d5260")
    CH["lucia_prison"].draw(g, 900, 812, 620, x.t, pose="hold_r", held="photo",
                            face={"brows": "sad", "mouth": "frown", "gaze": 0.6}, look=0.2, sit=True)
    dk = x.cue("dream"); fk = x.cue("further")
    k = ease_back(clamp((x.t - dk) / 0.6))
    if x.t > fk:
        k *= lerp(1.0, 0.45, ease_io((x.t - fk) / 1.2))
    g.save()
    off = ease_io((x.t - fk) / 1.4) * 200 if x.t > fk else 0
    g.tr(off, -off * 0.6)
    g.alpha(1 - 0.6 * clamp((x.t - fk) / 1.4))
    dream_bubble(g, 1350, 420, 520, 360, k, lambda g, cx, cy, w, h: good_life_content(g, cx, cy, w, h, x.t),
                 x.t, tail=(-300, 200))
    g.restore(); g.restore()
    vignette(g, 0.55)

# ================================================================== IV · SHEER LUCK
def gate_scene(g, t, open_k):
    sky(g, "#7cc6f0", "#d6eefa", h=700)
    sun(g, 1650, 150, 70, "#fff1b8")
    g.rect_fill(0, 640, W, 440, "#c9b98a")
    g.rrect(1480, 300, 330, 360, 10, "#cfd4dc")
    g.rrect(1520, 360, 250, 120, 8, "#bfe6ff")
    text(g, "LEONIDA PENITENTIARY", 1645, 335, 30, fill="#2b2233", outline=None, shadow=False)
    for i in range(0, 1480, 70):
        g.line(i, 300, i, 650, color="#7a8494", w=8)
    g.line(0, 310, 1480, 310, color="#7a8494", w=10); g.line(0, 640, 1480, 640, color="#7a8494", w=10)
    for i in range(0, 1480, 46):
        g.circle(i, 290, 14, None, outline="#5e6270", w=4)
    gx = 520 + ease_io(open_k) * 420
    g.rect_fill(gx, 300, 420, 345, "#5e6270", 0.25)
    for i in range(7):
        g.line(gx + i * 70, 300, gx + i * 70, 645, color="#4d5260", w=12)

@scene
def gate_open(g, x):
    cam(g, x, 1.0, 1.08, fx=760)
    ok = clamp((x.t - x.cue("out") + 0.3) / 1.2)
    gate_scene(g, x.t, ok)
    if ok > 0.3:
        light_rays(g, 730, 470, x.t, a=0.12 * ok)
    wk = clamp((x.t - x.cue("out")) / 2.0)
    CH["lucia"].draw(g, lerp(730, 900, wk), lerp(820, 1000, wk), lerp(420, 600, wk), x.t, pose="relaxed",
                     face={"brows": "raised", "mouth": "smile" if ok > 0.5 else "flat"}, walk=1.0 if 0 < wk < 1 else 0)
    ck = pop(x.t, x.cue("luck"), 0.5)
    clover(g, 1250, 360, 70 * ck, x.t)
    if ck > 0: sparkles(g, 1250, 330, x.t, 160, 7)
    pop_text(g, "SHEER LUCK", 1300, 640, 90, pop(x.t, x.cue("luck") + 0.6), fill="#7be37b", rot=-5)

@scene
def jason_gate(g, x):
    cam(g, x, 1.0, 1.06, fx=1000)
    gate_scene(g, x.t, 0.0)
    car(g, 460, 1000, 1.2, "#d63d3d", x.t)
    gk = x.t > x.cue("guard")
    g.save(); g.c.clipPath(G.rrect_p(1520, 360, 250, 120, 8), doAntiAlias=True)
    CH["guard"].draw(g, 1645, 760, 420, x.t, pose="idle", face={"brows": "skeptical" if gk else "neutral", "mouth": "flat"},
                     look=-0.6)
    g.restore()
    CH["jason"].draw(g, 1050, 1000, 600, x.t, pose="hips",
                     face={"brows": "raised", "mouth": "smile"}, look=0.4, talk=x.talking("jason"))
    nk = pop(x.t, x.span_start("jason", 1))
    label_tag(g, "JASON DUVAL", 1050, 260, nk, fill="#ffd166", size=64)

@scene
def luck_name(g, x):
    cam(g, x, 1.0, 1.04)
    sh, nm = x.cue("sheer"), x.cue("name")
    split = ease_io((x.t - sh + 0.2) / 0.5)
    # left: bad luck (cell)
    g.save(); g.c.clipRect(skia.Rect.MakeXYWH(0, 0, W / 2 + (1 - split) * W / 2, H))
    g.vgrad(0, 0, W, H, [(0, "#3a3d50"), (1, "#22232e")])
    g.save(); g.tr(lerp(490, 0, split), 0)
    CH["lucia_prison"].draw(g, 470, 980, 520, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"})
    bars(g, 120, 160, 700, 760, 6, "#5e6270", x.t, wdt=20)
    text(g, "BAD LUCK", 470, 140, 96, fill="#9aa0ad")
    g.restore()
    g.restore()
    if split > 0:
        g.save(); g.c.clipRect(skia.Rect.MakeXYWH(W - split * W / 2, 0, W / 2 + 4, H))
        g.vgrad(0, 0, W, H, [(0, "#7cc6f0"), (1, "#fff1c8")])
        light_rays(g, 1440, 600, x.t, a=0.15)
        clover(g, 1700, 330, 60, x.t)
        CH["lucia"].draw(g, 1440, 1000, 520, x.t, pose="hands_up", face={"mouth": "grin", "eyes": "happy"})
        text(g, "SHEER LUCK", 1440, 140, 96, fill="#7be37b")
        g.restore()
        g.line(W - split * W / 2, 0, W - split * W / 2, H, w=12)
    nk = ease_back(clamp((x.t - nm) / 0.5))
    if nk > 0:
        g.save(); g.alpha(clamp((x.t - nm) / 0.25))
        g.vgrad(0, 0, W, H, [(0, "#ffb37a"), (1, "#ff7b9c")])
        light_rays(g, 960, 560, x.t, a=0.18)
        CH["jason"].draw(g, 960, 1060, 700 * nk, x.t, pose="wave_r", face={"mouth": "grin", "brows": "raised"})
        label_tag(g, "LUCK HAS A NAME", 960, 170, nk, fill="#ffd166", size=72)
        g.restore(); g.restore()

@scene
def cta(g, x):
    cam(g, x, 1.0, 1.03)
    g.vgrad(0, 0, W, H, [(0, "#2b2456"), (1, "#5b3b7a")])
    stars(g, x.t, 40, h=H)
    CH["lucia"].draw(g, 470, 1060, 720, x.t, pose="point_r" if x.t > x.cue("who") else "wave_r",
                     face={"mouth": "smile", "brows": "raised"}, look=0.4)
    # comment panel
    g.rrect(860, 180, 920, 700, 30, "#fbf7f0")
    text(g, "WHO'S BORN NEXT?", 1320, 270, 66, fill=PAL["red"], outline=None, shadow=False)
    names = [("Jason", x.cue("jason")), ("Cal Hampton", x.cue("drop") + 0.2), ("Boobie Ike", x.cue("drop") + 0.6),
             ("Brian Heder", x.cue("drop") + 1.0)]
    for i, (nm, t0) in enumerate(names):
        k = pop(x.t, t0, 0.35)
        if k <= 0: continue
        g.save(); g.tr(1320, 380 + i * 120); g.sc(k)
        g.rrect(-400, -46, 800, 92, 20, "#ece4f5", w=g.lw * 0.7)
        g.circle(-340, 0, 30, ["#ff5fa2", "#2fb3a6", "#ffd166", "#7b4bc4"][i], w=g.lw * 0.6)
        text(g, nm + ("?" if i == 0 else "!"), -290, 16, 46, fill="#2b2233", outline=None, align="left", shadow=False, name="ui")
        heart(g, 340, 0, 18, a=1.0)
        g.restore()
    lk = pop(x.t, x.cue("liked"), 0.4)
    if lk > 0:
        g.save(); g.tr(1320, 940); g.sc(lk * (1 + 0.06 * math.sin(x.t * 8)))
        g.rrect(-190, -55, 380, 110, 55, PAL["red"])
        text(g, "LIKE + COMMENT", 0, 18, 46, fill="#ffffff", outline=None, shadow=False)
        g.restore()

# ================================================================== V · JASON
@scene
def grifters(g, x):
    cam(g, x, 1.0, 1.07, fy=520)
    wall(g, "#4a3a3a", 820, stripes=(70, "#3e3030"))
    floor(g, 820, "#3a2a24")
    g.glow(960, 300, 700, "#ffcf7a", 0.4)
    g.line(960, 0, 960, 230, w=g.lw); g.poly([(900, 230), (1020, 230), (1060, 290), (860, 290)], "#2fb3a6")
    CH["grifter1"].draw(g, 520, 1000, 640, x.t, pose="hold_front", face={"mouth": "smirk"}, look=0.4, legs_hidden=True)
    CH["grifter2"].draw(g, 1400, 1000, 640, x.t, pose="hold_r", held="cards", face={"mouth": "grin"}, look=-0.4,
                        legs_hidden=True)
    lie = x.t > x.cue("lie")
    CH["jason_kid"].draw(g, 960, 900, 520, x.t, pose="hold_r", held="cards",
                         face={"mouth": "smirk" if lie else "o", "brows": "skeptical" if lie else "raised"}, look=0.1,
                         legs_hidden=True)
    g.rrect(320, 840, 1280, 260, 10, "#245c3c")
    g.rrect(300, 800, 1320, 60, 14, "#2f7a4f")
    for i in range(5):
        g.save(); g.tr(800 + i * 70, 800); g.rot(-10 + i * 5)
        g.rrect(-28, -40, 56, 80, 6, "#fbf7f0", w=g.lw * 0.6)
        g.restore()
    for i in range(3):
        g.rrect(1180 + i * 20, 770 - i * 14, 120, 26, 4, "#7bbf6a", w=g.lw * 0.6)
    if lie:
        g.save(); g.tr(960, 360); g.sc(pop(x.t, x.cue("lie")))
        g.rrect(-190, -60, 380, 110, 26, "#fbf7f0")
        g.poly([(-30, 46), (10, 46), (-10, 90)], "#fbf7f0")
        text(g, "Trust me ;)", 0, 16, 54, fill="#2b2233", outline=None, shadow=False)
        g.restore()
    bk = pop(x.t, x.cue("bike"))
    if bk > 0:
        g.save(); g.tr(1620, 420); g.sc(bk)
        g.circle(0, 0, 110, "#fbf7f0", w=g.lw)
        for bx in (-45, 45):
            g.circle(bx, 25, 32, None, w=g.lw * 1.1)
        g.polyline([(-45, 25), (-10, -25), (35, -25), (45, 25)], w=g.lw * 1.1)
        g.polyline([(-10, -25), (0, 25), (-45, 25)], w=g.lw * 1.1)
        g.restore()
        pop_text(g, "LATER", 1620, 570, 54, pop(x.t, x.cue("bike") + 0.2), fill="#ffd166", rot=6)

@scene
def army(g, x):
    cam(g, x, 1.0, 1.08)
    sky(g, "#b9d7e8", "#efe2c2", h=700)
    for i, xx in enumerate((300, 700, 1500)):
        g.poly([(xx - 200, 700), (xx, 470), (xx + 200, 700)], PAL["olive"] if i != 1 else PAL["olive_sh"])
    g.rect_fill(0, 690, W, 400, "#c8b27a"); g.line(0, 690, W, 690, w=g.lw)
    wk = x.t > x.cue("work")
    salute = ((-3, 21), (7, -26))
    CH["jason_army"].draw(g, 960, 1010, 640, x.t, pose="idle", hand_override=salute if not wk else None,
                          face={"brows": "determined" if not wk else "sad", "mouth": "flat" if not wk else "frown"},
                          sweat=wk)
    cloud(g, 960, 220, 1.4, rain=True, t=x.t, k=pop(x.t, x.cue("work")))

@scene
def keys_roof(g, x):
    cam(g, x, 1.0, 1.06, fx=900)
    sky(g, "#6fc3f0", "#d6f0fa", h=760)
    sun(g, 1700, 140, 70, "#fff1b8")
    ocean(g, 640, 440, "#5fd3e8", "#2f8fbf", x.t, sparkle="#ffffff")
    for i in range(4):
        g.ellipse(200 + i * 420, 700, 160, 22, "#f3d9a0", w=g.lw * 0.6)
    # stilt house
    for sx in (520, 640, 1080, 1200):
        g.rrect(sx, 760, 26, 300, 6, "#8a5a3a")
    g.rrect(460, 500, 820, 280, 10, "#f5e6c8")
    g.rrect(560, 560, 160, 130, 8, "#bfe6ff"); g.rrect(1000, 560, 160, 130, 8, "#bfe6ff")
    g.rrect(790, 580, 120, 200, 8, "#2fb3a6")
    g.rrect(380, 900, 1000, 40, 8, "#a8744a")
    lk = x.t > x.cue("leaks")
    hammer_ph = (x.t * 3) % 1
    CH["jason"].draw(g, 760, 500, 470, x.t, pose="hammer" if (lk and hammer_ph < 0.5) else "relaxed",
                     held="hammer", face={"brows": "sad" if lk else "neutral", "mouth": "frown" if lk else "flat"},
                     look=0.3, legs_hidden=True)
    g.poly([(420, 510), (870, 330), (1320, 510)], "#5e6b8a")
    if lk:
        for i in range(4):
            ph = (x.t * 1.3 + i * 0.25) % 1.0
            dx_ = 760 + i * 70
            g.fillp(G.ellipse_p(dx_, 520 + ph * 140, 8, 12), "#6fb6ff", 1 - ph)
    bk = x.t > x.cue("brian")
    bx = lerp(2100, 1480, ease_out((x.t - x.cue("brian") + 0.2) / 0.7)) if bk else 2200
    CH["brian"].draw(g, bx, 1030, 560, x.t, pose="hold_r", held="beer", face={"mouth": "grin", "brows": "raised"},
                     look=-0.6)
    if bk: label_tag(g, "BRIAN", bx, 380, pop(x.t, x.cue("brian") + 0.4), fill="#ffd166", size=48)

@scene
def jason_sigh(g, x):
    cam(g, x, 1.05, 1.14, fy=520)
    sky(g, "#ff8a5c", "#ffd6a0", mid="#ffb37a", h=760)
    sun(g, 1400, 640, 200, "#fff1b8", bg="#ffb37a")
    ocean(g, 700, 380, "#ff9a8b", "#c65a8a", x.t)
    g.poly([(-50, 820), (W + 50, 640), (W + 50, H + 10), (-50, H + 10)], "#5e6b8a")
    hk = x.t > x.cue("harder")
    CH["jason"].draw(g, 900, 1100, 900, x.t, pose="chin" if not hk else "facepalm",
                     face={"brows": "sad", "eyes": "half", "mouth": "frown"}, look=0.3, legs_hidden=True, sweat=hk)
    cloud(g, 920, 160, 1.6, rain=True, t=x.t, k=pop(x.t, x.cue("harder")))

# ================================================================== VI · TRUST
def motel_room(g, t, neon_on=True):
    wall(g, "#5b6e8a", 780, stripes=(46, "#52637d"))
    floor(g, 780, "#6a4f5a")
    def view(g2, w, h, tt):
        g2.vgrad(0, 0, w, h, [(0, "#1d1b3a"), (1, "#3a2a5a")])
        on = neon_on and ((tt * 1.3) % 1 > 0.08)
        if on: g2.glow(w * 0.5, h * 0.4, w * 0.6, "#ff5fa2", 0.5)
        text(g2, "MOTEL", w * 0.5, h * 0.5, 84, fill="#ff9ccc" if on else "#5a3a4a",
             outline="#ff5fa2" if on else "#3a2a3a", ow=6, shadow=False)
        g2.save(); g2.sc(0.45); car(g2, w * 0.45 / 0.45, (h + 30) / 0.45, 1.0, "#d63d3d", tt); g2.restore()
    window(g, 1180, 140, 520, 340, view, t, curtains="#c46a6a")

@scene
def motel(g, x):
    cam(g, x, 1.0, 1.06)
    motel_room(g, x.t, neon_on=x.t > x.cue("motel") - 1.5)
    g.rrect(160, 700, 640, 220, 26, "#e9e3d6"); g.rrect(160, 640, 160, 120, 30, "#fbf7f0")
    g.rrect(140, 860, 680, 60, 12, "#8a5a6a")
    CH["lucia"].draw(g, 500, 742, 560, x.t, pose="cross", face={"brows": "skeptical", "mouth": "flat"}, look=0.4,
                     sit=True)
    tk = x.talking("jason")
    CH["jason"].draw(g, 1250, 1010, 620, x.t, pose="point_viewer" if tk else "hips",
                     face={"brows": "raised", "mouth": "smile"}, look=-0.5, talk=tk)
    g.rrect(900, 860, 90, 140, 8, "#8a6a4a")
    label_tag(g, "NOT EXACTLY THE GOOD LIFE", 760, 200, pop(x.t, x.cue("motel") + 0.4), fill="#ffd166", size=46)

@scene
def toast(g, x):
    cam(g, x, 1.08, 1.16, fy=560)
    motel_room(g, x.t)
    gk = x.t > x.cue("glass") - 0.2
    CH["lucia"].draw(g, 700, 1180, 900, x.t, pose="raise_r" if gk else "idle", held="glass" if gk else None,
                     face={"mouth": "smile", "brows": "raised"}, look=0.45, talk=x.talking("lucia"), legs_hidden=True)
    CH["jason"].draw(g, 1240, 1180, 900, x.t, pose="raise_r" if gk else "idle", held="glass" if gk else None,
                     face={"mouth": "grin"}, look=-0.45, flip=True, legs_hidden=True)
    clink = x.span_end("lucia", 0)
    if x.t > clink - 0.3:
        sparkles(g, 960, 330, x.t, 120, 7, seed=9)

@scene
def car_hood(g, x):
    cam(g, x, 1.0, 1.07, fy=540)
    sky(g, "#0f0e26", "#3b2a6a", h=H)
    stars(g, x.t, 90, h=520)
    g.glow(1500, 200, 200, "#fff3c4", 0.3)
    g.circle(1500, 200, 60, "#fff3c4", w=g.lw * 0.6)
    g.save(); g.sc(0.7); g.tr(0, 300)
    skyline_vice(g, 820, x.t, sunset=False)
    g.restore()
    g.rect_fill(0, 870, W, 210, "#1e1b2e")
    car(g, 960, 1075, 1.45, "#d63d3d", x.t)
    lt, jt = x.talking("lucia"), x.talking("jason")
    tk = x.span_start("jason", 0)
    CH["lucia"].draw(g, 800, 905, 520, x.t, pose="relaxed", face={"brows": "determined", "mouth": "flat"},
                     look=0.5 if x.t > tk - 0.3 else 0.2, talk=lt, sit=True)
    CH["jason"].draw(g, 1110, 905, 540, x.t, pose="relaxed", face={"brows": "raised", "mouth": "smile"},
                     look=-0.5, talk=jt, sit=True)
    t2 = x.span_start("lucia", 1)
    k = pop(x.t, t2, 0.5)
    if k > 0:
        heart(g, 970, 300, 60 * k)
        pop_text(g, "TRUST", 970, 180, 110, k, fill="#ffd166")

# ================================================================== VII · VICE CITY
def store_bg(g, t):
    wall(g, "#e6f0e8", 760)
    floor(g, 760, "#c9cfd6")
    for i in range(0, W, 120):
        g.line(i, 760, i, H, color="#b3bac2", w=3)
    for s in range(3):
        y = 230 + s * 170
        g.rrect(60, y, 760, 22, 6, "#9aa0ad")
        rnd = random.Random(s)
        for k in range(10):
            col = rnd.choice(["#e2483d", "#ffd166", "#2fb3a6", "#7b4bc4", "#ff8a5c", "#5fb0d8"])
            hh = rnd.uniform(70, 120)
            g.rrect(80 + k * 72, y - hh, 56, hh, 8, col, w=g.lw * 0.6)
    text(g, "24/7", 1560, 200, 110, fill=PAL["red"])
    g.glow(1560, 180, 300, "#ff3b3b", 0.25)

@scene
def store_masks(g, x):
    ld = x.cue("loud")
    cam(g, x, 1.0, 1.06, shake=[(ld, 0.4, 12)])
    store_bg(g, x.t)
    g.rrect(1180, 640, 640, 320, 12, "#d0563d")
    loud = x.t > ld
    CH["cashier"].draw(g, 1500, 900, 520, x.t, pose="hands_up" if loud else "idle",
                       face={"brows": "raised" if loud else "neutral", "eyes": "wide" if loud else "open",
                             "mouth": "o" if loud else "flat"}, sweat=loud, legs_hidden=True)
    g.rrect(1160, 700, 680, 360, 12, "#e2483d")
    g.rrect(1160, 700, 680, 40, 12, "#b8302a")
    m1, m2 = x.t > x.cue("mask1") - 0.3, x.t > x.cue("mask2") + 0.3
    CH["lucia"].draw(g, 520, 1010, 600, x.t, pose="hold_r" if loud else "relaxed", held="bag" if loud else None,
                     face={"brows": "determined", "mouth": "smirk"}, look=0.4, mask="#ff5fa2" if m1 else False)
    CH["jason"].draw(g, 900, 1010, 620, x.t, pose="hips", face={"brows": "raised", "mouth": "grin"},
                     look=0.3, mask="#2b2b3b" if m2 else False)
    pow_burst(g, 1400, 300, 170, pop(x.t, ld) * (1 - clamp((x.t - ld - 0.9) / 0.3)), "!!!", col="#ffd166")

@scene
def chase(g, x):
    cam(g, x, 1.0, 1.05, shake=[(0, x.d, 3)])
    hook_chase_bg(g, x)
    police_car(g, 380, 1010, 0.85, x.t, driving=True)
    car(g, 1150, 1010, 0.95, "#d63d3d", x.t, driving=True, lights=True)
    hk = ease_out((x.t - x.cue("heli")) / 1.0)
    if x.t > x.cue("heli") - 0.1:
        helicopter(g, lerp(2200, 1450, hk), 180, 0.8, x.t)
    fk = pop(x.t, x.cue("film"), 0.45)
    if fk > 0:
        g.save(); g.tr(1580, 560); g.sc(fk); g.rot(6)
        g.circle(120, 330, 46, PAL["skin_light"])
        phone_frame(g, -170, -330, 360, 640, live=True, t=x.t, overlay=False)
        g.c.save(); g.c.clipPath(G.rrect_p(-170, -330, 360, 640, 20), doAntiAlias=True)
        g.vgrad(-170, -330, 360, 640, [(0, "#1d1b3a"), (1, "#3b2a6a")])
        g.rect_fill(-170, 120, 360, 200, "#2b2a3a")
        g.save(); g.tr(60, 150); g.sc(0.42); car(g, 0, 0, 1.0, "#d63d3d", x.t, driving=True, lights=True); g.restore()
        g.save(); g.tr(-110, 150); g.sc(0.36); police_car(g, 0, 0, 1.0, x.t, driving=True); g.restore()
        g.c.restore()
        phone_frame(g, -170, -330, 360, 640, live=True, t=x.t, body=False)
        hearts(g, 120, 200, x.t, x.cue("film") + 0.3)
        g.restore()

def hook_chase_bg(g, x):
    sky(g, "#141230", "#3b2a6a", h=700)
    stars(g, x.t, 50, h=380)
    g.save(); g.tr(-(x.t * 120) % 400, 0)
    skyline_vice(g, 640, x.t, sunset=False, scale=0.9)
    g.restore()
    g.rect_fill(0, 640, W, 440, "#2b2a3a")
    for i in range(-1, 12):
        xx = (i * 260 - x.t * 1400) % (W + 260) - 130
        g.rrect(xx, 850, 130, 16, 6, "#ffd166", outline=None)
    speed_lines(g, x.t, a=0.25, y0=640, y1=1060)

@scene
def who_you_know(g, x):
    cam(g, x, 1.05, 1.12, fy=500)
    g.vgrad(0, 0, W, H, [(0, "#1d1b3a"), (1, "#5b2a6a")])
    rnd = random.Random(12)
    for i in range(40):
        xx = (rnd.uniform(0, W * 2) - x.t * rnd.uniform(500, 1100)) % (W + 400) - 200
        yy = rnd.uniform(120, 700)
        col = rnd.choice(["#ff5fa2", "#2ff3e0", "#ffd166", "#ff8a5c", "#b38aff"])
        g.glow(xx, yy, rnd.uniform(30, 90), col, 0.55)
    # car door frame
    q = skia.Path(); q.addRect(skia.Rect.MakeWH(W, H))
    q.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(140, 90, 1640, 700), 80, 80))
    q.setFillType(skia.PathFillType.kEvenOdd)
    CH["lucia"].draw(g, 960, 1180, 950, x.t, pose="idle", face={"brows": "determined", "mouth": "smirk"},
                     look=0.15, talk=x.talking("lucia"), legs_hidden=True)
    g.fillp(q, "#a8303a"); g.strokep(q)
    g.rrect(-20, 860, W + 40, 260, 30, "#7a2028")
    label_tag(g, "WHO YOU KNOW + WHAT YOU GOT", 960, 960, pop(x.t, x.span_start("lucia", 0) + 0.8), fill="#ffd166", size=50)

@scene
def bonnie(g, x):
    cam(g, x, 1.0, 1.06)
    ph = x.cue("phones")
    color_k = clamp((x.t - ph) / 0.3)
    def content():
        g.vgrad(0, 0, W, H, [(0, "#ffb37a"), (1, "#ff7b9c")])
        g.rrect(330, 120, 1260, 840, 20, "#fbf7f0")
        g.rrect(370, 160, 1180, 760, 12, "#cfa77a")
        g.c.save(); g.c.clipPath(G.rrect_p(370, 160, 1180, 760, 12), doAntiAlias=True)
        g.vgrad(370, 160, 1180, 760, [(0, "#d9b98a"), (1, "#a8845a")])
        car(g, 960, 1000, 1.1, "#5b4a3a", x.t)
        phones = x.t > ph
        CH["lucia"].draw(g, 760, 980, 600, x.t, pose="phone" if phones else "hips", held="phone" if phones else None,
                         face={"mouth": "smirk", "brows": "determined"}, look=0.3)
        CH["jason"].draw(g, 1160, 980, 620, x.t, pose="phone" if phones else "cross", held="phone" if phones else None,
                         face={"mouth": "grin"}, look=-0.3)
        g.c.restore()
    # sepia -> colour
    if color_k < 1:
        m = [0.393, 0.769, 0.189, 0, 0, 0.349, 0.686, 0.168, 0, 0, 0.272, 0.534, 0.131, 0, 0, 0, 0, 0, 1, 0]
        ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        mm = [lerp(a, b, color_k) for a, b in zip(m, ident)]
        p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix(mm))
        g.c.saveLayer(None, p)
        content()
        g.c.restore()
    else:
        content()
    if x.t < ph:
        text(g, "BONNIE & CLYDE, 1934", 960, 1030, 60, fill="#f6ead2")
    else:
        text(g, "LUCIA & JASON, 2026", 960, 1030, 60, fill="#ffd166")
    gk = pop(x.t, x.cue("gator"), 0.5)
    if gk > 0:
        g.save(); g.tr(1600, 1070); g.sc(gk)
        alligator(g, 0, 0, 1.5, x.t, mouth=0.4 + 0.3 * math.sin(x.t * 4), sunglasses=True)
        g.restore()

# ================================================================== VIII · DAY ONE
@scene
def beach_sunset(g, x):
    cam(g, x, 1.0, 1.08, fy=600)
    sky(g, "#ff7b6b", "#ffd6a0", mid="#ffa36c", h=720)
    sun(g, 960, 560, 260, "#fff1b8", bg="#ffb37a")
    ocean(g, 620, 260, "#ff9a8b", "#c65a8a", x.t)
    palm(g, 160, 920, 1.25, x.t); palm(g, 1780, 940, 1.15, x.t, flip=True)
    g.rect_fill(0, 840, W, 260, "#f3d9a0"); g.line(0, 840, W, 840, w=g.lw)
    nk = x.t > x.cue("you")
    CH["lucia"].draw(g, 800, 925, 560, x.t, pose="relaxed" if not nk else "shrug",
                     face={"brows": "neutral" if not nk else "skeptical", "mouth": "smile" if not nk else "smirk"},
                     look=0.5 if not nk else 0.0, sit=True)
    CH["jason"].draw(g, 1110, 925, 580, x.t, pose="relaxed", face={"mouth": "smile"}, look=-0.4, sit=True)
    bk = pop(x.t, x.cue("best"))
    if bk > 0:
        heart(g, 640, 320, 70 * bk)
        pop_text(g, "BEST", 640, 460, 70, bk, fill="#ffd166")
    wk = pop(x.t, x.cue("worst"))
    cloud(g, 1300, 300, 1.2, rain=True, t=x.t, k=wk)
    if wk > 0: pop_text(g, "WORST", 1300, 460, 70, wk, fill="#9aa0ad")

@scene
def memories(g, x):
    cam(g, x, 1.0, 1.06)
    g.vgrad(0, 0, W, H, [(0, "#ffb37a"), (1, "#ff7b9c")])
    nw = x.cue("now")
    light_rays(g, 960, 620, x.t, a=0.12 * clamp((x.t - nw) / 0.6))
    def dad_mem(g2, cx, cy, w, h):
        gym_bg_small(g2, cx, cy, w, h)
        CH["dad"].draw(g2, cx + 90, cy + h * 0.5, 330, x.t, pose="guard", held="gloves", face={"mouth": "grin"}, look=-0.4)
        CH["lucia_toddler"].draw(g2, cx - 90, cy + h * 0.5, 220, x.t, pose="guard", held="gloves",
                                 face={"brows": "angry", "mouth": "frown"}, look=0.4)
    def mom_mem(g2, cx, cy, w, h):
        good_life_content(g2, cx, cy, w, h, x.t)
        CH["mom"].draw(g2, cx - 60, cy + h * 0.5, 320, x.t, pose="hold_front", face={"mouth": "smile"}, look=0.2)
        CH["lucia_baby"].draw(g2, cx - 60, cy + h * 0.5 - 115, 120, x.t, face={"brows": "angry", "mouth": "frown"})
    mv = ease_io((x.t - nw) / 0.8)
    k1 = ease_back(clamp(x.t / 0.6)) * (1 - 0.35 * mv)
    k2 = ease_back(clamp((x.t - x.cue("mom")) / 0.6)) * (1 - 0.35 * mv)
    dream_bubble(g, lerp(470, 300, mv), lerp(400, 250, mv), 600, 460, k1, dad_mem, x.t, tail=(220, 240))
    dream_bubble(g, lerp(1450, 1620, mv), lerp(400, 250, mv), 600, 460, k2, mom_mem, x.t, tail=(-220, 240))
    CH["lucia"].draw(g, 960, 1100, 700, x.t, pose="hips" if x.t > nw else "relaxed",
                     face={"brows": "determined", "mouth": "smirk" if x.t > nw else "flat"}, look=0.0)

def gym_bg_small(g, cx, cy, w, h):
    g.vgrad(cx - w / 2, cy - h / 2, w, h, [(0, "#3f4a6b"), (1, "#2f3956")])
    g.rect_fill(cx - w / 2, cy + h * 0.25, w, h, "#7a5236")
    for k in range(3):
        g.line(cx - w / 2, cy - h * 0.05 + k * 30, cx + w / 2, cy - h * 0.05 + k * 30, color=PAL["red"], w=7)

@scene
def recap(g, x):
    cam(g, x, 1.0, 1.0)
    td = x.cue("today")
    dawn = clamp((x.t - td + 0.3) / 1.0)
    g.vgrad(0, 0, W, H, [(0, mix("#2b2456", "#ff8a5c", dawn)), (1, mix("#5b3b7a", "#ffd6a0", dawn))])
    sun(g, 960, lerp(1100, 560, ease_out(dawn)), 230, "#fff1b8")
    if dawn > 0: light_rays(g, 960, lerp(1100, 560, ease_out(dawn)), x.t, a=0.12 * dawn)
    g.rect_fill(0, 880, W, 200, mix("#3a2f5a", "#f3d9a0", dawn)); g.line(0, 880, W, 880, w=g.lw)
    stages = [("lucia_baby", 170, 300, "AGE 0"), ("lucia_toddler", 450, 340, "AGE 2"), ("lucia_kid", 750, 420, "AGE 7"),
              ("lucia_teen", 1070, 480, "AGE 16"), ("lucia_prison", 1400, 520, "LOCKED UP"), ("lucia", 1730, 540, "TODAY")]
    span = max(1.0, td - 0.5)
    for i, (key, sx, sz, lab) in enumerate(stages):
        t0 = 0.2 + i * span / len(stages)
        k = pop(x.t, t0, 0.45)
        if k <= 0: continue
        g.save(); g.tr(sx, 900); g.sc(k); g.tr(-sx, -900)
        face = {"brows": "angry", "mouth": "frown"} if i < 5 else {"brows": "determined", "mouth": "smirk"}
        if key == "lucia_baby":
            CH[key].draw(g, sx, 890, sz * 0.8, x.t, face=face, anger=True)
        else:
            CH[key].draw(g, sx, 890, sz, x.t, pose="cross" if i in (2, 4) else ("guard" if i == 1 else "hips"),
                         held="gloves" if i == 1 else None, face=face, look=0.2)
        label_tag(g, lab, sx, 960, 1.0, fill="#ffd166" if i == 5 else "#fbf7f0", size=36, rot=0)
        g.restore()
    pop_text(g, "DAY ONE", 960, 200, 150, pop(x.t, td, 0.5), fill="#ffd166")

@scene
def question(g, x):
    cam(g, x, 1.0, 1.08)
    g.vgrad(0, 0, W, H, [(0, "#2b2456"), (1, "#7b4bc4")])
    stars(g, x.t, 30, h=H)
    CH["lucia"].draw(g, 620, 1060, 760, x.t, pose="cross", face={"brows": "skeptical", "mouth": "flat"}, look=0.6)
    CH["jason"].draw(g, 1300, 1060, 780, x.t, pose="wave_r", face={"mouth": "grin", "brows": "raised"}, look=-0.5)
    k = pop(x.t, 0.9, 0.5)
    pop_text(g, "?", 960, 300, 260, k, fill="#ffd166", rot=8 * math.sin(x.t * 2))
    label_tag(g, "WOULD YOU TRUST JASON?", 960, 90, pop(x.t, 1.2), fill="#ffd166", size=60, rot=0)

@scene
def endcard(g, x):
    g.vgrad(0, 0, W, H, [(0, "#2b2456"), (1, "#5b3b7a")])
    stars(g, x.t, 50, h=H)
    pop_text(g, "WHO'S NEXT?", 960, 170, 130, pop(x.t, 0.1), fill="#ffd166")
    for i, xx in enumerate((560, 960, 1360)):
        k = pop(x.t, 0.4 + i * 0.25)
        if k <= 0: continue
        g.save(); g.tr(xx, 560); g.sc(k)
        g.circle(0, 0, 170, "#3a2f5a", w=g.lw * 1.2)
        g.circle(0, -20, 70, "#1a1020", outline=None); g.rrect(-90, 40, 180, 110, 50, "#1a1020", outline=None)
        text(g, "?", 0, 40, 160, fill="#ffd166")
        g.restore()
    sk = pop(x.t, 1.4)
    if sk > 0:
        g.save(); g.tr(960, 900); g.sc(sk * (1 + 0.04 * math.sin(x.t * 6)))
        g.rrect(-260, -70, 520, 140, 70, PAL["red"])
        text(g, "SUBSCRIBE", 0, 26, 76, fill="#ffffff", outline=None, shadow=False)
        g.restore()
