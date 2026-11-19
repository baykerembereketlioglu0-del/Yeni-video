# -*- coding: utf-8 -*-
"""Chibi character rig. One function draws every person in the video so proportions,
outline weight, eyes, cheeks and shading stay identical from shot to shot.

Coordinates: units where an adult is ~100 units tall, feet at (0, 0), y grows downward
(head is at negative y). `size` = pixels per 100 units.
"""
import math
import skia
from gfx import (G, PAL, OUTLINE, LW, C, P_fill, P_stroke, shade, tint, mix, clamp, lerp,
                 ease_io, wob)

# ------------------------------------------------------------------ proportions
STAGES = {
    #           head_r head_cy  t_top  t_bot  hw_top hw_bot  sh_x  sh_y  arm1 arm2 limb hand leg_x
    "adult":   (24,   -74,     -52,   -25,   12.5,  12.5,   11.5, -47,  12.5, 12,  8.5, 4.8, 6.3),
    "teen":    (25,   -72,     -50,   -25,   11.5,  11.5,   10.5, -45,  12,   11,  8,   4.6, 5.8),
    "kid":     (27,   -66,     -42,   -20,   11,    11.5,   10,   -38,  10,   9.5, 7.5, 4.4, 5.6),
    "toddler": (29,   -58,     -32,   -13,   11,    12,     10,   -29,  8,    7.5, 7.5, 4.4, 5.6),
}

def V(spec, key, default=None):
    return spec.get(key, default)

# ------------------------------------------------------------------ cast
def CAST():
    P = PAL
    return {
        # LUCIA at every stage of life ------------------------------------------------
        "lucia_baby": dict(stage="baby", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="baby_curl",
                           top="#f3a6b8", female=True),
        "lucia_toddler": dict(stage="toddler", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="puffs",
                              top="#f3a6b8", bottom="#7f6fc9", shoes="#e2483d", female=True),
        "lucia_kid": dict(stage="kid", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="pigtails",
                          top="#e2483d", top_style="tee", bottom="#3f4a7a", shoes="#fbf7f0", female=True),
        "lucia_preteen": dict(stage="kid", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="pony",
                              top="#2fb3a6", top_style="tank", bottom="#2d2f45", shoes="#fbf7f0", female=True),
        "lucia_teen": dict(stage="teen", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="pony",
                           top="#ff5fa2", top_style="tank", bottom=P["denim"], shoes="#fbf7f0", female=True,
                           acc=["hoops"]),
        "lucia": dict(stage="adult", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="long",
                      top="#fbf7f0", top_style="jacket", jacket=P["denim"], bottom="#2d2f45",
                      shoes="#2b2233", female=True, acc=["hoops"]),
        "lucia_prison": dict(stage="adult", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="pony",
                             top=P["orange"], top_style="jumpsuit", bottom=P["orange"], shoes="#fbf7f0",
                             female=True, acc=["hoops_small"]),
        "lucia_night": dict(stage="adult", skin=P["skin_lucia"], hair=P["hair_dark"], hair_style="long",
                            top="#2b2440", top_style="tank", bottom="#2d2f45", shoes="#2b2233", female=True,
                            acc=["hoops"]),
        # JASON ---------------------------------------------------------------------
        "jason_kid": dict(stage="kid", skin=P["skin_jason"], hair=P["hair_brown"], hair_style="buzz",
                          top="#f2c14e", top_style="tee", bottom="#4a5a7a", shoes="#fbf7f0"),
        "jason_army": dict(stage="adult", skin=P["skin_jason"], hair=P["hair_brown"], hair_style="buzz",
                           top=P["olive"], top_style="army", bottom=P["olive_sh"], shoes="#3a2e24",
                           acc=["helmet"]),
        "jason": dict(stage="adult", skin=P["skin_jason"], hair=P["hair_brown"], hair_style="short",
                      top="#5b6b4a", top_style="tee", bottom="#3b4a63", shoes="#2b2233",
                      beard="stubble", acc=["tattoo"]),
        # FAMILY & OTHERS -----------------------------------------------------------
        "mom": dict(stage="adult", skin=P["skin_mom"], hair=P["hair_dark"], hair_style="bun",
                    top="#c46aa0", top_style="cardigan", bottom="#4b3f6b", shoes="#2b2233", female=True,
                    acc=["earrings_small"]),
        "dad": dict(stage="adult", skin=P["skin_dad"], hair=P["hair_dark"], hair_style="short",
                    top="#e2483d", top_style="tank", bottom="#3b3f55", shoes="#2b2233",
                    beard="mustache", acc=["chain"], big=1.08),
        "officer": dict(stage="adult", skin=P["skin_light"], hair="#8a5a3a", hair_style="bun",
                        top="#7a8494", top_style="uniform", bottom="#4d5563", shoes="#2b2233", female=True),
        "guard": dict(stage="adult", skin=P["skin_dark"], hair=P["hair_dark"], hair_style="buzz",
                      top="#7a8494", top_style="uniform", bottom="#4d5563", shoes="#2b2233", acc=["cap"]),
        "brian": dict(stage="adult", skin=P["skin_jason"], hair=P["hair_grey"], hair_style="long_m",
                      top="#2fb3a6", top_style="hawaiian", bottom="#e8dcc0", shoes="#8a5a3a",
                      beard="full_grey", big=1.04),
        "bully": dict(stage="kid", skin=P["skin_light"], hair="#c9884a", hair_style="buzz",
                      top="#6f7a3c", top_style="tee", bottom="#3b3f55", shoes="#2b2233", big=1.12),
        "grifter1": dict(stage="adult", skin=P["skin_light"], hair="#2b2233", hair_style="slick",
                         top="#3a2e4a", top_style="suit", bottom="#2b2233", shoes="#1a1020",
                         acc=["shades"], beard="mustache"),
        "grifter2": dict(stage="adult", skin=P["skin_dark"], hair="#2b2233", hair_style="buzz",
                         top="#8a3a3a", top_style="hawaiian", bottom="#2b2233", shoes="#1a1020",
                         acc=["shades", "chain"]),
        "cashier": dict(stage="adult", skin=P["skin_light"], hair="#c9884a", hair_style="short",
                        top="#e2483d", top_style="tee", bottom="#3b3f55", shoes="#2b2233", acc=["cap_red"]),
    }

