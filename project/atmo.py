# -*- coding: utf-8 -*-
"""Cinematic layer used by every scene: depth-of-field blur, light shafts, floating particles,
bokeh, colour grade, vignette, film grain, and the channel-style on-screen labels."""
import math, random
import numpy as np
import skia
from gfx import G, W, H, PAL, OUTLINE, C, P_fill, P_stroke, clamp, lerp, ease_out, ease_back, ease_io, text, text_w

# ------------------------------------------------------------ layers
class blur_layer:
    """with blur_layer(g, 4): draw background...  -> drawn content is blurred (depth of field)"""
    def __init__(self, g, sigma):
        self.g = g; self.sigma = sigma
    def __enter__(self):
        if self.sigma > 0:
            p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(self.sigma, self.sigma, skia.TileMode.kClamp))
            self.g.c.saveLayer(None, p)
        return self
    def __exit__(self, *a):
        if self.sigma > 0:
            self.g.c.restore()

def grade(g, top, bottom, a=0.25, mode=skia.BlendMode.kSoftLight):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C(top, a), C(bottom, a)], [0, 1])
    p = skia.Paint(); p.setShader(sh); p.setBlendMode(mode)
    g.c.drawRect(skia.Rect.MakeWH(W, H), p)

def tint_overlay(g, col, a=0.15, mode=skia.BlendMode.kMultiply):
    p = skia.Paint(Color=C(col, a)); p.setBlendMode(mode)
    g.c.drawRect(skia.Rect.MakeWH(W, H), p)

def vignette(g, a=0.45):
    sh = skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), W * 0.7, [C("#000000", 0), C("#000000", 0), C("#0a0610", a)],
                                        [0, 0.55, 1])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    g.c.drawRect(skia.Rect.MakeWH(W, H), p)

_GRAIN = None
def grain(g, t, a=0.06):
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(1)
        n = (rng.normal(128, 40, (540, 960))).clip(0, 255).astype(np.uint8)
        rgba = np.dstack([n, n, n, np.full_like(n, 255)])
        _GRAIN = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)
    k = int(t * 24) % 8
    ox, oy = (k * 137) % 400, (k * 211) % 300
    p = skia.Paint(); p.setAlphaf(a); p.setBlendMode(skia.BlendMode.kOverlay)
    g.c.save(); g.c.scale(2.2, 2.2)
    g.c.drawImage(_GRAIN, -ox / 2.2, -oy / 2.2, skia.SamplingOptions(), p)
    g.c.restore()

def shafts(g, x, y, t, col="#fff3c8", a=0.22, n=7, spread=0.55, angle=100, length=1700, seed=2):
    """soft light shafts from (x, y) pointing at `angle` degrees."""
    rnd = random.Random(seed)
    for i in range(n):
        ang = math.radians(angle + (i - n / 2) * spread * 12 / n + math.sin(t * 0.4 + i) * 1.2)
        w = rnd.uniform(0.04, 0.09)
        q = skia.Path(); q.moveTo(x, y)
        q.lineTo(x + math.cos(ang - w) * length, y + math.sin(ang - w) * length)
        q.lineTo(x + math.cos(ang + w) * length, y + math.sin(ang + w) * length); q.close()
        sh = skia.GradientShader.MakeRadial(skia.Point(x, y), length, [C(col, a * rnd.uniform(0.5, 1)), C(col, 0)], [0, 1])
        p = skia.Paint(AntiAlias=True); p.setShader(sh)
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
        g.c.drawPath(q, p)

def beam(g, x0, y0, x1, y1, w0, w1, t, col="#fff6d8", a=0.28):
    """window light beam (trapezoid) from x0,y0 (width w0) to x1,y1 (width w1)."""
    q = skia.Path()
    q.moveTo(x0 - w0 / 2, y0); q.lineTo(x0 + w0 / 2, y0); q.lineTo(x1 + w1 / 2, y1); q.lineTo(x1 - w1 / 2, y1); q.close()
    sh = skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [C(col, a), C(col, 0.0)], [0, 1])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    g.c.drawPath(q, p)

def particles(g, t, n=60, col="#ffe2a8", seed=3, region=(0, 0, W, H), size=(2, 5), speed=18, a=0.75, rise=True):
    rnd = random.Random(seed)
    x0, y0, w, h = region
    for i in range(n):
        px = rnd.uniform(0, w); py = rnd.uniform(0, h); s = rnd.uniform(*size); sp_ = rnd.uniform(0.5, 1.4) * speed
        ph = rnd.uniform(0, 6.28)
        yy = (py - t * sp_) % h if rise else (py + t * sp_) % h
        xx = (px + math.sin(t * 0.5 + ph) * 20) % w
        tw = 0.55 + 0.45 * math.sin(t * 1.7 + ph)
        p = skia.Paint(AntiAlias=True, Color=C(col, a * tw))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, s * 0.8))
        g.c.drawCircle(x0 + xx, y0 + yy, s, p)

