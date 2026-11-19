# -*- coding: utf-8 -*-
"""Grown-up scenes in the channel's semi-realistic, cinematic style.
Childhood scenes keep the chibi rig (scenes.py) - exactly like the reference channel,
where the cute kid turns into a realistic adult."""
import math, random
import skia
from gfx import (G, W, H, PAL, OUTLINE, C, P_fill, P_stroke, shade, tint, mix, clamp, lerp,
                 ease_io, ease_out, ease_in, ease_back, pop, fade, wob, text, text_w)
from realistic import Adult, ADULTS
from scenes_bg import *
from atmo import *
import scenes as S
from scenes import scene, SCENES, cam, pop_text, remember_tag, stamp, sparkles, cloud, lightbulb, chess_knight

RA = {k: Adult(v, i + 1) for i, (k, v) in enumerate(ADULTS().items())}
CH = S.CH

def A(name, x, head_y, hh, t, **kw):
    """draw a realistic adult whose head centre is at head_y, head height hh px."""
    RA[name].draw(G_ref[0], x, head_y + 7.0 * hh, 7.5 * hh, t, **kw)

G_ref = [None]

def begin(g, lw=4.2):
    G_ref[0] = g
    g.lw = lw

def finish(g, x, vig=0.5, gr=0.05):
    vignette(g, vig)
    grain(g, x.t, gr)

def bench(g, x, seat_y, floor_y, w, top="#e9e3d6", frame="#5e6270"):
    for sd in (-1, 1):
        g.rrect(x + sd * (w / 2 - 30) - 12, seat_y, 24, floor_y - seat_y + 6, 6, shade(frame, 0.85), outline="#1b1820", w=3)
    g.rrect(x - w / 2, seat_y + 18, w, 30, 6, frame, outline="#1b1820", w=3)
    g.rrect(x - w / 2, seat_y - 34, w, 52, 10, top, outline="#1b1820", w=3)

def bubble_for(g, x, who, idx, txt, bx, by, tail=(-40, 60), size=40):
    a, b = x.span_start(who, idx), x.span_end(who, idx)
    if a - 0.15 <= x.t <= b + 0.6:
        k = clamp((x.t - a + 0.15) / 0.25) * (1 - clamp((x.t - b - 0.35) / 0.25))
        speech(g, txt, bx, by, k, tail, size)

