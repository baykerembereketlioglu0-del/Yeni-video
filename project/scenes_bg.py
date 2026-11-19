# -*- coding: utf-8 -*-
"""Backgrounds and props shared by all scenes (same outline, same palette)."""
import math, random
import skia
from gfx import (G, W, H, PAL, OUTLINE, C, P_fill, P_stroke, shade, tint, mix, clamp, lerp,
                 ease_io, ease_out, ease_back, pop, wob, text, text_w)

# ================================================================== generic pieces
def sky(g, top, bottom, mid=None, h=H):
    stops = [(0, top), (1, bottom)] if mid is None else [(0, top), (0.55, mid), (1, bottom)]
    g.vgrad(0, 0, W, h, stops)

def stars(g, t, n=70, seed=3, h=600, a=0.9):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(0, W); y = rnd.uniform(0, h); r = rnd.uniform(1.2, 3.2)
        tw = 0.55 + 0.45 * math.sin(t * rnd.uniform(1, 3) + i)
        g.fillp(G.circle_p(x, y, r), "#fff6d8", a * tw)

def sun(g, x, y, r, col="#ffd166", stripes=True, bg=None):
    g.glow(x, y, r * 2.4, col, 0.35)
    p = G.circle_p(x, y, r)
    g.fillp(p, col)
    if stripes and bg:
        for k in range(5):
            yy = y + r * (0.15 + k * 0.17); hh = r * (0.03 + k * 0.022)
            g.c.save(); g.c.clipPath(p, doAntiAlias=True)
            g.rect_fill(x - r, yy, 2 * r, hh, bg)
            g.c.restore()

def palm(g, x, y, s=1.0, t=0.0, col="#2a6b4f", trunk="#8a5a3a", flip=False, sil=None):
    """palm tree, base at (x, y)."""
    g.save(); g.tr(x, y); g.sc(-s if flip else s, s)
    sway = math.sin(t * 1.3 + x * 0.01) * 2.5
    tp = skia.Path(); tp.moveTo(-9, 0); tp.cubicTo(-6, -120, 10, -220, 22 + sway, -300)
    tp.lineTo(34 + sway, -296); tp.cubicTo(24, -210, 10, -120, 9, 0); tp.close()
    if sil:
        g.fillp(tp, sil)
    else:
        g.shape(tp, trunk)
        for k in range(1, 9):
            yy = -k * 33
            g.line(-8 + k * 2.5 + (k / 9) * sway * 0.5, yy, 9 + k * 2.6 + (k / 9) * sway * 0.5, yy - 4, w=g.lw * 0.6, color=shade(trunk, 0.7))
    cx, cy = 28 + sway, -300
    for ang, ln in ((-170, 150), (-140, 165), (-100, 120), (-60, 160), (-20, 150), (15, 120), (-205, 120)):
        a = math.radians(ang + math.sin(t * 1.5 + ang) * 3)
        ex, ey = cx + math.cos(a) * ln, cy + math.sin(a) * ln * 0.55 + 55
        mx, my = cx + math.cos(a) * ln * 0.5, cy + math.sin(a) * ln * 0.3 - 30
        q = skia.Path(); q.moveTo(cx, cy)
        nx, ny = -(ey - cy), (ex - cx); nl = math.hypot(nx, ny) or 1; nx /= nl; ny /= nl
        q.quadTo(mx + nx * 26, my + ny * 26, ex, ey)
        q.quadTo(mx - nx * 6, my - ny * 6, cx, cy); q.close()
        if sil: g.fillp(q, sil)
        else: g.shape(q, col)
    if not sil:
        for k in range(3):
            g.circle(cx - 8 + k * 9, cy + 8, 8, "#6b4a2a")
    g.restore()

