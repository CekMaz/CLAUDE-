#!/usr/bin/env bash
# Rebuild dm/assets/footage*.mp4 + stills + SFX from the original IMG_6550.mov (footage not committed).
set -euo pipefail
SRC="$1"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; P="$HERE/dm/assets"
mkdir -p "$P/img" "$P/sfx"
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -map 0:a:0 -vf "scale=1080:1920:flags=lanczos,fps=30" -c:v libx264 -preset medium -crf 17 -g 15 \
  -pix_fmt yuv420p -af "highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$P/footage.mp4"
ffmpeg -v error -y -i "$P/footage.mp4" -filter_complex "[0:v]setpts=PTS/1.1,fps=30[v];[0:a]atempo=1.1[a]" -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 17 -g 15 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$P/footage_fast.mp4"
for t in 0.1 1.9 2.4 3.4 4.4 5.0 6.0 7.2 8.2; do
  ffmpeg -v error -y -ss $t -i "$P/footage.mp4" -frames:v 1 -vf scale=540:960 -q:v 3 "$P/img/s_$t.jpg"
done
python3 "$HERE/../sinki-edit/tools/make_sfx.py" "$P/sfx" 8
