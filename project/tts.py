# -*- coding: utf-8 -*-
"""Generate narration per shot & language with ElevenLabs (character timestamps)."""
import json, os, sys, base64, time, subprocess, concurrent.futures as cf
import urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from script_data import SHOTS, TTS_REPLACE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "build", "audio")
VOICE = "nPczCjzI2devNBz1zQrb"          # deep, warm storyteller voice (premade)
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}

def tts_text(text, lang):
    for a, b in TTS_REPLACE[lang]:
        text = text.replace(a, b)
    return text

def call(text, lang, prev, nxt, speed):
    body = {"text": text, "model_id": MODEL, "seed": 7,
            "voice_settings": dict(SETTINGS, speed=speed)}
    if prev: body["previous_text"] = prev
    if nxt: body["next_text"] = nxt
    if lang != "en": body["language_code"] = lang
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": "proxy-injected", "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except Exception as e:
            msg = getattr(e, "read", lambda: b"")()[:300]
            print("retry", lang, text[:30], e, msg, flush=True)
            time.sleep(4 * (attempt + 1))
    raise RuntimeError("TTS failed")

def job(i, lang, speed):
    s = SHOTS[i]
    if not s[lang]:
        return
    d = os.path.join(OUT, lang); os.makedirs(d, exist_ok=True)
    mp3 = os.path.join(d, s["id"] + ".mp3"); js = os.path.join(d, s["id"] + ".json")
    if os.path.exists(js):
        return
    prev = tts_text(SHOTS[i - 1][lang], lang) if i > 0 else None
    nxt = tts_text(SHOTS[i + 1][lang], lang) if i + 1 < len(SHOTS) and SHOTS[i + 1][lang] else None
    res = call(tts_text(s[lang], lang), lang, prev, nxt, speed)
    open(mp3, "wb").write(base64.b64decode(res["audio_base64"]))
    al = res.get("alignment") or res.get("normalized_alignment")
    json.dump({"text": tts_text(s[lang], lang), "alignment": al}, open(js, "w"), ensure_ascii=False)
    print("ok", lang, s["id"], round(al["character_end_times_seconds"][-1], 2), flush=True)

if __name__ == "__main__":
    langs = sys.argv[1:] or ["en", "tr", "de"]
    speeds = {"en": 1.0, "tr": 1.05, "de": 1.05}
    ids = [s["id"] for s in SHOTS]
    upto = ids.index(os.environ["UNTIL"]) + 1 if os.environ.get("UNTIL") else len(SHOTS)
    with cf.ThreadPoolExecutor(2) as ex:     # plan allows 2 concurrent requests
        futs = [ex.submit(job, i, l, speeds[l]) for l in langs for i in range(upto)]
        for f in futs:
            f.result()
    print("DONE")
