# -*- coding: utf-8 -*-
"""Semi-realistic adult rig (the channel's 'grown-up' look): realistic proportions, thin dark
outline, flat fills with one cel-shadow tone, detailed eyes / nose / lips, textured hair.

Units: hh = head height. Full figure = 7.5 hh, crown at y=-7.5hh, feet at y=0.
draw(g, x, y_feet, size, ...) -> size = full figure height in px (same call shape as the chibi rig).
"""
import math, random
import skia
from gfx import G, OUTLINE, PAL, C, P_fill, P_stroke, shade, tint, mix, clamp, lerp, ease_io

LINE = "#231a22"

def sp(pts, close=True, k=0.5):
    return G.smooth_p(pts, close, k)

# ------------------------------------------------------------------ cast
def ADULTS():
    return {
        "lucia": dict(sex="f", skin="#b9784f", hair="#241614", hair_hl="#5b3a2c", hair_style="long_wavy",
                      eyes="#3b2418", lips="#a5574f", outfit="jacket", top="#f4efe6", jacket="#4a6fa8",
                      pants="#26283a", shoes="#1e1a22", acc=["hoops"]),
        "lucia_night": dict(sex="f", skin="#b9784f", hair="#241614", hair_hl="#5b3a2c", hair_style="long_wavy",
                            eyes="#3b2418", lips="#a5574f", outfit="tank", top="#1f1b2c", pants="#26283a",
                            shoes="#1e1a22", acc=["hoops"]),
        "lucia_prison": dict(sex="f", skin="#b9784f", hair="#241614", hair_hl="#5b3a2c", hair_style="pony",
                             eyes="#3b2418", lips="#9c5a50", outfit="jumpsuit", top="#e8772c", pants="#e8772c",
                             shoes="#f2efe8", acc=["hoops_small"]),
        "lucia_teen": dict(sex="f", skin="#b9784f", hair="#241614", hair_hl="#5b3a2c", hair_style="pony",
                           eyes="#3b2418", lips="#a5574f", outfit="tank", top="#e85d9a", pants="#4a6fa8",
                           shoes="#f2efe8", acc=["hoops"], teen=True),
        "jason": dict(sex="m", skin="#dca47c", hair="#4a2e1e", hair_hl="#7a5236", hair_style="short_messy",
                      eyes="#4a5a3a", lips="#b77a66", outfit="tee", top="#556347", pants="#34425a",
                      shoes="#1e1a22", beard="stubble", acc=["tattoos"]),
        "jason_army": dict(sex="m", skin="#dca47c", hair="#4a2e1e", hair_hl="#7a5236", hair_style="buzz",
                           eyes="#4a5a3a", lips="#b77a66", outfit="army", top="#66703f", pants="#56602f",
                           shoes="#3a2e24", acc=["helmet"]),
        "mom": dict(sex="f", skin="#b5744d", hair="#2a1a16", hair_hl="#4e3328", hair_style="bun", eyes="#3b2418",
                    lips="#9c5a50", outfit="cardigan", top="#efe4cf", jacket="#b8608f", pants="#463a5e",
                    shoes="#1e1a22", acc=["earrings"], age=1),
        "brian": dict(sex="m", skin="#d99c76", hair="#c9c4bb", hair_hl="#eeeae2", hair_style="long_grey",
                      eyes="#5a6a7a", lips="#b77a66", outfit="hawaiian", top="#2a9d8f", pants="#d8ccb0",
                      shoes="#7a5236", beard="full_grey", age=2),
        "officer": dict(sex="f", skin="#e6b896", hair="#7a4e32", hair_hl="#a8744e", hair_style="bun",
                        eyes="#4a5a6a", lips="#b06a62", outfit="uniform", top="#6f7b8c", pants="#454d5a",
                        shoes="#1e1a22"),
        "guard": dict(sex="m", skin="#7a4e34", hair="#1c1414", hair_hl="#3a2a24", hair_style="buzz",
                      eyes="#2a1a14", lips="#5e3a30", outfit="uniform", top="#6f7b8c", pants="#454d5a",
                      shoes="#1e1a22", acc=["cap"]),
        "cashier": dict(sex="m", skin="#e8b896", hair="#b9763e", hair_hl="#d89a5e", hair_style="short_messy",
                        eyes="#4a6a8a", lips="#c08070", outfit="tee", top="#d8463c", pants="#3b3f55",
                        shoes="#1e1a22", acc=["cap_red"]),
        "grifter1": dict(sex="m", skin="#e2b08e", hair="#1c1616", hair_hl="#3a3030", hair_style="slick",
                         eyes="#2a1a14", lips="#b07a6a", outfit="suit", top="#2e2a3e", pants="#1f1c28",
                         shoes="#141018", beard="mustache", acc=["shades"]),
        "grifter2": dict(sex="m", skin="#6e4630", hair="#141010", hair_hl="#2e2422", hair_style="buzz",
                         eyes="#2a1a14", lips="#563428", outfit="hawaiian", top="#8a3a3a", pants="#1f1c28",
                         shoes="#141018", acc=["shades", "chain"]),
        "dad": dict(sex="m", skin="#a8693f", hair="#1e1614", hair_hl="#3e2c26", hair_style="short_messy",
                    eyes="#2a1a14", lips="#7a4a3a", outfit="tank", top="#d8463c", pants="#34384a",
                    shoes="#1e1a22", beard="mustache", acc=["chain"]),
    }

# ------------------------------------------------------------------ poses: hand target relative to shoulder (hh)
APOSE = {
    "idle":      ((-0.12, 2.65), (0.12, 2.65)),
    "relaxed":   ((-0.25, 2.55), (0.25, 2.55)),
    "hips":      ((0.02, 1.62), (-0.02, 1.62)),
    "cross":     ((1.05, 0.95), (-1.05, 0.95)),
    "hands_up":  ((-0.55, -1.25), (0.55, -1.25)),
    "shrug":     ((-0.85, 0.95), (0.85, 0.95)),
    "point_r":   ((-0.12, 2.65), (2.4, 0.15)),
    "point_viewer": ((-0.12, 2.65), (0.65, 0.6)),
    "wave_r":    ((-0.12, 2.65), (0.75, -1.15)),
    "raise_r":   ((-0.12, 2.65), (0.45, -0.95)),
    "phone":     ((-0.12, 2.65), (-0.45, -0.45)),
    "chin":      ((-0.12, 2.65), (-0.6, -0.55)),
    "facepalm":  ((-0.12, 2.65), (-0.62, -1.12)),
    "behind":    ((0.35, 2.2), (-0.35, 2.2)),
    "hold_front": ((0.95, 1.45), (-0.95, 1.45)),
    "hold_r":    ((-0.12, 2.65), (0.1, 1.3)),
    "guard":     ((0.22, -0.62), (-0.22, -0.62)),
    "punch_r":   ((0.22, -0.62), (2.6, -0.35)),
    "hammer":    ((-0.12, 2.65), (1.0, -0.8)),
    "salute":    ((-0.12, 2.65), (-0.36, -1.22)),
    "drive":     ((0.6, 1.3), (-0.6, 1.3)),
}
FRONT = {"guard", "hips", "punch_r", "phone", "chin", "facepalm", "cross", "hold_front", "raise_r", "salute", "hold_r",
         "point_viewer", "hands_up", "wave_r", "hammer", "shrug"}