# ------------------------------------------------------------------ poses (hand targets)
# relative to shoulder, in units; None = default dangling
POSES = {
    "idle":      ((-3, 21), (3, 21)),
    "relaxed":   ((-5, 20), (5, 20)),
    "guard":     ((3, -9), (-3, -9)),            # fists in front of chin
    "hands_up":  ((-8, -24), (8, -24)),
    "cross":     ((14, 8), (-14, 8)),
    "hips":      ((-2, 16), (2, 16)),
    "wave_r":    ((-3, 21), (14, -18)),
    "point_r":   ((-3, 21), (24, -2)),
    "point_viewer": ((-3, 21), (10, 2)),
    "raise_r":   ((-3, 21), (10, -18)),            # glass up
    "hold_front": ((10, 10), (-10, 10)),          # holding something in front
    "hold_r":    ((-3, 21), (8, 6)),
    "behind":    ((4, 18), (-4, 18)),              # hands behind back (cuffed)
    "shrug":     ((-14, 2), (14, 2)),
    "punch_r":   ((6, -14), (30, -10)),
    "phone":     ((-3, 21), (6, -10)),
    "facepalm":  ((-3, 21), (-4, -26)),
    "pushup":    ((-14, 18), (14, 18)),
    "hammer":    ((-3, 21), (20, -14)),
    "drive":     ((6, 4), (-6, 4)),
    "chin":      ((-3, 21), (2, -12)),
}

FRONT = {"guard", "hands_up", "facepalm", "punch_r", "phone", "chin", "raise_r", "hammer", "wave_r"}

def ik(sx, sy, hx, hy, l1, l2, outward):
    dx, dy = hx - sx, hy - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 0.05))
    a = math.atan2(dy, dx)
    cb = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    b = math.acos(cb)
    e1 = (sx + l1 * math.cos(a + b), sy + l1 * math.sin(a + b))
    e2 = (sx + l1 * math.cos(a - b), sy + l1 * math.sin(a - b))
    # outward = -1 (left arm wants elbow to the left) or +1
    e = e1 if (e1[0] - e2[0]) * outward > 0 else e2
    hx2 = sx + d * math.cos(a); hy2 = sy + d * math.sin(a)
    return e, (hx2, hy2)

def mixpose(p1, p2, k):
    a, b = POSES[p1], POSES[p2]
    return tuple((lerp(a[i][0], b[i][0], k), lerp(a[i][1], b[i][1], k)) for i in range(2))

