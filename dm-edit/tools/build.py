"""Generate dm/index.html (HyperFrames) for the 'DM saya sekarang' cafe clip (IMG_6550).

Edit the tables and re-run:  python3 tools/build.py
EDL times are ORIGINAL-source seconds; footage_fast.mp4 is the source sped up x SPEED (pitch kept).
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE / "dm"
W, H = 1080, 1920
SPEED = 1.1
FOOT = "assets/footage_fast.mp4"
WORDS = [w for s in json.loads((HERE / "transcript_raw.json").read_text()) for w in s["words"]]

# (id, src_in, src_out, audio, note)
EDL = [
    ("V1", 1.65, 3.05, 0.35, "HOOK: dia minum (ditutup clone wall + tajuk)"),
    ("V2", 3.05, 6.30, 1.0, "Tapi guys, kalau korang nak tahu apa perubahan besar tu"),
    ("V3", 6.86, 8.70, 1.0, "DM saya sekarang (+ senyum). Jeda 6.30-6.86 & pan kamera 8.75+ dibuang"),
]
CLIPS, t = [], 0.0
for cid, a, b, vol, note in EDL:
    CLIPS.append(dict(id=cid, start=round(t, 3), dur=round((b - a) / SPEED, 3), src=round(a / SPEED, 3),
                      src_out=round(b / SPEED, 3), vol=vol, note=note))
    t = CLIPS[-1]["start"] + CLIPS[-1]["dur"]
DUR = round(t, 3)
C = {c["id"]: c for c in CLIPS}
def o(cid, s):
    c = C[cid]
    return round(c["start"] + max(0.0, min(s / SPEED, c["src_out"]) - c["src"]), 3)

# captions: words of V2/V3 grouped by phrase
GROUPS = [
    ("V2", [("Tapi", 3.10), ("guys,", 3.24)]),
    ("V2", [("kalau", 3.52), ("korang", 4.24), ("nak", 4.62), ("tahu", 4.70)]),
    ("V2", [("apa", 4.98), ("perubahan", 5.26), ("besar", 5.76), ("tu", 5.96)]),
    ("V3", [("DM", 6.90), ("saya", 7.06), ("sekarang!", 7.30)]),
]
KEY = {"guys", "perubahan", "besar", "dm", "sekarang"}
CAPS = []
for i, (cid, ws) in enumerate(GROUPS):
    words = [(w, o(cid, s)) for w, s in ws]
    CAPS.append(dict(words=words, start=words[0][1]))
for i, g in enumerate(CAPS):
    g["end"] = CAPS[i + 1]["start"] if i + 1 < len(CAPS) else DUR
def clean(w): return re.sub(r"[.,?!]", "", w).lower()

B = dict(DUR=DUR, V2=C["V2"]["start"], V3=C["V3"]["start"], GUYS=o("V2", 3.24), KALAU=o("V2", 3.52),
         PERUBAHAN=o("V2", 5.26), DM=o("V3", 6.90), SEKARANG=o("V3", 7.30), SMILE=o("V3", 7.80))
B["WALL_OUT"] = B["V2"] + 0.04
FACE = "62% 36%"
CAM = [
    (0.0, FACE, 1.0, []),
    (B["V2"], FACE, 1.0, [(B["GUYS"], 0.12, 1.12, "power4.out"), (B["KALAU"], B["PERUBAHAN"] - B["KALAU"], 1.2, "none")]),
    (B["V3"], FACE, 1.15, [(B["DM"], 0.12, 1.35, "power4.out"), (B["SMILE"], 0.5, 1.12, "power2.inOut"),
                          (DUR - 0.3, 0.3, 1.4, "power3.in")]),
]
SFX = [
    ("impact", 0.0, 0.8), ("glitch", 0.02, 0.4), ("riser", 0.1, 0.3),
    ("tick", 0.42, 0.45), ("tick", 0.52, 0.45), ("tick", 0.62, 0.45), ("tick", 0.72, 0.45),
    ("whoosh", B["V2"] - 0.3, 0.6), ("pop", B["GUYS"], 0.4),
    ("whoosh", B["PERUBAHAN"] - 0.1, 0.45), ("impact", B["PERUBAHAN"], 0.5),
    ("whoosh_small", B["V3"] - 0.1, 0.45), ("ding2", B["DM"], 0.5), ("pop", B["DM"] + 0.15, 0.4),
    ("tick", B["SMILE"] - 0.15, 0.6), ("check", B["SMILE"] - 0.1, 0.45),
    ("whoosh", DUR - 0.35, 0.5),
]
SFX_LEN = {"impact": 1.4, "pop": 0.16, "riser": 1.6, "whoosh": 0.55, "whoosh_small": 0.28, "ding2": 1.2,
           "glitch": 0.45, "tick": 0.05, "check": 0.32}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def span(a, b): return f'data-start="{round(a,3)}" data-duration="{round(b-a,3)}"'

videos = "\n".join(
    f'      <!-- {c["id"]}: {esc(c["note"])} | src(orig) {EDL[i][1]:.2f}-{EDL[i][2]:.2f} -->\n'
    f'      <video id="v_{c["id"]}" class="clip vid" src="{FOOT}" playsinline data-has-audio="true" data-volume="{c["vol"]}" '
    f'data-fade-in="0.03" data-fade-out="0.03" data-start="{c["start"]}" data-duration="{c["dur"]}" '
    f'data-media-start="{c["src"]}" data-track-index="0"></video>' for i, c in enumerate(CLIPS))
caps_html = "\n".join(
    f'    <div id="cap{i}" class="clip cap" {span(g["start"], g["end"])} data-track-index="3">'
    + " ".join(f'<span class="w{" k" if clean(w) in KEY else ""}">{esc(w)}</span>' for w, _ in g["words"]) + "</div>"
    for i, g in enumerate(CAPS))
sfx_html = "\n".join(
    f'    <audio id="sfx{i}" src="assets/sfx/{f}.wav" data-start="{max(0, round(at, 3))}" '
    f'data-duration="{round(min(SFX_LEN[f], DUR - max(0, at)), 3)}" data-volume="{v}" data-track-index="{6 + i % 5}"></audio>'
    for i, (f, at, v) in enumerate(SFX))
STILLS = ["0.1", "1.9", "2.4", "3.4", "4.4", "5.0", "6.0", "7.2", "8.2"]
tiles = "\n".join(
    f'      <div class="tile" style="left:{(i%3)*360}px;top:{(i//3)*640}px"><img class="ta" src="assets/img/s_{STILLS[i]}.jpg" alt="">'
    f'<img class="tb" src="assets/img/s_{STILLS[(i+4)%9]}.jpg" alt=""></div>' for i in range(9))
hrows = "\n".join(
    f'      <div class="hrow {"solid" if r == 5 else ("outline" if r % 2 else "dim")}">PERUBAHAN BESAR &#8226; PERUBAHAN BESAR &#8226; PERUBAHAN BESAR</div>'
    for r in range(11))
ol = ["DM SAYA", "&#9679;", "SEKARANG", "&#9679;"] * 2
orbit_items = "\n".join(
    f'          <div class="oi" style="transform: rotateY({i*360/len(ol):.1f}deg) translateZ(330px)">{lab}</div>' for i, lab in enumerate(ol))
PLANE = ('<svg viewBox="0 0 24 24" width="44" height="44"><path d="M22 2 11 13" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
         '<path d="M22 2 15 22 11 13 2 9Z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></svg>')

html = f"""<!doctype html>
<!-- GENERATED by tools/build.py — edit the tables there, then re-run. -->
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat.ttf") format("truetype"); font-weight: 100 900; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      body {{ font-family: "Montserrat", sans-serif; color: #fff; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; isolation: isolate; background: #000; }}
      #shake, #cam {{ position: absolute; inset: 0; will-change: transform; }}
      #cam {{ filter: contrast(1.06) saturate(1.12); }}
      .vid {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .vignette {{ position: absolute; inset: 0; z-index: 5; pointer-events: none;
        background: radial-gradient(ellipse at 62% 40%, rgba(0,0,0,0) 50%, rgba(0,0,0,.35) 100%); }}
      .cap {{ position: absolute; left: 50px; right: 50px; top: 1420px; z-index: 20; text-align: center;
        font-weight: 900; font-size: 58px; line-height: 1.1; text-transform: uppercase; letter-spacing: -1px; }}
      .cap .w {{ display: inline-block; margin: 0 6px; color: #fff; -webkit-text-stroke: 11px #000; paint-order: stroke fill;
        text-shadow: 0 8px 16px rgba(0,0,0,.45); }}
      .cap .w.k {{ color: #FFD400; }}

      /* clone wall hook */
      #wall {{ position: absolute; inset: 0; z-index: 12; background: #000; }}
      #wallInner {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      .tile {{ position: absolute; width: 360px; height: 640px; overflow: hidden; border: 6px solid #000; border-radius: 22px; }}
      .tile img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .tile .tb {{ opacity: 0; }}
      #hook {{ position: absolute; left: 0; right: 0; top: 760px; z-index: 13; text-align: center; font-family: "Anton"; line-height: 1; }}
      #hook .h1 {{ display: inline-block; font-size: 64px; background: #111; padding: 10px 28px; border-radius: 16px; }}
      #hook .h2 {{ display: block; margin-top: 14px; }}
      #hook .h2 b {{ display: inline-block; font-weight: 400; font-size: 100px; color: #111; background: #FFD400; padding: 12px 26px 4px; white-space: nowrap; border-radius: 20px;
        box-shadow: 0 16px 40px rgba(0,0,0,.6); }}

      /* headline wall */
      #hwall {{ position: absolute; inset: 0; z-index: 11; background: rgba(6,8,14,.62); overflow: hidden; }}
      .hrow {{ position: absolute; left: 50%; white-space: nowrap; font-family: "Anton"; font-size: 150px; line-height: 1; letter-spacing: 2px; }}
      .hrow.outline {{ color: transparent; -webkit-text-stroke: 3px rgba(255,255,255,.85); }}
      .hrow.dim {{ color: rgba(255,255,255,.13); }}
      .hrow.solid {{ color: #FFD400; text-shadow: 0 10px 30px rgba(0,0,0,.8); }}

      /* orbit */
      #orbit {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 13; perspective: 1100px; perspective-origin: 670px 930px; }}
      #orbitPos {{ position: absolute; left: 670px; top: 930px; width: 0; height: 0; transform-style: preserve-3d; }}
      #ring {{ position: absolute; left: 0; top: 0; width: 0; height: 0; transform-style: preserve-3d; }}
      .oi {{ position: absolute; left: -200px; top: -34px; width: 400px; height: 68px; text-align: center; line-height: 68px; white-space: nowrap;
        font-weight: 900; font-size: 42px; color: #FFD400; -webkit-text-stroke: 8px #000; paint-order: stroke fill; backface-visibility: hidden; }}

      /* DM CTA */
      #cta {{ position: absolute; left: 0; right: 0; top: 230px; z-index: 14; text-align: center; }}
      #cta .btn {{ position: relative; display: inline-flex; align-items: center; gap: 18px; padding: 18px 40px; border-radius: 60px;
        background: linear-gradient(90deg, #7B2FF7, #E1306C 55%, #F77737); font-weight: 900; font-size: 50px; letter-spacing: 1px;
        box-shadow: 0 16px 36px rgba(0,0,0,.45); }}
      #cta .ripple {{ position: absolute; left: 50%; top: 50%; width: 120px; height: 120px; margin: -60px 0 0 -60px; border-radius: 50%;
        border: 6px solid #fff; opacity: 0; }}
      #cta .hand {{ position: absolute; left: 62%; top: 70px; width: 70px; height: 70px; border-radius: 50%; background: rgba(255,255,255,.9);
        box-shadow: 0 6px 16px rgba(0,0,0,.4); }}

      #flash {{ position: absolute; inset: 0; z-index: 40; background: #fff; opacity: 0; pointer-events: none; }}
      #progress {{ position: absolute; left: 0; top: 0; height: 10px; width: 100%; z-index: 41; background: #FFD400; transform-origin: 0 50%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}" data-fps="30">
      <div id="shake"><div id="cam">
{videos}
      </div></div>
      <div class="vignette"></div>

      <!-- HOOK: clone wall + headline, zooms into the live shot -->
      <div id="wall" class="clip" {span(0, B["WALL_OUT"])} data-track-index="2"><div id="wallInner">
{tiles}
      </div></div>
      <div id="hook" class="clip" {span(0, B["V2"] - 0.05)} data-track-index="2">
        <span class="h1">ADA</span><span class="h2"><b>PERUBAHAN BESAR!</b></span></div>

      <!-- HEADLINE WALL -->
      <div id="hwall" class="clip" {span(B["PERUBAHAN"], B["V3"])} data-track-index="2">
{hrows}
      </div>

      <!-- ORBIT -->
      <div id="orbit" class="clip" {span(B["DM"], B["SMILE"] + 0.2)} data-track-index="2"><div id="orbitPos"><div id="ring">
{orbit_items}
      </div></div></div>

      <!-- DM CTA -->
      <div id="cta" class="clip" {span(B["DM"] - 0.02, DUR)} data-track-index="2">
        <div class="btn">{PLANE}<span>DM SAYA SEKARANG</span><div class="ripple"></div></div>
        <div class="hand"></div></div>

{caps_html}

      <div id="flash" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <div id="progress" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <audio id="music" src="assets/sfx/music.wav" data-start="0" data-duration="{DUR}" data-volume="0.1" data-fade-out="0.3" data-track-index="5"></audio>
{sfx_html}
    </div>

    <script>
      const B = {json.dumps(B)};
      const CAM = {json.dumps(CAM)};
      const CAPW = {json.dumps([[w[1] for w in g["words"]] for g in CAPS])};
      const tl = gsap.timeline({{ paused: true }});
      const qa = (s) => Array.from(document.querySelectorAll(s));

      for (const [cut, origin, s0, keys] of CAM) {{
        tl.set("#cam", {{ scale: s0, transformOrigin: origin }}, cut);
        let prev = s0;
        for (const [t, d, s, ease] of keys) {{
          tl.fromTo("#cam", {{ scale: prev }}, {{ scale: s, duration: d, ease, immediateRender: false }}, t);
          prev = s;
        }}
      }}
      function shake(at, amp, len) {{
        const n = Math.round(len / 0.033);
        for (let i = 0; i < n; i++) {{
          const k = 1 - i / n, sx = ((i * 37) % 7 - 3) / 3, sy = ((i * 53) % 5 - 2) / 2;
          tl.set("#shake", {{ x: sx * amp * k, y: sy * amp * k }}, at + i * 0.033);
        }}
        tl.set("#shake", {{ x: 0, y: 0 }}, at + n * 0.033);
      }}
      shake(0, 16, 0.3); shake(B.PERUBAHAN, 12, 0.25); shake(B.DM, 10, 0.2);

      // flashes; ends white like it starts -> seamless loop
      tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.22 }}, 0);
      for (const at of [B.WALL_OUT, B.PERUBAHAN, B.V3]) tl.fromTo("#flash", {{ opacity: 0.6 }}, {{ opacity: 0, duration: 0.2, immediateRender: false }}, at);
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.3, ease: "power2.in", immediateRender: false }}, B.DUR - 0.3);
      tl.fromTo("#progress", {{ scaleX: 0 }}, {{ scaleX: 1, duration: B.DUR, ease: "none" }}, 0);

      // clone wall: tiles pop in, flip, zoom through the centre tile into the live shot
      const tiles = qa(".tile"), order = [4, 1, 3, 5, 7, 0, 2, 6, 8];
      order.forEach((idx, n) => tl.fromTo(tiles[idx], {{ scale: 0.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.16, ease: "back.out(2)" }}, n * 0.022));
      order.forEach((idx, n) => {{
        const at = 0.42 + n * 0.035, tile = tiles[idx];
        tl.to(tile, {{ scaleX: 0, duration: 0.05 }}, at);
        tl.set(tile.querySelector(".tb"), {{ opacity: 1 }}, at + 0.05);
        tl.set(tile.querySelector(".ta"), {{ opacity: 0 }}, at + 0.05);
        tl.to(tile, {{ scaleX: 1, duration: 0.06 }}, at + 0.05);
      }});
      tl.fromTo("#wallInner", {{ scale: 1 }}, {{ scale: 3.05, duration: 0.3, ease: "power3.in", immediateRender: false }}, B.WALL_OUT - 0.32);
      tl.to("#wall", {{ opacity: 0, duration: 0.06 }}, B.WALL_OUT - 0.06);
      tl.fromTo("#hook .h1", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.16 }}, 0.05);
      tl.fromTo("#hook .h2 b", {{ scale: 2.4, opacity: 0, rotation: -4 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.2, ease: "back.out(2.2)" }}, 0.14);
      tl.to("#hook .h2 b", {{ scale: 1.06, duration: 0.3, yoyo: true, repeat: 1, ease: "sine.inOut" }}, 0.5);
      tl.to("#hook", {{ scale: 1.6, opacity: 0, duration: 0.2, ease: "power2.in" }}, B.V2 - 0.25);

      // headline wall
      qa(".hrow").forEach((row, r) => {{
        const dir = r % 2 ? 1 : -1;
        tl.set(row, {{ y: -60 + r * 190, xPercent: -50 }}, B.PERUBAHAN);
        tl.fromTo(row, {{ x: dir * 700, opacity: 0 }}, {{ x: dir * -60, opacity: 1, duration: 0.22 + Math.abs(r - 5) * 0.02, ease: "power3.out" }}, B.PERUBAHAN + Math.abs(r - 5) * 0.025);
        tl.to(row, {{ x: dir * -200, duration: B.V3 - B.PERUBAHAN - 0.25, ease: "none" }}, B.PERUBAHAN + 0.25);
      }});
      tl.fromTo(".hrow.solid", {{ scale: 1.6 }}, {{ scale: 1.08, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, B.PERUBAHAN);
      tl.to("#hwall", {{ opacity: 0, scale: 1.2, duration: 0.12 }}, B.V3 - 0.12);

      // orbit
      tl.fromTo("#ring", {{ rotationX: -12, rotationY: 0 }}, {{ rotationX: -12, rotationY: -300, duration: B.SMILE + 0.2 - B.DM, ease: "power1.inOut" }}, B.DM);
      tl.fromTo("#orbitPos", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(1.8)" }}, B.DM);
      tl.to("#orbitPos", {{ scale: 1.5, opacity: 0, duration: 0.18 }}, B.SMILE + 0.02);

      // DM button: pop, tap, ripple, pulse
      tl.fromTo("#cta .btn", {{ scale: 0, rotation: -8 }}, {{ scale: 1, rotation: 0, duration: 0.25, ease: "back.out(2.4)" }}, B.DM);
      tl.fromTo("#cta .hand", {{ x: 160, y: 140, opacity: 0 }}, {{ x: 0, y: 0, opacity: 1, duration: 0.35, ease: "power2.out" }}, B.SMILE - 0.5);
      tl.to("#cta .hand", {{ scale: 0.8, duration: 0.08, yoyo: true, repeat: 1 }}, B.SMILE - 0.15);
      tl.to("#cta .btn", {{ scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }}, B.SMILE - 0.15);
      tl.fromTo("#cta .ripple", {{ scale: 0.3, opacity: 0.9 }}, {{ scale: 3, opacity: 0, duration: 0.45, ease: "power2.out", immediateRender: false }}, B.SMILE - 0.1);

      // captions
      qa(".cap").forEach((cap, gi) => {{
        tl.fromTo(cap, {{ scale: 0.82 }}, {{ scale: 1, duration: 0.15, ease: "back.out(2.5)" }}, CAPW[gi][0]);
        cap.querySelectorAll(".w").forEach((w, wi) => {{
          tl.fromTo(w, {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.09 }}, CAPW[gi][wi]);
          if (w.classList.contains("k")) tl.fromTo(w, {{ scale: 1.3 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, CAPW[gi][wi]);
        }});
      }});

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(html)
lines = [f"DURATION {DUR}s (asal 10.0s, suara x{SPEED})", "", "EDL (output -> source asal):"]
lines += [f"  {c['start']:5.2f}-{c['start']+c['dur']:5.2f}  src {EDL[i][1]:5.2f}-{EDL[i][2]:5.2f}  {c['id']} {c['note']}" for i, c in enumerate(CLIPS)]
lines += ["", "BEATS:"] + [f"  {k:10s} {v}" for k, v in B.items()]
lines += ["", "CAPTIONS:"] + [f"  {g['start']:5.2f}-{g['end']:5.2f}  " + " ".join(w for w, _ in g["words"]) for g in CAPS]
(HERE / "EDIT_PLAN.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
