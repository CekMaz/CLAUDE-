"""Generate sinki/index.html (HyperFrames composition) from the edit plan below.

Edit the EDL / CAPTIONS / SFX tables and re-run:  python3 tools/build.py
All times are OUTPUT (edited) seconds unless marked src.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "sinki"
W, H = 1080, 1920
FOOT = "assets/footage.mp4"

# ---------------------------------------------------------------- EDL
# (id, out_start, src_in, src_out, rate, has_audio, note)
EDL = [
    ("v_hook",   0.0,   12.70, 14.50, 1.0, False, "HOOK flash-forward: paip gunmetal tukar stream -> mist"),
    ("v_s1",     1.8,    1.80, 10.00, 1.0, True,  "Sinki silver: satu dua tiga / kalau yang ni / warna metal"),
    ("v_s2",    10.0,   11.70, 16.90, 1.0, True,  "Gunmetal: satu dua tiga / dua dia punya ni kecil / faham"),
    ("v_replay",15.2,   13.40, 14.20, 0.6, False, "REPLAY slow-mo mist (isi awkward pause 16.9-17.9)"),
    ("v_s3",    None,   17.92, 21.15, 1.0, True,  "Yang ni lagi okey / betul akak / ada warna ni tak"),
    ("v_s4",    None,   22.55, 26.13, 1.0, True,  "Ikut akak / akak tengok ni / dia cam ni sikit kan"),
]
t = 0.0
CLIPS = []
for cid, start, a, b, rate, aud, note in EDL:
    start = t if start is None else start
    dur = round((b - a) / rate, 3)
    CLIPS.append(dict(id=cid, start=round(start, 3), dur=dur, src=a, src_out=b, rate=rate, audio=aud, note=note))
    t = start + dur
DUR = round(t, 3)
C = {c["id"]: c for c in CLIPS}
def o(cid, src_t):
    """map a source time inside clip cid to output time"""
    c = C[cid]
    return round(c["start"] + (src_t - c["src"]) / c["rate"], 3)

# ---------------------------------------------------------------- CAPTIONS (word-timed)
# words: (text, src_time, keyword?) ; group end src time
def grp(cid, words, end, style=""):
    return dict(words=[(w, o(cid, s), k) for w, s, k in words], end=o(cid, end), style=style)
CAPTIONS = [
    grp("v_s1", [("Satu,", 2.98, 1), ("dua,", 3.50, 1), ("tiga!", 3.82, 1)], 4.30),
    grp("v_s1", [("Okey", 4.30, 0)], 5.20),
    grp("v_s1", [("Kalau", 5.32, 0), ("yang", 6.04, 0), ("ni...", 7.10, 0)], 7.54),
    grp("v_s1", [("Yang", 7.54, 0), ("macam", 7.68, 0), ("ni,", 7.88, 0)], 8.04),
    grp("v_s1", [("tapi", 8.04, 0), ("WARNA", 8.32, 1), ("macam", 8.62, 0), ("ni", 8.74, 0), ("lah", 8.96, 0)], 9.10),
    grp("v_s2", [("Satu,", 11.86, 1), ("dua,", 12.38, 1), ("tiga!", 12.94, 1)], 13.50),
    grp("v_s2", [("Dua", 13.50, 1), ("dia", 14.30, 0), ("punya", 14.36, 0), ("ni", 14.54, 0), ("KECIL", 14.62, 1)], 15.00),
    grp("v_s2", [("Faham", 15.88, 1)], 16.88),
    grp("v_s3", [("Yang", 17.98, 0), ("ni", 17.98, 0), ("lagi", 18.06, 0), ("OKEY", 18.18, 1)], 18.54),
    grp("v_s3", [("Betul", 18.54, 0), ("akak", 19.10, 0)], 19.36),
    grp("v_s4", [("Ikut", 22.60, 0), ("akak", 23.12, 0)], 23.32),
    grp("v_s4", [("Sebab", 23.32, 0), ("yang", 23.52, 0), ("ni", 23.62, 1)], 23.84),
    grp("v_s4", [("Akak", 23.84, 0), ("TENGOK", 24.32, 1), ("ni", 24.52, 0)], 24.60),
    grp("v_s4", [("Dia", 24.60, 0), ("cam", 24.88, 0), ("ni", 25.06, 0), ("sikit", 25.26, 1), ("kan?", 25.58, 0)], 26.10),
]

# key beats (output time)
T_HOOK_END = C["v_s1"]["start"]                 # 1.8
T_MODE_A = [o("v_s1", 2.98), o("v_s1", 3.50), o("v_s1", 3.82)]
T_WALL_IN, T_WALL_OUT = 6.42, 7.62              # clone wall covers camera swing 6.5-7.5
T_HWALL = o("v_s1", 9.10)                       # "warna metal"
T_S2 = C["v_s2"]["start"]
T_MODE_B = [o("v_s2", 11.86), o("v_s2", 12.38), o("v_s2", 12.94)]
T_MIST = o("v_s2", 13.50)
T_FAHAM = o("v_s2", 15.88)
T_REPLAY = C["v_replay"]["start"]
T_S3 = C["v_s3"]["start"]
T_ASK, T_ANS, T_ANS_END = o("v_s3", 19.36), o("v_s3", 20.44), o("v_s3", 21.12)
T_S4 = C["v_s4"]["start"]
T_LOOK = o("v_s4", 23.84)
T_CTA = round(T_S4 + 0.55, 3)

# ---------------------------------------------------------------- SFX  (file, out_time, volume)
SFX = [
    ("impact", 0.00, 0.85), ("pop", 0.26, 0.45), ("pop", 0.52, 0.45), ("riser", 0.22, 0.40),
    ("whoosh", T_HOOK_END - 0.18, 0.75),
    ("ding1", T_MODE_A[0], 0.5), ("ding2", T_MODE_A[1], 0.5), ("ding3", T_MODE_A[2], 0.55),
    ("whoosh_down", 4.55, 0.35),
    ("glitch", T_WALL_IN, 0.45), ("shutter", T_WALL_IN + 0.05, 0.6),
    ("tick", 6.78, 0.5), ("tick", 6.88, 0.5), ("tick", 6.98, 0.5), ("tick", 7.08, 0.5),
    ("whoosh", 7.28, 0.6),
    ("impact", T_HWALL, 0.6), ("metal_ting", T_HWALL + 0.02, 0.55),
    ("whoosh_small", T_S2 - 0.12, 0.6),
    ("ding1", T_MODE_B[0], 0.5), ("ding2", T_MODE_B[1], 0.5), ("ding3", T_MODE_B[2], 0.55),
    ("pop", T_MIST + 0.05, 0.5),
    ("pop", T_FAHAM, 0.35),
    ("rewind", T_REPLAY - 0.12, 0.6),
    ("whoosh_small", T_S3 - 0.1, 0.5),
    ("pop", T_ASK, 0.5), ("ding3", T_ANS, 0.5),
    ("whoosh", T_S4 - 0.2, 0.55),
    ("whoosh_small", T_LOOK - 0.05, 0.4),
    ("pop", T_CTA, 0.45), ("pop", T_CTA + 0.25, 0.45),
    ("whoosh_down", DUR - 1.0, 0.35),
    ("whoosh", DUR - 0.45, 0.6),
]
SFX_LEN = {"impact": 1.4, "pop": 0.16, "riser": 1.6, "whoosh": 0.55, "whoosh_small": 0.28, "whoosh_down": 0.5,
           "ding1": 1.2, "ding2": 1.2, "ding3": 1.2, "glitch": 0.45, "shutter": 0.22, "tick": 0.05,
           "metal_ting": 1.8, "rewind": 0.7}

# ---------------------------------------------------------------- CAMERA (digital zoom on #cam)
# segments: (cut_time, origin, [(t, dur, scale, ease)...], start_scale)
CAM = [
    (0.0, "45% 52%", 1.38, [(0.0, 0.35, 1.12, "power3.out"), (o("v_hook", 13.50), 0.14, 1.32, "power4.out"),
                            (1.0, 0.8, 1.40, "sine.inOut")]),
    (T_HOOK_END, "60% 45%", 1.0, [(T_MODE_A[0], 0.12, 1.08, "power4.out"), (T_MODE_A[1], 0.12, 1.16, "power4.out"),
                                  (T_MODE_A[2], 0.12, 1.26, "power4.out"), (4.45, 1.6, 1.0, "power2.inOut")]),
    (T_WALL_OUT - 0.05, "50% 50%", 1.0, [(8.04, 1.0, 1.10, "sine.inOut"), (T_HWALL, 0.9, 1.18, "power1.out")]),
    (T_S2, "46% 36%", 1.0, [(T_MODE_B[0], 0.12, 1.08, "power4.out"), (T_MODE_B[1], 0.12, 1.16, "power4.out"),
                            (T_MODE_B[2], 0.12, 1.26, "power4.out"), (T_MIST - 0.05, 0.45, 1.0, "power3.inOut"),
                            (T_MIST + 0.6, T_REPLAY - T_MIST - 0.6, 1.07, "none")]),
    (T_REPLAY, "43% 58%", 1.18, [(T_REPLAY, T_S3 - T_REPLAY, 1.30, "none")]),
    (T_S3, "50% 50%", 1.0, [(T_S3, T_S4 - T_S3, 1.05, "none")]),
    (T_S4, "55% 42%", 1.0, [(T_LOOK, 0.35, 1.30, "power3.out"), (o("v_s4", 24.62), 0.5, 1.0, "power2.inOut"),
                            (DUR - 0.45, 0.45, 1.45, "power3.in")]),
]

# ================================================================= HTML
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")

videos = []
for c in CLIPS:
    a = (f'data-has-audio="true" data-volume="1" data-fade-in="0.03" data-fade-out="0.04"' if c["audio"] else "muted")
    rate = f' data-playback-rate="{c["rate"]}"' if c["rate"] != 1 else ""
    videos.append(
        f'      <!-- {esc(c["note"])} | src {c["src"]:.2f}-{c["src_out"]:.2f} -->\n'
        f'      <video id="{c["id"]}" class="clip vid" src="{FOOT}" playsinline {a}{rate} '
        f'data-start="{c["start"]}" data-duration="{c["dur"]}" data-media-start="{c["src"]}" data-track-index="0"></video>')

caps_html = []
for i, g in enumerate(CAPTIONS):
    st = g["words"][0][1]
    spans = " ".join(f'<span class="w{" k" if k else ""}">{esc(w)}</span>' for w, _, k in g["words"])
    caps_html.append(f'    <div id="cap{i}" class="clip cap" data-start="{st}" data-duration="{round(g["end"] - st, 3)}" data-track-index="3">{spans}</div>')

sfx_html = []
for i, (f, at, vol) in enumerate(SFX):
    at = max(0.0, round(at, 3))
    d = round(min(SFX_LEN[f], DUR - at), 3)
    sfx_html.append(f'    <audio id="sfx{i}" src="assets/sfx/{f}.wav" data-start="{at}" data-duration="{d}" data-volume="{vol}" data-track-index="{6 + i % 5}"></audio>')

# clone wall tiles 3x3 (360x640 each), checker silver/metal; centre tile ends METAL
tiles = []
for r in range(3):
    for col in range(3):
        idx = r * 3 + col
        first = "silver" if (r + col) % 2 == 0 else "metal"
        second = "metal" if first == "silver" else "silver"
        if idx == 4:
            first, second = "silver", "metal"
        img = {"silver": "assets/img/still_5.0.jpg", "metal": "assets/img/still_12.0.jpg"}
        tiles.append(
            f'      <div class="tile" data-i="{idx}" style="left:{col*360}px;top:{r*640}px">'
            f'<img class="ta" src="{img[first]}" alt=""><img class="tb" src="{img[second]}" alt="">'
            f'<span class="tl tla">{first.upper()}</span><span class="tl tlb">{second.upper()}</span></div>')

hwall_rows = []
for r in range(11):
    cls = "hrow solid" if r == 5 else ("hrow outline" if r % 2 else "hrow dim")
    hwall_rows.append(f'      <div class="{cls}" data-r="{r}">WARNA METAL &#8226; WARNA METAL &#8226; WARNA METAL</div>')

orbit_items = []
labels = ["MOD 1", "&#9679;", "MOD 2", "&#9679;", "MOD 3", "&#9679;"] * 2
for i, lab in enumerate(labels):
    ang = i * 360 / len(labels)
    orbit_items.append(f'        <div class="oi" style="transform: rotateY({ang:.1f}deg) translateZ(310px)">{lab}</div>')

CAM_JS = json.dumps(CAM)
CAP_JS = json.dumps([[w[1] for w in g["words"]] for g in CAPTIONS])
BEATS = dict(DUR=DUR, HOOK_END=T_HOOK_END, MODE_A=T_MODE_A, WALL_IN=T_WALL_IN, WALL_OUT=T_WALL_OUT, HWALL=T_HWALL,
             FAHAM=T_FAHAM, S2=T_S2, MODE_B=T_MODE_B, MIST=T_MIST, REPLAY=T_REPLAY, S3=T_S3, ASK=T_ASK, ANS=T_ANS,
             ANS_END=T_ANS_END, S4=T_S4, LOOK=T_LOOK, CTA=T_CTA)

def span(a, b): return f'data-start="{round(a,3)}" data-duration="{round(b-a,3)}"'

html = f"""<!doctype html>
<!-- GENERATED by tools/build.py — edit the tables there, then re-run. -->
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; }}
      @font-face {{ font-family: "Montserrat"; src: url("assets/fonts/Montserrat.ttf") format("truetype"); font-weight: 100 900; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      body {{ font-family: "Montserrat", sans-serif; color: #fff; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; isolation: isolate; background: #000; }}
      .layer {{ position: absolute; inset: 0; }}
      #shake, #cam {{ position: absolute; inset: 0; will-change: transform; }}
      #cam {{ filter: contrast(1.07) saturate(1.12) brightness(1.02); }}
      .vid {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .vignette {{ position: absolute; inset: 0; pointer-events: none;
        background: radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.38) 100%); z-index: 5; }}

      /* ---------- hook headline ---------- */
      #hookShade {{ position: absolute; left: 0; right: 0; top: 0; height: 900px; z-index: 8;
        background: linear-gradient(180deg, rgba(0,0,0,.78) 0%, rgba(0,0,0,.45) 60%, rgba(0,0,0,0) 100%); }}
      #hook {{ position: absolute; left: 0; right: 0; top: 230px; z-index: 9; text-align: center; font-family: "Anton"; line-height: .98; }}
      #hook .hl {{ display: block; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 8px 0 rgba(0,0,0,.35), 0 0 40px rgba(0,0,0,.5); }}
      #hook .l1 {{ font-size: 150px; color: #fff; }}
      #hook .l2 {{ font-size: 178px; color: #FFD400; }}
      #hook .l3 {{ font-size: 104px; color: #fff; margin-top: 10px; }}
      #hook .l3 b {{ background: #E8262B; padding: 0 22px; border-radius: 14px; display: inline-block; }}

      /* ---------- captions ---------- */
      .cap {{ position: absolute; left: 60px; right: 60px; top: 1250px; z-index: 20; text-align: center;
        font-weight: 900; font-size: 84px; line-height: 1.1; text-transform: uppercase; letter-spacing: -1px; }}
      .cap .w {{ display: inline-block; margin: 0 8px; color: #fff; -webkit-text-stroke: 14px #000; paint-order: stroke fill;
        text-shadow: 0 10px 18px rgba(0,0,0,.45); }}
      .cap .w.k {{ color: #FFD400; }}

      /* ---------- mode badges ---------- */
      #badges {{ position: absolute; left: 0; right: 0; top: 300px; height: 300px; z-index: 12; }}
      #badges .ttl {{ position: absolute; left: 0; right: 0; top: 0; text-align: center; font-weight: 900; font-size: 54px; letter-spacing: 6px;
        -webkit-text-stroke: 10px #000; paint-order: stroke fill; }}
      #badges .b {{ position: absolute; top: 95px; width: 170px; height: 170px; margin-left: -85px; border-radius: 50%;
        background: #FFD400; color: #111; font-family: "Anton"; font-size: 120px; line-height: 170px; text-align: center;
        box-shadow: 0 14px 30px rgba(0,0,0,.45), inset 0 -10px 0 rgba(0,0,0,.12); border: 8px solid #fff; }}

      /* ---------- clone wall ---------- */
      #wall {{ position: absolute; inset: 0; z-index: 10; background: #000; perspective: 1400px; }}
      #wallInner {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      .tile {{ position: absolute; width: 360px; height: 640px; overflow: hidden; border: 6px solid #000; border-radius: 22px; }}
      .tile img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .tile .tb {{ opacity: 0; }}
      .tile .tl {{ position: absolute; left: 50%; bottom: 34px; transform: translateX(-50%); font-weight: 900; font-size: 40px; letter-spacing: 4px;
        padding: 6px 20px; border-radius: 40px; background: rgba(0,0,0,.72); white-space: nowrap; }}
      .tile .tlb {{ opacity: 0; }}

      /* ---------- headline wall ---------- */
      #hwall {{ position: absolute; inset: 0; z-index: 11; background: rgba(6,8,12,.62); overflow: hidden; }}
      .hrow {{ position: absolute; left: 50%; white-space: nowrap; font-family: "Anton"; font-size: 178px; line-height: 1; letter-spacing: 2px; }}
      .hrow.outline {{ color: transparent; -webkit-text-stroke: 3px rgba(255,255,255,.85); }}
      .hrow.dim {{ color: rgba(255,255,255,.14); }}
      .hrow.solid {{ background: linear-gradient(180deg, #ffffff 0%, #c9d0d8 38%, #6d7783 52%, #e9eef3 70%, #8f98a3 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 10px 22px rgba(0,0,0,.8)); }}

      /* ---------- orbit ---------- */
      #orbit {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 13; perspective: 1100px; perspective-origin: 497px 690px; }}
      #orbitPos {{ position: absolute; left: 497px; top: 690px; width: 0; height: 0; transform-style: preserve-3d; }}
      #ring {{ position: absolute; left: 0; top: 0; width: 0; height: 0; transform-style: preserve-3d; }}
      .oi {{ position: absolute; left: -110px; top: -40px; width: 220px; height: 80px; text-align: center; line-height: 80px;
        font-weight: 900; font-size: 50px; color: #FFD400; -webkit-text-stroke: 9px #000; paint-order: stroke fill; backface-visibility: hidden; }}
      #orbitTitle {{ position: absolute; left: 0; right: 0; top: 250px; text-align: center; z-index: 13; font-family: "Anton"; font-size: 120px;
        color: #fff; text-shadow: 0 8px 0 rgba(0,0,0,.4); }}
      #orbitTitle span {{ color: #FFD400; }}

      /* ---------- mist callout ---------- */
      #callout {{ position: absolute; left: 0; top: 0; z-index: 14; }}
      #callout .pill {{ position: absolute; left: 560px; top: 780px; padding: 18px 30px; border-radius: 26px; background: #fff; color: #111;
        font-weight: 900; font-size: 46px; line-height: 1.05; box-shadow: 0 14px 30px rgba(0,0,0,.45); white-space: nowrap; }}
      #callout .pill small {{ display: block; font-size: 30px; font-weight: 800; color: #E8262B; letter-spacing: 3px; }}
      #callout svg {{ position: absolute; left: 430px; top: 880px; overflow: visible; }}

      /* ---------- replay ---------- */
      #replay {{ position: absolute; inset: 0; z-index: 15; }}
      #replay .frame {{ position: absolute; inset: 34px; border: 6px solid rgba(255,255,255,.9); border-radius: 40px; }}
      #replay .tag {{ position: absolute; left: 80px; top: 120px; padding: 12px 28px 12px 64px; background: #E8262B; border-radius: 16px;
        font-weight: 900; font-size: 50px; letter-spacing: 4px; }}
      #replay .tag i {{ position: absolute; left: 24px; top: 50%; width: 24px; height: 24px; margin-top: -12px; border-radius: 50%; background: #fff; }}
      #replay .spd {{ position: absolute; right: 80px; top: 126px; font-weight: 900; font-size: 46px; letter-spacing: 2px;
        -webkit-text-stroke: 8px #000; paint-order: stroke fill; }}
      #replay .lines {{ position: absolute; inset: 0; opacity: .16;
        background: repeating-linear-gradient(0deg, rgba(255,255,255,.5) 0 2px, rgba(0,0,0,0) 2px 7px); }}
      #replay .rcap {{ position: absolute; left: 0; right: 0; top: 1250px; text-align: center; font-weight: 900; font-size: 74px;
        color: #FFD400; -webkit-text-stroke: 12px #000; paint-order: stroke fill; }}

      /* ---------- question / answer ---------- */
      #ask {{ position: absolute; left: 0; right: 0; top: 1180px; z-index: 21; text-align: center; }}
      #ask .bub {{ display: inline-block; position: relative; padding: 30px 50px; background: #fff; color: #111; border-radius: 48px;
        font-weight: 900; font-size: 78px; box-shadow: 0 16px 34px rgba(0,0,0,.45); }}
      #ask .bub:after {{ content: ""; position: absolute; left: 90px; bottom: -34px; border: 22px solid transparent;
        border-top: 26px solid #fff; border-left: 26px solid #fff; }}
      #ask .bub .w {{ display: inline-block; margin: 0 6px; }}
      #ans {{ position: absolute; left: 0; right: 0; top: 1190px; z-index: 21; text-align: center; }}
      #ans .stamp {{ display: inline-block; padding: 16px 54px; border: 10px solid #22C55E; border-radius: 30px; color: #22C55E;
        background: rgba(0,0,0,.55); font-family: "Anton"; font-size: 120px; letter-spacing: 3px; transform: rotate(-7deg); }}

      /* ---------- CTA ---------- */
      #cta {{ position: absolute; left: 0; right: 0; top: 210px; z-index: 22; text-align: center; }}
      #cta .vs {{ display: flex; justify-content: center; align-items: center; gap: 26px; }}
      #cta .chip {{ font-family: "Anton"; font-size: 104px; padding: 6px 38px; border-radius: 26px; letter-spacing: 2px; box-shadow: 0 14px 30px rgba(0,0,0,.45); }}
      #cta .silver {{ background: linear-gradient(180deg,#ffffff,#c7ced6 55%,#9aa3ad); color: #1b1f24; }}
      #cta .metal {{ background: linear-gradient(180deg,#5d6670,#2b3036 60%,#1a1d21); color: #fff; }}
      #cta .or {{ font-weight: 900; font-size: 58px; -webkit-text-stroke: 10px #000; paint-order: stroke fill; }}
      #cta .ask2 {{ margin-top: 26px; font-weight: 900; font-size: 62px; -webkit-text-stroke: 11px #000; paint-order: stroke fill; }}
      #cta .ask2 b {{ color: #FFD400; }}

      /* ---------- misc ---------- */
      #flash {{ position: absolute; inset: 0; z-index: 40; background: #fff; opacity: 0; pointer-events: none; }}
      #progress {{ position: absolute; left: 0; top: 0; height: 12px; width: 100%; z-index: 41; background: #FFD400; transform-origin: 0 50%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}" data-fps="30">
      <div id="shake"><div id="cam">
{chr(10).join(videos)}
      </div></div>
      <div class="vignette"></div>

      <!-- HOOK: headline slam -->
      <div id="hookShade" class="clip" {span(0, T_HOOK_END)} data-track-index="1"></div>
      <div id="hook" class="clip" {span(0, T_HOOK_END)} data-track-index="1">
        <span class="hl l1">Jangan beli</span>
        <span class="hl l2">sinki dapur</span>
        <span class="hl l3"><b>sebelum tengok ni!</b></span>
      </div>

      <!-- MOD AIR badges (digital zoom beats) -->
      <div id="badges" class="clip" {span(T_MODE_A[0] - 0.05, 4.9)} data-track-index="2">
        <div class="ttl">MOD AIR</div>
        <div class="b" id="b1" style="left:310px">1</div>
        <div class="b" id="b2" style="left:540px">2</div>
        <div class="b" id="b3" style="left:770px">3</div>
      </div>

      <!-- CLONE WALL transition: silver <-> metal -->
      <div id="wall" class="clip" {span(T_WALL_IN, T_WALL_OUT)} data-track-index="2">
        <div id="wallInner">
{chr(10).join(tiles)}
        </div>
      </div>

      <!-- HEADLINE WALL: WARNA METAL -->
      <div id="hwall" class="clip" {span(T_HWALL, T_S2)} data-track-index="2">
{chr(10).join(hwall_rows)}
      </div>

      <!-- ORBIT: 3 mod air orbit the spray head -->
      <div id="orbitTitle" class="clip" {span(T_S2 + 0.05, T_MIST)} data-track-index="2"><span>3</span> MOD AIR</div>
      <div id="orbit" class="clip" {span(T_S2 + 0.05, T_MIST)} data-track-index="2">
        <div id="orbitPos"><div id="ring">
{chr(10).join(orbit_items)}
        </div></div>
      </div>

      <!-- MIST callout -->
      <div id="callout" class="clip" {span(T_MIST + 0.05, T_FAHAM)} data-track-index="2">
        <div class="pill"><small>MOD 2</small>SEMBURAN HALUS</div>
        <svg width="200" height="220" viewBox="0 0 200 220"><path id="arrowPath" d="M150 10 C 150 120, 90 170, 20 200" fill="none"
          stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/>
          <path id="arrowHead" d="M20 200 L 62 196 M20 200 L 40 164" stroke="#fff" stroke-width="12" stroke-linecap="round" fill="none" opacity="0"/></svg>
      </div>

      <!-- REPLAY (fills the awkward pause) -->
      <div id="replay" class="clip" {span(T_REPLAY, T_S3)} data-track-index="2">
        <div class="lines"></div><div class="frame"></div>
        <div class="tag"><i></i>REPLAY</div><div class="spd">0.6x SLOW-MO</div>
        <div class="rcap">TENGOK SEMBURAN DIA</div>
      </div>

      <!-- ASK + ANSWER -->
      <div id="ask" class="clip" {span(T_ASK, T_ANS)} data-track-index="3"><div class="bub">
        <span class="w">Ada</span><span class="w">warna</span><span class="w">ni</span><span class="w">tak?</span></div></div>
      <div id="ans" class="clip" {span(T_ANS, T_ANS_END + 0.4)} data-track-index="3"><div class="stamp">ADA! &#10003;</div></div>

      <!-- CTA + loop-out -->
      <div id="cta" class="clip" {span(T_CTA, DUR)} data-track-index="2">
        <div class="vs"><div class="chip silver">SILVER</div><div class="or">ATAU</div><div class="chip metal">METAL</div></div>
        <div class="ask2">Korang pilih yang mana? <b>KOMEN!</b></div>
      </div>

      <!-- captions -->
{chr(10).join(caps_html)}

      <div id="flash" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <div id="progress" class="clip" {span(0, DUR)} data-track-index="4"></div>

      <!-- music + sfx -->
      <audio id="music" src="assets/sfx/music.wav" data-start="0" data-duration="{DUR}" data-volume="0.13" data-fade-in="0.2" data-fade-out="0.4" data-track-index="5"></audio>
{chr(10).join(sfx_html)}
    </div>

    <script>
      const B = {json.dumps(BEATS)};
      const CAM = {CAM_JS};
      const CAPW = {CAP_JS};
      const tl = gsap.timeline({{ paused: true }});
      const q = (s) => document.querySelector(s);
      const qa = (s) => Array.from(document.querySelectorAll(s));

      // ---------- digital zoom camera ----------
      for (const [cut, origin, s0, keys] of CAM) {{
        tl.set("#cam", {{ scale: s0, transformOrigin: origin }}, cut);
        let prev = s0;
        for (const [t, d, s, ease] of keys) {{
          tl.fromTo("#cam", {{ scale: prev }}, {{ scale: s, duration: d, ease, immediateRender: false }}, t);
          prev = s;
        }}
      }}
      // handheld shake on impacts
      function shake(at, amp, len) {{
        const n = Math.round(len / 0.033);
        for (let i = 0; i < n; i++) {{
          const k = 1 - i / n, sx = ((i * 37) % 7 - 3) / 3, sy = ((i * 53) % 5 - 2) / 2;
          tl.set("#shake", {{ x: sx * amp * k, y: sy * amp * k, rotation: sx * 0.25 * k }}, at + i * 0.033);
        }}
        tl.set("#shake", {{ x: 0, y: 0, rotation: 0 }}, at + n * 0.033);
      }}
      shake(0.0, 18, 0.3); shake(B.HWALL, 14, 0.3); shake(B.ANS, 8, 0.2);

      // ---------- flashes ----------
      tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.22, ease: "power2.out" }}, 0);
      for (const at of [B.HOOK_END, B.HWALL, B.S2, B.S4]) tl.fromTo("#flash", {{ opacity: 0.7 }}, {{ opacity: 0, duration: 0.2, ease: "power2.out", immediateRender: false }}, at);
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.3, ease: "power2.in", immediateRender: false }}, B.DUR - 0.3);   // loop seam: ends white like it starts
      tl.fromTo("#progress", {{ scaleX: 0 }}, {{ scaleX: 1, duration: B.DUR, ease: "none" }}, 0);

      // ---------- hook headline ----------
      [".l1", ".l2", ".l3"].forEach((s, i) => {{
        tl.fromTo("#hook " + s, {{ scale: i ? 2.4 : 1.6, opacity: 0, rotation: i % 2 ? 4 : -4 }},
          {{ scale: 1, opacity: 1, rotation: 0, duration: i ? 0.22 : 0.16, ease: "back.out(2.2)" }}, i ? 0.26 * i : 0);
      }});
      tl.to("#hook .l2", {{ scale: 1.06, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 0.62);
      tl.to("#hook", {{ y: -80, opacity: 0, scale: 1.15, duration: 0.2, ease: "power2.in" }}, B.HOOK_END - 0.2);
      tl.to("#hookShade", {{ opacity: 0, duration: 0.2 }}, B.HOOK_END - 0.2);

      // ---------- badges ----------
      tl.fromTo("#badges .ttl", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.2 }}, B.MODE_A[0] - 0.05);
      ["#b1", "#b2", "#b3"].forEach((s, i) => {{
        tl.fromTo(s, {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 0, duration: 0.25, ease: "back.out(3)" }}, B.MODE_A[i]);
      }});
      tl.to("#badges", {{ opacity: 0, y: -40, duration: 0.25 }}, 4.62);

      // ---------- clone wall ----------
      const tiles = qa(".tile");
      const order = [4, 1, 3, 5, 7, 0, 2, 6, 8];
      order.forEach((idx, n) => {{
        tl.fromTo(tiles[idx], {{ scale: 0.2, opacity: 0, rotation: (idx % 2 ? 6 : -6) }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.18, ease: "back.out(2)" }}, B.WALL_IN + n * 0.025);
      }});
      // flip tiles silver <-> metal (checker), centre last
      order.forEach((idx, n) => {{
        const at = 6.74 + n * 0.04;
        const tile = tiles[idx];
        tl.to(tile, {{ scaleX: 0, duration: 0.06, ease: "power1.in" }}, at);
        tl.set(tile.querySelectorAll(".tb, .tlb"), {{ opacity: 1 }}, at + 0.06);
        tl.set(tile.querySelectorAll(".ta, .tla"), {{ opacity: 0 }}, at + 0.06);
        tl.to(tile, {{ scaleX: 1, duration: 0.07, ease: "power1.out" }}, at + 0.06);
      }});
      tl.fromTo("#wallInner", {{ scale: 1 }}, {{ scale: 3.05, duration: 0.32, ease: "power3.in", immediateRender: false }}, B.WALL_OUT - 0.34);
      tl.to("#wall", {{ opacity: 0, duration: 0.08 }}, B.WALL_OUT - 0.08);

      // ---------- headline wall ----------
      qa(".hrow").forEach((row, r) => {{
        const y = -60 + r * 190;
        const dir = r % 2 ? 1 : -1;
        tl.set(row, {{ y, xPercent: -50 }}, B.HWALL);
        tl.fromTo(row, {{ x: dir * 700, opacity: 0 }}, {{ x: dir * -60, opacity: 1, duration: 0.25 + Math.abs(r - 5) * 0.02, ease: "power3.out" }}, B.HWALL + Math.abs(r - 5) * 0.03);
        tl.to(row, {{ x: dir * -170, duration: 0.6, ease: "none" }}, B.HWALL + 0.3);
      }});
      tl.fromTo(".hrow.solid", {{ scale: 1.6 }}, {{ scale: 1.08, duration: 0.22, ease: "back.out(2)", immediateRender: false }}, B.HWALL);
      tl.to("#hwall", {{ opacity: 0, scale: 1.25, duration: 0.14, ease: "power2.in" }}, B.S2 - 0.14);

      // ---------- orbit ----------
      tl.fromTo("#ring", {{ rotationX: -14, rotationY: 0 }}, {{ rotationX: -14, rotationY: -400, duration: B.MIST - B.S2, ease: "power1.inOut" }}, B.S2);
      tl.fromTo("#orbitPos", {{ scale: 0.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }}, B.S2 + 0.05);
      tl.to("#orbitPos", {{ scale: 1.6, opacity: 0, duration: 0.2, ease: "power2.in" }}, B.MIST - 0.2);
      tl.fromTo("#orbitTitle", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25, ease: "power3.out" }}, B.S2 + 0.05);
      B.MODE_B.forEach((t) => tl.fromTo("#orbitTitle span", {{ scale: 1.6 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, t));
      tl.to("#orbitTitle", {{ opacity: 0, y: -40, duration: 0.2 }}, B.MIST - 0.2);

      // ---------- mist callout ----------
      tl.fromTo("#callout .pill", {{ x: 200, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }}, B.MIST + 0.05);
      tl.fromTo("#arrowPath", {{ attr: {{ "stroke-dashoffset": 320 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 0.35, ease: "power2.out" }}, B.MIST + 0.25);
      tl.fromTo("#arrowHead", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.05 }}, B.MIST + 0.58);
      tl.to("#callout", {{ opacity: 0, duration: 0.2 }}, B.FAHAM - 0.2);

      // ---------- replay ----------
      tl.fromTo("#replay", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12 }}, B.REPLAY);
      for (let i = 0; i < 4; i++) tl.fromTo("#replay .tag i", {{ opacity: 1 }}, {{ opacity: 0.15, duration: 0.15, immediateRender: false }}, B.REPLAY + i * 0.33 + 0.15);
      tl.fromTo("#replay .rcap", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }}, B.REPLAY + 0.25);

      // ---------- captions: pop group, reveal words on their timestamps ----------
      qa(".cap").forEach((cap, gi) => {{
        const words = cap.querySelectorAll(".w");
        const t0 = CAPW[gi][0];
        tl.fromTo(cap, {{ scale: 0.8 }}, {{ scale: 1, duration: 0.16, ease: "back.out(2.5)" }}, t0);
        words.forEach((w, wi) => {{
          tl.fromTo(w, {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.1, ease: "power2.out" }}, CAPW[gi][wi]);
          if (w.classList.contains("k")) tl.fromTo(w, {{ scale: 1.35 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)", immediateRender: false }}, CAPW[gi][wi]);
        }});
      }});

      // ---------- ask / answer ----------
      tl.fromTo("#ask .bub", {{ scale: 0, rotation: -6 }}, {{ scale: 1, rotation: 0, duration: 0.25, ease: "back.out(2.4)" }}, B.ASK);
      qa("#ask .w").forEach((w, i) => tl.fromTo(w, {{ opacity: 0.15 }}, {{ opacity: 1, duration: 0.08 }}, B.ASK + [0, 0.1, 0.64, 0.92][i]));
      tl.fromTo("#ans .stamp", {{ scale: 2.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "power4.in" }}, B.ANS);

      // ---------- CTA ----------
      tl.fromTo("#cta .silver", {{ x: -500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }}, B.CTA);
      tl.fromTo("#cta .metal", {{ x: 500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "back.out(1.6)" }}, B.CTA + 0.25);
      tl.fromTo("#cta .or", {{ scale: 0 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)" }}, B.CTA + 0.4);
      tl.fromTo("#cta .ask2", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25 }}, B.CTA + 0.5);

      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(html)

# human-readable edit plan
lines = [f"DURATION {DUR}s", "", "EDL (output -> source):"]
for c in CLIPS:
    lines.append(f"  {c['start']:6.2f}-{c['start']+c['dur']:6.2f}  src {c['src']:5.2f}-{c['src_out']:5.2f}  x{c['rate']}  {c['note']}")
lines += ["", "BEATS:"] + [f"  {k:9s} {v}" for k, v in BEATS.items()]
(ROOT.parent / "EDIT_PLAN.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
