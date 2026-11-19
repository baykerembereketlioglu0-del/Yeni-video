# -*- coding: utf-8 -*-
"""Frame renderer: scenes + overlay UI (life badge, chapter banner) + crossfades.

usage:
  python3 render.py preview  [shot_id ...]   -> contact sheet PNGs in build/preview
  python3 render.py video                    -> build/video_noaudio.mp4 (parallel chunks)
"""
import os, sys, math, subprocess, time
import numpy as np
import skia
sys.path.insert(0, os.path.dirname(__file__))
from gfx import G, W, H, FPS, PAL, OUTLINE, C, text, text_w, clamp, ease_out, ease_back, ease_io, lerp, new_surface
from timeline import build, Ctx, ROOT
from script_data import CHAPTERS
import scenes

XF = 0.2   # crossfade seconds between shots
SHOTS, TOTAL = build()

def shot_at(T):
    for sh in SHOTS:
        if T < sh.start + sh.D:
            return sh
    return SHOTS[-1]

def draw_shot(g, sh, t):
    g.save()
    scenes.SCENES[sh.s["scene"]](g, Ctx(sh, t))
    g.restore()

def last_badge_before(idx):
    for j in range(idx, -1, -1):
        b = SHOTS[j].s.get("badge")
        if "badge" in SHOTS[j].s:
            return b, j
    return None, 0

def draw_badge(g, sh, t):
    b = sh.s.get("badge")
    if not b:
        return
    prev = SHOTS[sh.i - 1].s.get("badge") if sh.i > 0 else None
    k = ease_back(clamp(t / 0.45), 2.0) if prev != b else 1.0
    size = 58
    w = text_w(b, size) + 64
    g.save(); g.tr(70 + w / 2, 78); g.sc(k)
    g.rrect(-w / 2 + 5, -42 + 7, w, 84, 42, "#1a1020", outline=None, a=0.3)
    g.rrect(-w / 2, -42, w, 84, 42, "#2b2233", outline="#fbf7f0", w=5)
    text(g, b, 0, 21, size, fill="#ffd166" if b.startswith("AGE") else "#fbf7f0", outline=None, shadow=False)
    g.restore()

def draw_banner(g, sh, t):
    ch = sh.s.get("chapter")
    if ch is None:
        return
    t0 = 0.25 if ch > 0 else 0.15
    hold = 2.8
    if t < t0 or t > t0 + hold + 0.5:
        return
    kin = ease_out((t - t0) / 0.45)
    kout = ease_io((t - t0 - hold) / 0.45)
    title = CHAPTERS[ch]
    parts = title.split(" · ")
    num, name = (parts[0], parts[1]) if len(parts) == 2 else ("", title)
    size = 74
    w = max(text_w(name, size), text_w(num, 44)) + 140
    x = lerp(-w, 0, kin) - kout * (w + 60)
    y = 840
    g.save(); g.tr(x, y)
    g.poly([(0, -70), (w + 40, -70), (w, 70), (0, 70)], "#2b2233", outline=None)
    g.poly([(0, -58), (w + 18, -58), (w - 10, 58), (0, 58)], PAL["red"], outline="#fbf7f0", w=5)
    text(g, num, 60, -16, 40, fill="#ffd166", outline=None, align="left", shadow=False)
    text(g, name, 60, 44, size, fill="#fbf7f0", outline="#2b2233", ow=10, align="left", shadow=False)
    g.restore()

def render_frame(surface, T, tmp_surface=None):
    g = G(surface.getCanvas())
    g.c.clear(C("#000000"))
    sh = shot_at(T)
    t = T - sh.start
    draw_shot(g, sh, t)
    if sh.i > 0 and t < XF and tmp_surface is not None:
        prev = SHOTS[sh.i - 1]
        g2 = G(tmp_surface.getCanvas()); g2.c.clear(C("#000000"))
        draw_shot(g2, prev, prev.D + t)
        img = tmp_surface.makeImageSnapshot()
        p = skia.Paint(); p.setAlphaf(1 - ease_io(t / XF))
        g.c.drawImage(img, 0, 0, skia.SamplingOptions(), p)
    draw_badge(g, sh, t)
    draw_banner(g, sh, t)
    # fade from / to black at the very start and end
    if T < 0.25:
        g.rect_fill(0, 0, W, H, "#000000", 1 - T / 0.25)
    if T > TOTAL - 0.6:
        g.rect_fill(0, 0, W, H, "#000000", clamp((T - (TOTAL - 0.6)) / 0.6))

def render_chunk(f0, f1, out):
    s1 = new_surface(); s2 = new_surface()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-pix_fmt", "yuv420p", "-tune", "animation", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        render_frame(s1, f / FPS, s2)
        arr = s1.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
        p.stdin.write(arr.tobytes())
        if (f - f0) % 300 == 0:
            print(f"[{out[-12:]}] {f - f0}/{f1 - f0}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()

def preview(ids=None, cols=4, per_shot=4):
    outdir = os.path.join(ROOT, "build", "preview"); os.makedirs(outdir, exist_ok=True)
    s1 = new_surface(); s2 = new_surface()
    sel = [sh for sh in SHOTS if not ids or sh.id in ids]
    from PIL import Image
    for sh in sel:
        tiles = []
        for k in range(per_shot):
            t = sh.D * (k + 0.5) / per_shot
            render_frame(s1, sh.start + t, s2)
            arr = s1.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
            tiles.append(Image.fromarray(arr[:, :, :3]).resize((960, 540)))
        sheet = Image.new("RGB", (960 * 2, 540 * ((per_shot + 1) // 2)))
        for k, im in enumerate(tiles):
            sheet.paste(im, ((k % 2) * 960, (k // 2) * 540))
        sheet.save(os.path.join(outdir, f"{sh.i:02d}_{sh.id}.jpg"), quality=82)
        print("preview", sh.id, flush=True)

def video(nproc=4):
    from multiprocessing import Process
    N = int(math.ceil(TOTAL * FPS))
    os.makedirs(os.path.join(ROOT, "build", "chunks"), exist_ok=True)
    bounds = [int(N * k / nproc) for k in range(nproc + 1)]
    procs, outs = [], []
    for k in range(nproc):
        out = os.path.join(ROOT, "build", "chunks", f"c{k}.mp4"); outs.append(out)
        pr = Process(target=render_chunk, args=(bounds[k], bounds[k + 1], out)); pr.start(); procs.append(pr)
    for pr in procs: pr.join()
    lst = os.path.join(ROOT, "build", "chunks", "list.txt")
    open(lst, "w").write("".join(f"file '{o}'\n" for o in outs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(ROOT, "build", "video_noaudio.mp4")], check=True)
    print("VIDEO DONE", N, "frames", round(TOTAL, 2), "s")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        preview(sys.argv[2:] or None)
    elif mode == "video":
        video(int(os.environ.get("NPROC", "4")))
