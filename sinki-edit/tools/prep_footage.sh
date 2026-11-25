#!/usr/bin/env bash
# Rebuild sinki/assets/footage.mp4 + stills from the original iPhone .mov (not committed: too large).
# Usage: tools/prep_footage.sh /path/to/sinki.mov
set -euo pipefail
SRC="$1"; P="$(cd "$(dirname "$0")/.." && pwd)/sinki"
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -map 0:a:0 -vf "scale=1080:1920,fps=30" \
  -c:v libx264 -preset medium -crf 18 -g 15 -pix_fmt yuv420p \
  -af "highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k \
  -movflags +faststart "$P/assets/footage.mp4"
for t in 5.0 12.0 24.2 13.8; do
  ffmpeg -v error -y -ss $t -i "$P/assets/footage.mp4" -frames:v 1 -vf scale=540:960 -q:v 3 "$P/assets/img/still_$t.jpg"
done
python3 "$(dirname "$0")/make_sfx.py" "$P/assets/sfx" 24