# ------------------------------------------------------------------ the rig
class Person:
    def __init__(self, spec):
        self.s = spec

    def draw(self, g, x, y, size, t=0.0, pose="idle", pose2=None, pose_k=0.0, face=None,
             look=0.0, talk=False, flip=False, held=None, mask=False, anger=False, sweat=False,
             blink_seed=0.0, sit=False, walk=0.0, breathe=True, legs_hidden=False, tilt=0.0,
             hand_override=None):
        s = self.s
        face = face or {}
        if not blink_seed:
            blink_seed = (x * 0.0137 + len(s.get("top", "")) * 0.61) % 3.6
        big = s.get("big", 1.0)
        sc = size / 100.0 * big
        ow_px = 6.0 * (sc / 5.2) ** 0.45
        g.save(); g.tr(x, y); g.sc(-sc if flip else sc, sc)
        if tilt: g.rot(tilt)
        old = g.lw; g.lw = ow_px / sc
        if s["stage"] == "baby":
            self._baby(g, t, face, look, anger, blink_seed)
        else:
            self._body(g, t, pose, pose2, pose_k, face, look, talk, held, mask, anger, sweat,
                       blink_seed, sit, walk, breathe, legs_hidden, hand_override)
        g.lw = old
        g.restore()

    # ---------------------------------------------------------- body
    def _body(self, g, t, pose, pose2, pose_k, face, look, talk, held, mask, anger, sweat,
              blink_seed, sit, walk, breathe, legs_hidden, hand_override):
        s = self.s
        hr, hcy, tt, tb, hwt, hwb, shx, shy, l1, l2, lw, hand_r, legx = STAGES[s["stage"]]
        br = math.sin(t * 2 * math.pi * 0.35 + blink_seed) * 0.6 if breathe else 0.0
        bob = 0.0
        if walk:
            bob = -abs(math.sin(t * math.pi * 2 * 1.6)) * 2.2 * walk
        if sit:
            bob += -tb + 1      # hips sit exactly on the given y
        g.save(); g.tr(0, bob)
        top = s.get("top", "#ffffff"); topsty = s.get("top_style", "tee")
        skin = s["skin"]; skin_sh = shade(skin, 0.86)
        bottom = s.get("bottom", "#333344"); shoes = s.get("shoes", "#2b2233")

        # legs ---------------------------------------------------------------
        if not legs_hidden:
            for side in (-1, 1):
                hip = (side * legx, tb - 2)
                if sit:
                    foot = (side * (legx + 2.5), tb + 24)
                    knee = (side * (legx + 1.5), tb + 5)
                    pts = [hip, knee, foot]
                else:
                    sw = math.sin(t * math.pi * 2 * 1.6 + (0 if side < 0 else math.pi)) * 4 * walk
                    foot = (side * (legx + 1) + sw, -1 - max(0, sw) * 0.4)
                    pts = [hip, foot]
                g.limb(pts, bottom, lw + 1.2)
                fx, fy = pts[-1]
                g.ellipse(fx + side * 1.6, fy + 0.6, 5.2, 3.0, shoes)

        # back hair (behind body) ----------------------------------------------
        hx = 0; hy = hcy + br * 0.4
        self._hair_back(g, hx, hy, hr, t)

        # torso -------------------------------------------------------------
        g.save(); g.tr(0, tb); g.sc(1, 1 + br * 0.004); g.tr(0, -tb)
        self._torso(g, tt, tb, hwt, hwb, top, topsty, skin)
        g.restore()

        # arms --------------------------------------------------------------
        if hand_override is not None:
            hands = hand_override
        elif pose2 is not None:
            hands = mixpose(pose, pose2, ease_io(pose_k))
        else:
            hands = POSES[pose]
        sleeve = {"tank": None, "jumpsuit": top, "tee": top, "army": top, "uniform": top,
                  "hawaiian": top, "cardigan": top, "jacket": s.get("jacket", top), "suit": top}.get(topsty, top)
        long_sleeve = topsty in ("jacket", "cardigan", "suit", "uniform_long")
        front = (pose in FRONT) or (pose2 in FRONT and pose_k > 0.5)
        def draw_arms():
            for i, side in enumerate((-1, 1)):
                sx, sy = side * shx, shy
                tx, ty = hands[i]
                el, hd = ik(sx, sy, sx + tx, sy + ty, l1, l2, side)
                self._arm(g, (sx, sy), el, hd, skin, sleeve, long_sleeve, lw, hand_r, held, side,
                          "tattoo" in s.get("acc", []))
        if not front:
            draw_arms()
        g.restore()  # bob (head drawn with its own bob below)

        # head --------------------------------------------------------------
        g.save(); g.tr(0, bob)
        self.head(g, hx, hy, hr, t, face, look, talk, mask, anger, sweat, blink_seed)
        g.restore()
        if front:
            g.save(); g.tr(0, bob); draw_arms(); g.restore()

    def _torso(self, g, tt, tb, hwt, hwb, top, sty, skin):
        p = skia.Path()
        r = 5
        p.moveTo(-hwt, tt + r); p.quadTo(-hwt, tt, -hwt + r, tt)
        p.lineTo(hwt - r, tt); p.quadTo(hwt, tt, hwt, tt + r)
        p.lineTo(hwb, tb - 2); p.quadTo(hwb, tb + 1, hwb - 3, tb + 1)
        p.lineTo(-hwb + 3, tb + 1); p.quadTo(-hwb, tb + 1, -hwb, tb - 2); p.close()
        s = self.s
        if sty == "tank":
            g.shape(p, skin)
            q = skia.Path()
            q.moveTo(-hwt + 3.5, tt); q.lineTo(-hwt + 6.5, tt)
            q.quadTo(0, tt + 9, hwt - 6.5, tt); q.lineTo(hwt - 3.5, tt)
            q.lineTo(hwb, tb - 2); q.quadTo(hwb, tb + 1, hwb - 3, tb + 1)
            q.lineTo(-hwb + 3, tb + 1); q.quadTo(-hwb, tb + 1, -hwb, tb - 2); q.close()
            g.shape(q, top)
        elif sty == "jacket":
            g.shape(p, top)  # inner shirt
            jk = s.get("jacket", PAL["denim"])
            for side in (-1, 1):
                q = skia.Path()
                q.moveTo(side * hwt, tt + 5); q.quadTo(side * hwt, tt, side * (hwt - 5), tt)
                q.lineTo(side * 4.5, tt); q.lineTo(side * 5.5, tb + 1)
                q.lineTo(side * (hwb - 3), tb + 1); q.quadTo(side * hwb, tb + 1, side * hwb, tb - 2); q.close()
                g.shape(q, jk)
                g.line(side * 4.5, tt + 1, side * 9, tt + 9, w=g.lw * 0.8)
        elif sty == "jumpsuit":
            g.shape(p, top)
            g.poly([(-5, tt), (0, tt + 8), (5, tt)], self.s["skin"], w=g.lw * 0.9)
            g.line(0, tt + 8, 0, tb, w=g.lw * 0.7)
            g.rrect(hwt - 10, tt + 9, 7, 5, 1.2, "#fbf7f0", w=g.lw * 0.6)
        elif sty == "uniform":
            g.shape(p, top)
            g.poly([(-5, tt), (0, tt + 7), (5, tt)], "#e9edf2", w=g.lw * 0.8)
            g.poly([(-1.5, tt + 4), (1.5, tt + 4), (2, tt + 14), (0, tt + 16), (-2, tt + 14)], "#2b2b3b", w=g.lw * 0.5)
            g.circle(-hwt + 6, tt + 9, 2.3, PAL["gold"], w=g.lw * 0.6)
        elif sty == "army":
            g.shape(p, top)
            for (cx, cy, rr) in ((-6, tt + 8, 3), (5, tt + 15, 3.5), (-3, tt + 20, 2.5), (7, tt + 5, 2)):
                g.fillp(G.circle_p(cx, cy, rr), shade(top, 0.8))
            g.poly([(-5, tt), (0, tt + 6), (5, tt)], self.s["skin"], w=g.lw * 0.8)
        elif sty == "hawaiian":
            g.shape(p, top)
            g.c.save(); g.c.clipPath(p, doAntiAlias=True)
            for (cx, cy) in ((-8, tt + 6), (6, tt + 12), (-3, tt + 20), (9, tt + 22), (-10, tt + 18), (2, tt + 4)):
                for k in range(5):
                    a = k * 2 * math.pi / 5
                    g.fillp(G.circle_p(cx + 1.6 * math.cos(a), cy + 1.6 * math.sin(a), 1.4), "#fbf7f0", 0.9)
                g.fillp(G.circle_p(cx, cy, 0.9), PAL["gold"])
            g.c.restore()
            g.strokep(p)
            g.poly([(-6, tt), (0, tt + 7), (6, tt)], self.s["skin"], w=g.lw * 0.8)
        elif sty == "cardigan":
            g.shape(p, "#f6ead2")
            for side in (-1, 1):
                q = skia.Path()
                q.moveTo(side * hwt, tt + 5); q.quadTo(side * hwt, tt, side * (hwt - 5), tt)
                q.lineTo(side * 3, tt); q.lineTo(side * 4, tb + 1)
                q.lineTo(side * (hwb - 3), tb + 1); q.quadTo(side * hwb, tb + 1, side * hwb, tb - 2); q.close()
                g.shape(q, top)
        elif sty == "suit":
            g.shape(p, top)
            g.poly([(-5, tt), (0, tt + 12), (5, tt)], "#fbf7f0", w=g.lw * 0.8)
            g.poly([(-1.2, tt + 3), (1.2, tt + 3), (1.5, tt + 11), (0, tt + 13), (-1.5, tt + 11)], PAL["red"], w=g.lw * 0.5)
        else:  # tee
            g.shape(p, top)
            q = skia.Path(); q.moveTo(-5, tt); q.quadTo(0, tt + 5, 5, tt)
            g.strokep(q, w=g.lw * 0.8)
        acc = s.get("acc", [])
        if "chain" in acc:
            q = skia.Path(); q.moveTo(-6, tt + 0.5); q.quadTo(0, tt + 10, 6, tt + 0.5)
            g.strokep(q, OUTLINE, w=g.lw * 1.9); g.strokep(q, PAL["gold"], w=g.lw * 1.0)

    def _arm(self, g, sh, el, hd, skin, sleeve, long_sleeve, lw, hand_r, held, side, tattoo):
        pts = [sh, el, hd]
        # outline of whole arm in one go (no seams)
        path = G.poly_p(pts, close=False)
        g.c.drawPath(path, P_stroke(OUTLINE, lw + 2 * g.lw))
        g.c.drawPath(path, P_stroke(skin, lw))
        if sleeve:
            if long_sleeve:
                sp = G.poly_p([sh, el, (lerp(el[0], hd[0], 0.75), lerp(el[1], hd[1], 0.75))], close=False)
            else:
                sp = G.poly_p([sh, (lerp(sh[0], el[0], 0.7), lerp(sh[1], el[1], 0.7))], close=False)
            g.c.drawPath(sp, P_stroke(sleeve, lw + 0.6))
        if tattoo:
            mx, my = lerp(el[0], hd[0], 0.45), lerp(el[1], hd[1], 0.45)
            g.fillp(G.circle_p(mx, my, 1.5), "#2f3a5a", 0.6)
            g.fillp(G.circle_p(lerp(sh[0], el[0], 0.75), lerp(sh[1], el[1], 0.75) , 1.3), "#2f3a5a", 0.5)
        # hand / held item
        hx, hy = hd
        if held == "gloves":
            g.save(); g.tr(hx, hy)
            g.rrect(-hand_r * 1.45, -hand_r * 1.5, hand_r * 2.9, hand_r * 2.8, hand_r * 1.2, PAL["red"])
            g.rrect(-hand_r * 1.2, hand_r * 0.9, hand_r * 2.4, hand_r * 1.1, hand_r * 0.4, "#fbf7f0", w=g.lw * 0.8)
            g.fillp(G.ellipse_p(-hand_r * 0.5, -hand_r * 0.6, hand_r * 0.55, hand_r * 0.35), "#ffffff", 0.45)
            g.restore()
        else:
            g.circle(hx, hy, hand_r, skin)
        if side == 1 and held in ("glass", "photo", "hammer", "phone", "cards", "bag", "beer", "mic"):
            draw_prop(g, held, hx, hy, hand_r)

    # ---------------------------------------------------------- head
    def head(self, g, hx, hy, r, t, face, look, talk, mask, anger, sweat, blink_seed):
        s = self.s
        skin = s["skin"]
        acc = s.get("acc", [])
        fx = look * r * 0.22   # facial features shift for 3/4 looks
        # ears
        for side in (-1, 1):
            ex = hx + side * r * 0.98 + fx * 0.25
            g.ellipse(ex, hy + r * 0.12, r * 0.17, r * 0.22, skin)
        # head
        hp = G.ellipse_p(hx, hy, r * 1.0, r * 0.97)
        g.shape(hp, skin)
        # soft shadow under hair line / jaw
        g.c.save(); g.c.clipPath(hp, doAntiAlias=True)
        g.fillp(G.ellipse_p(hx - look * r * 0.5 + r * 0.25, hy + r * 1.05, r * 1.15, r * 0.35), shade(skin, 0.8), 0.35)
        g.c.restore()
        g.strokep(hp)
        if "hoops" in acc or "hoops_small" in acc or "earrings_small" in acc:
            rr = r * (0.22 if "hoops" in acc else 0.12)
            for side in (-1, 1):
                ex = hx + side * r * 0.98 + fx * 0.25
                q = G.circle_p(ex, hy + r * 0.35 + rr, rr)
                g.strokep(q, OUTLINE, w=g.lw * 1.5); g.strokep(q, PAL["gold"], w=g.lw * 0.7)

        if mask:
            self._mask(g, hx, hy, r, face, t, blink_seed, fx, mask)
        else:
            self._face(g, hx, hy, r, t, face, look, talk, blink_seed, fx)
            self._hair_front(g, hx, hy, r, t)
        # hats / extras
        if "helmet" in acc:
            q = skia.Path()
            q.moveTo(hx - r * 1.12, hy - r * 0.18)
            q.cubicTo(hx - r * 1.15, hy - r * 1.35, hx + r * 1.15, hy - r * 1.35, hx + r * 1.12, hy - r * 0.18)
            q.close()
            g.shape(q, PAL["olive"])
            g.rrect(hx - r * 1.2, hy - r * 0.32, r * 2.4, r * 0.2, r * 0.08, PAL["olive_sh"], w=g.lw * 0.8)
        if "cap" in acc or "cap_red" in acc:
            col = "#3b4a63" if "cap" in acc else PAL["red"]
            q = skia.Path()
            q.moveTo(hx - r * 0.98, hy - r * 0.3)
            q.cubicTo(hx - r * 1.0, hy - r * 1.25, hx + r * 1.0, hy - r * 1.25, hx + r * 0.98, hy - r * 0.3)
            q.close()
            g.shape(q, col)
            g.shape(G.ellipse_p(hx + r * 0.25 + fx, hy - r * 0.3, r * 0.85, r * 0.16), shade(col, 0.85))
            if "cap" in acc:
                g.circle(hx + fx, hy - r * 0.72, r * 0.13, PAL["gold"], w=g.lw * 0.6)
        if "shades" in acc and not mask:
            for side in (-1, 1):
                g.rrect(hx + fx + side * r * 0.36 - r * 0.24, hy - r * 0.02, r * 0.48, r * 0.3, r * 0.1, "#1a1020")
            g.line(hx + fx - r * 0.12, hy + r * 0.08, hx + fx + r * 0.12, hy + r * 0.08, w=g.lw)
        if anger:
            anger_mark(g, hx + r * 0.95, hy - r * 0.85, r * 0.32, t)
        if sweat:
            sweat_drop(g, hx - r * 0.95, hy - r * 0.35, r * 0.18, t)

    def _face(self, g, hx, hy, r, t, face, look, talk, blink_seed, fx):
        s = self.s
        brows = face.get("brows", "neutral")
        eyes = face.get("eyes", "open")
        mouth = face.get("mouth", "flat")
        cheeks = face.get("cheeks", True)
        ey = hy + r * 0.12
        # cheeks
        if cheeks:
            for side in (-1, 1):
                g.fillp(G.ellipse_p(hx + fx + side * r * 0.55, hy + r * 0.42, r * 0.17, r * 0.1), PAL["cheek"], 0.55)
        # blink
        blink = False
        ph = (t + blink_seed * 1.7) % 3.6
        if ph < 0.12 and eyes == "open":
            blink = True
        gaze = face.get("gaze", look * 0.5)
        for side in (-1, 1):
            ex = hx + fx + side * r * 0.36
            if eyes == "closed" or blink:
                q = skia.Path(); q.moveTo(ex - r * 0.13, ey); q.quadTo(ex, ey + (r * 0.1 if eyes == "closed" else r * 0.03), ex + r * 0.13, ey)
                g.strokep(q, w=g.lw * 1.1)
            elif eyes == "happy":
                q = skia.Path(); q.moveTo(ex - r * 0.13, ey + r * 0.04); q.quadTo(ex, ey - r * 0.14, ex + r * 0.13, ey + r * 0.04)
                g.strokep(q, w=g.lw * 1.2)
            else:
                ry = r * 0.165; rx = r * 0.135
                if eyes == "wide":
                    g.fillp(G.ellipse_p(ex, ey, rx * 1.25, ry * 1.25), "#ffffff")
                    g.strokep(G.ellipse_p(ex, ey, rx * 1.25, ry * 1.25), w=g.lw * 0.7)
                    rx *= 0.7; ry *= 0.7
                px = ex + gaze * r * 0.04
                g.fillp(G.ellipse_p(px, ey, rx, ry), "#2a1d22")
                g.fillp(G.ellipse_p(px, ey + ry * 0.35, rx * 0.75, ry * 0.45), "#5b3a2e", 0.55)
                g.fillp(G.circle_p(px + rx * 0.35, ey - ry * 0.4, rx * 0.38), "#ffffff")
                g.fillp(G.circle_p(px - rx * 0.35, ey + ry * 0.35, rx * 0.17), "#ffffff", 0.9)
                if eyes == "half":
                    lid = G.rrect_p(ex - rx * 1.4, ey - ry * 1.6, rx * 2.8, ry * 1.55, 2)
                    g.fillp(lid, s["skin"])
                    g.line(ex - rx * 1.2, ey - ry * 0.05, ex + rx * 1.2, ey - ry * 0.05, w=g.lw * 1.0)
                if s.get("female") and s["stage"] in ("adult", "teen"):
                    # lashes
                    g.line(ex + side * rx * 0.9, ey - ry * 0.75, ex + side * rx * 1.45, ey - ry * 1.1, w=g.lw * 0.8)
        # brows
        by = ey - r * 0.32
        bw = g.lw * (1.6 if not s.get("female") else 1.3)
        bc = shade(s.get("hair", "#2b2233"), 0.7)
        if s.get("hair_style") == "baby_curl":
            bc = "#3a2a28"
        for side in (-1, 1):
            cx = hx + fx + side * r * 0.36
            inner = (cx - side * r * 0.17, by)
            outer = (cx + side * r * 0.17, by)
            if brows == "angry":
                inner = (inner[0], by + r * 0.11); outer = (outer[0], by - r * 0.04)
            elif brows == "determined":
                inner = (inner[0], by + r * 0.06); outer = (outer[0], by - r * 0.02)
            elif brows == "sad":
                inner = (inner[0], by - r * 0.08); outer = (outer[0], by + r * 0.04)
            elif brows == "raised":
                inner = (inner[0], by - r * 0.1); outer = (outer[0], by - r * 0.08)
            elif brows == "skeptical":
                if side == 1:
                    inner = (inner[0], by - r * 0.1); outer = (outer[0], by - r * 0.12)
                else:
                    inner = (inner[0], by + r * 0.05)
            g.line(inner[0], inner[1], outer[0], outer[1], color=bc, w=bw * 1.6)
        # nose
        q = skia.Path(); nx = hx + fx * 1.2; ny = hy + r * 0.36
        q.moveTo(nx - r * 0.05, ny); q.quadTo(nx, ny + r * 0.05, nx + r * 0.05, ny)
        g.strokep(q, shade(s["skin"], 0.6), w=g.lw * 0.8)
        # beard / stubble (under mouth)
        beard = s.get("beard")
        if beard == "stubble":
            q = skia.Path()
            q.moveTo(hx - r * 0.86, hy + r * 0.2)
            q.cubicTo(hx - r * 0.7, hy + r * 1.15, hx + r * 0.7, hy + r * 1.15, hx + r * 0.86, hy + r * 0.2)
            q.cubicTo(hx + r * 0.6, hy + r * 0.62, hx - r * 0.6, hy + r * 0.62, hx - r * 0.86, hy + r * 0.2)
            g.fillp(q, "#5a3a26", 0.2)
        elif beard == "full_grey":
            q = skia.Path()
            q.moveTo(hx - r * 0.9, hy + r * 0.15)
            q.cubicTo(hx - r * 0.8, hy + r * 1.45, hx + r * 0.8, hy + r * 1.45, hx + r * 0.9, hy + r * 0.15)
            q.cubicTo(hx + r * 0.55, hy + r * 0.55, hx - r * 0.55, hy + r * 0.55, hx - r * 0.9, hy + r * 0.15)
            q.close()
            g.shape(q, PAL["hair_grey"])
        # mouth
        mx = hx + fx * 1.2; my = hy + r * 0.58
        if talk:
            k = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 5.3) * math.sin(t * 2 * math.pi * 2.1 + 1)
            mouth = "open" if abs(k) > 0.25 else "flat"
            op = 0.3 + abs(k) * 0.7
        else:
            op = 1.0
        mw = r * 0.16
        if mouth == "smile":
            q = skia.Path(); q.moveTo(mx - mw, my - r * 0.02); q.quadTo(mx, my + r * 0.12, mx + mw, my - r * 0.02)
            g.strokep(q, w=g.lw * 1.0)
        elif mouth == "grin":
            q = skia.Path(); q.moveTo(mx - mw * 1.3, my - r * 0.04); q.quadTo(mx, my + r * 0.24, mx + mw * 1.3, my - r * 0.04); q.close()
            g.shape(q, "#7a2a33", w=g.lw * 0.9)
            g.fillp(G.rrect_p(mx - mw * 0.9, my - r * 0.03, mw * 1.8, r * 0.05, 1), "#ffffff")
        elif mouth == "smirk":
            q = skia.Path(); q.moveTo(mx - mw * 0.8, my + r * 0.02); q.quadTo(mx + mw * 0.3, my + r * 0.05, mx + mw * 1.1, my - r * 0.06)
            g.strokep(q, w=g.lw * 1.0)
        elif mouth == "frown":
            q = skia.Path(); q.moveTo(mx - mw * 0.9, my + r * 0.06); q.quadTo(mx, my - r * 0.06, mx + mw * 0.9, my + r * 0.06)
            g.strokep(q, w=g.lw * 1.0)
        elif mouth in ("open", "o", "shout", "gummy"):
            hgt = {"open": r * 0.13 * op, "o": r * 0.11, "shout": r * 0.2, "gummy": r * 0.16}[mouth]
            wid = {"open": mw * 0.95, "o": mw * 0.55, "shout": mw * 1.2, "gummy": mw * 1.1}[mouth]
            q = G.ellipse_p(mx, my + hgt * 0.4, wid, max(hgt, r * 0.03))
            g.shape(q, "#7a2a33", w=g.lw * 0.9)
            if mouth in ("open", "shout", "gummy") and hgt > r * 0.07:
                g.c.save(); g.c.clipPath(q, doAntiAlias=True)
                g.fillp(G.ellipse_p(mx, my + hgt * 1.25, wid * 0.7, hgt * 0.5), "#e8767c")
                g.c.restore()
        else:  # flat
            g.line(mx - mw * 0.7, my + r * 0.02, mx + mw * 0.7, my + r * 0.02, w=g.lw * 1.0)
        if beard == "mustache":
            q = skia.Path()
            q.moveTo(mx - r * 0.3, my + r * 0.0)
            q.cubicTo(mx - r * 0.25, my - r * 0.16, mx - r * 0.02, my - r * 0.14, mx, my - r * 0.08)
            q.cubicTo(mx + r * 0.02, my - r * 0.14, mx + r * 0.25, my - r * 0.16, mx + r * 0.3, my + r * 0.0)
            q.cubicTo(mx + r * 0.15, my - r * 0.04, mx - r * 0.15, my - r * 0.04, mx - r * 0.3, my)
            q.close()
            g.shape(q, s.get("hair", "#2b2233"), w=g.lw * 0.7)

    def _mask(self, g, hx, hy, r, face, t, blink_seed, fx, mask):
        col = mask if isinstance(mask, str) else "#2b2b3b"
        hp = G.ellipse_p(hx, hy - r * 0.02, r * 1.04, r * 1.02)
        g.shape(hp, col)
        g.c.save(); g.c.clipPath(hp, doAntiAlias=True)
        for k in range(-4, 5):
            g.line(hx - r * 1.2, hy + k * r * 0.22, hx + r * 1.2, hy + k * r * 0.22, color=shade(col, 0.85), w=g.lw * 0.5)
        g.c.restore()
        g.strokep(hp)
        g.circle(hx, hy - r * 1.05, r * 0.18, tint(col, 0.2))
        g.rrect(hx + fx - r * 0.62, hy - r * 0.08, r * 1.24, r * 0.42, r * 0.2, self.s["skin"])
        g.ellipse(hx + fx, hy + r * 0.62, r * 0.2, r * 0.13, self.s["skin"])
        for side in (-1, 1):
            ex = hx + fx + side * r * 0.3; ey = hy + r * 0.12
            g.fillp(G.ellipse_p(ex, ey, r * 0.11, r * 0.13), "#2a1d22")
            g.fillp(G.circle_p(ex + r * 0.04, ey - r * 0.05, r * 0.04), "#ffffff")
            g.line(ex - side * r * 0.14, ey - r * 0.12, ex + side * r * 0.12, ey - r * 0.22, w=g.lw * 1.4)

    # ---------------------------------------------------------- hair
    def _hair_back(self, g, hx, hy, r, t):
        s = self.s; st = s.get("hair_style"); col = s.get("hair", "#2b2233")
        sway = math.sin(t * 2 * math.pi * 0.4) * r * 0.03
        if st == "long":
            pts = [(hx - r * 1.02, hy - r * 0.3), (hx - r * 1.18, hy + r * 0.5), (hx - r * 1.12 + sway, hy + r * 1.15),
                   (hx - r * 1.3 + sway, hy + r * 1.55), (hx - r * 0.85 + sway, hy + r * 1.65), (hx - r * 0.5, hy + r * 1.3),
                   (hx + r * 0.5, hy + r * 1.3), (hx + r * 0.85 + sway, hy + r * 1.65), (hx + r * 1.3 + sway, hy + r * 1.55),
                   (hx + r * 1.12 + sway, hy + r * 1.15), (hx + r * 1.18, hy + r * 0.5), (hx + r * 1.02, hy - r * 0.3),
                   (hx, hy - r * 1.1)]
            g.smooth(pts, col)
        elif st == "pony":
            pts = [(hx + r * 0.6, hy - r * 0.75), (hx + r * 1.35 + sway, hy - r * 0.6), (hx + r * 1.55 + sway, hy + r * 0.1),
                   (hx + r * 1.35 + sway * 2, hy + r * 0.8), (hx + r * 1.1, hy + r * 0.2), (hx + r * 0.9, hy - r * 0.3)]
            g.smooth(pts, col)
        elif st == "pigtails":
            for side in (-1, 1):
                pts = [(hx + side * r * 0.85, hy - r * 0.45), (hx + side * r * 1.45, hy - r * 0.35 + sway),
                       (hx + side * r * 1.55, hy + r * 0.35), (hx + side * r * 1.25, hy + r * 0.55),
                       (hx + side * r * 1.05, hy + r * 0.05)]
                g.smooth(pts, col)
                g.circle(hx + side * r * 0.95, hy - r * 0.45, r * 0.12, PAL["red"], w=g.lw * 0.7)
        elif st == "long_m":
            pts = [(hx - r * 1.0, hy - r * 0.4), (hx - r * 1.15, hy + r * 0.6), (hx - r * 1.0, hy + r * 1.05),
                   (hx + r * 1.0, hy + r * 1.05), (hx + r * 1.15, hy + r * 0.6), (hx + r * 1.0, hy - r * 0.4),
                   (hx, hy - r * 1.05)]
            g.smooth(pts, col)
        elif st == "bun":
            g.circle(hx + r * 0.05, hy - r * 1.08, r * 0.38, col)

    def _hair_front(self, g, hx, hy, r, t):
        s = self.s; st = s.get("hair_style"); col = s.get("hair", "#2b2233")
        hl = tint(col, 0.18)
        if st in ("long", "pony", "pigtails", "bun"):
            # cap with middle/side part and framing strands
            q = skia.Path()
            q.moveTo(hx - r * 1.03, hy + (r * 0.55 if st == "long" else r * 0.05))
            q.cubicTo(hx - r * 1.12, hy - r * 0.9, hx - r * 0.5, hy - r * 1.1, hx + r * 0.05, hy - r * 1.04)
            q.cubicTo(hx + r * 0.65, hy - r * 1.1, hx + r * 1.12, hy - r * 0.8, hx + r * 1.03, hy + (r * 0.55 if st == "long" else r * 0.05))
            q.cubicTo(hx + r * 0.95, hy - r * 0.2, hx + r * 0.7, hy - r * 0.45, hx + r * 0.42, hy - r * 0.52)
            q.cubicTo(hx + r * 0.2, hy - r * 0.6, hx + r * 0.05, hy - r * 0.75, hx - r * 0.05, hy - r * 0.9)
            q.cubicTo(hx - r * 0.2, hy - r * 0.55, hx - r * 0.6, hy - r * 0.45, hx - r * 0.85, hy - r * 0.3)
            q.cubicTo(hx - r * 0.95, hy - r * 0.1, hx - r * 0.98, hy + r * 0.2, hx - r * 1.03, hy + (r * 0.55 if st == "long" else r * 0.05))
            q.close()
            g.shape(q, col)
            hq = skia.Path(); hq.moveTo(hx - r * 0.6, hy - r * 0.85); hq.quadTo(hx - r * 0.3, hy - r * 0.98, hx - r * 0.05, hy - r * 0.96)
            g.strokep(hq, hl, w=g.lw * 1.3, a=0.8)
        elif st == "short" or st == "slick":
            q = skia.Path()
            q.moveTo(hx - r * 1.0, hy - r * 0.05)
            q.cubicTo(hx - r * 1.1, hy - r * 1.05, hx + r * 1.1, hy - r * 1.05, hx + r * 1.0, hy - r * 0.05)
            if st == "short":
                q.lineTo(hx + r * 0.9, hy - r * 0.4)
                q.lineTo(hx + r * 0.62, hy - r * 0.5); q.lineTo(hx + r * 0.5, hy - r * 0.38)
                q.lineTo(hx + r * 0.25, hy - r * 0.55); q.lineTo(hx + r * 0.05, hy - r * 0.45)
                q.lineTo(hx - r * 0.2, hy - r * 0.6); q.lineTo(hx - r * 0.45, hy - r * 0.48)
                q.lineTo(hx - r * 0.7, hy - r * 0.58); q.lineTo(hx - r * 0.9, hy - r * 0.42)
            else:
                q.cubicTo(hx + r * 0.7, hy - r * 0.6, hx - r * 0.7, hy - r * 0.6, hx - r * 1.0, hy - r * 0.05)
            q.close()
            g.shape(q, col)
            hq = skia.Path(); hq.moveTo(hx - r * 0.5, hy - r * 0.86); hq.quadTo(hx, hy - r * 0.98, hx + r * 0.4, hy - r * 0.88)
            g.strokep(hq, hl, w=g.lw * 1.2, a=0.7)
        elif st == "buzz":
            q = skia.Path()
            q.moveTo(hx - r * 0.98, hy - r * 0.15)
            q.cubicTo(hx - r * 1.05, hy - r * 1.05, hx + r * 1.05, hy - r * 1.05, hx + r * 0.98, hy - r * 0.15)
            q.cubicTo(hx + r * 0.75, hy - r * 0.55, hx - r * 0.75, hy - r * 0.55, hx - r * 0.98, hy - r * 0.15)
            q.close()
            g.shape(q, col, w=g.lw * 0.8)
        elif st == "long_m":
            q = skia.Path()
            q.moveTo(hx - r * 1.0, hy + r * 0.1)
            q.cubicTo(hx - r * 1.1, hy - r * 1.05, hx + r * 1.1, hy - r * 1.05, hx + r * 1.0, hy + r * 0.1)
            q.cubicTo(hx + r * 0.85, hy - r * 0.55, hx + r * 0.3, hy - r * 0.62, hx, hy - r * 0.7)
            q.cubicTo(hx - r * 0.3, hy - r * 0.62, hx - r * 0.85, hy - r * 0.55, hx - r * 1.0, hy + r * 0.1)
            q.close()
            g.shape(q, col)
        elif st == "baby_curl":
            q = skia.Path()
            q.moveTo(hx - r * 0.05, hy - r * 0.92)
            q.cubicTo(hx - r * 0.1, hy - r * 1.35, hx + r * 0.35, hy - r * 1.4, hx + r * 0.32, hy - r * 1.12)
            q.cubicTo(hx + r * 0.3, hy - r * 0.98, hx + r * 0.12, hy - r * 1.0, hx + r * 0.14, hy - r * 1.12)
            g.strokep(q, OUTLINE, w=g.lw * 2.6); g.strokep(q, col, w=g.lw * 1.2)
        elif st == "puffs":
            for side in (-1, 1):
                g.circle(hx + side * r * 0.62, hy - r * 0.86, r * 0.3, col)
            q = skia.Path()
            q.moveTo(hx - r * 0.95, hy - r * 0.2)
            q.cubicTo(hx - r * 1.0, hy - r * 1.0, hx + r * 1.0, hy - r * 1.0, hx + r * 0.95, hy - r * 0.2)
            q.cubicTo(hx + r * 0.6, hy - r * 0.6, hx - r * 0.6, hy - r * 0.6, hx - r * 0.95, hy - r * 0.2)
            q.close()
            g.shape(q, col, w=g.lw * 0.8)

    # ---------------------------------------------------------- baby
    def _baby(self, g, t, face, look, anger, blink_seed):
        s = self.s
        r = 30
        hy = -38 + math.sin(t * 2 * math.pi * 0.5) * 0.6
        # little body bundle
        g.ellipse(0, -2, 26, 16, s.get("top", "#f3a6b8"))
        for side in (-1, 1):
            g.circle(side * 20, -10, 6, s["skin"])
        self.head(g, 0, hy, r, t, face, look, False, False, anger, False, blink_seed)

