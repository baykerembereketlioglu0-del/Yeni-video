# -*- coding: utf-8 -*-
"""Mux the rendered picture with each language mix and write upload-ready files to output/.

output/
  GTA6_Lucia_EN.mp4            main upload (English audio)
  GTA6_Lucia_MULTI.mp4         same video with EN/TR/DE audio tracks (for players / archive)
  audio_TR.m4a, audio_DE.m4a   YouTube Studio -> Languages -> add dubbed audio track
  subtitles_*.srt              YouTube Studio -> Subtitles
  thumbnail_*.jpg              1280x720
  youtube_*.txt                title, description (with chapters) and tags per language
"""
import os, sys, shutil, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from timeline import ROOT

B = os.path.join(ROOT, "build")
O = os.path.join(ROOT, "output")
LANG_ISO = {"en": "eng", "tr": "tur", "de": "ger"}
NORM = "loudnorm=I=-14:LRA=11:TP=-1.5"

def run(cmd):
    subprocess.run(cmd, check=True)

def main(langs, prefix="GTA6_Lucia"):
    os.makedirs(O, exist_ok=True)
    vid = os.path.join(B, "video_noaudio.mp4")
    for lang in langs:
        wav = os.path.join(B, f"mix_{lang}.wav")
        m4a = os.path.join(O, f"audio_{lang.upper()}.m4a")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", NORM, "-c:a", "aac", "-b:a", "192k",
             "-ar", "48000", m4a])
        if lang == "en":
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", m4a, "-map", "0:v", "-map", "1:a",
                 "-c", "copy", "-movflags", "+faststart", "-metadata:s:a:0", "language=eng",
                 os.path.join(O, f"{prefix}_EN.mp4")])
        srt = os.path.join(B, f"subtitles_{lang}.srt")
        if os.path.exists(srt):
            shutil.copy(srt, O)
    if len(langs) > 1:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", vid]
        for lang in langs:
            cmd += ["-i", os.path.join(O, f"audio_{lang.upper()}.m4a")]
        cmd += ["-map", "0:v"]
        for i, _ in enumerate(langs):
            cmd += ["-map", f"{i + 1}:a"]
        cmd += ["-c", "copy", "-movflags", "+faststart"]
        for i, lang in enumerate(langs):
            cmd += [f"-metadata:s:a:{i}", f"language={LANG_ISO[lang]}"]
        cmd += [os.path.join(O, f"{prefix}_MULTI.mp4")]
        run(cmd)
    os.remove(os.path.join(O, "audio_EN.m4a")) if os.path.exists(os.path.join(O, "audio_EN.m4a")) else None
    for lang in ("en", "tr", "de"):
        t = os.path.join(B, f"thumbnail_{lang}.jpg")
        if os.path.exists(t): shutil.copy(t, O)
    print("written to", O)

if __name__ == "__main__":
    main(sys.argv[1:] or ["en", "tr", "de"], prefix="GTA6_Lucia_PILOT" if os.environ.get("UNTIL") else "GTA6_Lucia")
