# -*- coding: utf-8 -*-
"""Low-level drawing helpers (skia). Every drawable uses the same outline colour and
line weight so all scenes stay visually consistent."""
import math, os
import skia

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
W, H = 1920, 1080
FPS = 30

# ---------------------------------------------------------------- style tokens
OUTLINE = "#2b2233"
LW = 6.0                   # default outline width at 1080p (scaled with the object)

PAL = {
    "skin_lucia": "#c98c62", "skin_lucia_sh": "#b0754f",
    "skin_jason": "#e3ad86", "skin_jason_sh": "#c99270",
    "skin_mom": "#c48a62", "skin_dad": "#b97c55",
    "skin_light": "#f0c3a0", "skin_dark": "#8d5a3b",
    "hair_dark": "#2d1d1a", "hair_brown": "#5a3a26", "hair_grey": "#b9b4ad",
    "cheek": "#f08a8a",
    "orange": "#f07a2a", "orange_sh": "#cf5f17",
    "denim": "#3f6fb0", "denim_sh": "#335a92",
    "white": "#fbf7f0", "cream": "#f6ead2",
    "red": "#e2483d", "red_dk": "#b8302a",
    "gold": "#f2c14e",
    "olive": "#6f7a3c", "olive_sh": "#5a6330",
    "teal": "#2fb3a6", "pink": "#ff5fa2", "purple": "#7b4bc4",
    "night": "#1d1b3a", "sky_day": "#9fd7f2",
    "grey": "#8e8f99", "grey_lt": "#c9cad1", "grey_dk": "#5e5f6b",
}

def C(hexstr, a=1.0):
    """hex -> skia color int (ARGB)."""
    h = hexstr.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)

def mix(c1, c2, k):
    a = c1.lstrip("#"); b = c2.lstrip("#")
    out = []
    for i in (0, 2, 4):
        x = int(a[i:i + 2], 16); y = int(b[i:i + 2], 16)
        out.append(int(x + (y - x) * k))
    return "#%02x%02x%02x" % tuple(out)

def shade(c, k=0.82):
    return mix(c, "#1a1020", 1 - k)

def tint(c, k=0.3):
    return mix(c, "#ffffff", k)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, k):
    return a + (b - a) * k

def ease_io(x):
    x = clamp(x); return x * x * (3 - 2 * x)

def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3

def ease_in(x):
    x = clamp(x); return x ** 3

def ease_back(x, s=1.70158):
    x = clamp(x); x -= 1
    return x * x * ((s + 1) * x + s) + 1

def pop(t, t0, dur=0.35):
    """0 -> overshoot -> 1 scale for elements that 'pop' in at t0."""
    if t < t0: return 0.0
    return ease_back((t - t0) / dur, 2.2)

def fade(t, t0, dur=0.3):
    return ease_io((t - t0) / dur)

def wob(t, f=1.0, a=1.0, ph=0.0):
    return math.sin((t * f + ph) * 2 * math.pi) * a

# ---------------------------------------------------------------- paints
def P_fill(color, a=1.0):
    return skia.Paint(AntiAlias=True, Color=C(color, a), Style=skia.Paint.kFill_Style)