# ================================================================== shared backgrounds
def bg_cell(g, t, night=False, blur=2.5, beam_on=True):
    wl = "#8d93a0" if not night else "#3a3f56"
    with blur_layer(g, blur):
        g.vgrad(0, 0, W, 880, [(0, shade(wl, 0.8)), (1, wl)])
        for row in range(0, 880, 64):
            off = 0 if (row // 64) % 2 == 0 else 75
            for col in range(-off, W, 150):
                g.rrect(col + 4, row + 4, 142, 56, 4, mix(wl, "#ffffff", 0.06), outline=shade(wl, 0.85), w=2)
        g.vgrad(0, 880, W, 200, [(0, "#5a5f6c" if not night else "#2a2d3e"), (1, "#3e424e" if not night else "#1c1e2a")])
        g.line(0, 880, W, 880, color="#2a2630", w=3)
        window(g, 1420, 140, 230, 170, view_moon if night else view_prison, t, frame="#6f7686")
        bars(g, 1420, 140, 230, 170, 4, "#454a58", t, wdt=12)
        # bar shadows on the floor / wall
        for i in range(5):
            q = G.poly_p([(1440 + i * 46, 330), (1452 + i * 46, 330), (1160 + i * 110, 1080), (1120 + i * 110, 1080)])
            g.fillp(q, "#000000", 0.12)
    if beam_on:
        beam(g, 1535, 230, 1180, 1080, 200, 620, t, "#fff6d8" if not night else "#cfe0ff", 0.22 if not night else 0.16)
        particles(g, t, 40, "#fff3c8" if not night else "#dfe8ff", seed=5, region=(1000, 200, 700, 880), size=(1.5, 3.5), speed=10, a=0.6)

def bg_exterior_prison(g, t, open_k=0.0, blur=1.5):
    with blur_layer(g, blur):
        g.vgrad(0, 0, W, 700, [(0, "#5fb3e8"), (0.7, "#bfe3f5"), (1, "#f4ead0")])
        glow_at(g, 1650, 150, 380, "#fff6d0", 0.6)
        g.circle(1650, 150, 70, "#fff8dc", outline=None)
        # distant hills & tower
        g.smooth([(-50, 560), (300, 470), (700, 520), (1100, 450), (1500, 510), (1980, 460), (1980, 700), (-50, 700)], "#9db58a", outline=None)
        g.rrect(1500, 250, 70, 300, 6, "#a9adb6", outline="#5a5f6c", w=3)
        g.rrect(1470, 220, 130, 50, 6, "#8f949e", outline="#5a5f6c", w=3)
        g.vgrad(0, 640, W, 440, [(0, "#d7c79a"), (1, "#b9a676")])
        for i in range(0, W, 64):
            g.line(i, 300, i, 650, color="#7d8494", w=6)
        g.line(0, 310, W, 310, color="#7d8494", w=8); g.line(0, 640, W, 640, color="#7d8494", w=8)
        for i in range(0, W, 40):
            g.circle(i, 292, 13, None, outline="#5e6270", w=3)
        gx = 520 + ease_io(open_k) * 420
        g.rect_fill(gx, 300, 420, 345, "#5e6270", 0.22)
        for i in range(7):
            g.line(gx + i * 70, 300, gx + i * 70, 645, color="#4d5260", w=11)
    shafts(g, 1650, 150, t, "#fff6d0", 0.16, n=8, angle=135)

def bg_vice_sunset(g, t, blur=3.0, horizon=640):
    with blur_layer(g, blur):
        g.vgrad(0, 0, W, horizon + 40, [(0, "#3b2463"), (0.45, "#c2536f"), (0.75, "#ff9a62"), (1, "#ffd59a")])
        glow_at(g, 960, horizon - 40, 700, "#ffcf8a", 0.55)
        sun(g, 960, horizon - 30, 210, "#fff0c0", bg="#ff9a62")
        skyline_vice(g, horizon + 20, t, scale=1.0)
        g.vgrad(0, horizon, W, H - horizon, [(0, "#ff9a8b"), (1, "#5b2a6a")])
        for i in range(40):
            rnd = random.Random(i)
            xx = (rnd.uniform(0, W) + t * 10) % W; yy = horizon + rnd.uniform(10, 300)
            g.line(xx, yy, xx + rnd.uniform(30, 120), yy, color="#ffe0b0", w=3, a=0.5)
        palm(g, 110, horizon + 300, 1.5, t, sil="#2a1638"); palm(g, 1820, horizon + 320, 1.4, t, sil="#2a1638", flip=True)
    particles(g, t, 35, "#ffd9a0", seed=7, size=(1.5, 3.5), speed=8, a=0.5)

def bg_night_city(g, t, blur=3.0, horizon=700):
    with blur_layer(g, blur):
        g.vgrad(0, 0, W, horizon, [(0, "#0d0b22"), (1, "#3a2160")])
        stars(g, t, 60, h=horizon * 0.5)
        skyline_vice(g, horizon, t, sunset=False, scale=1.05)
        glow_at(g, 960, horizon, 900, "#ff5fa2", 0.25)
        g.vgrad(0, horizon, W, H - horizon, [(0, "#25213a"), (1, "#141222")])
    bokeh(g, t, 18, region=(0, 200, W, 500), a=0.35)

# ================================================================== PROLOGUE hook (grown-up Lucia)
@scene
def hook_prison(g, x):
    begin(g)
    cam(g, x, 1.0, 1.1, fy=420)
    bg_cell(g, x.t, blur=3)
    k_fam = pop(x.t, x.cue("family"), 0.4)
    if k_fam > 0:
        g.save(); g.tr(470, 360); g.sc(k_fam); g.rot(-5)
        g.rrect(-110, -90, 220, 180, 6, "#f4efe6", outline="#231a22", w=4)
        g.rrect(-92, -72, 184, 132, 4, "#e8b46a", outline=None)
        for i, (xx, sz, col) in enumerate(((-48, 30, "#b5744d"), (0, 22, "#b9784f"), (48, 32, "#a8693f"))):
            g.rrect(xx - sz * 0.8, 20, sz * 1.6, 60, 10, ["#b8608f", "#d8463c", "#d8463c"][i], outline="#231a22", w=2)
            g.circle(xx, 8, sz, col, outline="#231a22", w=2)
            q = skia.Path(); q.moveTo(xx - sz, 4); q.cubicTo(xx - sz, 8 - sz * 1.4, xx + sz, 8 - sz * 1.4, xx + sz, 4); q.close()
            g.shape(q, "#241614", outline="#231a22", w=2)
        g.restore()
    A("lucia_prison", 960, 330, 205, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"}, look=-0.1,
      anger=x.t > 1.2)
    k = ease_out(x.t / 0.7)
    g.save(); g.tr(lerp(W, 0, k), 0)
    for i in range(9):
        xx = 330 + i * 160
        g.rrect(xx, -20, 34, H + 40, 17, "#3a3e4c", outline="#1b1820", w=4)
        g.line(xx + 10, 0, xx + 10, H, color="#6c7080", w=4)
    g.rrect(250, 70, 1420, 34, 10, "#3a3e4c", outline="#1b1820", w=4)
    g.restore()
    finish(g, x, 0.55)

@scene
def hook_gate(g, x):
    begin(g)
    cam(g, x, 1.0, 1.05)
    bg_exterior_prison(g, x.t, open_k=x.t / 1.2)
    car(g, 1560, 1010, 1.25, "#c8302a", x.t)
    ground_shadow(g, 1200, 1010, 120)
    A("jason", 1200, 360, 95, x.t, pose="wave_r" if x.t > x.cue("car") else "hips",
      face={"mouth": "smile", "brows": "raised"}, look=-0.5)
    wk = clamp((x.t - 0.5) / 2.6)
    ground_shadow(g, lerp(700, 860, wk), lerp(900, 1000, wk), 100)
    A("lucia", lerp(700, 860, wk), lerp(380, 360, wk), lerp(78, 92, wk), x.t, pose="relaxed",
      face={"brows": "skeptical", "mouth": "flat"}, look=0.5, walk=1.0 if wk < 1 else 0.0)
    clover(g, 520, 240, 50 * pop(x.t, 0.8), x.t)
    finish(g, x, 0.35)

@scene
def hook_chase(g, x):
    begin(g)
    cam(g, x, 1.05, 1.0, shake=[(0, x.d, 3)])
    S.hook_chase_bg(g, x)
    police_car(g, 420, 1010, 0.85, x.t, driving=True)
    car(g, 1250, 1010, 0.95, "#c8302a", x.t, driving=True, lights=True)
    helicopter(g, 1500 - x.t * 40, 170, 0.8, x.t)
    bokeh(g, x.t, 14, region=(0, 300, W, 400), a=0.3, drift=200)
    era = pop(x.t, x.cue("state"), 0.5)
    S.label_tag(g, "LEONIDA", 960, 220, era, fill="#ffd166", size=80)
    finish(g, x, 0.5)

# ================================================================== I · THE GOOD LIFE
@scene
def vice_skyline(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06, fy=420)
    bg_vice_sunset(g, x.t, blur=3.5)
    fin = x.t > x.cue("finally")
    A("mom", 700, 380, 165, x.t, pose="hands_up" if fin else "relaxed",
      face={"mouth": "grin" if fin else "smile", "eyes": "happy" if fin else "open"}, look=0.25, light=1)
    A("lucia_teen", 1160, 420, 160, x.t, pose="hips", face={"mouth": "smile", "brows": "neutral"}, look=-0.2)
    gk = pop(x.t, x.cue("gator"), 0.5)
    if gk > 0:
        g.save(); g.tr(1650, 1100 - 120 * gk)
        alligator(g, 0, 0, 1.3, x.t, mouth=0.4 + 0.3 * math.sin(x.t * 3), sunglasses=True, flip=True)
        g.restore()
        callout(g, "YES, REALLY", None, 1600, 990, 1420, 820, clamp((x.t - x.cue("gator") - 0.3) / 0.5))
    fk = pop(x.t, x.cue("film"), 0.4)
    if fk > 0:
        g.save(); g.tr(260, 560); g.sc(fk); g.rot(-8)
        g.circle(40, 210, 34, "#e6b896", outline="#231a22", w=4)
        phone_frame(g, -60, -110, 170, 300, live=False)
        g.rrect(-60, -110, 170, 300, 18, "#ff8a5c", outline=None)
        g.save(); g.sc(0.25); palm(g, 100, 600, 1.0, x.t, sil="#5b3b7a"); g.restore()
        g.circle(-30, -80, 10, "#ff3b5c", outline=None, a=0.5 + 0.5 * math.sin(x.t * 6))
        text(g, "REC", 10, -70, 28, fill="#ffffff", outline=None, shadow=False, name="ui")
        g.restore()
    if fin: sparkles(g, 700, 300, x.t, 240, 8, seed=6)
    finish(g, x, 0.4)

@scene
def bills(g, x):
    begin(g)
    cam(g, x, 1.0, 1.07, fy=450)
    tr_t = x.cue("trouble")
    with blur_layer(g, 2.5):
        g.vgrad(0, 0, W, 820, [(0, "#3c3346"), (1, "#5c4c4a")])
        for i in range(0, W, 90):
            g.rect_fill(i, 0, 45, 820, "#000000", 0.05)
        g.vgrad(0, 820, W, 260, [(0, "#3b2e2a"), (1, "#241c1a")])
        def view(g2, w, h, t):
            g2.vgrad(0, 0, w, h, [(0, "#14122e"), (1, "#2c2450")])
            g2.save(); g2.sc(0.55); skyline_lc(g2, h / 0.55 + 10, t, True, width=w / 0.55); g2.restore()
        window(g, 1380, 140, 380, 300, view, x.t, frame="#cfc6b8")
    glow_at(g, 760, 140, 520, "#ffd9a0", 0.35)
    if x.t > tr_t:
        blink = (x.t * 3) % 1 < 0.5
        glow_at(g, 1570, 290, 600, "#ff3b3b" if blink else "#3b6bff", 0.4)
    A("mom", 620, 470, 150, x.t, pose="cross", face={"brows": "sad", "mouth": "frown", "eyes": "half"}, look=0.2, legs_hidden=True)
    g.rrect(250, 760, 900, 340, 10, "#5a3a26", outline="#1b1820", w=4)
    g.rrect(220, 735, 960, 40, 8, "#7a5236", outline="#1b1820", w=4)
    mk = pop(x.t, x.cue("money"), 0.4)
    for i in range(5 if mk > 0 else 0):
        g.save(); g.tr(420 + i * 120, 730); g.rot(-9 + i * 5); g.sc(mk)
        g.rrect(-58, -38, 116, 76, 4, "#f4efe6", outline="#231a22", w=3)
        text(g, ["DUE", "$0", "DUE", "FINAL", "DUE"][i], 0, 12, 30, fill="#c8302a", outline=None, shadow=False)
        g.restore()
    girl = x.t > x.cue("girl")
    A("lucia_teen", 1400, 380, 160, x.t, pose="cross", face={"brows": "angry" if girl else "sad", "mouth": "frown"},
      look=-0.4, anger=girl, light=1)
    finish(g, x, 0.55)

# ================================================================== II · FIGHTING FOR FAMILY
@scene
def fight_night(g, x):
    begin(g)
    hit = x.cue("w3")
    cam(g, x, 1.0, 1.08, fx=800, shake=[(hit, 0.4, 14)])
    with blur_layer(g, 2.0):
        g.vgrad(0, 0, W, H, [(0, "#0f0c1e"), (1, "#26193a")])
        for row in range(0, 900, 56):
            off = 0 if (row // 56) % 2 == 0 else 65
            for col in range(-off, W, 130):
                g.rrect(col + 3, row + 3, 124, 50, 4, "#33243f", outline="#1d1426", w=2)
        g.vgrad(0, 900, W, 180, [(0, "#1c1826"), (1, "#100e18")])
    glow_at(g, 480, 120, 600, "#ffcf7a", 0.4)
    beam(g, 480, 130, 700, 1080, 80, 700, x.t, "#ffdfa0", 0.18)
    back = x.t > hit
    g.c.saveLayer(None, None)
    for i, (fx_, hh_) in enumerate(((1380, 120), (1640, 128))):
        off = (x.t - hit) * 700 if back else 0
        A("grifter2" if i else "grifter1", fx_ + off * (1 + i * 0.3), 300, hh_, x.t, pose="hips",
          face={"brows": "angry", "mouth": "grin"}, look=-0.6, tilt=12 if back else 0)
    dk = skia.Paint(Color=C("#0c0814", 0.72)); dk.setBlendMode(skia.BlendMode.kSrcATop)
    g.c.drawRect(skia.Rect.MakeWH(W, H), dk)
    g.c.restore()
    A("lucia_night", 760, 330, 140, x.t, pose="punch_r" if (hit <= x.t < hit + 0.6) else "guard",
      face={"brows": "angry", "mouth": "frown"}, look=0.5, anger=x.t > x.cue("w1"))
    pop_text(g, "HANDS UP", 380, 220, 92, pop(x.t, x.cue("w1")), fill="#ffd166", rot=-6)
    pop_text(g, "CHIN DOWN", 980, 150, 92, pop(x.t, x.cue("w2")), fill="#ffd166", rot=4)
    pop_text(g, "HIT BACK!", 1430, 260, 116, pop(x.t, hit), fill="#ff5a3c", rot=-4)
    pow_burst(g, 1180, 520, 160, pop(x.t, hit) * (1 - clamp((x.t - hit - 0.7) / 0.3)), "POW!")
    finish(g, x, 0.6)

@scene
def arrest(g, x):
    begin(g)
    cam(g, x, 1.0, 1.08, fy=420)
    bg_night_city(g, x.t, blur=4)
    blink = (x.t * 3) % 1 < 0.5
    with blur_layer(g, 3):
        police_car(g, 1450, 980, 1.1, x.t)
    glow_at(g, 300 if blink else 1600, 300, 900, "#ff3b3b" if blink else "#3b6bff", 0.32)
    A("guard", 1240, 330, 150, x.t, pose="hips", face={"brows": "angry", "mouth": "flat"}, look=-0.5)
    A("lucia_night", 700, 320, 160, x.t, pose="behind", face={"brows": "angry", "mouth": "frown"}, look=-0.2, anger=True)
    stamp(g, "LEONIDA PENITENTIARY", 960, 300, clamp((x.t - x.cue("sign")) / 0.25), size=86)
    finish(g, x, 0.55)

# ================================================================== III · BAD LUCK
@scene
def cell(g, x):
    begin(g)
    cam(g, x, 1.0, 1.08, fy=420)
    if x.t < x.cue("number"):
        bg_cell(g, x.t, blur=3)
        grey = clamp((x.t - x.cue("walls")) / 0.4)
        tint_overlay(g, "#8a90a0", 0.25 * grey, skia.BlendMode.kSaturation)
        A("lucia_prison", 960, 330, 200, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"})
    else:
        g.vgrad(0, 0, W, H, [(0, "#d9dde4"), (1, "#b9bec8")])
        for i, y in enumerate(range(120, 1000, 55)):
            g.line(0, y, W, y, color="#8f97a5", w=3)
            if i % 2 == 0:
                text(g, "%d'" % (7 - i // 2), 70, y + 12, 32, fill="#6a7180", outline=None, shadow=False)
        k = pop(x.t, x.cue("number"), 0.35)
        A("lucia_prison", 960, 340, 215, x.t, pose="hold_front", face={"brows": "angry", "mouth": "frown"})
        g.save(); g.tr(960, 900); g.sc(k)
        g.rrect(-240, -80, 480, 160, 8, "#1c1a22", outline="#f4efe6", w=4)
        text(g, "LP-0419", 0, 26, 90, fill="#f4efe6", outline=None, shadow=False)
        g.restore()
        glow_at(g, 960, 300, 900, "#ffffff", 0.5 * (1 - clamp((x.t - x.cue("number")) / 0.3)))
    finish(g, x, 0.5)

@scene
def interview(g, x):
    begin(g)
    cam(g, x, 1.0, 1.05)
    with blur_layer(g, 2.5):
        g.vgrad(0, 0, W, 760, [(0, "#2a2d38"), (1, "#4a4f5c")])
        g.vgrad(0, 760, W, 320, [(0, "#3a3e4a"), (1, "#22242e")])
    g.line(960, 0, 960, 70, color="#1b1820", w=4)
    g.poly([(870, 70), (1050, 70), (1010, 30), (910, 30)], "#2e313c", outline="#1b1820", w=4)
    beam(g, 960, 70, 960, 900, 180, 1100, x.t, "#fff4d6", 0.25)
    particles(g, x.t, 30, "#fff3c8", seed=9, region=(500, 80, 900, 800), size=(1.5, 3), speed=8, a=0.5)
    shrug = x.t > x.cue("shrug")
    A("lucia_prison", 560, 360, 175, x.t, pose="shrug" if shrug and x.t < x.cue("remember") else "cross",
      face={"brows": "skeptical" if shrug else "angry", "mouth": "smirk" if shrug else "frown"},
      look=0.5, talk=x.talking("lucia"), legs_hidden=True, light=1)
    A("officer", 1380, 360, 170, x.t, pose="hold_front", face={"brows": "neutral", "mouth": "flat"},
      look=-0.5, talk=x.talking("officer"), legs_hidden=True)
    g.rrect(200, 800, 1520, 300, 6, "#3a3e4a", outline="#1b1820", w=4)
    g.rrect(160, 770, 1600, 40, 8, "#5a5f6c", outline="#1b1820", w=4)
    g.save(); g.tr(1220, 760); g.rot(4)
    g.rrect(-90, -10, 180, 24, 3, "#e9c58a", outline="#1b1820", w=3)
    g.restore()
    bubble_for(g, x, "officer", 0, "Lucia. Do you know why you're here?", 1240, 110, tail=(60, 70))
    bubble_for(g, x, "lucia", 0, "Bad luck, I guess.", 560, 110, tail=(-10, 70))
    remember_tag(g, 560, 240, pop(x.t, x.cue("remember")), "REMEMBER THIS", x.t)
    finish(g, x, 0.6)

@scene
def workout(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06, fy=420)
    bg_cell(g, x.t, blur=2.5)
    marks = int(clamp(x.t / x.d) * 24) + 3
    for i in range(marks):
        gx = 200 + (i // 5) * 70 + (i % 5) * 12
        if i % 5 == 4:
            g.line(gx - 52, 330, gx + 4, 290, color="#2b2233", w=5)
        else:
            g.line(gx, 280, gx, 340, color="#2b2233", w=5)
    th, sm = x.cue("think"), x.cue("smart")
    if x.t < th:
        ph = (x.t * 2.4) % 1
        A("lucia_prison", 900, 330, 150, x.t, pose="punch_r" if ph < 0.4 else "guard",
          face={"brows": "angry", "mouth": "frown"}, look=0.4)
    else:
        bench(g, 1220, 604, 900, 640)
        RA["lucia_prison"].draw(g, 1220, 590, 7.5 * 120, x.t, pose="chin",
                                face={"brows": "determined", "mouth": "flat"}, look=-0.3, sit=True)
        lightbulb(g, 1050, 230, pop(x.t, th + 0.3))
        chess_knight(g, 600, 560, 2.0, pop(x.t, sm))
        pop_text(g, "SMART MOVES ONLY", 600, 860, 84, pop(x.t, sm + 0.2), fill="#ffd166", rot=-4)
    finish(g, x, 0.55)

@scene
def photo(g, x):
    begin(g)
    cam(g, x, 1.0, 1.1, fx=900, fy=480)
    bg_cell(g, x.t, night=True, blur=3)
    bench(g, 900, 592, 900, 700, top="#c9c4b8", frame="#454a58")
    RA["lucia_prison"].draw(g, 900, 578, 7.5 * 125, x.t, pose="hold_r", held="photo",
                            face={"brows": "sad", "mouth": "frown"}, look=0.25, sit=True, light=1)
    dk = x.cue("dream"); fk = x.cue("further")
    k = ease_back(clamp((x.t - dk) / 0.6))
    if x.t > fk:
        k *= lerp(1.0, 0.45, ease_io((x.t - fk) / 1.2))
    g.save()
    off = ease_io((x.t - fk) / 1.4) * 200 if x.t > fk else 0
    g.tr(off, -off * 0.6)
    g.alpha(1 - 0.6 * clamp((x.t - fk) / 1.4))
    dream_bubble(g, 1380, 330, 520, 360, k, lambda g_, cx, cy, w, h: good_life_content(g_, cx, cy, w, h, x.t),
                 x.t, tail=(-300, 200))
    g.restore(); g.restore()
    finish(g, x, 0.65)

# ================================================================== IV · SHEER LUCK
@scene
def gate_open(g, x):
    begin(g)
    cam(g, x, 1.0, 1.07, fx=760)
    ok = clamp((x.t - x.cue("out") + 0.3) / 1.2)
    bg_exterior_prison(g, x.t, ok)
    if ok > 0.2:
        shafts(g, 730, 470, x.t, "#fff6d0", 0.18 * ok, n=10, angle=90, spread=2.5)
    wk = clamp((x.t - x.cue("out")) / 2.2)
    ground_shadow(g, lerp(730, 900, wk), lerp(830, 1010, wk), lerp(60, 110, wk))
    A("lucia", lerp(730, 900, wk), lerp(390, 360, wk), lerp(55, 100, wk), x.t, pose="relaxed",
      face={"brows": "raised", "mouth": "smile" if ok > 0.5 else "flat"}, walk=1.0 if 0 < wk < 1 else 0)
    ck = pop(x.t, x.cue("luck"), 0.5)
    clover(g, 1300, 330, 70 * ck, x.t)
    if ck > 0: sparkles(g, 1300, 300, x.t, 160, 7)
    pop_text(g, "SHEER LUCK", 1320, 620, 90, pop(x.t, x.cue("luck") + 0.6), fill="#7be37b", rot=-5)
    finish(g, x, 0.35)

@scene
def jason_gate(g, x):
    begin(g)
    cam(g, x, 1.0, 1.05, fx=1000)
    bg_exterior_prison(g, x.t, 0.0, blur=4)
    with blur_layer(g, 3):
        car(g, 330, 1020, 1.4, "#c8302a", x.t)
    gk = x.t > x.cue("guard")
    A("jason", 1000, 330, 175, x.t, pose="hips", face={"brows": "raised", "mouth": "smile"}, look=0.35,
      talk=x.talking("jason"), legs_hidden=True)
    g.rrect(1410, 190, 300, 330, 10, "#c9cdd5", outline="#1b1820", w=4)
    g.rrect(1440, 230, 240, 150, 8, "#9fd3f0", outline="#1b1820", w=4)
    text(g, "VISITOR CHECK-IN", 1560, 440, 26, fill="#2a2a2a", outline=None, shadow=False, name="ui")
    g.c.save(); g.c.clipPath(G.rrect_p(1440, 230, 240, 150, 8), doAntiAlias=True)
    A("guard", 1560, 300, 62, x.t, pose="idle", face={"brows": "skeptical" if gk else "neutral", "mouth": "flat"},
      look=-0.6, legs_hidden=True)
    g.c.restore()
    bubble_for(g, x, "jason", 0, "I'm here for Lucia Caminos.", 900, 110, tail=(40, 70))
    nk = clamp((x.t - x.span_start("jason", 1)) / 0.6)
    callout(g, "JASON DUVAL", "the guy at the gate", 1060, 300, 560, 620, nk, x.t)
    finish(g, x, 0.4)

@scene
def luck_name(g, x):
    begin(g)
    cam(g, x, 1.0, 1.04)
    sh, nm = x.cue("sheer"), x.cue("name")
    split = ease_io((x.t - sh + 0.2) / 0.5)
    g.save(); g.c.clipRect(skia.Rect.MakeXYWH(0, 0, W / 2 + (1 - split) * W / 2, H))
    g.vgrad(0, 0, W, H, [(0, "#2a2d3c"), (1, "#15161e")])
    g.save(); g.tr(lerp(490, 0, split), 0)
    A("lucia_prison", 470, 330, 150, x.t, pose="cross", face={"brows": "angry", "mouth": "frown"})
    for i in range(6):
        g.rrect(140 + i * 130, 150, 22, 900, 11, "#3a3e4c", outline="#1b1820", w=3)
    text(g, "BAD LUCK", 470, 120, 92, fill="#9aa0ad")
    g.restore(); g.restore()
    if split > 0:
        g.save(); g.c.clipRect(skia.Rect.MakeXYWH(W - split * W / 2, 0, W / 2 + 4, H))
        g.vgrad(0, 0, W, H, [(0, "#5fb3e8"), (1, "#fff1c8")])
        shafts(g, 1440, 650, x.t, "#ffffff", 0.2, n=10, angle=-90, spread=3)
        clover(g, 1720, 300, 60, x.t)
        A("lucia", 1440, 330, 150, x.t, pose="hands_up", face={"mouth": "grin", "eyes": "happy"})
        text(g, "SHEER LUCK", 1440, 120, 92, fill="#7be37b")
        g.restore()
        g.line(W - split * W / 2, 0, W - split * W / 2, H, color="#f4efe6", w=10)
    nk = ease_back(clamp((x.t - nm) / 0.5))
    if nk > 0:
        g.save(); g.alpha(clamp((x.t - nm) / 0.25))
        g.vgrad(0, 0, W, H, [(0, "#ff9a62"), (1, "#c2536f")])
        shafts(g, 960, 1000, x.t, "#ffe8c0", 0.2, n=12, angle=-90, spread=3)
        A("jason", 960, 380, 190 * (0.8 + 0.2 * nk), x.t, pose="wave_r", face={"mouth": "grin", "brows": "raised"})
        S.label_tag(g, "LUCK HAS A NAME", 960, 130, nk, fill="#ffd166", size=72)
        g.restore(); g.restore()
    finish(g, x, 0.45)

@scene
def cta(g, x):
    begin(g)
    cam(g, x, 1.0, 1.03)
    bg_night_city(g, x.t, blur=5)
    A("lucia", 470, 330, 180, x.t, pose="point_r" if x.t > x.cue("who") else "wave_r",
      face={"mouth": "smile", "brows": "raised"}, look=0.4)
    g.rrect(880, 180, 900, 700, 30, "#fbf8f2", outline="#1b1622", w=5)
    text(g, "WHO'S BORN NEXT?", 1330, 270, 66, fill="#c8302a", outline=None, shadow=False)
    names = [("Jason?", x.cue("jason")), ("Cal Hampton!", x.cue("drop") + 0.2), ("Boobie Ike!", x.cue("drop") + 0.6),
             ("Brian Heder!", x.cue("drop") + 1.0)]
    for i, (nm, t0) in enumerate(names):
        k = pop(x.t, t0, 0.35)
        if k <= 0: continue
        g.save(); g.tr(1330, 380 + i * 120); g.sc(k)
        g.rrect(-400, -46, 800, 92, 20, "#ece4f5", outline="#1b1622", w=3)
        g.circle(-340, 0, 30, ["#ff5fa2", "#2fb3a6", "#ffd166", "#7b4bc4"][i], outline="#1b1622", w=3)
        text(g, nm, -290, 16, 46, fill="#1b1622", outline=None, align="left", shadow=False, name="ui")
        heart(g, 340, 0, 18)
        g.restore()
    lk = pop(x.t, x.cue("liked"), 0.4)
    if lk > 0:
        g.save(); g.tr(1330, 950); g.sc(lk * (1 + 0.06 * math.sin(x.t * 8)))
        g.rrect(-200, -55, 400, 110, 55, "#c8302a", outline="#1b1622", w=5)
        text(g, "LIKE + COMMENT", 0, 18, 46, fill="#ffffff", outline=None, shadow=False)
        g.restore()
    finish(g, x, 0.5)

# ================================================================== V · JASON (grown-up parts)
@scene
def army(g, x):
    begin(g)
    cam(g, x, 1.0, 1.07, fy=420)
    with blur_layer(g, 3):
        g.vgrad(0, 0, W, 700, [(0, "#9cc4dc"), (1, "#f0e2bf")])
        glow_at(g, 1500, 200, 500, "#fff6d0", 0.5)
        for i, xx in enumerate((250, 650, 1450, 1750)):
            g.poly([(xx - 220, 720), (xx, 470), (xx + 220, 720)], "#6b7440" if i % 2 else "#59622f", outline="#2a2a1a", w=3)
        g.vgrad(0, 700, W, 380, [(0, "#cdb682"), (1, "#a8915c")])
    wk = x.t > x.cue("work")
    A("jason_army", 960, 330, 190, x.t, pose="idle" if wk else "salute",
      face={"brows": "determined" if not wk else "sad", "mouth": "flat" if not wk else "frown"}, sweat=wk)
    cloud(g, 960, 120, 1.4, rain=True, t=x.t, k=pop(x.t, x.cue("work")))
    finish(g, x, 0.4)

@scene
def keys_roof(g, x):
    begin(g)
    cam(g, x, 1.0, 1.05, fx=900)
    with blur_layer(g, 2):
        g.vgrad(0, 0, W, 660, [(0, "#4fa8e0"), (1, "#cdeefa")])
        glow_at(g, 1700, 130, 420, "#fff6d0", 0.6)
        ocean(g, 640, 440, "#5fd3e8", "#2a7fb0", x.t, sparkle="#ffffff")
        for i in range(4):
            g.ellipse(200 + i * 420, 690, 160, 20, "#f3d9a0", outline="#5a5040", w=2)
        palm(g, 1750, 900, 1.2, x.t)
    for sx in (520, 640, 1080, 1200):
        g.rrect(sx, 760, 26, 300, 6, "#7a5236", outline="#1b1820", w=3)
    g.rrect(460, 500, 820, 280, 8, "#efe2c6", outline="#1b1820", w=4)
    g.rrect(560, 560, 160, 130, 6, "#a9dff5", outline="#1b1820", w=4)
    g.rrect(1000, 560, 160, 130, 6, "#a9dff5", outline="#1b1820", w=4)
    g.rrect(790, 580, 120, 200, 6, "#2a9d8f", outline="#1b1820", w=4)
    g.rrect(380, 900, 1000, 40, 6, "#8f6038", outline="#1b1820", w=4)
    lk = x.t > x.cue("leaks")
    hammer_ph = (x.t * 3) % 1
    A("jason", 770, 360, 46, x.t, pose="hammer" if (lk and hammer_ph < 0.5) else "relaxed", held="hammer",
      face={"brows": "sad" if lk else "neutral", "mouth": "frown" if lk else "flat"}, look=0.3)
    g.poly([(420, 510), (870, 330), (1320, 510)], "#55607e", outline="#1b1820", w=4)
    for k in range(1, 6):
        g.line(420 + k * 75, 510 - k * 30, 1320 - k * 75, 510 - k * 30, color="#46506a", w=3)
    if lk:
        for i in range(4):
            ph = (x.t * 1.3 + i * 0.25) % 1.0
            g.fillp(G.ellipse_p(760 + i * 70, 520 + ph * 140, 7, 11), "#6fb6ff", 1 - ph)
    bk = x.t > x.cue("brian") - 0.2
    bx = lerp(2300, 1500, ease_out((x.t - x.cue("brian") + 0.2) / 0.7)) if bk else 2400
    A("brian", bx, 420, 150, x.t, pose="hold_r", held="beer", face={"mouth": "grin", "brows": "raised"}, look=-0.6,
      legs_hidden=True)
    callout(g, "BRIAN", "your landlord", bx - 60, 330, 1170, 180, clamp((x.t - x.cue("brian") - 0.4) / 0.6), x.t)
    particles(g, x.t, 25, "#ffffff", seed=3, size=(1.5, 3), speed=6, a=0.4)
    finish(g, x, 0.35)

@scene
def jason_sigh(g, x):
    begin(g)
    cam(g, x, 1.03, 1.12, fy=420)
    bg_vice_sunset(g, x.t, blur=5, horizon=700)
    hk = x.t > x.cue("harder")
    A("jason", 900, 380, 260, x.t, pose="chin" if not hk else "facepalm",
      face={"brows": "sad", "eyes": "half", "mouth": "frown"}, look=0.3, legs_hidden=True, sweat=hk, light=1)
    cloud(g, 920, 100, 1.6, rain=True, t=x.t, k=pop(x.t, x.cue("harder")))
    finish(g, x, 0.5)

# ================================================================== VI · TRUST
def motel_bg(g, t, neon_on=True, blur=3):
    with blur_layer(g, blur):
        g.vgrad(0, 0, W, 780, [(0, "#1f2840"), (1, "#3a4a68")])
        for i in range(0, W, 46):
            g.rect_fill(i, 0, 23, 780, "#000000", 0.06)
        g.vgrad(0, 780, W, 300, [(0, "#4a3446"), (1, "#2a1e2a")])
        def view(g2, w, h, tt):
            g2.vgrad(0, 0, w, h, [(0, "#14122e"), (1, "#3a2a5a")])
            on = neon_on and ((tt * 1.3) % 1 > 0.08)
            if on: g2.glow(w * 0.5, h * 0.4, w * 0.6, "#ff5fa2", 0.55)
            text(g2, "MOTEL", w * 0.5, h * 0.5, 84, fill="#ffb0d8" if on else "#5a3a4a",
                 outline="#ff5fa2" if on else "#3a2a3a", ow=6, shadow=False)
            g2.save(); g2.sc(0.45); car(g2, w * 0.45 / 0.45, (h + 30) / 0.45, 1.0, "#c8302a", tt); g2.restore()
        window(g, 1180, 120, 520, 340, view, t, curtains="#8a3a5a")
    on = neon_on and ((t * 1.3) % 1 > 0.08)
    if on:
        glow_at(g, 1440, 290, 900, "#ff5fa2", 0.3)
        beam(g, 1440, 460, 1200, 1080, 520, 900, t, "#ff8fc8", 0.15)

@scene
def motel(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06)
    motel_bg(g, x.t, neon_on=x.t > x.cue("motel") - 1.5)
    g.rrect(100, 600, 740, 420, 12, "#6a3a4e", outline="#1b1820", w=4)
    g.rrect(120, 545, 700, 120, 20, "#e6dfd0", outline="#1b1820", w=4)
    g.rrect(140, 480, 170, 100, 26, "#f4efe6", outline="#1b1820", w=4)
    RA["lucia"].draw(g, 480, 560, 7.5 * 100, x.t, pose="cross", face={"brows": "skeptical", "mouth": "flat"},
                     look=0.4, sit=True)
    tk = x.talking("jason")
    A("jason", 1250, 320, 125, x.t, pose="hips", face={"brows": "raised", "mouth": "smile"},
      look=-0.5, talk=tk, light=1)
    bubble_for(g, x, "jason", 0, "Trust me. This place is just a start for us.", 1150, 110, tail=(60, 70), size=36)
    S.label_tag(g, "NOT EXACTLY THE GOOD LIFE", 520, 200, pop(x.t, x.cue("motel") + 0.4), fill="#ffd166", size=46)
    finish(g, x, 0.5)

@scene
def toast(g, x):
    begin(g)
    cam(g, x, 1.04, 1.12, fy=470)
    motel_bg(g, x.t, blur=6)
    gk = x.t > x.cue("glass") - 0.2
    A("lucia", 680, 400, 230, x.t, pose="raise_r" if gk else "idle", held="glass" if gk else None,
      face={"mouth": "smile", "brows": "raised"}, look=0.45, talk=x.talking("lucia"), legs_hidden=True)
    A("jason", 1260, 400, 235, x.t, pose="raise_r" if gk else "idle", held="glass" if gk else None,
      face={"mouth": "grin"}, look=-0.45, legs_hidden=True, light=1)
    bubble_for(g, x, "lucia", 0, "To new beginnings.", 600, 110, tail=(30, 70))
    if x.t > x.span_end("lucia", 0) - 0.3:
        sparkles(g, 960, 330, x.t, 120, 7, seed=9)
    finish(g, x, 0.55)

@scene
def car_hood(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06, fy=480)
    with blur_layer(g, 3):
        g.vgrad(0, 0, W, H, [(0, "#0b0a20"), (1, "#3a2160")])
        stars(g, x.t, 90, h=520)
        g.circle(1500, 200, 60, "#fff3c4", outline=None)
        g.save(); g.sc(0.7); g.tr(0, 300); skyline_vice(g, 820, x.t, sunset=False); g.restore()
    glow_at(g, 1500, 200, 300, "#fff3c4", 0.35)
    bokeh(g, x.t, 16, region=(0, 450, W, 300), a=0.3, rmin=15, rmax=40, drift=5)
    g.rect_fill(0, 870, W, 210, "#141222")
    car(g, 960, 1085, 1.5, "#c8302a", x.t)
    lt, jt = x.talking("lucia"), x.talking("jason")
    RA["lucia"].draw(g, 800, 900, 7.5 * 92, x.t, pose="relaxed", face={"brows": "determined", "mouth": "flat"},
                     look=0.5 if x.t > x.span_start("jason", 0) - 0.3 else 0.2, talk=lt, sit=True)
    RA["jason"].draw(g, 1110, 900, 7.5 * 96, x.t, pose="relaxed", face={"brows": "raised", "mouth": "smile"},
                     look=-0.5, talk=jt, sit=True, light=1)
    bubble_for(g, x, "lucia", 0, "The only way we get through this... is together.", 760, 110, tail=(20, 70), size=34)
    bubble_for(g, x, "jason", 0, "Trust?", 1250, 230, tail=(-30, 70))
    bubble_for(g, x, "lucia", 1, "Trust.", 640, 230, tail=(40, 70))
    k = pop(x.t, x.span_start("lucia", 1) + 0.5, 0.5)
    if k > 0:
        heart(g, 960, 420, 50 * k)
    finish(g, x, 0.55)

# ================================================================== VII · VICE CITY
@scene
def store_masks(g, x):
    begin(g)
    ld = x.cue("loud")
    cam(g, x, 1.0, 1.06, shake=[(ld, 0.4, 12)])
    with blur_layer(g, 2.5):
        S.store_bg(g, x.t)
    glow_at(g, 960, 0, 900, "#e8fff4", 0.25)
    loud = x.t > ld
    A("cashier", 1500, 420, 130, x.t, pose="hands_up" if loud else "idle",
      face={"brows": "raised" if loud else "neutral", "eyes": "wide" if loud else "open", "mouth": "o" if loud else "flat"},
      sweat=loud, legs_hidden=True)
    g.rrect(1160, 700, 680, 400, 10, "#c8402f", outline="#1b1820", w=4)
    g.rrect(1160, 700, 680, 40, 10, "#9a2e22", outline="#1b1820", w=4)
    m1, m2 = x.t > x.cue("mask1") - 0.3, x.t > x.cue("mask2") + 0.3
    A("lucia", 520, 340, 120, x.t, pose="hold_r" if loud else "relaxed", held="bag" if loud else None,
      face={"brows": "determined", "mouth": "smirk"}, look=0.4, mask="#e85d9a" if m1 else False)
    A("jason", 880, 330, 125, x.t, pose="hips", face={"brows": "raised", "mouth": "grin"}, look=0.3,
      mask="#262230" if m2 else False, light=1)
    pow_burst(g, 1400, 300, 170, pop(x.t, ld) * (1 - clamp((x.t - ld - 0.9) / 0.3)), "!!!", col="#ffd166")
    finish(g, x, 0.45)

@scene
def chase(g, x):
    begin(g)
    S.chase(g, x)
    bokeh(g, x.t, 12, region=(0, 300, W, 400), a=0.25, drift=200)
    finish(g, x, 0.5)

@scene
def who_you_know(g, x):
    begin(g)
    cam(g, x, 1.03, 1.1, fy=430)
    g.vgrad(0, 0, W, H, [(0, "#14102a"), (1, "#4a1f5a")])
    bokeh(g, x.t, 40, region=(0, 100, W, 700), drift=700, a=0.55, rmin=30, rmax=90)
    A("lucia", 960, 430, 270, x.t, pose="idle", face={"brows": "determined", "mouth": "smirk"},
      look=0.15, talk=x.talking("lucia"), legs_hidden=True)
    q = skia.Path(); q.addRect(skia.Rect.MakeWH(W, H))
    q.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(140, 80, 1640, 720), 90, 90))
    q.setFillType(skia.PathFillType.kEvenOdd)
    g.fillp(q, "#7a1f2a"); g.strokep(q, "#1b1820", w=5)
    g.rrect(-20, 860, W + 40, 260, 30, "#5a1620", outline="#1b1820", w=5)
    glow_at(g, 300, 400, 500, "#ff5fa2", 0.15)
    bubble_for(g, x, "lucia", 0, "Who you know, and what you got.", 960, 950, tail=(0, -90))
    finish(g, x, 0.5)

@scene
def bonnie(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06)
    ph = x.cue("phones")
    color_k = clamp((x.t - ph) / 0.3)
    def content():
        g.vgrad(0, 0, W, H, [(0, "#ff9a62"), (1, "#c2536f")])
        g.rrect(330, 110, 1260, 850, 16, "#f4efe6", outline="#1b1820", w=5)
        g.c.save(); g.c.clipPath(G.rrect_p(370, 150, 1180, 770, 8), doAntiAlias=True)
        g.vgrad(370, 150, 1180, 770, [(0, "#d9b98a"), (1, "#a8845a")])
        with blur_layer(g, 2):
            car(g, 960, 1010, 1.2, "#5b4a3a", x.t)
        phones = x.t > ph
        A("lucia", 790, 330, 125, x.t, pose="phone" if phones else "hips", held="phone" if phones else None,
          face={"mouth": "smirk", "brows": "determined"}, look=0.3)
        A("jason", 1140, 320, 130, x.t, pose="phone" if phones else "cross", held="phone" if phones else None,
          face={"mouth": "grin"}, look=-0.3, light=1)
        g.c.restore()
        g.rrect(370, 150, 1180, 770, 8, None, outline="#1b1820", w=4)
    if color_k < 1:
        m = [0.393, 0.769, 0.189, 0, 0, 0.349, 0.686, 0.168, 0, 0, 0.272, 0.534, 0.131, 0, 0, 0, 0, 0, 1, 0]
        ident = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        p = skia.Paint(); p.setColorFilter(skia.ColorFilters.Matrix([lerp(a, b, color_k) for a, b in zip(m, ident)]))
        g.c.saveLayer(None, p); content(); g.c.restore()
    else:
        content()
    text(g, "BONNIE & CLYDE, 1934" if x.t < ph else "LUCIA & JASON, 2026", 960, 1030, 60,
         fill="#f6ead2" if x.t < ph else "#ffd166")
    gk = pop(x.t, x.cue("gator"), 0.5)
    if gk > 0:
        g.save(); g.tr(1620, 1075); g.sc(gk)
        alligator(g, 0, 0, 1.5, x.t, mouth=0.4 + 0.3 * math.sin(x.t * 4), sunglasses=True)
        g.restore()
    finish(g, x, 0.45, 0.08)

# ================================================================== VIII · DAY ONE
@scene
def beach_sunset(g, x):
    begin(g)
    cam(g, x, 1.0, 1.07, fy=500)
    bg_vice_sunset(g, x.t, blur=3, horizon=620)
    g.vgrad(0, 800, W, 280, [(0, "#e9c890"), (1, "#c9a070")])
    g.rrect(-20, 890, W + 40, 220, 6, "#cbbfae", outline="#1b1820", w=4)
    g.rrect(-20, 878, W + 40, 30, 6, "#ddd2c2", outline="#1b1820", w=4)
    nk = x.t > x.cue("you")
    RA["lucia"].draw(g, 820, 892, 7.5 * 105, x.t, pose="relaxed" if not nk else "shrug",
                     face={"brows": "neutral" if not nk else "skeptical", "mouth": "smile" if not nk else "smirk"},
                     look=0.5 if not nk else 0.0, sit=True)
    RA["jason"].draw(g, 1110, 892, 7.5 * 108, x.t, pose="relaxed", face={"mouth": "smile"}, look=-0.4, sit=True, light=1)
    bk = pop(x.t, x.cue("best"))
    if bk > 0:
        heart(g, 600, 280, 70 * bk)
        pop_text(g, "BEST", 600, 420, 70, bk, fill="#ffd166")
    wk = pop(x.t, x.cue("worst"))
    cloud(g, 1340, 260, 1.2, rain=True, t=x.t, k=wk)
    if wk > 0: pop_text(g, "WORST", 1340, 420, 70, wk, fill="#c9cdd5")
    finish(g, x, 0.45)

@scene
def memories(g, x):
    begin(g)
    cam(g, x, 1.0, 1.05)
    bg_vice_sunset(g, x.t, blur=7)
    nw = x.cue("now")
    if x.t > nw:
        shafts(g, 960, 700, x.t, "#fff0c0", 0.18 * clamp((x.t - nw) / 0.6), n=12, angle=-90, spread=3)
    def dad_mem(g2, cx, cy, w, h):
        S.gym_bg_small(g2, cx, cy, w, h)
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
    old = g.lw; g.lw = 6
    dream_bubble(g, lerp(430, 290, mv), lerp(360, 240, mv), 580, 440, k1, dad_mem, x.t, tail=(230, 240))
    dream_bubble(g, lerp(1490, 1630, mv), lerp(360, 240, mv), 580, 440, k2, mom_mem, x.t, tail=(-230, 240))
    g.lw = old
    A("lucia", 960, 430, 210, x.t, pose="hips" if x.t > nw else "relaxed",
      face={"brows": "determined", "mouth": "smirk" if x.t > nw else "flat"}, legs_hidden=True)
    finish(g, x, 0.45)

@scene
def recap(g, x):
    begin(g)
    cam(g, x, 1.0, 1.0)
    td = x.cue("today")
    dawn = clamp((x.t - td + 0.3) / 1.0)
    g.vgrad(0, 0, W, H, [(0, mix("#1f1a40", "#c2536f", dawn)), (1, mix("#4a2f6a", "#ffd59a", dawn))])
    sy = lerp(1150, 560, ease_out(dawn))
    glow_at(g, 960, sy, 800, "#ffd9a0", 0.5 * dawn + 0.1)
    g.circle(960, sy, 220, "#fff0c0", outline=None)
    if dawn > 0: shafts(g, 960, sy, x.t, "#fff0c0", 0.16 * dawn, n=12, angle=-90, spread=3)
    g.vgrad(0, 900, W, 180, [(0, mix("#2a2448", "#e9c890", dawn)), (1, mix("#16132a", "#c9a070", dawn))])
    g.line(0, 900, W, 900, color="#1b1820", w=3)
    stages = [("c", "lucia_baby", 170, 260, "AGE 0"), ("c", "lucia_toddler", 430, 330, "AGE 2"),
              ("c", "lucia_kid", 700, 410, "AGE 7"), ("r", "lucia_teen", 1010, 72, "AGE 16"),
              ("r", "lucia_prison", 1360, 78, "LOCKED UP"), ("r", "lucia", 1720, 80, "TODAY")]
    span = max(1.0, td - 0.5)
    for i, (kind, key, sx, sz, lab) in enumerate(stages):
        t0 = 0.2 + i * span / len(stages)
        k = pop(x.t, t0, 0.45)
        if k <= 0: continue
        g.save(); g.tr(sx, 900); g.sc(k); g.tr(-sx, -900)
        face = {"brows": "angry", "mouth": "frown"} if i < 5 else {"brows": "determined", "mouth": "smirk"}
        if kind == "c":
            old = g.lw; g.lw = 6
            if key == "lucia_baby":
                CH[key].draw(g, sx, 890, sz * 0.8, x.t, face=face, anger=True)
            else:
                CH[key].draw(g, sx, 892, sz, x.t, pose="cross" if i == 2 else "guard", held="gloves" if i == 1 else None,
                             face=face, look=0.2)
            g.lw = old
        else:
            ground_shadow(g, sx, 895, 90)
            RA[key].draw(g, sx, 895, 7.5 * sz, x.t, pose="cross" if i == 4 else "hips", face=face, look=-0.1)
        S.label_tag(g, lab, sx, 965, 1.0, fill="#ffd166" if i == 5 else "#fbf7f0", size=36, rot=0)
        g.restore()
    pop_text(g, "DAY ONE", 960, 190, 150, pop(x.t, td, 0.5), fill="#ffd166")
    finish(g, x, 0.4)

@scene
def question(g, x):
    begin(g)
    cam(g, x, 1.0, 1.06, fy=460)
    bg_night_city(g, x.t, blur=6)
    A("lucia", 600, 400, 210, x.t, pose="cross", face={"brows": "skeptical", "mouth": "flat"}, look=0.6, legs_hidden=True)
    A("jason", 1330, 400, 215, x.t, pose="wave_r", face={"mouth": "grin", "brows": "raised"}, look=-0.5,
      legs_hidden=True, light=1)
    k = pop(x.t, 0.9, 0.5)
    pop_text(g, "?", 960, 300, 240, k, fill="#ffd166", rot=8 * math.sin(x.t * 2))
    S.label_tag(g, "WOULD YOU TRUST JASON?", 960, 90, pop(x.t, 1.2), fill="#ffd166", size=60, rot=0)
    finish(g, x, 0.55)

# ================================================================== atmosphere for the chibi childhood scenes
def chibi_post(name, light=None, parts=None):
    base = SCENES[name]
    def wrapped(g, x):
        base(g, x)
        if light:
            lx, ly, col, a = light
            shafts(g, lx, ly, x.t, col, a, n=8, angle=120)
        if parts:
            particles(g, x.t, parts[0], parts[1], seed=hash(name) % 97, size=(1.5, 3.5), speed=10, a=0.55)
        grade(g, "#fff2d8", "#5a3a6a", 0.22)
        vignette(g, 0.4)
        grain(g, x.t, 0.05)
    SCENES[name] = wrapped

for nm, li, pa in (("baby", (1460, 300, "#fff3d0", 0.12), (25, "#fff3c8")),
                   ("mom", (1460, 300, "#fff6d8", 0.16), (30, "#fff3c8")),
                   ("dad_gloves", (300, 0, "#ffe8c0", 0.14), (30, "#ffe2a8")),
                   ("guard", (300, 0, "#ffe8c0", 0.12), (25, "#ffe2a8")),
                   ("school", (1700, 0, "#fff6d0", 0.18), (20, "#ffffff")),
                   ("gym", (300, 0, "#ffe8c0", 0.14), (30, "#ffe2a8")),
                   ("move_map", None, None),
                   ("grifters", (960, 230, "#ffcf7a", 0.14), (35, "#ffd9a0"))):
    chibi_post(nm, li, pa)