# ------------------------------------------------------------------ small symbols
def anger_mark(g, x, y, s, t=0.0):
    k = 1 + 0.12 * math.sin(t * 2 * math.pi * 2.2)
    g.save(); g.tr(x, y); g.sc(k)
    for i in range(4):
        g.save(); g.rot(i * 90 + 45)
        q = skia.Path(); q.moveTo(s * 0.22, -s * 0.75); q.quadTo(s * 0.18, -s * 0.2, s * 0.75, -s * 0.22)
        g.strokep(q, "#ffffff", w=s * 0.5)
        g.strokep(q, PAL["red"], w=s * 0.26)
        g.restore()
    g.restore()

def sweat_drop(g, x, y, s, t=0.0):
    yy = y + (t * 0.6 % 1.0) * s * 0.6
    q = skia.Path(); q.moveTo(x, yy - s * 1.2); q.cubicTo(x + s, yy, x + s * 0.6, yy + s * 0.8, x, yy + s * 0.8)
    q.cubicTo(x - s * 0.6, yy + s * 0.8, x - s, yy, x, yy - s * 1.2)
    g.shape(q, "#8fd3ff", w=g.lw * 0.7)

def draw_prop(g, kind, x, y, hr):
    if kind == "glass":
        q = skia.Path()
        q.moveTo(x - hr * 1.0, y - hr * 3.2); q.lineTo(x + hr * 1.0, y - hr * 3.2)
        q.lineTo(x + hr * 0.8, y - hr * 0.6); q.lineTo(x - hr * 0.8, y - hr * 0.6); q.close()
        g.shape(q, "#d8f1ff", w=g.lw * 0.8, a=0.9)
        g.fillp(G.rrect_p(x - hr * 0.86, y - hr * 2.2, hr * 1.72, hr * 1.55, 0.6), PAL["gold"], 0.85)
        g.circle(x, y, hr, None)
    elif kind == "beer":
        g.rrect(x - hr * 0.8, y - hr * 2.6, hr * 1.6, hr * 2.8, hr * 0.4, "#8a5a2a", w=g.lw * 0.8)
        g.rrect(x - hr * 0.8, y - hr * 1.9, hr * 1.6, hr * 1.0, 0.5, PAL["cream"], w=g.lw * 0.6)
    elif kind == "photo":
        g.save(); g.tr(x, y - hr * 2.6); g.rot(-8)
        g.rrect(-hr * 2.2, -hr * 2.6, hr * 4.4, hr * 4.4, hr * 0.3, "#fbf7f0", w=g.lw * 0.8)
        g.rrect(-hr * 1.7, -hr * 2.1, hr * 3.4, hr * 2.9, hr * 0.2, "#f6c27a", w=g.lw * 0.5)
        g.circle(0, -hr * 0.9, hr * 0.7, PAL["skin_mom"], w=g.lw * 0.5)
        g.circle(0, -hr * 1.45, hr * 0.38, PAL["hair_dark"], w=g.lw * 0.4)
        g.restore()
    elif kind == "hammer":
        g.save(); g.tr(x, y); g.rot(-30)
        g.rrect(-hr * 0.35, -hr * 4.2, hr * 0.7, hr * 4.6, hr * 0.3, "#b07a46", w=g.lw * 0.7)
        g.rrect(-hr * 1.6, -hr * 5.0, hr * 3.2, hr * 1.2, hr * 0.3, "#7a8494", w=g.lw * 0.7)
        g.restore()
    elif kind == "phone":
        g.rrect(x - hr * 1.0, y - hr * 3.2, hr * 2.0, hr * 3.4, hr * 0.35, "#2b2233", w=g.lw * 0.7)
        g.rrect(x - hr * 0.75, y - hr * 2.9, hr * 1.5, hr * 2.6, hr * 0.2, "#8fd3ff", w=0)
    elif kind == "cards":
        for k, col in enumerate(("#fbf7f0", "#fbf7f0", "#fbf7f0")):
            g.save(); g.tr(x, y - hr); g.rot(-20 + k * 18)
            g.rrect(-hr * 0.8, -hr * 2.4, hr * 1.6, hr * 2.4, hr * 0.25, col, w=g.lw * 0.6)
            g.fillp(G.circle_p(0, -hr * 1.2, hr * 0.35), PAL["red"])
            g.restore()
    elif kind == "bag":
        q = skia.Path()
        q.moveTo(x - hr * 2.2, y + hr * 0.5); q.cubicTo(x - hr * 2.8, y + hr * 4.5, x + hr * 2.8, y + hr * 4.5, x + hr * 2.2, y + hr * 0.5)
        q.lineTo(x + hr * 0.8, y - hr * 0.2); q.lineTo(x - hr * 0.8, y - hr * 0.2); q.close()
        g.shape(q, "#8a7a52", w=g.lw * 0.8)
        from gfx import text as _t
        _t(g, "$", x, y + hr * 3.1, hr * 2.6, fill=PAL["gold"], ow=hr * 0.4, shadow=False)
    elif kind == "mic":
        g.rrect(x - hr * 0.4, y - hr * 2.5, hr * 0.8, hr * 2.5, hr * 0.3, "#3b3f55", w=g.lw * 0.6)
        g.circle(x, y - hr * 2.8, hr * 0.8, "#9aa0ad", w=g.lw * 0.6)