def P_stroke(color=OUTLINE, w=LW, a=1.0, cap=True):
    p = skia.Paint(AntiAlias=True, Color=C(color, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    if cap: p.setStrokeCap(skia.Paint.kRound_Cap)
    return p

class G:
    """Thin wrapper around a skia canvas with the house style baked in."""
    def __init__(self, canvas):
        self.c = canvas
        self.lw = LW

    # transforms
    def save(self): self.c.save()
    def restore(self): self.c.restore()
    def tr(self, x, y): self.c.translate(x, y)
    def sc(self, sx, sy=None): self.c.scale(sx, sx if sy is None else sy)
    def rot(self, deg): self.c.rotate(deg)
    def alpha(self, a):
        self.c.saveLayerAlpha(None, int(clamp(a) * 255))

    # core: fill + outline
    def shape(self, path, fill, outline=OUTLINE, w=None, a=1.0, shader=None):
        if fill:
            p = P_fill(fill, a)
            if shader is not None: p.setShader(shader)
            self.c.drawPath(path, p)
        if outline:
            self.c.drawPath(path, P_stroke(outline, self.lw if w is None else w, a))

    def fillp(self, path, color, a=1.0, shader=None, blur=0):
        p = P_fill(color, a)
        if shader is not None: p.setShader(shader)
        if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        self.c.drawPath(path, p)

    def strokep(self, path, color=OUTLINE, w=None, a=1.0, cap=True):
        self.c.drawPath(path, P_stroke(color, self.lw if w is None else w, a, cap))

    # primitives -> path
    @staticmethod
    def circle_p(x, y, r):
        p = skia.Path(); p.addCircle(x, y, r); return p

    @staticmethod
    def ellipse_p(x, y, rx, ry):
        p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)); return p

    @staticmethod
    def rrect_p(x, y, w, h, r):
        p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p

    @staticmethod
    def poly_p(pts, close=True):
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        if close: p.close()
        return p

    @staticmethod
    def smooth_p(pts, close=True, k=0.5):
        """Catmull-Rom spline through points -> cubic bezier path."""
        n = len(pts); p = skia.Path(); p.moveTo(*pts[0])
        rng = range(n) if close else range(n - 1)
        for i in rng:
            p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
            p1 = pts[i]; p2 = pts[(i + 1) % n]
            p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
            c1 = (p1[0] + (p2[0] - p0[0]) * k / 3, p1[1] + (p2[1] - p0[1]) * k / 3)
            c2 = (p2[0] - (p3[0] - p1[0]) * k / 3, p2[1] - (p3[1] - p1[1]) * k / 3)
            p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
        if close: p.close()
        return p

    # convenience draws
    def circle(self, x, y, r, fill, **kw): self.shape(self.circle_p(x, y, r), fill, **kw)
    def ellipse(self, x, y, rx, ry, fill, **kw): self.shape(self.ellipse_p(x, y, rx, ry), fill, **kw)
    def rrect(self, x, y, ww, hh, r, fill, **kw): self.shape(self.rrect_p(x, y, ww, hh, r), fill, **kw)
    def poly(self, pts, fill, **kw): self.shape(self.poly_p(pts), fill, **kw)
    def smooth(self, pts, fill, **kw): self.shape(self.smooth_p(pts), fill, **kw)

    def line(self, x1, y1, x2, y2, color=OUTLINE, w=None, a=1.0):
        p = skia.Path(); p.moveTo(x1, y1); p.lineTo(x2, y2); self.strokep(p, color, w, a)

    def polyline(self, pts, color=OUTLINE, w=None, a=1.0, smooth=False):
        p = self.smooth_p(pts, close=False) if smooth else self.poly_p(pts, close=False)
        self.strokep(p, color, w, a)

    def limb(self, pts, color, width, outline=OUTLINE, ow=None):
        """Thick rounded limb through points, with outline (two strokes)."""
        ow = self.lw if ow is None else ow
        p = self.poly_p(pts, close=False)
        if outline:
            self.c.drawPath(p, P_stroke(outline, width + 2 * ow))
        self.c.drawPath(p, P_stroke(color, width))

    def rect_fill(self, x, y, w, h, color, a=1.0):
        self.c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), P_fill(color, a))

    def vgrad(self, x, y, w, h, stops):
        """vertical gradient; stops = [(pos, hex), ...]"""
        sh = skia.GradientShader.MakeLinear(
            [skia.Point(x, y), skia.Point(x, y + h)], [C(c) for _, c in stops], [s for s, _ in stops])
        p = skia.Paint(AntiAlias=True); p.setShader(sh)
        self.c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)

    def glow(self, x, y, r, color, a=0.6):
        sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [C(color, a), C(color, 0)], [0, 1])
        p = skia.Paint(AntiAlias=True); p.setShader(sh)
        self.c.drawCircle(x, y, r, p)

    def shadow(self, x, y, rx, ry, a=0.22):
        self.fillp(self.ellipse_p(x, y, rx, ry), "#1a1020", a, blur=4)

# ---------------------------------------------------------------- text
_FONTS = {}
def typeface(name):
    if name not in _FONTS:
        paths = {
            "display": os.path.join(ROOT, "assets/fonts/LilitaOne-Regular.ttf"),
            "display_tr": os.path.join(ROOT, "assets/fonts/Baloo2-ExtraBold.ttf"),
            "serif": os.path.join(ROOT, "assets/fonts/Cinzel-Bold.ttf"),
            "ui": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
            "ui_reg": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
        }
        _FONTS[name] = skia.Typeface.MakeFromFile(paths[name])
    return _FONTS[name]

def font(size, name="display"):
    f = skia.Font(typeface(name), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f

def text_w(s, size, name="display"):
    return font(size, name).measureText(s)

def text(g, s, x, y, size, fill="#ffffff", outline=OUTLINE, ow=None, name="display",
         align="center", a=1.0, shadow=True, rot=0):
    f = font(size, name)
    w = f.measureText(s)
    dx = {"center": -w / 2, "left": 0, "right": -w}[align]
    g.save(); g.tr(x, y)
    if rot: g.rot(rot)
    ow = size * 0.16 if ow is None else ow
    if shadow:
        sp = P_fill("#1a1020", 0.35 * a)
        g.c.drawString(s, dx + size * 0.04, size * 0.07, f, sp)
    if outline:
        g.c.drawString(s, dx, 0, f, P_stroke(outline, ow, a))
    g.c.drawString(s, dx, 0, f, P_fill(fill, a))
    g.restore()
    return w

# ---------------------------------------------------------------- surface
def new_surface():
    return skia.Surface(W, H)

def snapshot_rgba(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
