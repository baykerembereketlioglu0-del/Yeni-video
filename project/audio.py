# -*- coding: utf-8 -*-
"""Procedural soundtrack (synthwave), SFX, narration placement, ducking, SRT export."""
import os, sys, re, json, math, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from timeline import build, LEAD, ROOT, AUD, TTS_REPLACE
from script_data import SHOTS as RAW

SR = 44100
OUT = os.path.join(ROOT, "build")

# ============================================================ helpers
def decode(path, tempo=1.0):
    af = []
    t = tempo
    while t > 2.0: af.append("atempo=2.0"); t /= 2.0
    if abs(t - 1.0) > 1e-3: af.append(f"atempo={t:.4f}")
    cmd = ["ffmpeg", "-loglevel", "error", "-i", path]
    if af: cmd += ["-af", ",".join(af)]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()

def lp(x, fc):
    """fast low-pass: FFT brick-ish with soft roll-off"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X * H, n).astype(np.float32)

def hp(x, fc):
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1 - 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X * H, n).astype(np.float32)

def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    t = np.arange(n) / SR
    dur = n / SR
    e = np.where(t < a, t / max(a, 1e-6), np.where(t < a + d, 1 - (1 - s) * (t - a) / d, s))
    rel = np.clip((dur - t) / max(r, 1e-6), 0, 1)
    return (e * rel).astype(np.float32)

def saw(f, n, ph=0.0):
    t = np.arange(n) / SR
    return (2 * ((t * f + ph) % 1.0) - 1).astype(np.float32)

def sq(f, n, duty=0.5):
    t = np.arange(n) / SR
    return np.where((t * f) % 1.0 < duty, 1.0, -1.0).astype(np.float32)

def sine(f, n, ph=0.0):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t + ph).astype(np.float32)

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ============================================================ music
BPM = 92
BEAT = 60 / BPM
BAR = 4 * BEAT
# A minor: Am - F - C - G   (root midi notes, chord tones as semitone offsets)
PROG = [(57, (0, 3, 7)), (53, (0, 4, 7)), (60, (0, 4, 7)), (55, (0, 4, 7))]
# moods per chapter: gains for (pad, bass, arp, kick, snare, hats), filter cutoff
MOODS = {
    "tense":  (0.9, 0.9, 0.25, 0.8, 0.0, 0.25, 900),
    "soft":   (0.8, 0.45, 0.6, 0.0, 0.0, 0.0, 1500),
    "groove": (0.75, 0.9, 0.55, 0.85, 0.6, 0.45, 2200),
    "dark":   (0.9, 0.6, 0.15, 0.35, 0.0, 0.0, 700),
    "hope":   (0.85, 0.7, 0.7, 0.4, 0.0, 0.3, 2600),
    "hype":   (0.7, 1.0, 0.7, 1.0, 0.8, 0.7, 3000),
    "warm":   (0.9, 0.7, 0.6, 0.5, 0.35, 0.35, 2000),
}
SHOT_MOOD = {"h1": "tense", "h2": "tense", "h3": "hype", "b1": "soft", "c1a": "groove", "c2a": "tense",
             "c3a": "dark", "c4a": "hope", "cta": "groove", "c5a": "groove", "c6a": "warm", "c7a": "hype",
             "c8a": "warm", "c8c": "hope", "end": "groove"}

def mood_curve(shots, total):
    """per-bar mood gains."""
    nb = int(math.ceil(total / BAR)) + 1
    cur = "tense"; marks = []
    for sh in shots:
        if sh.id in SHOT_MOOD:
            cur = SHOT_MOOD[sh.id]
        marks.append((sh.start, cur))
    out = []
    for b in range(nb):
        t = b * BAR
        m = marks[0][1]
        for (st, mm) in marks:
            if st <= t + BAR * 0.5: m = mm
        out.append(np.array(MOODS[m], dtype=np.float32))
    return out

def make_music(shots, total):
    n = int((total + 2) * SR)
    pad = np.zeros(n, np.float32); bass = np.zeros(n, np.float32); arp = np.zeros(n, np.float32)
    kick = np.zeros(n, np.float32); snare = np.zeros(n, np.float32); hats = np.zeros(n, np.float32)
    rng = np.random.default_rng(3)
    moods = mood_curve(shots, total)
    nb = len(moods)
    gains = np.zeros((6, n), np.float32)
    cut = np.zeros(n, np.float32)
    for b in range(nb):
        s0 = int(b * BAR * SR); s1 = min(n, int((b + 1) * BAR * SR))
        if s0 >= n: break
        root, tones = PROG[b % 4]
        L = s1 - s0
        # pad: 3 detuned saws per chord tone + octave
        chord = np.zeros(L, np.float32)
        for tt in tones:
            for det in (-0.12, 0.0, 0.11):
                chord += saw(midi(root + tt) * (1 + det / 100), L, ph=rng.random()) * 0.11
        chord += saw(midi(root + 12), L, ph=rng.random()) * 0.06
        chord *= env_adsr(L, a=0.35, d=0.4, s=0.85, r=0.25)
        pad[s0:s1] += chord
        # bass: 8th notes
        for k in range(8):
            a = s0 + int(k * BEAT / 2 * SR); e = min(s1, a + int(BEAT / 2 * SR * 0.9))
            if a >= n: break
            m = midi(root - 12)
            seg = (sine(m, e - a) * 0.7 + saw(m, e - a) * 0.25) * env_adsr(e - a, 0.004, 0.12, 0.5, 0.05)
            bass[a:e] += seg
        # arp: 16ths through chord tones
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for k in range(16):
            a = s0 + int(k * BEAT / 4 * SR); e = min(n, a + int(BEAT / 4 * SR))
            if a >= n: break
            m = midi(root + 12 + tones[pat[k % 8] % 3])
            seg = sq(m, e - a, 0.3) * env_adsr(e - a, 0.002, 0.08, 0.15, 0.03) * 0.22
            arp[a:e] += seg
        # drums
        for k in range(4):
            a = s0 + int(k * BEAT * SR)
            if a >= n: break
            if k in (0, 2):
                ln = int(0.32 * SR); ln = min(ln, n - a)
                t = np.arange(ln) / SR
                f = 50 + 90 * np.exp(-t * 30)
                kick[a:a + ln] += (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)
            if k in (1, 3):
                ln = min(int(0.22 * SR), n - a)
                t = np.arange(ln) / SR
                snare[a:a + ln] += ((rng.standard_normal(ln) * 0.6 + np.sin(2 * np.pi * 190 * t) * 0.5) * np.exp(-t * 18)).astype(np.float32)
        for k in range(8):
            a = s0 + int(k * BEAT / 2 * SR)
            ln = min(int(0.05 * SR), n - a)
            if ln <= 0: break
            t = np.arange(ln) / SR
            hats[a:a + ln] += (rng.standard_normal(ln) * np.exp(-t * 90) * (0.5 if k % 2 else 0.8)).astype(np.float32)
        g = moods[b]
        prev = moods[b - 1] if b > 0 else g
        ramp = np.linspace(0, 1, L, dtype=np.float32) ** 0.5
        for i in range(6):
            gains[i, s0:s1] = prev[i] + (g[i] - prev[i]) * ramp
        cut[s0:s1] = prev[6] + (g[6] - prev[6]) * ramp
    # filter pad by mood: blend between dark & bright versions
    pad_dark = lp(pad, 700); pad_bright = lp(pad, 3000)
    k = np.clip((cut - 700) / 2300, 0, 1)
    pad_f = pad_dark * (1 - k) + pad_bright * k
    arp_f = lp(arp, 2500)
    hats_f = hp(hats, 7000)
    mix = (pad_f * gains[0] * 0.55 + lp(bass, 600) * gains[1] * 0.55 + arp_f * gains[2] * 0.35 +
           kick * gains[3] * 0.6 + lp(snare, 5000) * gains[4] * 0.22 + hats_f * gains[5] * 0.12)
    # simple stereo widening via short delay
    left = mix
    right = np.concatenate([np.zeros(int(0.012 * SR), np.float32), mix[:-int(0.012 * SR)]])
    st = np.stack([left, right], 1)
    st /= (np.abs(st).max() + 1e-6)
    # fade in / out
    fi = int(1.0 * SR); fo = int(2.5 * SR)
    st[:fi] *= np.linspace(0, 1, fi)[:, None]
    end = int(total * SR)
    st[end - fo:end] *= np.linspace(1, 0, fo)[:, None]
    st[end:] = 0
    return st[:n]

# ============================================================ sfx
def sfx_pop():
    ln = int(0.09 * SR); t = np.arange(ln) / SR
    f = 950 - 450 * (t / t[-1])
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.6).astype(np.float32)

def sfx_whoosh():
    ln = int(0.55 * SR); rng = np.random.default_rng(5)
    noise = rng.standard_normal(ln).astype(np.float32)
    t = np.arange(ln) / ln
    out = np.zeros(ln, np.float32)
    for k, fc in enumerate((600, 1200, 2400, 4000)):
        seg = lp(noise, fc) * np.exp(-((t - (0.25 + k * 0.12)) ** 2) / 0.02)
        out += seg.astype(np.float32)
    return (out / (np.abs(out).max() + 1e-6) * 0.5).astype(np.float32)

def sfx_impact():
    ln = int(0.45 * SR); t = np.arange(ln) / SR
    f = 45 + 120 * np.exp(-t * 25)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    rng = np.random.default_rng(9)
    crack = lp(rng.standard_normal(ln).astype(np.float32), 3500) * np.exp(-t * 30) * 0.7
    out = thump + crack
    return (out / np.abs(out).max() * 0.9).astype(np.float32)

def sfx_ding():
    ln = int(0.9 * SR); t = np.arange(ln) / SR
    out = (np.sin(2 * np.pi * 1318.5 * t) + 0.5 * np.sin(2 * np.pi * 1975.5 * t) + 0.25 * np.sin(2 * np.pi * 2637 * t))
    return (out * np.exp(-t * 5) * 0.35).astype(np.float32)

IMPACT = {("guard", "w3"), ("fight_night", "w3"), ("school", "once"), ("gym", "back"), ("store_masks", "loud"),
          ("arrest", "sign"), ("cell", "number")}

def sfx_track(shots, total):
    n = int((total + 2) * SR)
    tr = np.zeros(n, np.float32)
    P, Wh, I, D = sfx_pop(), sfx_whoosh(), sfx_impact(), sfx_ding()
    def put(sig, t, g=1.0):
        a = int(t * SR); b = min(n, a + len(sig))
        if 0 <= a < n: tr[a:b] += sig[:b - a] * g
    prev_badge = None
    for sh in shots:
        s = sh.s
        if s.get("chapter") is not None:
            put(Wh, sh.start + (0.25 if s["chapter"] > 0 else 0.15) - 0.1, 0.8)
        if s.get("badge") and s.get("badge") != prev_badge:
            put(P, sh.start + 0.05, 0.5)
        prev_badge = s.get("badge")
        for name, tt in sh.cues.items():
            if (s["scene"], name) in IMPACT:
                put(I, sh.start + tt, 0.9)
            elif name == "remember":
                put(D, sh.start + tt + 0.05, 0.8)
            else:
                put(P, sh.start + tt, 0.45)
    return tr

# ============================================================ narration + mix
def narration_track(shots, total, lang):
    n = int((total + 2) * SR)
    tr = np.zeros(n, np.float32)
    missing = []
    for sh in shots:
        if lang not in sh.al or sh.al[lang].get("estimated"):
            if RAW[sh.i][lang]:
                missing.append(sh.id)
            continue
        sig = decode(os.path.join(AUD, lang, sh.id + ".mp3"), sh.speed.get(lang, 1.0))
        a = int((sh.start + LEAD) * SR); b = min(n, a + len(sig))
        tr[a:b] += sig[:b - a]
    return tr, missing

def duck_env(voice):
    hop = 441
    frames = len(voice) // hop
    rms = np.sqrt(np.mean(voice[:frames * hop].reshape(frames, hop) ** 2, 1) + 1e-9)
    act = (rms > 0.01).astype(np.float32)
    env = np.zeros_like(act); acc = 0.0
    for i, v in enumerate(act):
        coef = 0.35 if v > acc else 0.04      # fast attack, slow release
        acc += (v - acc) * coef
        env[i] = acc
    env = np.repeat(env, hop)
    return np.pad(env, (0, len(voice) - len(env)), mode="edge")

def mix_lang(shots, total, lang, music, sfx):
    voice, missing = narration_track(shots, total, lang)
    env = duck_env(voice)
    mg = (0.32 * (1 - 0.62 * env))[:, None]
    out = music * mg + (voice * 1.0)[:, None] + (sfx * 0.55)[:, None]
    out = out[: int(total * SR)]
    peak = np.abs(out).max()
    if peak > 0.98: out *= 0.98 / peak
    path = os.path.join(OUT, f"mix_{lang}.wav")
    write_wav(path, out)
    return path, missing

def write_wav(path, st):
    data = (np.clip(st, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())

# ============================================================ subtitles
def undo_tts(text, lang):
    for a, b in TTS_REPLACE[lang]:
        text = text.replace(b, a)
    return text

def srt_time(t):
    ms = int(round(t * 1000)); h = ms // 3600000; m = ms // 60000 % 60; s = ms // 1000 % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms % 1000:03d}"

def wrap(s, width=42):
    words = s.split(); lines = [""]
    for w in words:
        if len(lines[-1]) + len(w) + 1 > width and lines[-1]:
            lines.append(w)
        else:
            lines[-1] = (lines[-1] + " " + w).strip()
    return lines

def make_srt(shots, lang):
    items = []
    for sh in shots:
        if lang not in sh.al or sh.al[lang].get("estimated"):
            continue
        al = sh.al[lang]; txt = al["text"]; sp = sh.speed.get(lang, 1.0)
        # split into sentences (keep quotes together reasonably)
        for m in re.finditer(r"[^.!?…]+[.!?…]+[\"”“„]?|[^.!?…]+$", txt):
            a, b = m.start(), m.end() - 1
            while a < b and txt[a] == " ": a += 1
            seg = txt[a:b + 1].strip()
            if not seg: continue
            t0 = sh.start + LEAD + al["start"][a] / sp
            t1 = sh.start + LEAD + al["end"][b] / sp
            items.append([t0, t1, undo_tts(seg, lang)])
    # long sentences -> balanced blocks of max 2 lines x 42 chars
    out = []
    for t0, t1, s_ in items:
        words = s_.split()
        k = max(1, math.ceil(len(s_) / 92))
        target = len(s_) / k
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) >= target and len(chunks) < k - 1:
                chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        tot = sum(len(" ".join(c)) for c in chunks); tt = t0
        for c in chunks:
            txt_ = " ".join(c)
            d = (t1 - t0) * len(txt_) / tot
            out.append((tt, tt + d, "\n".join(wrap(txt_, max(24, math.ceil(len(txt_) / 2) + 6)))))
            tt += d
    path = os.path.join(OUT, f"subtitles_{lang}.srt")
    with open(path, "w", encoding="utf-8") as f:
        for i, (t0, t1, s) in enumerate(out, 1):
            f.write(f"{i}\n{srt_time(t0)} --> {srt_time(max(t1, t0 + 0.6))}\n{s}\n\n")
    return path

if __name__ == "__main__":
    shots, total = build()
    music = make_music(shots, total)
    sfx = sfx_track(shots, total)
    for lang in (sys.argv[1:] or ["en", "tr", "de"]):
        p, miss = mix_lang(shots, total, lang, music, sfx)
        s = make_srt(shots, lang)
        print(lang, p, "missing narration:", miss if miss else "none")
