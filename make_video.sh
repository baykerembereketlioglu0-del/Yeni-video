#!/usr/bin/env bash
# Full production run: voice -> timeline -> music/sfx mix -> render -> mux -> metadata.
# Re-running is safe: tts.py skips lines that already exist in build/audio.
#   ./make_video.sh            full video, all languages
#   UNTIL=c1a ./make_video.sh en   pilot cut (stops after shot c1a), English only
set -euo pipefail
cd "$(dirname "$0")/project"
LANGS="${*:-en tr de}"

python3 tts.py $LANGS          # ElevenLabs narration with word timestamps
python3 audio.py $LANGS        # music + SFX + ducking + SRT, per language
python3 render.py video        # 1080p30 picture, rendered in parallel chunks
python3 thumbnail.py
python3 finalize.py $LANGS     # upload-ready files in ../output
python3 build_meta.py          # titles, descriptions with chapters, tags
echo "Done -> $(cd .. && pwd)/output"