FORESHORT = {"guard": (0.58, 0.58), "punch_r": (0.58, 1.0), "chin": (1.0, 0.62), "phone": (1.0, 0.62),
             "facepalm": (1.0, 0.7), "raise_r": (1.0, 0.85)}

ELBOW_DOWN = {"guard", "punch_r", "chin", "phone", "raise_r", "facepalm", "wave_r", "hammer", "point_viewer"}

def ik(sx, sy, hx, hy, l1, l2, outward, down=False):
    dx, dy = hx - sx, hy - sy
    d = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    a = math.atan2(dy, dx)
    b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    e1 = (sx + l1 * math.cos(a + b), sy + l1 * math.sin(a + b))
    e2 = (sx + l1 * math.cos(a - b), sy + l1 * math.sin(a - b))
    if down:
        e = e1 if e1[1] > e2[1] else e2
    else:
        e = e1 if (e1[0] - e2[0]) * outward > 0 else e2
    return e, (sx + d * math.cos(a), sy + d * math.sin(a))

def taper(p0, p1, w0, w1):
    """quad polygon around a segment with widths w0 -> w1"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    return [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
            (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]

# ------------------------------------------------------------------ rig
class Adult:
    def __init__(self, spec, seed=1):
        self.s = spec
        self.rnd = random.Random(seed)
        r = random.Random(seed * 7 + 3)
        self.stubble = [(r.uniform(-0.36, 0.36), r.uniform(0.12, 0.52), r.uniform(0.0025, 0.005)) for _ in range(900)]

    # public ---------------------------------------------------------
    def draw(self, g, x, y, size, t=0.0, pose="idle", pose2=None, pose_k=0.0, face=None, look=0.0, talk=False,
             flip=False, held=None, mask=False, anger=False, sweat=False, blink_seed=0.0, sit=False, walk=0.0,
             breathe=True, legs_hidden=False, tilt=0.0, hand_override=None, light=-1.0, **kw):
        s = self.s
        face = face or {}
        hh = size / 7.5
        if not blink_seed:
            blink_seed = (x * 0.0131 + len(s["skin"]) * 0.37) % 3.7
        g.save(); g.tr(x, y); g.sc(-hh if flip else hh, hh)
        if tilt: g.rot(tilt)
        old = g.lw; g.lw = max(2.2, 3.4 * (hh / 150) ** 0.35) / hh
        br = math.sin(t * 2 * math.pi * 0.3 + blink_seed) * 0.012 if breathe else 0
        bob = -abs(math.sin(t * math.pi * 2 * 1.5)) * 0.06 * walk
        if sit:
            g.tr(0, 3.75 - 0.05)      # hips on y
        g.tr(0, bob)
        f = 0.92 if s["sex"] == "f" else 1.0
        P = dict(
            crown=-7.5, head_c=-7.0, chin=-6.5,
            sh_y=-6.05, sh_x=0.86 * f + (0.06 if s.get("sex") == "m" else 0),
            waist_y=-4.55, waist_x=0.58 if s["sex"] == "f" else 0.72,
            hip_y=-3.75, hip_x=0.8 if s["sex"] == "f" else 0.74,
            l1=1.45, l2=1.32,
        )
        self.P = P
        # hands
        if hand_override is not None:
            hands = hand_override
        elif pose2:
            a, b = APOSE[pose], APOSE[pose2]; k = ease_io(pose_k)
            hands = tuple((lerp(a[i][0], b[i][0], k), lerp(a[i][1], b[i][1], k)) for i in range(2))
        else:
            hands = APOSE[pose]
        front = (pose in FRONT) or (pose2 in FRONT and pose_k > 0.5)
        # back hair
        self._hair_back(g, t)
        # legs
        if not legs_hidden:
            self._legs(g, t, sit, walk)
        self._neck(g)
        # torso
        g.save(); g.tr(0, P["waist_y"]); g.sc(1, 1 + br); g.tr(0, -P["waist_y"])
        self._torso(g, t)
        g.restore()
        self.fs = FORESHORT.get(pose2 if (pose2 and pose_k > 0.5) else pose, (1.0, 1.0)) if hand_override is None else (1.0, 1.0)
        self.pose_now = pose2 if (pose2 and pose_k > 0.5) else pose
        self.elbow_down = (pose in ELBOW_DOWN) if not (pose2 and pose_k > 0.5) else (pose2 in ELBOW_DOWN)
        arms = lambda: self._arms(g, hands, held, t)
        if not front: arms()
        self._head(g, t, face, look, talk, blink_seed, mask, light)
        if front: arms()
        if anger:
            from characters import anger_mark
            anger_mark(g, 0.55, -7.55, 0.22, t)
        if sweat:
            from characters import sweat_drop
            sweat_drop(g, -0.45, -7.25, 0.09, t)
        g.lw = old
        g.restore()

    # parts ---------------------------------------------------------------
    def _skin(self):
        s = self.s
        return s["skin"], shade(s["skin"], 0.84), shade(s["skin"], 0.7)

    def _neck(self, g):
        sk, sh, dk = self._skin()
        P = self.P
        w = 0.17 if self.s["sex"] == "f" else 0.21
        p = sp([(-w, P["chin"] - 0.2), (w, P["chin"] - 0.2), (w + 0.02, P["sh_y"] - 0.25), (w + 0.16, P["sh_y"] - 0.08),
                (-w - 0.16, P["sh_y"] - 0.08), (-w - 0.02, P["sh_y"] - 0.25)], k=0.2)
        g.shape(p, sk)
        q = skia.Path(); q.moveTo(-w, P["chin"] - 0.1); q.quadTo(0, P["chin"] + 0.12, w, P["chin"] - 0.1)
        q.lineTo(w, P["chin"] + 0.05); q.quadTo(0, P["chin"] + 0.25, -w, P["chin"] + 0.05); q.close()
        g.fillp(q, sh)

    def _head(self, g, t, face, look, talk, blink_seed, mask, light):
        s = self.s; sk, sh, dk = self._skin()
        cy = self.P["head_c"]
        fem = s["sex"] == "f"
        jw = 0.3 if fem else 0.33
        fx = look * 0.07
        # ears
        for side in (-1, 1):
            ex = side * (0.355 if fem else 0.37) + fx * 0.3
            q = sp([(ex, cy - 0.0), (ex + side * 0.055, cy - 0.02), (ex + side * 0.065, cy + 0.08), (ex + side * 0.025, cy + 0.17),
                    (ex - side * 0.01, cy + 0.14)])
            g.shape(q, sk)
            g.line(ex + side * 0.035, cy + 0.02, ex + side * 0.04, cy + 0.12, color=sh, w=g.lw * 0.9)
        # face
        pts = [(0, cy - 0.5), (0.3, cy - 0.44), (0.365, cy - 0.2), (0.365, cy + 0.05), (jw, cy + 0.27),
               (0.13 if fem else 0.15, cy + 0.46), (0, cy + 0.5), (-(0.13 if fem else 0.15), cy + 0.46), (-jw, cy + 0.27),
               (-0.365, cy + 0.05), (-0.365, cy - 0.2), (-0.3, cy - 0.44)]
        fp = sp(pts)
        g.fillp(fp, sk)
        # cel shadow on the side away from light
        side = -light   # +1: shadow on right
        g.c.save(); g.c.clipPath(fp, doAntiAlias=True)
        q = skia.Path()
        q.moveTo(side * 0.45, cy - 0.6); q.lineTo(side * 0.2, cy - 0.45)
        q.cubicTo(side * 0.27, cy - 0.15, side * 0.25, cy + 0.15, side * 0.17, cy + 0.32)
        q.quadTo(side * 0.1, cy + 0.45, 0, cy + 0.53); q.lineTo(side * 0.5, cy + 0.6); q.close()
        g.fillp(q, sh, 0.9)
        # under-hair shadow & cheekbone accent
        g.fillp(G.ellipse_p(0, cy - 0.47, 0.42, 0.14), dk, 0.35)
        q = skia.Path(); q.moveTo(-side * 0.33, cy + 0.12); q.quadTo(-side * 0.25, cy + 0.2, -side * 0.24, cy + 0.27)
        g.strokep(q, sh, w=g.lw * 1.2, a=0.7)
        g.c.restore()
        g.strokep(fp, LINE)
        # stubble / beard
        beard = s.get("beard")
        if beard == "stubble":
            g.c.save(); g.c.clipPath(fp, doAntiAlias=True)
            bp = skia.Path(); bp.moveTo(-0.37, cy + 0.08); bp.cubicTo(-0.3, cy + 0.6, 0.3, cy + 0.6, 0.37, cy + 0.08)
            bp.cubicTo(0.2, cy + 0.27, 0.12, cy + 0.2, 0, cy + 0.22); bp.cubicTo(-0.12, cy + 0.2, -0.2, cy + 0.27, -0.37, cy + 0.08)
            g.fillp(bp, "#3a2618", 0.14)
            for (dx, dy, r) in self.stubble:
                if bp.contains(dx, cy + dy):
                    g.fillp(G.circle_p(dx, cy + dy, r), "#3a2618", 0.3)
            g.c.restore()
        # eyes
        ey = cy + 0.02
        brows = face.get("brows", "neutral"); eyes = face.get("eyes", "open")
        blink = ((t + blink_seed) % 3.7) < 0.11 and eyes == "open"
        for sd in (-1, 1):
            self._eye(g, sd * 0.155 + fx, ey, sd, eyes, brows, blink, fem, look)
        # brows
        bc = shade(s["hair"], 0.9) if s.get("hair_style") != "long_grey" else "#9a958c"
        for sd in (-1, 1):
            bx = sd * 0.155 + fx
            by = ey - 0.105
            inner = (bx - sd * 0.085, by + 0.01); mid = (bx, by - 0.025); outer = (bx + sd * 0.1, by + 0.012)
            dy_in = {"angry": 0.045, "determined": 0.028, "sad": -0.035, "raised": -0.035, "skeptical": 0.0}.get(brows, 0.0)
            dy_mid = {"raised": -0.03, "sad": -0.01, "angry": 0.01}.get(brows, 0.0)
            if brows == "skeptical" and sd == 1:
                dy_in, dy_mid = -0.035, -0.04
            inner = (inner[0], inner[1] + dy_in); mid = (mid[0], mid[1] + dy_mid)
            thick = 0.032 if not fem else 0.022
            q = skia.Path(); q.moveTo(*inner); q.quadTo(mid[0], mid[1] - thick, outer[0], outer[1])
            q.quadTo(mid[0], mid[1] + thick * 0.4, inner[0], inner[1] + thick); q.close()
            g.fillp(q, bc)
        # nose
        nx = fx * 1.35
        q = skia.Path(); q.moveTo(nx + side * 0.03, cy - 0.04); q.cubicTo(nx + side * 0.045, cy + 0.08, nx + side * 0.06, cy + 0.14, nx + side * 0.05, cy + 0.2)
        g.strokep(q, sh, w=g.lw * 1.4)
        q = skia.Path()
        q.moveTo(nx - 0.055, cy + 0.19); q.quadTo(nx - 0.065, cy + 0.235, nx - 0.03, cy + 0.235)
        q.quadTo(nx, cy + 0.25, nx + 0.03, cy + 0.235); q.quadTo(nx + 0.065, cy + 0.235, nx + 0.055, cy + 0.19)
        g.strokep(q, LINE, w=g.lw * 0.9)
        g.fillp(G.ellipse_p(nx - 0.025, cy + 0.228, 0.012, 0.006), dk)
        g.fillp(G.ellipse_p(nx + 0.025, cy + 0.228, 0.012, 0.006), dk)
        g.fillp(G.ellipse_p(nx + side * 0.01, cy + 0.255, 0.05, 0.012), sh, 0.6)
        # mouth
        self._mouth(g, nx, cy + 0.33, face.get("mouth", "flat"), talk, t, fem)
        if beard == "mustache":
            q = skia.Path(); mx, my = nx, cy + 0.3
            q.moveTo(mx - 0.11, my + 0.02); q.cubicTo(mx - 0.09, my - 0.05, mx - 0.02, my - 0.05, mx, my - 0.035)
            q.cubicTo(mx + 0.02, my - 0.05, mx + 0.09, my - 0.05, mx + 0.11, my + 0.02)
            q.cubicTo(mx + 0.06, my - 0.005, mx - 0.06, my - 0.005, mx - 0.11, my + 0.02); q.close()
            g.shape(q, s["hair"], LINE, w=g.lw * 0.6)
        if beard == "full_grey":
            q = skia.Path()
            q.moveTo(-0.36, cy + 0.02); q.cubicTo(-0.36, cy + 0.7, 0.36, cy + 0.7, 0.36, cy + 0.02)
            q.cubicTo(0.26, cy + 0.3, 0.12, cy + 0.26, 0.05, cy + 0.28)
            q.lineTo(0.08, cy + 0.38); q.quadTo(0, cy + 0.42, -0.08, cy + 0.38); q.lineTo(-0.05, cy + 0.28)
            q.cubicTo(-0.12, cy + 0.26, -0.26, cy + 0.3, -0.36, cy + 0.02); q.close()
            g.shape(q, s["hair"], LINE, w=g.lw * 0.8)
            for k in range(9):
                xx = -0.25 + k * 0.06
                g.line(xx, cy + 0.38, xx * 0.8, cy + 0.6, color=s["hair_hl"], w=g.lw * 0.8, a=0.8)
            mx, my = nx, cy + 0.3
            q = skia.Path(); q.moveTo(mx - 0.13, my + 0.03); q.cubicTo(mx - 0.08, my - 0.06, mx + 0.08, my - 0.06, mx + 0.13, my + 0.03)
            q.cubicTo(mx + 0.05, my, mx - 0.05, my, mx - 0.13, my + 0.03); q.close()
            g.shape(q, s["hair_hl"], LINE, w=g.lw * 0.6)
        self._hair_front(g, t)
        acc = s.get("acc", [])
        if "hoops" in acc or "hoops_small" in acc or "earrings" in acc:
            r = 0.085 if "hoops" in acc else 0.045
            for sd in (-1, 1):
                ex = sd * 0.385 + fx * 0.3
                q = G.circle_p(ex, cy + 0.2 + r, r)
                g.strokep(q, LINE, w=g.lw * 2.6); g.strokep(q, "#e9b949", w=g.lw * 1.3)
        if "shades" in acc:
            for sd in (-1, 1):
                g.shape(G.rrect_p(sd * 0.155 + fx - 0.11, ey - 0.06, 0.22, 0.12, 0.04), "#151018", LINE, w=g.lw * 0.8)
                g.line(sd * 0.155 + fx - 0.06, ey - 0.03, sd * 0.155 + fx - 0.02, ey - 0.045, color="#ffffff", w=g.lw, a=0.5)
            g.line(fx - 0.045, ey - 0.02, fx + 0.045, ey - 0.02, color=LINE, w=g.lw * 1.2)
        if "cap" in acc or "cap_red" in acc:
            col = "#2f3b52" if "cap" in acc else "#c83a32"
            q = skia.Path(); q.moveTo(-0.39, cy - 0.2); q.cubicTo(-0.4, cy - 0.66, 0.4, cy - 0.66, 0.39, cy - 0.2); q.close()
            g.shape(q, col, LINE)
            q = skia.Path(); q.moveTo(-0.4, cy - 0.2); q.quadTo(fx * 2, cy - 0.27, 0.4, cy - 0.2); q.quadTo(fx * 2 + 0.05, cy - 0.08, -0.4, cy - 0.2)
            g.shape(q, shade(col, 0.8), LINE)
            if "cap" in acc:
                g.shape(G.circle_p(fx, cy - 0.37, 0.05), "#d8b04a", LINE, w=g.lw * 0.6)
        if "helmet" in acc:
            q = skia.Path(); q.moveTo(-0.45, cy - 0.12); q.cubicTo(-0.48, cy - 0.78, 0.48, cy - 0.78, 0.45, cy - 0.12); q.close()
            g.shape(q, "#5f6a38", LINE)
            g.shape(G.rrect_p(-0.47, cy - 0.17, 0.94, 0.07, 0.03), "#4c552b", LINE, w=g.lw * 0.7)
        if mask:
            col = mask if isinstance(mask, str) else "#262230"
            g.c.save(); g.c.clipPath(fp, doAntiAlias=True)
            g.rect_fill(-0.6, cy - 0.7, 1.2, 1.4, col)
            for k in range(-8, 9):
                g.line(-0.6, cy + k * 0.06, 0.6, cy + k * 0.06, color=shade(col, 0.85), w=g.lw * 0.6)
            g.c.restore()
            g.strokep(fp, LINE)
            g.shape(G.rrect_p(fx - 0.29, ey - 0.08, 0.58, 0.16, 0.07), sk, LINE)
            for sd in (-1, 1):
                self._eye(g, sd * 0.155 + fx, ey, sd, "open", "angry", False, fem, look)
            g.shape(G.ellipse_p(nx, cy + 0.33, 0.07, 0.045), sk, LINE)
            g.shape(G.circle_p(0, cy - 0.55, 0.08), tint(col, 0.2), LINE)

    def _eye(self, g, ex, ey, sd, eyes, brows, blink, fem, look):
        s = self.s; sk, sh, dk = self._skin()
        w = 0.076; h = 0.039
        if eyes in ("closed",) or blink:
            q = skia.Path(); q.moveTo(ex - w, ey); q.quadTo(ex, ey + h * 0.9, ex + w, ey)
            g.strokep(q, LINE, w=g.lw * 1.3)
            return
        top = -h * (0.55 if brows in ("angry",) or eyes == "half" else (0.75 if brows == "determined" else 1.0))
        if eyes == "wide": top = -h * 1.3
        bot = h * (0.45 if eyes == "happy" else 0.8)
        q = skia.Path()
        q.moveTo(ex - w * sd, ey + 0.004)
        q.cubicTo(ex - w * 0.5 * sd, ey + top * 1.25, ex + w * 0.45 * sd, ey + top * 1.2, ex + w * sd, ey - 0.004)
        q.cubicTo(ex + w * 0.5 * sd, ey + bot, ex - w * 0.4 * sd, ey + bot, ex - w * sd, ey + 0.004); q.close()
        g.fillp(q, "#f3ede6")
        g.c.save(); g.c.clipPath(q, doAntiAlias=True)
        ix = ex + look * 0.025
        g.fillp(G.circle_p(ix, ey + 0.002, 0.034), s["eyes"])
        g.fillp(G.circle_p(ix, ey + 0.002, 0.016), "#120c0c")
        g.fillp(G.circle_p(ix + 0.012, ey - 0.013, 0.009), "#ffffff", 0.95)
        g.fillp(G.rect_p(ex - w, ey + top * 1.3, 2 * w, h * 0.5) if hasattr(G, "rect_p") else G.rrect_p(ex - w, ey + top * 1.3, 2 * w, h * 0.45, 0.001), sh, 0.45)
        g.c.restore()
        # upper lid line (thicker), lash wing for women
        ql = skia.Path(); ql.moveTo(ex - w * sd * 1.02, ey + 0.004)
        ql.cubicTo(ex - w * 0.5 * sd, ey + top * 1.25, ex + w * 0.45 * sd, ey + top * 1.2, ex + w * sd * 1.05, ey - 0.004)
        g.strokep(ql, LINE, w=g.lw * (1.9 if fem else 1.5))
        if fem:
            g.line(ex + w * sd * 1.0, ey - 0.004, ex + w * sd * 1.35, ey - 0.03, color=LINE, w=g.lw * 1.3)
        qb = skia.Path(); qb.moveTo(ex - w * sd * 0.8, ey + bot * 0.85); qb.quadTo(ex, ey + bot * 1.15, ex + w * sd * 0.85, ey + bot * 0.6)
        g.strokep(qb, sh, w=g.lw * 0.8)
        # crease
        qc = skia.Path(); qc.moveTo(ex - w * sd * 0.7, ey + top * 1.25 - 0.018); qc.quadTo(ex, ey + top * 1.6 - 0.02, ex + w * sd * 0.9, ey + top * 0.9 - 0.016)
        g.strokep(qc, sh, w=g.lw * 0.8, a=0.9)

    def _mouth(self, g, mx, my, mouth, talk, t, fem):
        s = self.s; sk, sh, dk = self._skin()
        w = 0.075 if fem else 0.08
        lip = s.get("lips", shade(sk, 0.8))
        if talk:
            k = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 5.1) * math.sin(t * 2 * math.pi * 2.3 + 1)
            mouth = "open" if k > 0.35 else "flat"
            op = 0.35 + 0.65 * k
        else:
            op = 1.0
        cu = {"smile": -0.022, "grin": -0.028, "frown": 0.018, "smirk": 0.0}.get(mouth, 0.0)
        if mouth in ("open", "shout", "o", "grin"):
            hgt = {"open": 0.05 * op, "shout": 0.08, "o": 0.045, "grin": 0.035}[mouth]
            ww = w * (0.55 if mouth == "o" else 1.0)
            q = skia.Path(); q.moveTo(mx - ww, my + cu)
            q.cubicTo(mx - ww * 0.5, my - 0.012, mx + ww * 0.5, my - 0.012, mx + ww, my + cu)
            q.cubicTo(mx + ww * 0.6, my + hgt * 1.4, mx - ww * 0.6, my + hgt * 1.4, mx - ww, my + cu); q.close()
            g.shape(q, "#3a1418", LINE, w=g.lw * 0.9)
            g.c.save(); g.c.clipPath(q, doAntiAlias=True)
            g.fillp(G.rrect_p(mx - ww, my - 0.02, 2 * ww, 0.028, 0.005), "#f4efe8")
            g.fillp(G.ellipse_p(mx, my + hgt * 1.25, ww * 0.6, hgt * 0.5), "#b24a52")
            g.c.restore()
            # upper lip
            ul = skia.Path(); ul.moveTo(mx - ww, my + cu); ul.cubicTo(mx - ww * 0.5, my - 0.03, mx - 0.012, my - 0.032, mx, my - 0.018)
            ul.cubicTo(mx + 0.012, my - 0.032, mx + ww * 0.5, my - 0.03, mx + ww, my + cu)
            ul.cubicTo(mx + ww * 0.5, my - 0.008, mx - ww * 0.5, my - 0.008, mx - ww, my + cu); ul.close()
            g.fillp(ul, shade(lip, 0.9))
            return
        cl, cr = cu, cu
        if mouth == "smirk":
            cl, cr = 0.008, -0.025
        # lips
        ul = skia.Path(); ul.moveTo(mx - w, my + cl)
        ul.cubicTo(mx - w * 0.5, my - 0.028, mx - 0.012, my - 0.03, mx, my - 0.016)
        ul.cubicTo(mx + 0.012, my - 0.03, mx + w * 0.5, my - 0.028, mx + w, my + cr)
        ul.cubicTo(mx + w * 0.5, my + 0.004, mx - w * 0.5, my + 0.004, mx - w, my + cl); ul.close()
        g.fillp(ul, shade(lip, 0.88) if fem else shade(sk, 0.78))
        ll = skia.Path(); ll.moveTo(mx - w * 0.9, my + cl * 0.8 + 0.003)
        ll.cubicTo(mx - w * 0.4, my + 0.045, mx + w * 0.4, my + 0.045, mx + w * 0.9, my + cr * 0.8 + 0.003)
        ll.cubicTo(mx + w * 0.4, my + 0.006, mx - w * 0.4, my + 0.006, mx - w * 0.9, my + cl * 0.8 + 0.003); ll.close()
        g.fillp(ll, lip if fem else shade(sk, 0.86))
        if not fem:
            g.fillp(G.ellipse_p(mx, my + 0.032, w * 0.4, 0.008), "#ffffff", 0.18)
        q = skia.Path(); q.moveTo(mx - w, my + cl); q.cubicTo(mx - w * 0.4, my + 0.006, mx + w * 0.4, my + 0.006, mx + w, my + cr)
        g.strokep(q, LINE, w=g.lw * 1.1)
        # under-lip shadow
        g.fillp(G.ellipse_p(mx, my + 0.075, 0.04, 0.012), sh, 0.6)

    # hair --------------------------------------------------------------
    def _hair_back(self, g, t):
        s = self.s; st = s.get("hair_style"); col = s["hair"]
        cy = self.P["head_c"]
        sway = math.sin(t * 1.6) * 0.02
        if st == "long_wavy":
            pts = [(0, cy - 0.58), (0.42, cy - 0.45), (0.5, cy - 0.1), (0.52, cy + 0.3), (0.6 + sway, cy + 0.7),
                   (0.66 + sway, cy + 1.1), (0.58 + sway, cy + 1.45), (0.68 + sway, cy + 1.75), (0.45 + sway, cy + 1.9),
                   (0.25, cy + 1.6), (-0.25, cy + 1.6), (-0.45 + sway, cy + 1.9), (-0.68 + sway, cy + 1.75),
                   (-0.58 + sway, cy + 1.45), (-0.66 + sway, cy + 1.1), (-0.6 + sway, cy + 0.7), (-0.52, cy + 0.3),
                   (-0.5, cy - 0.1), (-0.42, cy - 0.45)]
            g.shape(sp(pts), col, LINE)
            for k in range(6):
                xx = -0.5 + k * 0.2
                q = skia.Path(); q.moveTo(xx * 0.9, cy + 0.5); q.cubicTo(xx * 1.15, cy + 0.9, xx * 0.95, cy + 1.2, xx * 1.2 + sway, cy + 1.6)
                g.strokep(q, s["hair_hl"], w=g.lw * 1.2, a=0.6)
        elif st == "pony":
            pts = [(0.25, cy - 0.45), (0.55 + sway, cy - 0.5), (0.72 + sway, cy - 0.1), (0.66 + sway * 2, cy + 0.6),
                   (0.52 + sway * 2, cy + 1.0), (0.48, cy + 0.4), (0.4, cy - 0.15)]
            g.shape(sp(pts), col, LINE)
            g.line(0.5, cy - 0.3, 0.6 + sway * 2, cy + 0.6, color=s["hair_hl"], w=g.lw * 1.1, a=0.6)
        elif st == "bun":
            g.shape(G.circle_p(0.02, cy - 0.55, 0.17), col, LINE)
        elif st == "long_grey":
            pts = [(0, cy - 0.5), (0.4, cy - 0.4), (0.48, cy + 0.1), (0.52, cy + 0.55), (0.42, cy + 0.85),
                   (-0.42, cy + 0.85), (-0.52, cy + 0.55), (-0.48, cy + 0.1), (-0.4, cy - 0.4)]
            g.shape(sp(pts), col, LINE)

    def _hair_front(self, g, t):
        s = self.s; st = s.get("hair_style"); col = s["hair"]; hl = s["hair_hl"]
        cy = self.P["head_c"]
        if st in ("long_wavy", "pony", "bun"):
            q = skia.Path()
            q.moveTo(-0.39, cy + (0.35 if st == "long_wavy" else -0.02))
            q.cubicTo(-0.46, cy - 0.45, -0.25, cy - 0.6, 0.02, cy - 0.58)
            q.cubicTo(0.3, cy - 0.6, 0.47, cy - 0.42, 0.39, cy + (0.35 if st == "long_wavy" else -0.02))
            if st == "long_wavy":
                q.cubicTo(0.36, cy + 0.0, 0.33, cy - 0.2, 0.28, cy - 0.3)
            else:
                q.cubicTo(0.37, cy - 0.15, 0.34, cy - 0.25, 0.3, cy - 0.3)
            q.cubicTo(0.2, cy - 0.36, 0.08, cy - 0.38, -0.03, cy - 0.44)     # side part
            q.cubicTo(-0.12, cy - 0.33, -0.25, cy - 0.3, -0.31, cy - 0.22)
            q.cubicTo(-0.36, cy - 0.1, -0.37, cy + 0.1, -0.39, cy + (0.35 if st == "long_wavy" else -0.02))
            q.close()
            g.shape(q, col, LINE)
            for k, (a, b) in enumerate(((-0.25, -0.5), (-0.12, -0.53), (0.12, -0.53), (0.25, -0.48))):
                hq = skia.Path(); hq.moveTo(a, cy + b + 0.02); hq.quadTo(a * 1.15, cy + b + 0.06, a * 1.25, cy + b + 0.11)
                g.strokep(hq, hl, w=g.lw * 1.3, a=0.75)
        elif st == "short_messy":
            q = skia.Path()
            q.moveTo(-0.37, cy - 0.12)
            q.cubicTo(-0.44, cy - 0.5, -0.28, cy - 0.66, 0.0, cy - 0.64)
            q.cubicTo(0.3, cy - 0.66, 0.45, cy - 0.5, 0.37, cy - 0.12)
            q.lineTo(0.33, cy - 0.28); q.lineTo(0.27, cy - 0.33); q.lineTo(0.2, cy - 0.31); q.lineTo(0.14, cy - 0.38)
            q.lineTo(0.06, cy - 0.33); q.lineTo(-0.02, cy - 0.4); q.lineTo(-0.1, cy - 0.34); q.lineTo(-0.18, cy - 0.38)
            q.lineTo(-0.25, cy - 0.31); q.lineTo(-0.32, cy - 0.3); q.close()
            g.shape(q, col, LINE)
            for k in range(6):
                xx = -0.25 + k * 0.1
                g.line(xx, cy - 0.58, xx + 0.04, cy - 0.45, color=hl, w=g.lw * 1.1, a=0.7)
        elif st == "buzz":
            q = skia.Path(); q.moveTo(-0.37, cy - 0.12); q.cubicTo(-0.42, cy - 0.62, 0.42, cy - 0.62, 0.37, cy - 0.12)
            q.cubicTo(0.3, cy - 0.3, -0.3, cy - 0.3, -0.37, cy - 0.12); q.close()
            g.fillp(q, col, 0.85)
            g.strokep(q, LINE, w=g.lw * 0.7)
        elif st == "slick":
            q = skia.Path(); q.moveTo(-0.37, cy - 0.1); q.cubicTo(-0.44, cy - 0.62, 0.44, cy - 0.62, 0.37, cy - 0.1)
            q.cubicTo(0.3, cy - 0.38, -0.1, cy - 0.42, -0.37, cy - 0.1); q.close()
            g.shape(q, col, LINE)
            for k in range(4):
                g.line(-0.2 + k * 0.12, cy - 0.5, 0.0 + k * 0.12, cy - 0.38, color=hl, w=g.lw, a=0.7)
        elif st == "long_grey":
            q = skia.Path(); q.moveTo(-0.38, cy - 0.05); q.cubicTo(-0.44, cy - 0.6, 0.44, cy - 0.6, 0.38, cy - 0.05)
            q.cubicTo(0.33, cy - 0.3, 0.2, cy - 0.38, 0.0, cy - 0.4); q.cubicTo(-0.2, cy - 0.38, -0.33, cy - 0.3, -0.38, cy - 0.05); q.close()
            g.shape(q, col, LINE)
            for k in range(5):
                g.line(-0.3 + k * 0.15, cy - 0.5, -0.32 + k * 0.16, cy - 0.3, color=hl, w=g.lw, a=0.8)

    # body --------------------------------------------------------------
    def _torso(self, g, t):
        s = self.s; P = self.P; sk, sh, dk = self._skin()
        fem = s["sex"] == "f"
        o = s["outfit"]
        sx, sy = P["sh_x"], P["sh_y"]
        wx, wy = P["waist_x"], P["waist_y"]
        hx, hy = P["hip_x"], P["hip_y"]
        nw = 0.2 if fem else 0.24
        body = [(-nw, sy - 0.18), (-sx * 0.75, sy - 0.08), (-sx, sy + 0.08), (-sx * 0.98, sy + 0.5),
                (-wx * 1.05, sy + 1.05), (-wx, wy), (-hx, hy + 0.1), (hx, hy + 0.1), (wx, wy), (wx * 1.05, sy + 1.05),
                (sx * 0.98, sy + 0.5), (sx, sy + 0.08), (sx * 0.75, sy - 0.08), (nw, sy - 0.18)]
        bp = sp(body, k=0.55)
        top = s.get("top", "#888888")
        if o in ("tank",):
            g.shape(bp, sk, LINE)
            tq = sp([(-0.32, sy - 0.12), (-0.5, sy + 0.05), (-sx * 0.82, sy + 0.55), (-wx * 1.02, sy + 1.05), (-wx, wy),
                     (-hx, hy + 0.1), (hx, hy + 0.1), (wx, wy), (wx * 1.02, sy + 1.05), (sx * 0.82, sy + 0.55),
                     (0.5, sy + 0.05), (0.32, sy - 0.12), (0.18, sy + 0.25), (0, sy + 0.32), (-0.18, sy + 0.25)], k=0.3)
            g.shape(tq, top, LINE)
            self._fold_shadow(g, tq, top)
        else:
            col = top if o != "jacket" else s.get("top")
            g.shape(bp, col, LINE)
            self._fold_shadow(g, bp, col)
            if o in ("tee", "army", "uniform", "hawaiian", "jumpsuit"):
                q = skia.Path(); q.moveTo(-nw - 0.02, sy - 0.17); q.quadTo(0, sy + 0.12, nw + 0.02, sy - 0.17)
                q.quadTo(0, sy + 0.02, -nw - 0.02, sy - 0.17); q.close()
                g.shape(q, sk, LINE, w=g.lw * 0.8)
            if o == "jumpsuit":
                g.shape(G.poly_p([(-0.22, sy - 0.15), (0, sy + 0.4), (0.22, sy - 0.15), (0.12, sy - 0.15), (0, sy + 0.18), (-0.12, sy - 0.15)]),
                        shade(top, 0.9), LINE, w=g.lw * 0.8)
                g.line(0, sy + 0.4, 0, hy, color=shade(top, 0.75), w=g.lw * 1.0)
                g.shape(G.rrect_p(0.25, sy + 0.45, 0.32, 0.18, 0.02), "#f2efe8", LINE, w=g.lw * 0.6)
                from gfx import text as _t
                g.save(); g.tr(0.41, sy + 0.58); g.sc(0.0018)
                _t(g, "LP-0419", 0, 0, 56, fill="#2a2a2a", outline=None, shadow=False, name="ui")
                g.restore()
            if o == "uniform":
                g.shape(G.poly_p([(-0.18, sy - 0.15), (0, sy + 0.3), (0.18, sy - 0.15)]), "#e9edf2", LINE, w=g.lw * 0.7)
                g.shape(G.poly_p([(-0.035, sy + 0.0), (0.035, sy + 0.0), (0.045, sy + 0.55), (0, sy + 0.62), (-0.045, sy + 0.55)]),
                        "#22222e", LINE, w=g.lw * 0.6)
                g.shape(sp([(-0.55, sy + 0.35), (-0.42, sy + 0.3), (-0.38, sy + 0.45), (-0.47, sy + 0.55), (-0.56, sy + 0.47)]),
                        "#d8b04a", LINE, w=g.lw * 0.6)
                for sd in (-1, 1):
                    g.shape(G.rrect_p(sd * 0.42 - 0.13, sy + 0.62, 0.26, 0.2, 0.03), shade(top, 0.9), LINE, w=g.lw * 0.6)
            if o == "hawaiian":
                g.c.save(); g.c.clipPath(bp, doAntiAlias=True)
                rnd = random.Random(4)
                for i in range(26):
                    cx_, cy_ = rnd.uniform(-1, 1), rnd.uniform(sy, hy)
                    for k in range(5):
                        a = k * 2 * math.pi / 5
                        g.fillp(G.circle_p(cx_ + 0.05 * math.cos(a), cy_ + 0.05 * math.sin(a), 0.04), "#f4efe6", 0.9)
                    g.fillp(G.circle_p(cx_, cy_, 0.025), "#e9b949")
                g.c.restore()
                g.strokep(bp, LINE)
                g.line(0, sy + 0.1, 0, hy, color=LINE, w=g.lw * 0.8)
            if o == "army":
                g.c.save(); g.c.clipPath(bp, doAntiAlias=True)
                rnd = random.Random(2)
                for i in range(30):
                    g.fillp(G.ellipse_p(rnd.uniform(-1, 1), rnd.uniform(sy, hy), rnd.uniform(0.08, 0.16), rnd.uniform(0.05, 0.1)),
                            rnd.choice(["#4c552b", "#7d8650", "#3e3a24"]), 0.8)
                g.c.restore(); g.strokep(bp, LINE)
            if o == "suit":
                g.shape(G.poly_p([(-0.2, sy - 0.15), (0, sy + 0.75), (0.2, sy - 0.15)]), "#f2efe8", LINE, w=g.lw * 0.7)
                g.shape(G.poly_p([(-0.04, sy - 0.05), (0.04, sy - 0.05), (0.05, sy + 0.6), (0, sy + 0.68), (-0.05, sy + 0.6)]),
                        "#b8302a", LINE, w=g.lw * 0.6)
                for sd in (-1, 1):
                    g.shape(G.poly_p([(sd * 0.2, sy - 0.15), (sd * 0.42, sy + 0.05), (sd * 0.2, sy + 0.45), (sd * 0.02, sy + 0.8)]),
                            shade(top, 0.8), LINE, w=g.lw * 0.7)
        if o in ("jacket", "cardigan"):
            jk = s.get("jacket")
            for sd in (-1, 1):
                q = sp([(sd * nw, sy - 0.2), (sd * sx * 0.78, sy - 0.07), (sd * sx * 1.02, sy + 0.08), (sd * sx * 1.0, sy + 0.55),
                        (sd * wx * 1.1, sy + 1.05), (sd * hx * 1.05, hy + 0.15), (sd * 0.3, hy + 0.15), (sd * 0.24, sy + 0.9),
                        (sd * 0.3, sy + 0.4), (sd * 0.24, sy + 0.05)], k=0.25)
                g.shape(q, jk, LINE)
                self._fold_shadow(g, q, jk, side=sd)
                g.line(sd * 0.3, sy + 0.4, sd * 0.45, sy + 0.15, color=shade(jk, 0.75), w=g.lw)
                if o == "jacket":
                    g.shape(G.rrect_p(sd * 0.55 - 0.12, sy + 0.5, 0.24, 0.16, 0.02), shade(jk, 0.92), LINE, w=g.lw * 0.6)
        if "chain" in s.get("acc", []):
            q = skia.Path(); q.moveTo(-0.2, sy - 0.15); q.quadTo(0, sy + 0.35, 0.2, sy - 0.15)
            g.strokep(q, LINE, w=g.lw * 3.2); g.strokep(q, "#e9b949", w=g.lw * 1.8)
        # belt line
        if o not in ("jumpsuit", "hawaiian"):
            g.line(-hx * 0.98, hy + 0.08, hx * 0.98, hy + 0.08, color=LINE, w=g.lw)

    def _fold_shadow(self, g, path, col, side=1):
        g.c.save(); g.c.clipPath(path, doAntiAlias=True)
        P = self.P
        q = skia.Path()
        q.moveTo(side * 0.35, P["sh_y"] - 0.3); q.cubicTo(side * 0.6, P["sh_y"] + 0.6, side * 0.45, P["waist_y"], side * 0.6, P["hip_y"] + 0.3)
        q.lineTo(side * 1.4, P["hip_y"] + 0.3); q.lineTo(side * 1.4, P["sh_y"] - 0.3); q.close()
        g.fillp(q, shade(col, 0.82), 0.85)
        g.c.restore()

    def _arms(self, g, hands, held, t):
        s = self.s; P = self.P; sk, sh, dk = self._skin()
        o = s["outfit"]
        long_sleeve = o in ("jacket", "cardigan", "uniform", "suit", "army", "jumpsuit")
        sleeve_col = {"jacket": s.get("jacket"), "cardigan": s.get("jacket")}.get(o, s.get("top"))
        fem = s["sex"] == "f"
        w0, w1, w2 = (0.36, 0.3, 0.22) if fem else (0.43, 0.35, 0.26)
        if o in ("jacket", "army", "uniform", "suit"): w0, w1, w2 = w0 * 1.12, w1 * 1.15, w2 * 1.2
        for i, sd in enumerate((-1, 1)):
            shx, shy = sd * (P["sh_x"] - 0.16), P["sh_y"] + 0.2
            tx, ty = hands[i]
            f_ = self.fs[i]
            el, hd = ik(shx, shy, shx + tx, shy + ty, P["l1"] * f_, P["l2"] * f_, sd, down=self.elbow_down)
            if self.pose_now == "guard" or (self.pose_now == "punch_r" and i == 0):
                el = (shx + sd * 0.1, shy + 0.85)            # elbows tucked down
                hd = (sd * 0.3, P["head_c"] + 0.42)          # fists at the cheeks
            def capsule(a, b, wa, wb):
                q = G.poly_p(taper(a, b, wa, wb))
                q = skia.Op(q, G.circle_p(a[0], a[1], wa / 2), skia.PathOp.kUnion_PathOp)
                return skia.Op(q, G.circle_p(b[0], b[1], wb / 2), skia.PathOp.kUnion_PathOp)
            up = capsule((shx, shy), el, w0, w1)
            lo = capsule(el, hd, w1, w2)
            whole = skia.Op(up, lo, skia.PathOp.kUnion_PathOp)
            if long_sleeve:
                g.fillp(whole, sleeve_col)
                # sleeve shading on the outer side
                g.c.save(); g.c.clipPath(whole, doAntiAlias=True)
                g.c.drawPath(G.poly_p(taper((shx + sd * w0 * 0.3, shy), (el[0] + sd * w1 * 0.3, el[1]), w0 * 0.5, w1 * 0.5)),
                             P_fill(shade(sleeve_col, 0.82)))
                g.c.restore()
                cuff = G.poly_p(taper((lerp(el[0], hd[0], 0.86), lerp(el[1], hd[1], 0.86)), hd, w2 * 1.08, w2 * 1.08))
                g.strokep(whole, LINE)
                g.line(lerp(el[0], hd[0], 0.86) - (hd[1] - el[1]) * 0.0, lerp(el[1], hd[1], 0.86), lerp(el[0], hd[0], 0.86), lerp(el[1], hd[1], 0.86), color=LINE, w=g.lw)
            else:
                g.fillp(whole, sk)
                g.c.save(); g.c.clipPath(whole, doAntiAlias=True)
                g.c.drawPath(G.poly_p(taper((shx + sd * w0 * 0.32, shy), (el[0] + sd * w1 * 0.32, el[1]), w0 * 0.45, w1 * 0.45)),
                             P_fill(sh))
                g.c.drawPath(G.poly_p(taper((el[0] + sd * w1 * 0.32, el[1]), (hd[0] + sd * w2 * 0.3, hd[1]), w1 * 0.4, w2 * 0.4)),
                             P_fill(sh))
                if "tattoos" in s.get("acc", []):
                    for k in range(4):
                        px = lerp(el[0], hd[0], 0.15 + k * 0.2); py = lerp(el[1], hd[1], 0.15 + k * 0.2)
                        g.fillp(G.ellipse_p(px, py, 0.07, 0.05), "#2f3a5a", 0.45)
                    g.fillp(G.ellipse_p(lerp(shx, el[0], 0.5), lerp(shy, el[1], 0.5), 0.09, 0.07), "#2f3a5a", 0.4)
                g.c.restore()
                g.strokep(whole, LINE)
                if o in ("tee", "hawaiian"):
                    mid = (lerp(shx, el[0], 0.5), lerp(shy, el[1], 0.5))
                    sl = capsule((shx, shy), mid, w0 * 1.06, w0 * 0.98)
                    g.shape(sl, sleeve_col, LINE)
            # hand: mitten aligned with the forearm
            ang = math.degrees(math.atan2(hd[1] - el[1], hd[0] - el[0])) - 90
            g.save(); g.tr(hd[0], hd[1]); g.rot(ang)
            hw = 0.115 if fem else 0.135
            hq = sp([(-hw, 0.0), (hw, 0.0), (hw * 1.05, 0.12), (hw * 0.7, 0.24), (0, 0.27), (-hw * 0.7, 0.24), (-hw * 1.05, 0.12)], k=0.4)
            g.shape(hq, sk, LINE)
            th = sp([(-hw * 0.9, 0.02), (-hw * 1.5, 0.1), (-hw * 1.35, 0.17), (-hw * 0.8, 0.12)], k=0.4)
            g.shape(th, sk, LINE, w=g.lw * 0.8)
            for k in (-0.35, 0.05, 0.42):
                g.line(hw * k, 0.16, hw * k, 0.24, color=sh, w=g.lw * 0.8)
            g.restore()
            if held and sd == 1:
                self._prop(g, held, hd[0], hd[1] + 0.12)

    def _prop(self, g, kind, x, y):
        if kind == "glass":
            q = G.poly_p([(x - 0.1, y - 0.32), (x + 0.1, y - 0.32), (x + 0.08, y + 0.05), (x - 0.08, y + 0.05)])
            g.shape(q, "#dff3ff", LINE, w=g.lw * 0.8, a=0.85)
            g.fillp(G.poly_p([(x - 0.09, y - 0.18), (x + 0.09, y - 0.18), (x + 0.08, y + 0.04), (x - 0.08, y + 0.04)]), "#e9b949", 0.85)
        elif kind == "phone":
            g.shape(G.rrect_p(x - 0.07, y - 0.28, 0.14, 0.3, 0.03), "#1c1a22", LINE)
            g.fillp(G.rrect_p(x - 0.055, y - 0.26, 0.11, 0.25, 0.02), "#7fc8f0")
        elif kind == "photo":
            g.save(); g.tr(x, y - 0.2); g.rot(-8)
            g.shape(G.rrect_p(-0.2, -0.25, 0.4, 0.42, 0.02), "#f4efe6", LINE)
            g.fillp(G.rrect_p(-0.16, -0.21, 0.32, 0.28, 0.01), "#f2c27a")
            g.shape(G.circle_p(0, -0.1, 0.07), "#b5744d", LINE, w=g.lw * 0.5)
            g.restore()
        elif kind == "beer":
            g.shape(G.rrect_p(x - 0.07, y - 0.25, 0.14, 0.3, 0.03), "#7a4a1e", LINE)
            g.fillp(G.rrect_p(x - 0.07, y - 0.15, 0.14, 0.09, 0.0), "#efe2c0")
        elif kind == "hammer":
            g.save(); g.tr(x, y); g.rot(-30)
            g.shape(G.rrect_p(-0.03, -0.45, 0.06, 0.55, 0.02), "#a8743e", LINE)
            g.shape(G.rrect_p(-0.13, -0.53, 0.26, 0.1, 0.02), "#6f7b8c", LINE)
            g.restore()
        elif kind == "bag":
            q = skia.Path(); q.moveTo(x - 0.2, y + 0.05); q.cubicTo(x - 0.3, y + 0.55, x + 0.3, y + 0.55, x + 0.2, y + 0.05)
            q.lineTo(x + 0.07, y - 0.02); q.lineTo(x - 0.07, y - 0.02); q.close()
            g.shape(q, "#8a7a52", LINE)
            from gfx import text as _t
            g.save(); g.tr(x, y + 0.36); g.sc(0.004)
            _t(g, "$", 0, 0, 60, fill="#e9b949", outline="#231a22", ow=8, shadow=False)
            g.restore()
        elif kind == "cards":
            for k in range(3):
                g.save(); g.tr(x, y - 0.05); g.rot(-20 + k * 18)
                g.shape(G.rrect_p(-0.07, -0.22, 0.14, 0.2, 0.02), "#f4efe6", LINE, w=g.lw * 0.7)
                g.fillp(G.circle_p(0, -0.12, 0.025), "#c8302a")
                g.restore()

    def _sit_legs(self, g, pc, shoes):
        P = self.P; hy = P["hip_y"]
        for sd in (-1, 1):
            knee = (sd * 0.42, hy + 0.55); ankle = (sd * 0.4, hy + 2.2)
            lo = G.poly_p(taper(knee, ankle, 0.36, 0.27))
            g.shape(lo, shade(pc, 0.85), LINE)
            ax, ay = ankle
            q = sp([(ax - 0.15, ay - 0.05), (ax + 0.15, ay - 0.05), (ax + sd * 0.1 + 0.12, ay + 0.17), (ax - 0.15, ay + 0.17)], k=0.3)
            g.shape(q, shoes, LINE)
        # lap: thighs coming towards the viewer
        for sd in (-1, 1):
            lap = sp([(sd * 0.05, hy - 0.05), (sd * 0.72, hy - 0.08), (sd * 0.68, hy + 0.55), (sd * 0.42, hy + 0.78),
                      (sd * 0.14, hy + 0.6)], k=0.45)
            g.shape(lap, pc, LINE)
            g.fillp(G.ellipse_p(sd * 0.42, hy + 0.5, 0.2, 0.14), tint(pc, 0.12), 0.8)

    def _legs(self, g, t, sit, walk):
        s = self.s; P = self.P
        pc = s.get("pants", "#333"); shoes = s.get("shoes", "#222")
        fem = s["sex"] == "f"
        if sit:
            self._sit_legs(g, pc, shoes)
            return
        for sd in (-1, 1):
            hip = (sd * 0.38, P["hip_y"] + 0.05)
            if sit:
                knee = (sd * 0.48, P["hip_y"] + 0.45); ankle = (sd * 0.44, P["hip_y"] + 2.15)
            else:
                sw = math.sin(t * math.pi * 2 * 1.5 + (0 if sd < 0 else math.pi)) * 0.25 * walk
                knee = (sd * 0.36 + sw * 0.5, -1.9); ankle = (sd * 0.33 + sw, -0.18)
            up = G.poly_p(taper(hip, knee, 0.5 if fem else 0.48, 0.34))
            lo = G.poly_p(taper(knee, ankle, 0.34, 0.26))
            g.shape(up, pc, LINE); g.shape(lo, pc, LINE)
            g.fillp(G.circle_p(knee[0], knee[1], 0.165), pc)
            g.line(knee[0] + sd * 0.06, knee[1] - 0.6, knee[0] + sd * 0.05, knee[1] + 0.4, color=shade(pc, 0.75), w=g.lw * 0.9)
            ax, ay = ankle
            q = sp([(ax - 0.15, ay - 0.05), (ax + 0.15, ay - 0.05), (ax + sd * 0.3 + 0.03, ay + 0.1), (ax + sd * 0.28, ay + 0.19),
                    (ax - 0.17, ay + 0.19)], k=0.3)
            g.shape(q, shoes, LINE)
