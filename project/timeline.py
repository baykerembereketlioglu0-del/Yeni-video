# -*- coding: utf-8 -*-
"""Builds the master timeline shared by every language.

Each shot lasts long enough for the longest language (TR/DE may be sped up a little,
max MAX_SPEED). Visual cues are timed from the English word timestamps."""
import json, os, re
from script_data import SHOTS, CHAPTERS, TTS_REPLACE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUD = os.path.join(ROOT, "build", "audio")
LANGS = ("en", "tr", "de")
LEAD = 0.18          # silence before narration inside a shot
TAIL = 0.42          # breathing room after narration
MAX_SPEED = 1.12     # max tempo-up for TR/DE to stay in sync
EST_CPS = {"en": 14.5, "tr": 14.0, "de": 15.0}

def tts_text(text, lang):
    for a, b in TTS_REPLACE[lang]:
        text = text.replace(a, b)
    return text

def load_align(lang, sid):
    p = os.path.join(AUD, lang, sid + ".json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding="utf-8"))
    al = d["alignment"]
    return {"text": "".join(al["characters"]), "start": al["character_start_times_seconds"],
            "end": al["character_end_times_seconds"]}

def est_align(text, lang):
    n = len(text); dur = n / EST_CPS[lang]
    return {"text": text, "start": [i / n * dur for i in range(n)], "end": [(i + 1) / n * dur for i in range(n)],
            "estimated": True}

class Shot:
    pass

def build():
    shots = []
    t = 0.0
    until = os.environ.get("UNTIL")       # pilot renders: stop after this shot id
    for i, s in enumerate(SHOTS):
        if until and shots and shots[-1].id == until:
            break
        sh = Shot(); sh.i = i; sh.s = s; sh.id = s["id"]
        sh.al = {}; sh.dur = {}
        for lang in LANGS:
            if not s[lang]:
                continue
            al = load_align(lang, s["id"]) or est_align(tts_text(s[lang], lang), lang)
            sh.al[lang] = al
            sh.dur[lang] = al["end"][-1]
        if s.get("silent"):
            D = s["silent"]
        else:
            D = sh.dur["en"] + LEAD + TAIL
            for lang in ("tr", "de"):
                if lang in sh.dur and not sh.al[lang].get("estimated"):
                    D = max(D, sh.dur[lang] / MAX_SPEED + LEAD + 0.25)
        sh.start = t; sh.D = D
        sh.speed = {}
        for lang, dd in sh.dur.items():
            room = D - LEAD - 0.2
            sh.speed[lang] = max(1.0, dd / room) if lang != "en" else 1.0
        sh.cues = {}
        sh.spans = []
        if "en" in sh.al:
            al = sh.al["en"]; txt = al["text"]
            for name, word in s.get("cues", {}).items():
                idx = find_word(txt, word)
                sh.cues[name] = (al["start"][idx] + LEAD) if idx is not None else D * 0.5
            q = [m.start() for m in re.finditer('"', txt)]
            speakers = s.get("speakers", [])
            for k in range(0, len(q) - 1, 2):
                who = speakers[k // 2] if k // 2 < len(speakers) else None
                a = al["start"][q[k] + 1] + LEAD
                b = al["end"][q[k + 1] - 1] + LEAD
                sh.spans.append((who, a, b))
        shots.append(sh)
        t += D
    return shots, t

def find_word(txt, word):
    m = re.search(r"(?<![A-Za-z])" + re.escape(word), txt)
    return m.start() if m else None

class Ctx:
    def __init__(self, sh, t):
        self.sh = sh; self.t = t; self.d = sh.D
    def cue(self, name):
        return self.sh.cues.get(name, self.d * 0.5)
    def talking(self, who):
        for w, a, b in self.sh.spans:
            if w == who and a <= self.t <= b:
                return True
        return False
    def _spans(self, who):
        return [(a, b) for w, a, b in self.sh.spans if w == who]
    def span_start(self, who, idx):
        s = self._spans(who)
        return s[idx][0] if idx < len(s) else self.d * 0.5
    def span_end(self, who, idx):
        s = self._spans(who)
        return s[idx][1] if idx < len(s) else self.d * 0.7

def chapter_starts(shots):
    out = []
    for sh in shots:
        ch = sh.s.get("chapter")
        if ch is not None:
            out.append((sh.start if ch > 0 else 0.0, CHAPTERS[ch]))
    return out

if __name__ == "__main__":
    shots, total = build()
    for sh in shots:
        est = any(a.get("estimated") for a in sh.al.values())
        print(f"{sh.id:5s} start {sh.start:7.2f}  D {sh.D:5.2f}  " +
              " ".join(f"{l}:{sh.dur.get(l, 0):5.2f}x{sh.speed.get(l, 1):.2f}" for l in LANGS) + ("  (est)" if est else ""))
    print("TOTAL", round(total, 1), "s =", round(total / 60, 2), "min")
