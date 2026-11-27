#!/usr/bin/env bash
# Rebuild dm/assets footage + stills + SFX from the two originals (footage not committed).
# Usage: tools/prep_footage.sh /path/to/IMG_6547.MOV /path/to/IMG_6550.mov
set -euo pipefail
P1="$1"; P2="$2"; HERE="$(cd "$(dirname "$0")/.." && pwd)"; P="$HERE/dm/assets"
mkdir -p "$P/img" "$P/sfx"
prep() {  # $1 = source, $2 = output prefix
  ffmpeg -v error -y -i "$1" -map 0:v:0 -map 0:a:0 -vf "scale=1080:1920:flags=lanczos,fps=30" -c:v libx264 -preset medium -crf 17 -g 15 \
    -pix_fmt yuv420p -af "highpass=f=80,afftdn=nf=-30,loudnorm=I=-16:TP=-1.5:LRA=9" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$P/$2.mp4"
  ffmpeg -v error -y -i "$P/$2.mp4" -filter_complex "[0:v]setpts=PTS/1.1,fps=30[v];[0:a]atempo=1.1[a]" -map "[v]" -map "[a]" \
    -c:v libx264 -preset medium -crf 17 -g 15 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$P/$2_fast.mp4"
}
prep "$P1" p1_footage
prep "$P2" footage
for t in 2.0 6.0 9.0 10.6 12.8; do ffmpeg -v error -y -ss $t -i "$P/p1_footage.mp4" -frames:v 1 -vf scale=540:960 -q:v 3 "$P/img/p1_$t.jpg"; done
for t in 0.1 1.9 2.4 3.4 4.4 5.0 6.0 7.2 8.2; do ffmpeg -v error -y -ss $t -i "$P/footage.mp4" -frames:v 1 -vf scale=540:960 -q:v 3 "$P/img/s_$t.jpg"; done
python3 "$HERE/../sinki-edit/tools/make_sfx.py" "$P/sfx" 14