def bokeh(g, t, n=26, cols=("#ff5fa2", "#2ff3e0", "#ffd166", "#ff8a5c", "#b38aff"), seed=12, region=(0, 0, W, 700),
          drift=30, a=0.45, rmin=25, rmax=80):
    rnd = random.Random(seed)
    x0, y0, w, h = region
    for i in range(n):
        xx = (rnd.uniform(0, w) - t * drift * rnd.uniform(0.5, 1.5)) % (w + 200) - 100
        yy = rnd.uniform(0, h); r = rnd.uniform(rmin, rmax)
        p = skia.Paint(AntiAlias=True, Color=C(rnd.choice(cols), a * rnd.uniform(0.5, 1)))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, r * 0.25))
        g.c.drawCircle(x0 + xx, y0 + yy, r, p)

def glow_at(g, x, y, r, col, a=0.5):
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [C(col, a), C(col, 0)], [0, 1])
    p = skia.Paint(AntiAlias=True); p.setShader(sh)
    g.c.drawCircle(x, y, r, p)

def ground_shadow(g, x, y, rx, ry=None, a=0.3):
    ry = ry or rx * 0.12
    p = skia.Paint(AntiAlias=True, Color=C("#120a18", a))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, ry * 0.8))
    g.c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), p)

# ------------------------------------------------------------ channel-style labels
def age_box(g, s, k=1.0, x=150, y=110):
    """white rounded box with dark text, like the channel's 'AGE 51'."""
    if k <= 0: return
    size = 54
    w = text_w(s, size) + 56
    g.save(); g.tr(x + w / 2 - 75, y); g.sc(k)
    p = skia.Paint(AntiAlias=True, Color=C("#000000", 0.28)); p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    g.c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 4, -38 + 6, w, 76), 14, 14), p)
    g.rrect(-w / 2, -38, w, 76, 14, "#fbf8f2", outline="#2a2230", w=5)
    text(g, s, 0, 19, size, fill="#2a2230", outline=None, shadow=False)
    g.restore()

def era_label(g, s, a=1.0, x=W - 70, y=72):
    """top-right serif caps label in a thin box (like 'REVELATIONS · 1511')."""
    if a <= 0: return
    size = 30
    f_w = text_w(s, size, "serif") + 44
    g.save(); g.alpha(a)
    g.rrect(x - f_w, y - 30, f_w, 56, 6, "#1b1622", outline="#cfc6b8", w=2.2, a=0.82)
    text(g, s, x - f_w / 2, y + 9, size, fill="#efe6d6", outline=None, shadow=False, name="serif")
    g.restore(); g.restore()

def callout(g, title, sub, tx, ty, lx, ly, k=1.0, t=0.0):
    """white label + hand-drawn arrow pointing at (tx, ty) from the label at (lx, ly)."""
    if k <= 0: return
    g.save(); g.alpha(clamp(k * 2))
    text(g, title, lx, ly, 62, fill="#ffffff", outline="#1b1622", ow=10)
    if sub:
        text(g, sub, lx, ly + 40, 30, fill="#ffffff", outline="#1b1622", ow=6, name="ui")
    # arrow
    sx, sy = lx + (40 if tx > lx else -40), ly + (52 if sub else 20)
    mx, my = (sx + tx) / 2 + (ty - sy) * 0.15, (sy + ty) / 2 - abs(tx - sx) * 0.12
    kk = ease_out(k)
    ex, ey = lerp(sx, tx, kk), lerp(sy, ty, kk)
    q = skia.Path(); q.moveTo(sx, sy); q.quadTo(lerp(sx, mx, kk), lerp(sy, my, kk), ex, ey)
    g.strokep(q, "#1b1622", w=11); g.strokep(q, "#ffffff", w=5.5)
    ang = math.atan2(ey - lerp(sy, my, kk), ex - lerp(sx, mx, kk))
    for s_ in (-1, 1):
        a2 = ang + math.pi + s_ * 0.5
        g.line(ex, ey, ex + math.cos(a2) * 26, ey + math.sin(a2) * 26, color="#1b1622", w=11)
    for s_ in (-1, 1):
        a2 = ang + math.pi + s_ * 0.5
        g.line(ex, ey, ex + math.cos(a2) * 26, ey + math.sin(a2) * 26, color="#ffffff", w=5.5)
    g.restore(); g.restore()

def speech(g, s, x, y, k=1.0, tail=(-40, 60), size=40):
    """white rounded speech bubble with dark text (channel style)."""
    if k <= 0: return
    w = text_w(s, size, "ui") + 60; h = size * 1.7
    g.save(); g.tr(x, y); g.sc(ease_back(clamp(k), 1.6))
    q = skia.Path(); q.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 2.2, h / 2.2))
    tq = G.poly_p([(-18, h / 2 - 4), (18, h / 2 - 4), (tail[0], h / 2 + tail[1])])
    q2 = skia.Op(q, tq, skia.PathOp.kUnion_PathOp)
    g.shape(q2, "#fbf8f2", outline="#1b1622", w=5)
    text(g, s, 0, size * 0.35, size, fill="#1b1622", outline=None, shadow=False, name="ui")
    g.restore()
