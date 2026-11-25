#!/usr/bin/env bash
# Rebuild waiver/assets/footage.mp4 + face stills + SFX from the original .mov (footage not committed).
# Usage: tools/prep_footage.sh /path/to/Waiver.mov
set -euo pipefail
SRC="$1"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; P="$HERE/waiver"
mkdir -p "$P/assets/img" "$P/assets/sfx"
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -map 0:a:0 -vf "scale=1080:1920:flags=lanczos,fps=30" \
  -c:v libx264 -preset medium -crf 17 -g 15 -pix_fmt yuv420p \
  -af "highpass=f=70,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k \
  -movflags +faststart "$P/assets/footage.mp4"
for t in 1.0 6.0 9.6 12.2 16.0 19.0 25.0 30.0 33.0 38.5; do
  ffmpeg -v error -y -ss $t -i "$P/assets/footage.mp4" -frames:v 1 -vf scale=540:960 -q:v 3 "$P/assets/img/face_$t.jpg"
done
python3 "$HERE/../sinki-edit/tools/make_sfx.py" "$P/assets/sfx" 48
