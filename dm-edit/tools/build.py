"""Generate dm/index.html (HyperFrames): Medical Card 2027 — Part 1 (IMG_6547) + Part 2 (IMG_6550).

Edit the tables and re-run:  python3 tools/build.py
EDL / word times are ORIGINAL-source seconds; footage *_fast.mp4 files are sped up x SPEED (pitch kept).
Word times were hand-aligned to the audio energy (whisper timestamps drifted on these clips).
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE / "dm"
W, H = 1080, 1920
SPEED = 1.1
SRC = {"p1": "assets/p1_footage_fast.mp4", "p2": "assets/footage_fast.mp4"}

# (id, source, src_in, src_out, volume, note)   -- awkward pauses removed between clips
EDL = [
    ("A", "p1", 3.90, 7.45, 1.0, "IMG_6547: 'tepi tepi tepi' + keluar pintu + 'ok guys'"),
    ("B", "p1", 8.05, 9.42, 1.0, "korang nak tahu tak, tahun depan"),
    ("C", "p1", 10.15, 11.72, 1.0, "medical card banyak perubahan"),
    ("D", "p1", 12.25, 13.65, 1.0, "pada tahun 2027  (rakaman 'dah' di hujung dibuang)"),
    ("E", "p2", 3.05, 6.30, 1.0, "IMG_6550: Tapi guys, kalau korang nak tahu apa perubahan besar tu"),
    ("F", "p2", 6.86, 8.70, 1.0, "DM saya sekarang (+ senyum)"),
]
CLIPS, t = [], 0.0
for cid, src, a, b, vol, note in EDL:
    CLIPS.append(dict(id=cid, srcfile=SRC[src], start=round(t, 3), dur=round((b - a) / SPEED, 3),
                      src=round(a / SPEED, 3), src_out=round(b / SPEED, 3), a=a, b=b, vol=vol, note=note))
    t = CLIPS[-1]["start"] + CLIPS[-1]["dur"]
DUR = round(t, 3)
C = {c["id"]: c for c in CLIPS}
def o(cid, s):
    c = C[cid]
    return round(c["start"] + max(0.0, min(s / SPEED, c["src_out"]) - c["src"]), 3)
def end(cid): return round(C[cid]["start"] + C[cid]["dur"], 3)

# captions (clip, [(word, original src time)])
GROUPS = [
    ("A", [("Ok", 6.62), ("guys!", 6.85)]),
    ("B", [("Korang", 8.12), ("nak", 8.22), ("tahu", 8.30), ("tak,", 8.56)]),
    ("B", [("tahun", 8.74), ("depan", 8.96)]),
    ("C", [("medical", 10.22), ("card", 10.46)]),
    ("C", [("banyak", 10.76), ("perubahan", 11.12)]),
    ("D", [("pada", 12.32), ("tahun", 12.44), ("2027", 12.74)]),
    ("E", [("Tapi", 3.10), ("guys,", 3.24)]),
    ("E", [("kalau", 3.52), ("korang", 4.24), ("nak", 4.62), ("tahu", 4.70)]),
    ("E", [("apa", 4.98), ("perubahan", 5.26), ("besar", 5.76), ("tu", 5.96)]),
    ("F", [("DM", 6.90), ("saya", 7.06), ("sekarang!", 7.30)]),
]
KEY = {"guys", "tahun", "depan", "medical", "card", "perubahan", "2027", "besar", "dm", "sekarang"}
CAPS = [dict(words=[(w, o(cid, s)) for w, s in ws]) for cid, ws in GROUPS]
for i, g in enumerate(CAPS):
    g["start"] = g["words"][0][1]
    nxt = CAPS[i + 1]["words"][0][1] if i + 1 < len(CAPS) else DUR
    clip_end = next(end(c["id"]) for c in CLIPS if c["start"] <= g["start"] < end(c["id"]))
    g["end"] = round(min(nxt, clip_end + 0.25) if nxt > clip_end else nxt, 3)
def clean(w): return re.sub(r"[.,?!]", "", w).lower()

B = dict(DUR=DUR, A=0.0, B=C["B"]["start"], C=C["C"]["start"], D=C["D"]["start"], E=C["E"]["start"], F=C["F"]["start"],
         TEPI=o("A", 4.32), TEPI_END=o("A", 5.62), OKGUYS=o("A", 6.62), TAHUN=o("B", 8.74), MED=o("C", 10.22),
         Y2027=o("D", 12.74), GUYS=o("E", 3.24), KALAU=o("E", 3.52), PERUBAHAN=o("E", 5.26), DM=o("F", 6.90),
         SMILE=o("F", 7.80))
B["WALL_IN"] = round(end("D") - 0.25, 3)
B["WALL_OUT"] = round(B["E"] + 0.42, 3)

CAM = [  # (cut, origin, start_scale, [(t, dur, scale, ease)])
    (0.0, "60% 42%", 1.0, [(0.0, B["OKGUYS"], 1.08, "none"), (B["OKGUYS"], 0.12, 1.16, "power4.out")]),
    (B["B"], "48% 28%", 1.0, [(B["TAHUN"], 0.12, 1.12, "power4.out")]),
    (B["C"], "48% 28%", 1.06, [(B["MED"], C["C"]["dur"], 1.14, "none")]),
    (B["D"], "46% 26%", 1.0, [(B["Y2027"], 0.12, 1.2, "power4.out")]),
    (B["E"], "62% 36%", 1.0, [(B["GUYS"], 0.12, 1.12, "power4.out"), (B["KALAU"], B["PERUBAHAN"] - B["KALAU"], 1.2, "none")]),
    (B["F"], "62% 36%", 1.15, [(B["DM"], 0.12, 1.35, "power4.out"), (B["SMILE"], 0.5, 1.12, "power2.inOut"),
                              (DUR - 0.3, 0.3, 1.4, "power3.in")]),
]
SFX = [
    ("whoosh", 0.0, 0.5), ("impact", 0.08, 0.6), ("pop", 0.32, 0.45),
    ("pop", B["TEPI"], 0.5), ("pop", o("A", 4.56), 0.5), ("pop", o("A", 4.82), 0.55),
    ("whoosh_small", B["OKGUYS"] - 0.1, 0.45), ("ding1", B["OKGUYS"], 0.3),
    ("whoosh_small", B["TAHUN"] - 0.05, 0.45),
    ("whoosh", B["MED"] - 0.15, 0.45), ("check", B["MED"] + 0.2, 0.45),
    ("tick", B["Y2027"] - 0.30, 0.5), ("tick", B["Y2027"] - 0.20, 0.5), ("tick", B["Y2027"] - 0.10, 0.5), ("impact", B["Y2027"], 0.55),
    ("glitch", B["WALL_IN"], 0.4), ("shutter", B["WALL_IN"] + 0.03, 0.5), ("tick", B["WALL_IN"] + 0.3, 0.45),
    ("tick", B["WALL_IN"] + 0.4, 0.45), ("whoosh", B["WALL_OUT"] - 0.3, 0.55),
    ("pop", B["GUYS"], 0.35),
    ("whoosh", B["PERUBAHAN"] - 0.1, 0.45), ("impact", B["PERUBAHAN"], 0.5),
    ("whoosh_small", B["F"] - 0.1, 0.45), ("ding2", B["DM"], 0.5), ("pop", B["DM"] + 0.15, 0.4),
    ("tick", B["SMILE"] - 0.15, 0.6), ("check", B["SMILE"] - 0.1, 0.45),
    ("whoosh", DUR - 0.35, 0.5),
]
SFX_LEN = {"impact": 1.4, "pop": 0.16, "riser": 1.6, "whoosh": 0.55, "whoosh_small": 0.28, "ding1": 1.2, "ding2": 1.2,
           "glitch": 0.45, "tick": 0.05, "check": 0.32, "shutter": 0.22}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def span(a, b): return f'data-start="{round(a,3)}" data-duration="{round(b-a,3)}"'

videos = "\n".join(
    f'      <!-- {c["id"]}: {esc(c["note"])} | src(orig) {c["a"]:.2f}-{c["b"]:.2f} -->\n'
    f'      <video id="v_{c["id"]}" class="clip vid" src="{c["srcfile"]}" playsinline data-has-audio="true" data-volume="{c["vol"]}" '
    f'data-fade-in="0.03" data-fade-out="0.03" data-start="{c["start"]}" data-duration="{c["dur"]}" '
    f'data-media-start="{c["src"]}" data-track-index="0"></video>' for c in CLIPS)
caps_html = "\n".join(
    f'    <div id="cap{i}" class="clip cap" {span(g["start"], g["end"])} data-track-index="3">'
    + " ".join(f'<span class="w{" k" if clean(w) in KEY else ""}">{esc(w)}</span>' for w, _ in g["words"]) + "</div>"
    for i, g in enumerate(CAPS))
sfx_html = "\n".join(
    f'    <audio id="sfx{i}" src="assets/sfx/{f}.wav" data-start="{max(0, round(at, 3))}" '
    f'data-duration="{round(min(SFX_LEN[f], DUR - max(0, at)), 3)}" data-volume="{v}" data-track-index="{6 + i % 5}"></audio>'
    for i, (f, at, v) in enumerate(SFX))
STILLS = ["p1_2.0", "s_1.9", "p1_9.0", "s_5.0", "s_3.4", "p1_12.8", "p1_6.0", "s_7.2", "p1_10.6"]
STILLS_B = ["s_6.0", "p1_10.6", "s_4.4", "p1_12.8", "s_3.4", "s_0.1", "s_8.2", "p1_9.0", "s_2.4"]
tiles = "\n".join(
    f'      <div class="tile" style="left:{(i%3)*360}px;top:{(i//3)*640}px"><img class="ta" src="assets/img/{STILLS[i]}.jpg" alt="">'
    f'<img class="tb" src="assets/img/{STILLS_B[i]}.jpg" alt=""></div>' for i in range(9))
hrows = "\n".join(
    f'      <div class="hrow {"solid" if r == 5 else ("outline" if r % 2 else "dim")}">PERUBAHAN BESAR &#8226; PERUBAHAN BESAR &#8226; PERUBAHAN BESAR</div>'
    for r in range(11))
ol = ["DM SAYA", "&#9679;", "SEKARANG", "&#9679;"] * 2
orbit_items = "\n".join(
    f'          <div class="oi" style="transform: rotateY({i*360/len(ol):.1f}deg) translateZ(330px)">{lab}</div>' for i, lab in enumerate(ol))
PLANE = ('<svg viewBox="0 0 24 24" width="44" height="44"><path d="M22 2 11 13" stroke="#fff" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
         '<path d="M22 2 15 22 11 13 2 9Z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></svg>')
digits = "".join(f'<div>{d}</div>' for d in "4567")

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
        background: radial-gradient(ellipse at 55% 40%, rgba(0,0,0,0) 50%, rgba(0,0,0,.3) 100%); }}
      .cap {{ position: absolute; left: 50px; right: 50px; top: 1420px; z-index: 20; text-align: center;
        font-weight: 900; font-size: 58px; line-height: 1.1; text-transform: uppercase; letter-spacing: -1px; }}
      .cap .w {{ display: inline-block; margin: 0 6px; color: #fff; -webkit-text-stroke: 11px #000; paint-order: stroke fill;
        text-shadow: 0 8px 16px rgba(0,0,0,.45); }}
      .cap .w.k {{ color: #FFD400; }}

      /* hook title */
      #hook {{ position: absolute; left: 0; right: 0; top: 170px; z-index: 13; text-align: center; font-family: "Anton"; line-height: 1; }}
      #hook .h1 {{ display: inline-block; font-size: 66px; color: #fff; background: #111; padding: 12px 26px 8px; border-radius: 16px; }}
      #hook .h2 {{ display: block; margin-top: 12px; }}
      #hook .h2 b {{ display: inline-block; font-weight: 400; font-size: 92px; color: #111; background: #FFD400; padding: 12px 26px 4px; border-radius: 18px;
        box-shadow: 0 14px 34px rgba(0,0,0,.35); white-space: nowrap; }}
      #tepi {{ position: absolute; left: 560px; top: 560px; z-index: 14; }}
      #tepi .bub {{ position: relative; display: inline-block; padding: 14px 26px; background: #fff; color: #111; border-radius: 30px; border: 5px solid #111;
        font-weight: 900; font-size: 46px; white-space: nowrap; box-shadow: 0 10px 24px rgba(0,0,0,.3); }}
      #tepi .bub:after {{ content: ""; position: absolute; left: 40px; bottom: -30px; border: 16px solid transparent; border-top: 22px solid #111; }}

      /* medical card + 2027 */
      #med {{ position: absolute; right: 50px; top: 330px; z-index: 14; }}
      #med .card {{ width: 380px; height: 236px; border-radius: 26px; padding: 22px 26px; text-align: left;
        background: linear-gradient(135deg, #0EA5E9, #2563EB 55%, #1E3A8A); box-shadow: 0 18px 40px rgba(0,0,0,.4); transform: rotate(-6deg); }}
      #med .chip {{ width: 64px; height: 48px; border-radius: 10px; background: linear-gradient(135deg, #FDE68A, #D4A017); }}
      #med .cross {{ position: absolute; right: 26px; top: 22px; width: 58px; height: 58px; border-radius: 14px; background: #fff; }}
      #med .cross:before, #med .cross:after {{ content: ""; position: absolute; background: #EF4444; border-radius: 3px; }}
      #med .cross:before {{ left: 23px; top: 10px; width: 12px; height: 38px; }}
      #med .cross:after {{ left: 10px; top: 23px; width: 38px; height: 12px; }}
      #med .ttl {{ margin-top: 40px; font-family: "Anton"; font-size: 54px; line-height: 1; letter-spacing: 1px; }}
      #med .sub {{ margin-top: 8px; font-weight: 800; font-size: 22px; letter-spacing: 4px; opacity: .85; }}
      #yr {{ position: absolute; left: 0; right: 0; top: 80px; z-index: 14; text-align: center; }}
      #yr .box {{ display: inline-flex; align-items: flex-start; font-family: "Anton"; font-size: 150px; line-height: 1; color: #111; background: #FFD400;
        padding: 10px 30px 0; border-radius: 22px; box-shadow: 0 16px 36px rgba(0,0,0,.35); height: 170px; overflow: hidden; }}
      #yr .wheel {{ display: inline-block; height: 150px; overflow: hidden; }}
      #yr .wheel .col {{ display: flex; flex-direction: column; }}
      #yr .wheel .col div {{ height: 150px; }}

      /* clone wall transition */
      #wall {{ position: absolute; inset: 0; z-index: 12; background: #000; }}
      #wallInner {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      .tile {{ position: absolute; width: 360px; height: 640px; overflow: hidden; border: 6px solid #000; border-radius: 22px; }}
      .tile img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .tile .tb {{ opacity: 0; }}

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

      <!-- HOOK -->
      <div id="hook" class="clip" {span(0, B["OKGUYS"] - 0.05)} data-track-index="2">
        <span class="h1">MEDICAL CARD 2027</span><span class="h2"><b>BANYAK PERUBAHAN?!</b></span></div>
      <div id="tepi" class="clip" {span(B["TEPI"], B["TEPI_END"])} data-track-index="2"><div class="bub">TEPI, TEPI, TEPI!</div></div>

      <!-- MEDICAL CARD + 2027 -->
      <div id="med" class="clip" {span(B["MED"] - 0.05, B["D"])} data-track-index="2"><div class="card">
        <div class="chip"></div><div class="cross"></div><div class="ttl">MEDICAL CARD</div><div class="sub">TAHUN DEPAN</div></div></div>
      <div id="yr" class="clip" {span(B["D"], B["WALL_IN"] + 0.05)} data-track-index="2">
        <div class="box"><span>202</span><span class="wheel"><div class="col">{digits}</div></span></div></div>

      <!-- CLONE WALL transition (pintu kafe -> meja) -->
      <div id="wall" class="clip" {span(B["WALL_IN"], B["WALL_OUT"])} data-track-index="2"><div id="wallInner">
{tiles}
      </div></div>

      <!-- HEADLINE WALL -->
      <div id="hwall" class="clip" {span(B["PERUBAHAN"], B["F"])} data-track-index="2">
{hrows}
      </div>

      <!-- ORBIT + DM CTA -->
      <div id="orbit" class="clip" {span(B["DM"], B["SMILE"] + 0.2)} data-track-index="2"><div id="orbitPos"><div id="ring">
{orbit_items}
      </div></div></div>
      <div id="cta" class="clip" {span(B["DM"] - 0.02, DUR)} data-track-index="2">
        <div class="btn">{PLANE}<span>DM SAYA SEKARANG</span><div class="ripple"></div></div>
        <div class="hand"></div></div>

{caps_html}

      <div id="flash" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <div id="progress" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <audio id="music" src="assets/sfx/music.wav" data-start="0" data-duration="{DUR}" data-volume="0.09" data-fade-out="0.3" data-track-index="5"></audio>
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
      shake(0.08, 14, 0.25); shake(B.Y2027, 12, 0.25); shake(B.PERUBAHAN, 12, 0.25); shake(B.DM, 10, 0.2);

      // flashes; end goes white like the start -> seamless loop
      tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.22 }}, 0);
      for (const at of [B.WALL_OUT, B.PERUBAHAN, B.F]) tl.fromTo("#flash", {{ opacity: 0.6 }}, {{ opacity: 0, duration: 0.2, immediateRender: false }}, at);
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.3, ease: "power2.in", immediateRender: false }}, B.DUR - 0.3);
      tl.fromTo("#progress", {{ scaleX: 0 }}, {{ scaleX: 1, duration: B.DUR, ease: "none" }}, 0);

      // hook
      tl.fromTo("#hook .h1", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.18, ease: "power3.out" }}, 0.05);
      tl.fromTo("#hook .h2 b", {{ scale: 2.4, opacity: 0, rotation: -4 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.2, ease: "back.out(2.2)" }}, 0.25);
      tl.to("#hook .h2 b", {{ scale: 1.05, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }}, 0.6);
      tl.to("#hook", {{ y: -40, opacity: 0, duration: 0.18 }}, B.OKGUYS - 0.23);
      [B.TEPI, B.TEPI + 0.22, B.TEPI + 0.45].forEach((t, i) =>
        tl.fromTo("#tepi .bub", {{ scale: i ? 1.18 : 0, rotation: i % 2 ? 4 : -4 }}, {{ scale: 1, rotation: 0, duration: 0.18, ease: "back.out(3)", immediateRender: !i }}, t));

      // medical card + 2027 roll
      tl.fromTo("#med .card", {{ x: 500, rotation: 20, opacity: 0 }}, {{ x: 0, rotation: -6, opacity: 1, duration: 0.35, ease: "back.out(1.5)" }}, B.MED - 0.05);
      tl.to("#med .card", {{ y: -10, duration: 0.6, yoyo: true, repeat: 1, ease: "sine.inOut" }}, B.MED + 0.4);
      tl.fromTo("#yr .box", {{ scale: 0.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2)" }}, B.D);
      tl.fromTo("#yr .col", {{ y: 0 }}, {{ y: -450, duration: B.Y2027 - B.D, ease: "power2.inOut" }}, B.D);
      tl.fromTo("#yr .box", {{ scale: 1.3 }}, {{ scale: 1, duration: 0.25, ease: "back.out(3)", immediateRender: false }}, B.Y2027);

      // clone wall transition
      const tiles = qa(".tile"), order = [4, 1, 3, 5, 7, 0, 2, 6, 8];
      order.forEach((idx, n) => tl.fromTo(tiles[idx], {{ scale: 0.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.14, ease: "back.out(2)" }}, B.WALL_IN + n * 0.02));
      order.forEach((idx, n) => {{
        const at = B.WALL_IN + 0.28 + n * 0.025, tile = tiles[idx];
        tl.to(tile, {{ scaleX: 0, duration: 0.04 }}, at);
        tl.set(tile.querySelector(".tb"), {{ opacity: 1 }}, at + 0.04);
        tl.set(tile.querySelector(".ta"), {{ opacity: 0 }}, at + 0.04);
        tl.to(tile, {{ scaleX: 1, duration: 0.05 }}, at + 0.04);
      }});
      tl.fromTo("#wallInner", {{ scale: 1 }}, {{ scale: 3.05, duration: 0.24, ease: "power3.in", immediateRender: false }}, B.WALL_OUT - 0.26);
      tl.to("#wall", {{ opacity: 0, duration: 0.05 }}, B.WALL_OUT - 0.05);

      // headline wall
      qa(".hrow").forEach((row, r) => {{
        const dir = r % 2 ? 1 : -1;
        tl.set(row, {{ y: -60 + r * 190, xPercent: -50 }}, B.PERUBAHAN);
        tl.fromTo(row, {{ x: dir * 700, opacity: 0 }}, {{ x: dir * -60, opacity: 1, duration: 0.22 + Math.abs(r - 5) * 0.02, ease: "power3.out" }}, B.PERUBAHAN + Math.abs(r - 5) * 0.025);
        tl.to(row, {{ x: dir * -200, duration: B.F - B.PERUBAHAN - 0.25, ease: "none" }}, B.PERUBAHAN + 0.25);
      }});
      tl.fromTo(".hrow.solid", {{ scale: 1.6 }}, {{ scale: 1.08, duration: 0.2, ease: "back.out(2)", immediateRender: false }}, B.PERUBAHAN);
      tl.to("#hwall", {{ opacity: 0, scale: 1.2, duration: 0.12 }}, B.F - 0.12);

      // orbit + DM button
      tl.fromTo("#ring", {{ rotationX: -12, rotationY: 0 }}, {{ rotationX: -12, rotationY: -300, duration: B.SMILE + 0.2 - B.DM, ease: "power1.inOut" }}, B.DM);
      tl.fromTo("#orbitPos", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(1.8)" }}, B.DM);
      tl.to("#orbitPos", {{ scale: 1.5, opacity: 0, duration: 0.18 }}, B.SMILE + 0.02);
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
lines = [f"DURATION {DUR}s (IMG_6547 + IMG_6550, suara x{SPEED})", "", "EDL (output -> source asal):"]
lines += [f"  {c['start']:5.2f}-{c['start']+c['dur']:5.2f}  {c['srcfile'].split('/')[-1]:22s} {c['a']:5.2f}-{c['b']:5.2f}  {c['id']} {c['note']}" for c in CLIPS]
lines += ["", "BEATS:"] + [f"  {k:10s} {v}" for k, v in B.items()]
lines += ["", "CAPTIONS:"] + [f"  {g['start']:5.2f}-{g['end']:5.2f}  " + " ".join(w for w, _ in g["words"]) for g in CAPS]
(HERE / "EDIT_PLAN.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