def building(g, x, y_base, w, h, col, win_col="#ffe28a", lit=0.5, seed=1, t=0.0, roof=None, outline=True):
    rnd = random.Random(seed)
    p = G.rrect_p(x, y_base - h, w, h + 10, 4)
    if outline: g.shape(p, col)
    else: g.fillp(p, col)
    cols = max(2, int(w // 34)); rows = max(2, int(h // 46))
    ww = w / cols
    for i in range(cols):
        for j in range(rows):
            if rnd.random() < lit:
                fl = 1.0 if rnd.random() > 0.05 else (0.6 + 0.4 * math.sin(t * 3 + i * j))
                g.fillp(G.rrect_p(x + i * ww + ww * 0.25, y_base - h + 18 + j * 46, ww * 0.5, 22, 3), win_col, 0.85 * fl)
    if roof == "antenna":
        g.line(x + w * 0.5, y_base - h, x + w * 0.5, y_base - h - 50, w=g.lw * 0.8)
        g.circle(x + w * 0.5, y_base - h - 52, 5, "#ff4d4d", w=g.lw * 0.5)

def skyline_lc(g, y_base, t=0.0, night=True, a=1.0, scale=1.0, x0=0, width=W):
    """Liberty City: tall dense towers, cool colours."""
    rnd = random.Random(11)
    x = x0 - 40
    while x < x0 + width + 40:
        w = rnd.uniform(90, 170) * scale; h = rnd.uniform(250, 560) * scale
        col = mix("#3b4466", "#2a2f4a", rnd.random()) if night else mix("#8aa0c8", "#6f86b0", rnd.random())
        building(g, x, y_base, w, h, col, "#ffe28a" if night else "#d9ecff", 0.45, seed=int(x), t=t,
                 roof="antenna" if rnd.random() < 0.3 else None)
        x += w - 6

def skyline_vice(g, y_base, t=0.0, a=1.0, sunset=True, scale=1.0):
    rnd = random.Random(5)
    x = -30
    cols = ["#5b3b7a", "#6c4189", "#4a3570", "#7a4b8f", "#3e2f63"] if sunset else ["#2b2550", "#33285e", "#251f48"]
    while x < W + 40:
        w = rnd.uniform(80, 150) * scale; h = rnd.uniform(140, 380) * scale
        building(g, x, y_base, w, h, rnd.choice(cols), "#ffd38a" if sunset else "#ff8adf", 0.35, seed=int(x) + 3, t=t,
                 outline=True)
        if rnd.random() < 0.35:   # neon trim
            g.line(x + 6, y_base - h + 6, x + w - 6, y_base - h + 6, color=rnd.choice(["#ff5fa2", "#2ff3e0", "#ffd166"]), w=5,
                   a=0.85 + 0.15 * math.sin(t * 4 + x))
        x += w + rnd.uniform(-10, 14)

def ocean(g, y, h, col_top="#ff9a8b", col_bot="#5b3b7a", t=0.0, sparkle="#ffe5b0"):
    g.vgrad(0, y, W, h, [(0, col_top), (1, col_bot)])
    rnd = random.Random(9)
    for i in range(36):
        xx = (rnd.uniform(0, W) + t * 12 * (1 + i % 3)) % (W + 100) - 50
        yy = y + rnd.uniform(8, h - 10)
        ww = rnd.uniform(30, 90) * (0.4 + (yy - y) / h)
        g.line(xx, yy, xx + ww, yy, color=sparkle, w=4, a=0.5)

def floor(g, y, col, line=True):
    g.rect_fill(0, y, W, H - y, col)
    if line: g.line(-10, y, W + 10, y, w=g.lw)

def wall(g, col, y_floor, wainscot=None, stripes=None):
    g.rect_fill(0, 0, W, y_floor, col)
    if stripes:
        for i in range(0, W, stripes[0] * 2):
            g.rect_fill(i, 0, stripes[0], y_floor, stripes[1], 0.25)
    if wainscot:
        g.rect_fill(0, y_floor - 150, W, 150, wainscot)
        g.line(-10, y_floor - 150, W + 10, y_floor - 150, w=g.lw)

def window(g, x, y, w, h, view, t=0.0, frame="#fbf7f0", curtains=None):
    p = G.rrect_p(x, y, w, h, 10)
    g.c.save(); g.c.clipPath(p, doAntiAlias=True)
    g.save(); g.tr(x, y)
    view(g, w, h, t)
    g.restore()
    g.c.restore()
    g.shape(p, None, w=g.lw)
    g.rrect(x - 12, y - 12, w + 24, 18, 6, frame)
    g.rrect(x - 18, y + h - 4, w + 36, 22, 6, frame)
    g.line(x + w / 2, y, x + w / 2, y + h, w=g.lw * 1.4, color=OUTLINE)
    g.line(x + w / 2, y, x + w / 2, y + h, w=g.lw * 0.6, color=frame)
    g.line(x, y + h * 0.45, x + w, y + h * 0.45, w=g.lw * 1.4, color=OUTLINE)
    g.line(x, y + h * 0.45, x + w, y + h * 0.45, w=g.lw * 0.6, color=frame)
    if curtains:
        for side in (0, 1):
            cx = x - 40 if side == 0 else x + w - 30
            q = skia.Path(); q.moveTo(cx, y - 25); q.lineTo(cx + 70, y - 25)
            q.cubicTo(cx + 40, y + h * 0.4, cx + 80, y + h * 0.8, cx + 60, y + h + 30)
            q.lineTo(cx + 5, y + h + 30); q.cubicTo(cx + 20, y + h * 0.6, cx - 10, y + h * 0.3, cx, y - 25); q.close()
            g.shape(q, curtains)

def view_lc_night(g, w, h, t):
    g.vgrad(0, 0, w, h, [(0, "#1d1b3a"), (1, "#3a3a6a")])
    g.save(); g.sc(0.6); stars(g, t, 25, seed=4, h=h / 0.6 * 0.5); g.restore()
    g.save(); g.sc(0.55)
    skyline_lc(g, h / 0.55 + 10, t, True, width=w / 0.55)
    g.restore()

def view_lc_day(g, w, h, t):
    g.vgrad(0, 0, w, h, [(0, "#9fd0f0"), (1, "#d9eef9")])
    g.save(); g.sc(0.55)
    skyline_lc(g, h / 0.55 + 10, t, False, width=w / 0.55)
    g.restore()

def view_vice(g, w, h, t):
    g.vgrad(0, 0, w, h, [(0, "#ff8a5c"), (0.6, "#ffb37a"), (1, "#ffd6a0")])
    sun(g, w * 0.5, h * 0.62, h * 0.22, "#fff1b8")
    g.save(); g.sc(0.5)
    skyline_vice(g, h / 0.5 + 10, t)
    g.restore()
    palm(g, w * 0.15, h + 10, 0.55, t, sil="#3a2552")
    palm(g, w * 0.85, h + 10, 0.5, t, sil="#3a2552", flip=True)

def view_prison(g, w, h, t):
    g.vgrad(0, 0, w, h, [(0, "#8fc7ec"), (1, "#cfe8f6")])
    g.rect_fill(0, h * 0.7, w, h * 0.3, "#a7b38a")

def view_moon(g, w, h, t):
    g.vgrad(0, 0, w, h, [(0, "#14122e"), (1, "#2b2856")])
    g.save(); g.sc(0.6); stars(g, t, 18, seed=8, h=h / 0.6); g.restore()
    g.glow(w * 0.62, h * 0.35, h * 0.4, "#fff6d8", 0.25)
    g.circle(w * 0.62, h * 0.35, h * 0.13, "#fff3c4", w=g.lw * 0.6)

def bars(g, x, y, w, h, n, col="#5e6270", t=0.0, wdt=16):
    for i in range(n):
        xx = x + (i + 0.5) * w / n
        g.rrect(xx - wdt / 2, y, wdt, h, wdt / 2, col)
        g.line(xx - wdt * 0.15, y + 10, xx - wdt * 0.15, y + h - 10, color=tint(col, 0.35), w=3)
    g.rrect(x - 10, y - 14, w + 20, 26, 8, shade(col, 0.9))
    g.rrect(x - 10, y + h - 12, w + 20, 26, 8, shade(col, 0.9))

# ================================================================== furniture & props
def crib(g, x, y, w=420, h=220, col="#c98e5a"):
    g.rrect(x - w / 2, y - h, 26, h + 40, 10, col)
    g.rrect(x + w / 2 - 26, y - h, 26, h + 40, 10, col)
    g.rrect(x - w / 2, y - h, w, 26, 10, tint(col, 0.15))
    n = 9
    for i in range(1, n):
        xx = x - w / 2 + i * w / n
        g.rrect(xx - 6, y - h + 20, 12, h - 20, 6, tint(col, 0.1))
    g.rrect(x - w / 2, y - 30, w, 34, 10, col)

def crib_front(g, x, y, w=420, h=150, col="#c98e5a"):
    """Front rail only (drawn over the baby)."""
    n = 9
    for i in range(1, n):
        xx = x - w / 2 + i * w / n
        g.rrect(xx - 7, y - h + 20, 14, h - 10, 6, tint(col, 0.1))
    g.rrect(x - w / 2 - 10, y - h, w + 20, 26, 10, tint(col, 0.15))
    g.rrect(x - w / 2 - 10, y - 20, w + 20, 34, 10, col)
    g.rrect(x - w / 2 - 22, y - h - 30, 30, h + 70, 10, col)
    g.rrect(x + w / 2 - 8, y - h - 30, 30, h + 70, 10, col)

def table(g, x, y, w, h=26, col="#a8744a", legs=110):
    for side in (-1, 1):
        g.rrect(x + side * (w / 2 - 40) - 9, y, 18, legs, 6, shade(col, 0.85))
    g.rrect(x - w / 2, y - h, w, h, 8, col)

def chair_back(g, x, y, col="#7a5236"):
    g.rrect(x - 55, y - 170, 110, 150, 16, col)
    g.rrect(x - 60, y - 30, 120, 26, 8, shade(col, 0.9))

def bunk(g, x, y, w=520, col="#7a8494"):
    g.rrect(x - w / 2, y - 60, w, 40, 10, "#e9e3d6")
    g.rrect(x - w / 2, y - 26, w, 22, 6, col)
    for side in (-1, 1):
        g.rrect(x + side * (w / 2 - 14) - 10, y - 26, 20, 90, 6, shade(col, 0.85))
    g.rrect(x - w / 2 + 20, y - 92, 120, 40, 18, "#fbf7f0")

def punching_bag(g, x, y_top, ang=0.0, col="#e2483d"):
    g.line(x, y_top - 80, x, y_top, w=g.lw * 0.8)
    g.save(); g.tr(x, y_top); g.rot(ang)
    g.line(0, 0, 0, 30, w=g.lw * 1.2)
    g.rrect(-62, 30, 124, 300, 50, col)
    g.rrect(-64, 70, 128, 22, 6, "#2b2233", w=g.lw * 0.6)
    g.rrect(-64, 270, 128, 22, 6, "#2b2233", w=g.lw * 0.6)
    g.fillp(G.rrect_p(-40, 50, 22, 240, 11), "#ffffff", 0.25)
    g.restore()

def car(g, x, y, s=1.0, col="#d63d3d", t=0.0, flip=False, driving=False, people=None, lights=False,
        windows_dark=False, roof_col=None):
    """Chibi coupe, side view. (x, y) = ground centre."""
    g.save(); g.tr(x, y); g.sc(-s if flip else s, s)
    bounce = math.sin(t * 2 * math.pi * 3) * 2.2 if driving else 0
    g.shadow(0, 4, 250, 18, 0.25)
    g.save(); g.tr(0, bounce)
    body = skia.Path()
    body.moveTo(-250, -40); body.cubicTo(-255, -95, -230, -110, -190, -112)
    body.lineTo(-120, -118); body.cubicTo(-90, -185, -50, -195, 20, -195)
    body.cubicTo(90, -195, 120, -170, 150, -120)
    body.lineTo(215, -110); body.cubicTo(250, -105, 258, -80, 255, -40)
    body.cubicTo(250, -18, 230, -14, 200, -14); body.lineTo(-210, -14)
    body.cubicTo(-238, -14, -250, -22, -250, -40); body.close()
    g.shape(body, col)
    g.fillp(G.rrect_p(-235, -70, 470, 10, 5), shade(col, 0.8))
    # windows
    wcol = "#2d3550" if windows_dark else "#bfe6ff"
    win = skia.Path()
    win.moveTo(-100, -122); win.cubicTo(-80, -172, -50, -180, -20, -180); win.lineTo(-20, -122); win.close()
    win2 = skia.Path()
    win2.moveTo(0, -122); win2.lineTo(0, -180); win2.cubicTo(70, -180, 95, -160, 122, -122); win2.close()
    if people:
        for (px, draw_fn) in people:
            g.c.save()
            clip = skia.Path(); clip.addPath(win); clip.addPath(win2)
            g.c.clipPath(clip, doAntiAlias=True)
            g.fillp(win, wcol); g.fillp(win2, wcol)
            draw_fn(g, px)
            g.c.restore()
        g.strokep(win); g.strokep(win2)
    else:
        g.shape(win, wcol); g.shape(win2, wcol)
        g.fillp(G.poly_p([(-80, -128), (-55, -172), (-40, -172), (-65, -128)]), "#ffffff", 0.5)
    g.line(-235, -60, 240, -60, color=shade(col, 0.75), w=g.lw * 0.6)
    g.rrect(-20, -95, 34, 8, 4, "#e9e3d6", w=g.lw * 0.5)
    # lights
    g.ellipse(242, -78, 12, 9, "#fff1b8", w=g.lw * 0.6)
    g.ellipse(-243, -78, 10, 9, "#ff6b5b", w=g.lw * 0.6)
    if lights:
        g.glow(300, -78, 120, "#fff1b8", 0.45)
    g.restore()
    # wheels
    for wx in (-150, 150):
        g.save(); g.tr(wx, -14)
        g.circle(0, 0, 48, "#2b2233")
        g.circle(0, 0, 24, "#c9cad1", w=g.lw * 0.7)
        ang = (t * 720 if driving else 0)
        g.rot(ang)
        for k in range(5):
            g.line(0, 0, 0, -20, w=g.lw * 0.6)
            g.rot(72)
        g.restore()
    g.restore()

def police_car(g, x, y, s=1.0, t=0.0, flip=False, driving=False):
    g.save(); g.tr(x, y); g.sc(-s if flip else s, s)
    bounce = math.sin(t * 2 * math.pi * 3 + 1) * 2 if driving else 0
    g.shadow(0, 4, 250, 18, 0.25)
    g.save(); g.tr(0, bounce)
    body = skia.Path()
    body.moveTo(-250, -40); body.cubicTo(-252, -100, -230, -112, -190, -112)
    body.lineTo(-110, -116); body.lineTo(-70, -180); body.lineTo(110, -180); body.lineTo(150, -116)
    body.lineTo(215, -110); body.cubicTo(250, -105, 258, -80, 255, -40)
    body.cubicTo(250, -18, 230, -14, 200, -14); body.lineTo(-210, -14)
    body.cubicTo(-238, -14, -250, -22, -250, -40); body.close()
    g.shape(body, "#fbf7f0")
    g.c.save(); g.c.clipPath(body, doAntiAlias=True)
    g.rect_fill(-260, -75, 520, 70, "#2b2233")
    g.c.restore(); g.strokep(body)
    g.poly([(-90, -120), (-60, -170), (10, -170), (10, -120)], "#bfe6ff")
    g.poly([(25, -120), (25, -170), (100, -170), (130, -120)], "#bfe6ff")
    blink = (t * 4) % 1 < 0.5
    g.rrect(-40, -205, 40, 24, 6, "#ff3b3b" if blink else "#7a2020")
    g.rrect(0, -205, 40, 24, 6, "#3b6bff" if not blink else "#20307a")
    g.glow(-20, -195, 150, "#ff3b3b", 0.5 if blink else 0.1)
    g.glow(20, -195, 150, "#3b6bff", 0.5 if not blink else 0.1)
    text(g, "POLICE", 0, -32, 34, fill="#fbf7f0", outline=None, shadow=False)
    g.restore()
    for wx in (-150, 150):
        g.save(); g.tr(wx, -14)
        g.circle(0, 0, 48, "#2b2233"); g.circle(0, 0, 24, "#c9cad1", w=g.lw * 0.7)
        g.rot(t * 720 if driving else 0)
        for k in range(5): g.line(0, 0, 0, -20, w=g.lw * 0.6); g.rot(72)
        g.restore()
    g.restore()

def helicopter(g, x, y, s=1.0, t=0.0, beam=True):
    g.save(); g.tr(x, y); g.sc(s)
    if beam:
        q = skia.Path(); q.moveTo(-20, 40); q.lineTo(20, 40); q.lineTo(260, 900); q.lineTo(-180, 900); q.close()
        sh = skia.GradientShader.MakeLinear([skia.Point(0, 40), skia.Point(0, 900)], [C("#fff6c8", 0.45), C("#fff6c8", 0.0)], [0, 1])
        g.fillp(q, "#ffffff", 1.0, shader=sh)
    g.rrect(60, -18, 230, 26, 12, "#3b3f55")
    g.poly([(270, -40), (300, -40), (300, 10), (275, 10)], "#3b3f55")
    g.ellipse(0, 0, 110, 62, "#3b3f55")
    g.ellipse(-35, -10, 55, 38, "#8fd3ff")
    g.line(-70, 70, 70, 70, w=g.lw * 1.6); g.line(-40, 55, -50, 70); g.line(40, 55, 50, 70)
    g.line(0, -62, 0, -80, w=g.lw)
    k = math.sin(t * 40)
    g.line(-170 * k, -82, 170 * k, -82, w=g.lw * 1.6)
    g.restore()

def alligator(g, x, y, s=1.0, t=0.0, flip=False, mouth=0.0, sunglasses=False):
    g.save(); g.tr(x, y); g.sc(-s if flip else s, s)
    body = skia.Path()
    body.moveTo(-160, 0); body.cubicTo(-120, -40, 40, -55, 100, -40)
    body.lineTo(190, -40 - mouth * 30); body.cubicTo(205, -38 - mouth * 30, 205, -22 - mouth * 20, 190, -22 - mouth * 10)
    body.lineTo(110, -18); body.lineTo(190, -10 + mouth * 10); body.cubicTo(205, -8, 205, 8, 190, 8)
    body.lineTo(60, 10); body.cubicTo(0, 14, -100, 12, -160, 0); body.close()
    g.shape(body, "#4f9a52")
    for k in range(6):
        g.circle(-110 + k * 30, -30 + abs(k - 3) * 2, 7, "#3f7d43", w=g.lw * 0.5)
    g.circle(95, -48, 16, "#4f9a52"); g.circle(97, -50, 7, "#2b2233", w=0)
    g.fillp(G.circle_p(99, -53, 2.5), "#ffffff")
    if sunglasses:
        g.rrect(78, -60, 40, 18, 6, "#1a1020")
    g.restore()

def phone_frame(g, x, y, w, h, live=True, t=0.0, body=True, overlay=True):
    if body:
        g.rrect(x - 14, y - 14, w + 28, h + 28, 34, "#2b2233")
    if not overlay:
        return
    g.rrect(x + w / 2 - 50, y - 6, 100, 16, 8, "#1a1020", w=0)
    if live:
        g.rrect(x + 20, y + 26, 92, 40, 10, "#ff3b5c", w=g.lw * 0.6)
        text(g, "LIVE", x + 66, y + 58, 30, fill="#ffffff", outline=None, shadow=False)
        text(g, "12.4K watching", x + w - 20, y + 56, 24, fill="#ffffff", outline=OUTLINE, ow=5, align="right",
             name="ui", shadow=False)

def hearts(g, x, y, t, t0, n=7, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + i * 0.25
        if t < st: continue
        k = (t - st) / 2.0
        if k > 1: continue
        xx = x + rnd.uniform(-30, 30) + math.sin(k * 6 + i) * 20
        yy = y - k * 300
        heart(g, xx, yy, 22 * (1 - k * 0.3), a=1 - k)

def heart(g, x, y, s, col="#ff4d6d", a=1.0):
    q = skia.Path()
    q.moveTo(x, y + s * 0.9)
    q.cubicTo(x - s * 1.6, y - s * 0.2, x - s * 0.7, y - s * 1.3, x, y - s * 0.45)
    q.cubicTo(x + s * 0.7, y - s * 1.3, x + s * 1.6, y - s * 0.2, x, y + s * 0.9); q.close()
    g.shape(q, col, a=a, w=g.lw * 0.7)

def clover(g, x, y, s, t=0.0):
    g.save(); g.tr(x, y); g.rot(math.sin(t * 2) * 8)
    g.line(0, 0, 10, 70, w=g.lw * 1.8, color=OUTLINE); g.line(0, 0, 10, 70, w=g.lw * 0.8, color="#3f9a4f")
    for k in range(4):
        g.save(); g.rot(k * 90 + 45)
        heart_leaf = skia.Path()
        heart_leaf.moveTo(0, 0)
        heart_leaf.cubicTo(-s * 0.9, -s * 0.4, -s * 0.6, -s * 1.3, 0, -s * 0.85)
        heart_leaf.cubicTo(s * 0.6, -s * 1.3, s * 0.9, -s * 0.4, 0, 0); heart_leaf.close()
        g.shape(heart_leaf, "#4fbf5f")
        g.restore()
    g.restore()

def dream_bubble(g, x, y, w, h, k, content=None, t=0.0, tail=(0, 0)):
    """thought bubble that scales in with k (0..1). content(g, cx, cy, w, h)"""
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    tx, ty = tail
    for i, rr in enumerate((12, 18, 26)):
        g.circle(tx * (1 - i / 3.0), ty * (1 - i / 3.0), rr, "#ffffff", w=g.lw * 0.8)
    pts = []
    n = 14
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = 1 + 0.08 * math.sin(i * 2.3)
        pts.append((math.cos(a) * w / 2 * rr, math.sin(a) * h / 2 * rr))
    g.smooth(pts, "#ffffff")
    if content:
        clip = G.ellipse_p(0, 0, w / 2 - 14, h / 2 - 14)
        g.c.save(); g.c.clipPath(clip, doAntiAlias=True)
        content(g, 0, 0, w - 28, h - 28)
        g.c.restore()
    g.restore()

def good_life_content(g, cx, cy, w, h, t=0.0):
    g.vgrad(cx - w / 2, cy - h / 2, w, h, [(0, "#ffb37a"), (1, "#ffe0a8")])
    sun(g, cx + w * 0.15, cy - h * 0.05, h * 0.2, "#fff1b8")
    g.rect_fill(cx - w / 2, cy + h * 0.18, w, h, "#7fd0e8")
    g.rect_fill(cx - w / 2, cy + h * 0.3, w, h, "#f3d9a0")
    # small house
    g.rrect(cx - w * 0.38, cy - h * 0.02, w * 0.3, h * 0.3, 6, "#fbf7f0", w=g.lw * 0.6)
    g.poly([(cx - w * 0.42, cy), (cx - w * 0.23, cy - h * 0.2), (cx - w * 0.04, cy)], "#e2483d", w=g.lw * 0.6)
    g.save(); g.sc(0.35); palm(g, (cx + w * 0.32) / 0.35, (cy + h * 0.35) / 0.35, 1.0, t); g.restore()

def icon_record(g, x, y, s):
    g.save(); g.tr(x, y); g.sc(s)
    g.rrect(-50, -65, 100, 130, 10, "#f6ead2")
    g.rrect(-30, -50, 40, 46, 6, "#c9cad1", w=g.lw * 0.6)
    for k in range(4):
        g.line(-30, 14 + k * 14, 32, 14 + k * 14, w=g.lw * 0.7)
    g.restore()

def icon_gun(g, x, y, s):
    g.save(); g.tr(x, y); g.sc(s)
    q = skia.Path()
    q.moveTo(-70, -30); q.lineTo(60, -30); q.lineTo(60, -6); q.lineTo(-10, -6)
    q.lineTo(-18, 40); q.lineTo(-50, 40); q.lineTo(-40, -6); q.lineTo(-70, -6); q.close()
    g.shape(q, "#5e6270")
    g.restore()

def icon_tooth(g, x, y, s):
    g.save(); g.tr(x, y); g.sc(s)
    q = skia.Path()
    q.moveTo(-40, -40); q.cubicTo(-20, -60, 20, -60, 40, -40); q.cubicTo(55, -10, 30, 10, 28, 50)
    q.cubicTo(20, 60, 8, 40, 0, 20); q.cubicTo(-8, 40, -20, 60, -28, 50); q.cubicTo(-30, 10, -55, -10, -40, -40); q.close()
    g.shape(q, "#fbf7f0")
    g.restore()

def no_sign(g, x, y, r, k=1.0):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    q = G.circle_p(0, 0, r)
    g.strokep(q, OUTLINE, w=r * 0.3); g.strokep(q, PAL["red"], w=r * 0.18)
    g.line(-r * 0.7, r * 0.7, r * 0.7, -r * 0.7, color=OUTLINE, w=r * 0.3)
    g.line(-r * 0.7, r * 0.7, r * 0.7, -r * 0.7, color=PAL["red"], w=r * 0.18)
    g.restore()

def badge_icon(g, x, y, r, k, draw_fn):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    g.circle(0, 0, r, "#fbf7f0", w=g.lw * 1.1)
    draw_fn(g)
    g.restore()

def pow_burst(g, x, y, r, k, word="POW!", col="#ffd166"):
    if k <= 0: return
    g.save(); g.tr(x, y); g.sc(k)
    pts = []
    for i in range(24):
        a = i / 24 * 2 * math.pi
        rr = r if i % 2 == 0 else r * 0.62
        pts.append((math.cos(a) * rr, math.sin(a) * rr * 0.8))
    g.poly(pts, col)
    text(g, word, 0, r * 0.18, r * 0.5, fill=PAL["red"], ow=r * 0.08, rot=-8)
    g.restore()

def speed_lines(g, t, col="#ffffff", a=0.35, y0=0, y1=H, n=24, seed=1, speed=2600):
    rnd = random.Random(seed)
    for i in range(n):
        yy = rnd.uniform(y0, y1)
        ln = rnd.uniform(120, 380)
        xx = W - ((t * speed * rnd.uniform(0.7, 1.3) + rnd.uniform(0, W * 2)) % (W * 2 + ln))
        g.line(xx, yy, xx + ln, yy, color=col, w=rnd.uniform(3, 7), a=a)

def light_rays(g, x, y, t, col="#fff6c8", a=0.25, n=12):
    for i in range(n):
        ang = i / n * 2 * math.pi + t * 0.15
        q = skia.Path(); q.moveTo(x, y)
        q.lineTo(x + math.cos(ang - 0.08) * 1600, y + math.sin(ang - 0.08) * 1600)
        q.lineTo(x + math.cos(ang + 0.08) * 1600, y + math.sin(ang + 0.08) * 1600); q.close()
        g.fillp(q, col, a)

def vignette(g, a=0.35):
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.72, [C("#000000", 0), C("#000000", 0), C("#120a1a", a)], [0, 0.6, 1])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    g.c.drawRect(skia.Rect.MakeWH(W, H), p)

def leonida_map(g, k, t):
    """stylised east coast: Liberty City up north, Leonida peninsula down south."""
    g.vgrad(0, 0, W, H, [(0, "#7fc8e8"), (1, "#5fb0d8")])
    rnd = random.Random(3)
    for i in range(40):
        xx = rnd.uniform(0, W); yy = rnd.uniform(0, H)
        g.line(xx, yy, xx + 40, yy, color="#ffffff", w=3, a=0.25)
    land = [(560, -40), (980, -40), (1010, 120), (930, 240), (900, 380), (850, 470), (880, 600), (930, 700),
            (1010, 800), (1060, 930), (1040, 1030), (990, 1050), (930, 960), (870, 840), (800, 760), (690, 720),
            (560, 700), (400, 690), (300, 660), (200, 700), (-40, 700), (-40, -40)]
    g.smooth(land, "#f3d9a0")
    g.c.save(); g.c.clipPath(G.smooth_p(land), doAntiAlias=True)
    g.rect_fill(0, 0, W, 360, "#a7c98a", 0.6)
    g.c.restore()
    g.smooth(land, None)
    # keys
    for i in range(6):
        g.ellipse(960 - i * 55, 1060 + i * 6, 26, 10, "#f3d9a0", w=g.lw * 0.6)
    # LC star + label
    lcx, lcy = 820, 140
    vcx, vcy = 1010, 880
    g.circle(lcx, lcy, 16, PAL["red"], w=g.lw * 0.8)
    text(g, "LIBERTY CITY", lcx - 240, lcy + 15, 46, fill="#fbf7f0")
    g.circle(vcx, vcy, 16, PAL["pink"], w=g.lw * 0.8)
    text(g, "VICE CITY", vcx + 210, vcy + 15, 46, fill="#fbf7f0")
    text(g, "LEONIDA", 760, 860, 70, fill="#ffffff", a=clamp(k * 2 - 1), rot=-6)
    # route
    route = [(lcx, lcy), (900, 300), (860, 450), (900, 640), (vcx, vcy)]
    path = G.smooth_p(route, close=False)
    meas = skia.PathMeasure(path, False)
    L = meas.getLength()
    dash = skia.Path()
    seg = 0
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=9, Color=C("#ffffff"))
    p.setStrokeCap(skia.Paint.kRound_Cap)
    p.setPathEffect(skia.DashPathEffect.Make([22, 18], 0))
    q = skia.Path()
    meas.getSegment(0, L * k, q, True)
    g.c.drawPath(q, P_stroke(OUTLINE, 15))
    g.c.drawPath(q, p)
    pos = meas.getPosTan(L * k)
    if pos:
        (px, py), (tx, ty) = pos if isinstance(pos[0], tuple) else ((pos[0].x(), pos[0].y()), (pos[1].x(), pos[1].y()))
        g.save(); g.tr(px, py); g.sc(0.22)
        car(g, 0, 40, 1.0, "#d6a13d", t, driving=True, flip=tx < 0)
        g.restore()
