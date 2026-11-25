"""Generate waiver/index.html (HyperFrames) for the CI Protection / Waiver talking-head video.

Edit the tables (EDL, CAM, SFX, beats) and re-run:  python3 tools/build.py
Times are OUTPUT seconds unless marked src.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE / "waiver"
W, H = 1080, 1920
SPEED = 1.15   # suara dilajukan (pitch kekal) - footage_fast.mp4 dibuat dengan setpts/atempo
FOOT = "assets/footage_fast.mp4"
WORDS = [w for s in json.loads((HERE / "transcript_raw.json").read_text()) for w in s["words"]]
FIX = {"Cik": "Cek", "Mas": "Maz"}   # betul ejaan nama
for _w in WORDS:
    _t = _w["w"].strip()
    if _t in FIX: _w["w"] = " " + FIX[_t]
    _w["s"] /= SPEED; _w["e"] /= SPEED

# ---------------------------------------------------------------- EDL (awkward pauses removed)
# (id, src_in, src_out, note)
EDL = [
    ("H1", 15.20, 16.56, "HOOK a: 'Contoh anda kena cancer.'"),
    ("H2", 22.08, 23.88, "HOOK b: 'tapi anda tak perlu bayar apa-apa.'"),
    ("M1", 0.42, 3.24, "Hai Assalamualaikum semua. Ok hari ni saya nak bercakap"),
    ("M2", 3.48, 8.72, "tentang CI Protection. Untuk CI Protection ni kita ada dua jenis. Yang pertama waiver."),
    ("M3", 9.02, 13.58, "Waiver ni maksudnya pengecualian bayaran sekiranya berlaku sakit kritikal"),
    ("M4", 13.82, 16.92, "kepada orang yang dilindungi. Contoh anda kena cancer."),
    ("M5", 17.20, 20.12, "So boleh apply untuk pengecualian bayaran sijil."),
    ("M6", 20.28, 24.02, "Dan sijil tetap diteruskan tapi anda tak perlu bayar apa-apa."),
    ("M7", 24.40, 27.80, "Ok yang kedua pula adalah pampasan sakit kritikal."),
    ("M8", 28.04, 36.58, "So sekiranya berlaku salah satu penyakit kritikal yang dilindungi. Anda boleh dapat duit pampasan. Ikutlah berapa sum cover yang anda nak."),
    ("M9", 37.00, 41.70, "Dan kalau nak tahu lebih detail boleh refer saya Cek Maz AIA Johor Bahru."),
    ("M10", 41.88, 44.26, "Untuk saya brief lebih detail tentang"),
    ("M11", 44.48, 46.70, "critical illness protection. Ok."),
]
CLIPS, t = [], 0.0
for cid, a, b, note in EDL:
    a, b = a / SPEED, b / SPEED
    CLIPS.append(dict(id=cid, start=round(t, 3), dur=round(b - a, 3), src=round(a, 3), src_out=round(b, 3), note=note))
    t = CLIPS[-1]["start"] + CLIPS[-1]["dur"]
DUR = round(t, 3)
C = {c["id"]: c for c in CLIPS}
def o(cid, s):
    """map ORIGINAL-source seconds inside clip cid to output time"""
    s = s / SPEED
    c = C[cid]
    return round(c["start"] + max(0.0, min(s, c["src_out"]) - c["src"]), 3)

# ---------------------------------------------------------------- CAPTIONS (auto-grouped from whisper words)
KEY = {"ci", "protection", "waiver", "pengecualian", "bayaran", "sakit", "kritikal", "cancer", "sijil", "diteruskan",
       "tak", "perlu", "bayar", "apa-apa", "pampasan", "duit", "sum", "cover", "penyakit", "dilindungi", "dua",
       "pertama", "kedua", "detail", "critical", "illness", "cek", "maz"}
MAIN = [c for c in CLIPS if not c["id"].startswith("H")]
def owner(w):
    mid = (w["s"] + w["e"]) / 2
    for c in MAIN:
        if c["src"] <= mid < c["src_out"]:
            return c["id"]
    later = [c for c in MAIN if c["src"] > mid]
    return later[0]["id"] if later else None
def words_in(c):
    out = []
    for w in WORDS:
        txt = w["w"].strip()
        if not txt:
            continue
        if txt.startswith("-") and out and owner(w) == c["id"]:
            out[-1] = (out[-1][0] + txt, out[-1][1]); continue
        if owner(w) == c["id"]:
            out.append((txt, min(max(w["s"], c["src"]), c["src_out"] - 0.1)))
    return out
BIND = {("ci", "protection"), ("cek", "maz"), ("johor", "bahru"), ("sum", "cover"), ("sakit", "kritikal"),
        ("penyakit", "kritikal"), ("critical", "illness"), ("tak", "perlu"), ("perlu", "bayar"), ("duit", "pampasan"),
        ("salah", "satu"), ("maz", "aia"), ("aia", "johor"), ("pengecualian", "bayaran")}
def _c(w): return re.sub(r"[.,?!]", "", w).lower()
CAPTIONS = []
for c in CLIPS:
    if c["id"].startswith("H"):
        continue
    ws = words_in(c)
    grp = []
    for i, (txt, s) in enumerate(ws):
        grp.append((txt, o(c["id"], s * SPEED)))   # s is already sped-up time
        nxt = ws[i + 1][0] if i + 1 < len(ws) else None
        bound = nxt is not None and (_c(txt), _c(nxt)) in BIND and txt[-1] not in ".,?!"
        if (len(grp) >= 3 and not bound) or len(grp) >= 5 or txt[-1] in ".,?!" or nxt is None:
            CAPTIONS.append(grp); grp = []
# merge too-short groups (< 0.4s) forward into the next group when it is in the same clip
def clip_of(t):
    return next(c for c in CLIPS if c["start"] <= t < c["start"] + c["dur"] + 1e-6)
merged = []
i = 0
while i < len(CAPTIONS):
    g = CAPTIONS[i]
    if i + 1 < len(CAPTIONS):
        n = CAPTIONS[i + 1]
        if n[0][1] - g[0][1] < 0.4 and clip_of(g[0][1]) is clip_of(n[0][1]) and len(g) + len(n) <= 5:
            CAPTIONS[i + 1] = g + n; i += 1; continue
        if n[0][1] - g[0][1] < 0.4 and len(n) + len(g) <= 5:
            CAPTIONS[i + 1] = [(w, n[0][1]) for w, _ in g] + n; i += 1; continue
    merged.append(g); i += 1
CAPTIONS = merged
CAPS = []
for i, g in enumerate(CAPTIONS):
    nxt = CAPTIONS[i + 1][0][1] if i + 1 < len(CAPTIONS) else DUR
    CAPS.append(dict(words=g, start=g[0][1], end=round(nxt, 3)))

def clean(w): return re.sub(r"[.,?!]", "", w).lower()

# ---------------------------------------------------------------- BEATS (output time)
B = dict(
    DUR=DUR,
    H2=C["H2"]["start"], CANCER_H=o("H1", 16.10), BAYAR_H=o("H2", 23.12), MAIN=C["M1"]["start"],
    HWALL=o("M2", 3.56), HWALL_END=o("M2", 4.75),
    DUA=o("M2", 6.70), PERTAMA=o("M2", 7.52), M3=C["M3"]["start"], DEF=o("M3", 9.84),
    CANCER=o("M4", 16.10), M5=C["M5"]["start"], CHK1=o("M5", 18.50), CHK2=o("M6", 21.64), CHK3=o("M6", 22.72),
    RM0=o("M6", 23.12), M7=C["M7"]["start"], WALL_OUT=o("M7", 25.66), SEC2=o("M7", 26.00),
    ORBIT=o("M8", 29.42), ORBIT_END=o("M8", 31.96), DUIT=o("M8", 33.06), SUM=o("M8", 34.22),
    M9=C["M9"]["start"], NAME=o("M9", 39.00), M10=C["M10"]["start"], END_OK=o("M11", 45.92),
)
FACE = "54% 44%"   # digital-zoom origin on her face

# ---------------------------------------------------------------- CAMERA (digital zoom)  (cut, origin, start_scale, [(t,dur,scale,ease)])
def seg(cid, s0, keys=()):
    return (C[cid]["start"], FACE, s0, list(keys))
CAM = [
    seg("H1", 1.05, [(B["CANCER_H"], 0.12, 1.24, "power4.out")]),
    seg("H2", 1.16, [(B["H2"], C["H2"]["dur"], 1.28, "none")]),
    seg("M1", 1.0),
    seg("M2", 1.12),
    seg("M3", 1.0, [(B["M3"], C["M3"]["dur"], 1.1, "none")]),
    seg("M4", 1.12, [(B["CANCER"], 0.12, 1.28, "power4.out")]),
    seg("M5", 1.0),
    seg("M6", 1.1, [(B["CHK3"], 0.14, 1.22, "power4.out")]),
    seg("M7", 1.0),
    seg("M8", 1.1, [(B["DUIT"], 0.12, 1.25, "power4.out"), (B["SUM"], 2.2, 1.0, "power2.inOut")]),
    seg("M9", 1.12),
    seg("M10", 1.0),
    seg("M11", 1.12, [(B["END_OK"] - 0.2, 0.5, 1.0, "power2.inOut"), (DUR - 0.35, 0.35, 1.35, "power3.in")]),
]

# ---------------------------------------------------------------- SFX (file, time, volume)
SFX = [
    ("impact", 0.0, 0.8), ("pop", B["CANCER_H"], 0.4), ("whoosh_small", B["H2"] - 0.1, 0.5), ("riser", B["H2"], 0.3),
    ("kaching", B["BAYAR_H"], 0.7), ("whoosh", B["MAIN"] - 0.2, 0.7),
    ("impact", B["HWALL"], 0.5), ("whoosh", B["HWALL"] - 0.1, 0.45), ("whoosh_small", B["HWALL_END"] - 0.1, 0.4),
    ("pop", B["DUA"], 0.45), ("pop", B["DUA"] + 0.22, 0.45), ("ding2", B["PERTAMA"], 0.45),
    ("whoosh_small", B["M3"], 0.4), ("pop", B["DEF"], 0.45),
    ("impact", B["CANCER"], 0.4),
    ("check", B["CHK1"], 0.6), ("check", B["CHK2"], 0.6), ("check", B["CHK3"], 0.6), ("kaching", B["RM0"], 0.55),
    ("glitch", B["M7"] - 0.05, 0.4), ("shutter", B["M7"], 0.55),
    ("tick", B["M7"] + 0.45, 0.45), ("tick", B["M7"] + 0.55, 0.45), ("tick", B["M7"] + 0.65, 0.45), ("tick", B["M7"] + 0.75, 0.45),
    ("whoosh", B["WALL_OUT"] - 0.35, 0.55), ("pop", B["SEC2"], 0.45),
    ("whoosh", B["ORBIT"] - 0.1, 0.4), ("ding1", B["ORBIT"] + 0.1, 0.3),
    ("kaching", B["DUIT"], 0.7), ("impact", B["DUIT"], 0.35), ("whoosh_small", B["SUM"], 0.35),
    ("pop", B["NAME"], 0.45), ("ding1", B["NAME"] + 0.05, 0.35),
    ("whoosh_small", B["M10"] - 0.05, 0.4), ("pop", B["M10"] + 0.15, 0.4),
    ("whoosh_down", DUR - 0.9, 0.35), ("whoosh", DUR - 0.45, 0.55),
]
SFX_LEN = {"impact": 1.4, "pop": 0.16, "riser": 1.6, "whoosh": 0.55, "whoosh_small": 0.28, "whoosh_down": 0.5,
           "ding1": 1.2, "ding2": 1.2, "ding3": 1.2, "glitch": 0.45, "shutter": 0.22, "tick": 0.05,
           "metal_ting": 1.8, "rewind": 0.7, "kaching": 1.2, "check": 0.32}

# ================================================================= HTML pieces
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def span(a, b): return f'data-start="{round(a,3)}" data-duration="{round(b-a,3)}"'

videos = "\n".join(
    f'      <!-- {c["id"]}: {esc(c["note"])} | src {c["src"]:.2f}-{c["src_out"]:.2f} -->\n'
    f'      <video id="v_{c["id"]}" class="clip vid" src="{FOOT}" playsinline data-has-audio="true" data-volume="1" '
    f'data-fade-in="0.025" data-fade-out="0.03" data-start="{c["start"]}" data-duration="{c["dur"]}" '
    f'data-media-start="{c["src"]}" data-track-index="0"></video>' for c in CLIPS)

caps_html = "\n".join(
    f'    <div id="cap{i}" class="clip cap" {span(g["start"], g["end"])} data-track-index="3">'
    + " ".join(f'<span class="w{" k" if clean(w) in KEY else ""}">{esc(w)}</span>' for w, _ in g["words"]) + "</div>"
    for i, g in enumerate(CAPS))

sfx_html = "\n".join(
    f'    <audio id="sfx{i}" src="assets/sfx/{f}.wav" data-start="{max(0, round(at, 3))}" '
    f'data-duration="{round(min(SFX_LEN[f], DUR - max(0, at)), 3)}" data-volume="{v}" data-track-index="{6 + i % 5}"></audio>'
    for i, (f, at, v) in enumerate(SFX))

FACES = ["1.0", "6.0", "9.6", "12.2", "16.0", "19.0", "25.0", "30.0", "33.0", "38.5"]
tiles = []
for r in range(3):
    for col in range(3):
        i = r * 3 + col
        a, b = FACES[i], FACES[(i + 4) % len(FACES)]
        la, lb = ("#1 WAIVER", "#2 PAMPASAN")
        tiles.append(
            f'      <div class="tile" style="left:{col*360}px;top:{r*640}px"><img class="ta" src="assets/img/face_{a}.jpg" alt="">'
            f'<img class="tb" src="assets/img/face_{b}.jpg" alt=""><span class="tl tla">{la}</span><span class="tl tlb">{lb}</span></div>')

hrows = "\n".join(
    f'      <div class="hrow {"solid" if r == 5 else ("outline" if r % 2 else "dim")}">CI PROTECTION &#8226; CI PROTECTION &#8226; CI PROTECTION</div>'
    for r in range(11))

orbit_labels = ["PENYAKIT KRITIKAL", "&#9679;", "DILINDUNGI", "&#9679;"] * 2
orbit_items = "\n".join(
    f'          <div class="oi" style="transform: rotateY({i*360/len(orbit_labels):.1f}deg) translateZ(400px)">{lab}</div>'
    for i, lab in enumerate(orbit_labels))

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
      #shake, #cam {{ position: absolute; inset: 0; will-change: transform; }}
      #cam {{ filter: contrast(1.06) saturate(1.08) brightness(1.03); }}
      .vid {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .vignette {{ position: absolute; inset: 0; z-index: 5; pointer-events: none;
        background: radial-gradient(ellipse at 54% 44%, rgba(0,0,0,0) 50%, rgba(0,0,0,.4) 100%); }}
      .topshade {{ position: absolute; left: 0; right: 0; top: 0; height: 520px; z-index: 6; pointer-events: none;
        background: linear-gradient(180deg, rgba(0,0,0,.55), rgba(0,0,0,0)); }}

      /* captions */
      .cap {{ position: absolute; left: 50px; right: 50px; top: 1370px; z-index: 20; text-align: center;
        font-weight: 900; font-size: 58px; line-height: 1.1; text-transform: uppercase; letter-spacing: -1px; }}
      .cap .w {{ display: inline-block; margin: 0 6px; color: #fff; -webkit-text-stroke: 11px #000; paint-order: stroke fill;
        text-shadow: 0 10px 18px rgba(0,0,0,.45); }}
      .cap .w.k {{ color: #FFD400; }}

      /* hook */
      #hookShade {{ position: absolute; left: 0; right: 0; bottom: 0; height: 1000px; z-index: 8;
        background: linear-gradient(0deg, rgba(0,0,0,.8) 0%, rgba(0,0,0,.5) 55%, rgba(0,0,0,0) 100%); }}
      .hook {{ position: absolute; left: 0; right: 0; top: 1190px; z-index: 9; text-align: center; font-family: "Anton"; line-height: 1; }}
      .hook .hl {{ display: block; text-transform: uppercase; text-shadow: 0 8px 0 rgba(0,0,0,.35); }}
      #hookA .a1 {{ font-size: 88px; margin-bottom: 26px; }}
      #hookA .a2 {{ font-size: 138px; color: #fff; }}
      #hookA .a2 b {{ display: inline-block; background: #E8262B; padding: 18px 34px 8px; border-radius: 18px; font-weight: 400; line-height: 1; }}
      #hookB .b1 {{ font-size: 86px; color: #FFD400; }}
      #hookB .b2 {{ font-size: 104px; }}
      #rm0 {{ position: absolute; left: 0; right: 0; top: 150px; z-index: 9; text-align: center; }}
      #rm0 .stamp {{ display: inline-block; font-family: "Anton"; font-size: 130px; line-height: 1; padding: 6px 40px; color: #22C55E;
        border: 10px solid #22C55E; border-radius: 40px; background: rgba(0,0,0,.6); transform: rotate(-6deg); }}

      /* headline wall */
      #hwall {{ position: absolute; inset: 0; z-index: 11; background: rgba(4,10,22,.66); overflow: hidden; }}
      .hrow {{ position: absolute; left: 50%; white-space: nowrap; font-family: "Anton"; font-size: 150px; line-height: 1; letter-spacing: 2px; }}
      .hrow.outline {{ color: transparent; -webkit-text-stroke: 3px rgba(255,255,255,.85); }}
      .hrow.dim {{ color: rgba(255,255,255,.13); }}
      .hrow.solid {{ color: #FFD400; text-shadow: 0 10px 30px rgba(0,0,0,.8); }}

      /* top-zone UI */
      .topui {{ position: absolute; left: 0; right: 0; top: 170px; z-index: 14; text-align: center; }}
      #title .t1 {{ font-family: "Anton"; font-size: 88px; line-height: 1; color: #FFD400; text-shadow: 0 8px 0 rgba(0,0,0,.4); }}
      #title .t2 {{ margin-top: 8px; font-weight: 800; font-size: 32px; letter-spacing: 6px; }}
      #cards {{ display: flex; justify-content: center; gap: 30px; }}
      .card {{ width: 360px; padding: 18px 16px; border-radius: 24px; background: rgba(255,255,255,.96); color: #111; box-shadow: 0 16px 34px rgba(0,0,0,.5); }}
      .card .n {{ display: inline-block; width: 62px; height: 62px; line-height: 62px; border-radius: 50%; background: #111; color: #FFD400;
        font-family: "Anton"; font-size: 42px; }}
      .card .lbl {{ margin-top: 8px; font-family: "Anton"; font-size: 48px; line-height: 1; }}
      .card .sub {{ margin-top: 4px; font-weight: 800; font-size: 23px; color: #555; }}
      .chip {{ display: inline-block; padding: 10px 26px; border-radius: 18px; background: #FFD400; color: #111; font-family: "Anton"; font-size: 52px;
        box-shadow: 0 12px 26px rgba(0,0,0,.45); }}
      .chip small {{ font-family: "Montserrat"; font-weight: 900; font-size: 26px; }}
      #def .box {{ display: inline-block; margin-top: 18px; padding: 12px 26px; border-radius: 18px; background: rgba(0,0,0,.72); border: 3px solid #FFD400;
        font-weight: 900; font-size: 38px; }}
      #def .box b {{ color: #FFD400; }}
      #check {{ text-align: left; left: 190px; right: 190px; }}
      #check .it {{ display: flex; align-items: center; gap: 18px; margin-bottom: 14px; padding: 12px 22px; border-radius: 20px;
        background: rgba(255,255,255,.96); color: #111; font-weight: 900; font-size: 36px; box-shadow: 0 12px 26px rgba(0,0,0,.4); }}
      #check .it i {{ flex: none; width: 46px; height: 46px; border-radius: 50%; background: #22C55E; color: #fff; font-style: normal;
        text-align: center; line-height: 46px; font-size: 30px; }}

      /* clone wall */
      #wall {{ position: absolute; inset: 0; z-index: 12; background: #000; }}
      #wallInner {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      .tile {{ position: absolute; width: 360px; height: 640px; overflow: hidden; border: 6px solid #000; border-radius: 22px; }}
      .tile img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .tile .tb, .tile .tlb {{ opacity: 0; }}
      .tile .tl {{ position: absolute; left: 50%; bottom: 36px; transform: translateX(-50%); font-family: "Anton"; font-size: 36px; letter-spacing: 2px;
        padding: 4px 18px; border-radius: 16px; background: #FFD400; color: #111; white-space: nowrap; }}

      /* orbit */
      #orbit {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; z-index: 13; perspective: 1200px; perspective-origin: 583px 1170px; }}
      #orbitPos {{ position: absolute; left: 583px; top: 1170px; width: 0; height: 0; transform-style: preserve-3d; }}
      #ring {{ position: absolute; left: 0; top: 0; width: 0; height: 0; transform-style: preserve-3d; }}
      .oi {{ position: absolute; left: -240px; top: -40px; width: 480px; height: 80px; text-align: center; line-height: 80px; white-space: nowrap;
        font-weight: 900; font-size: 40px; color: #FFD400; -webkit-text-stroke: 8px #000; paint-order: stroke fill; backface-visibility: hidden; }}

      /* duit pampasan + slider */
      #duit .big {{ font-family: "Anton"; font-size: 108px; line-height: 1; color: #22C55E; text-shadow: 0 8px 0 rgba(0,0,0,.45); }}
      #duit .rm {{ position: absolute; font-family: "Anton"; font-size: 50px; color: #22C55E; padding: 2px 18px; border-radius: 14px;
        background: rgba(0,0,0,.6); border: 4px solid #22C55E; }}
      #slider .lbl {{ font-family: "Anton"; font-size: 66px; line-height: 1; }}
      #slider .lbl b {{ color: #FFD400; font-weight: 400; }}
      #slider .track {{ position: relative; margin: 26px auto 0; width: 600px; height: 18px; border-radius: 9px; background: rgba(255,255,255,.3); }}
      #slider .fill {{ position: absolute; left: 0; top: 0; bottom: 0; width: 100%; border-radius: 11px; background: #FFD400; transform-origin: 0 50%; }}
      #slider .knob {{ position: absolute; top: -18px; left: -27px; width: 54px; height: 54px; border-radius: 50%; background: #fff; box-shadow: 0 6px 16px rgba(0,0,0,.5); }}
      #slider .sub {{ margin-top: 22px; font-weight: 900; font-size: 34px; -webkit-text-stroke: 8px #000; paint-order: stroke fill; }}

      /* name + CTA */
      #name .nm {{ display: inline-block; padding: 12px 34px 10px; border-radius: 22px; background: #fff; color: #111; box-shadow: 0 16px 34px rgba(0,0,0,.5); }}
      #name .nm .a {{ font-family: "Anton"; font-size: 80px; line-height: 1; }}
      #name .nm .b {{ font-weight: 900; font-size: 29px; letter-spacing: 3px; color: #D31145; }}
      #name .cta {{ margin-top: 20px; font-weight: 900; font-size: 40px; -webkit-text-stroke: 8px #000; paint-order: stroke fill; }}
      #name .cta b {{ color: #FFD400; }}

      #flash {{ position: absolute; inset: 0; z-index: 40; background: #fff; opacity: 0; pointer-events: none; }}
      #progress {{ position: absolute; left: 0; top: 0; height: 12px; width: 100%; z-index: 41; background: #FFD400; transform-origin: 0 50%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}" data-fps="30">
      <div id="shake"><div id="cam">
{videos}
      </div></div>
      <div class="vignette"></div>
      <div class="topshade"></div>

      <!-- HOOK (flash-forward) -->
      <div id="hookShade" class="clip" {span(0, B["MAIN"])} data-track-index="1"></div>
      <div id="hookA" class="clip hook" {span(0, B["H2"])} data-track-index="1">
        <span class="hl a1">Kalau anda</span><span class="hl a2"><b>kena cancer</b></span></div>
      <div id="hookB" class="clip hook" {span(B["H2"], B["MAIN"])} data-track-index="1">
        <span class="hl b1">tapi tak perlu</span><span class="hl b2">bayar apa-apa?!</span></div>
      <div id="rm0" class="clip" {span(B["BAYAR_H"], B["MAIN"])} data-track-index="2"><div class="stamp">RM0</div></div>

      <!-- HEADLINE WALL: CI PROTECTION -->
      <div id="hwall" class="clip" {span(B["HWALL"], B["HWALL_END"])} data-track-index="2">
{hrows}
      </div>
      <div id="title" class="clip topui" {span(B["HWALL_END"] - 0.05, B["DUA"] - 0.05)} data-track-index="2">
        <div class="t1">CI PROTECTION</div><div class="t2">CRITICAL ILLNESS</div></div>

      <!-- 2 JENIS cards -->
      <div id="cards" class="clip topui" {span(B["DUA"] - 0.05, B["M3"])} data-track-index="2">
        <div class="card" id="card1"><div class="n">1</div><div class="lbl">WAIVER</div><div class="sub">Pengecualian bayaran</div></div>
        <div class="card" id="card2"><div class="n">2</div><div class="lbl">PAMPASAN</div><div class="sub">Sakit kritikal</div></div>
      </div>

      <!-- #1 WAIVER definition -->
      <div id="def" class="clip topui" {span(B["M3"], B["CHK1"] - 0.05)} data-track-index="2">
        <div class="chip">#1 WAIVER</div>
        <div><div class="box">= <b>PENGECUALIAN BAYARAN</b></div></div></div>

      <!-- checklist -->
      <div id="check" class="clip topui" {span(B["CHK1"] - 0.05, B["M7"])} data-track-index="2">
        <div class="it" id="c1"><i>&#10003;</i>Pengecualian bayaran sijil</div>
        <div class="it" id="c2"><i>&#10003;</i>Sijil tetap diteruskan</div>
        <div class="it" id="c3"><i>&#10003;</i>Tak perlu bayar apa-apa</div></div>
      <div id="rm0b" class="clip" {span(B["RM0"], B["M7"])} data-track-index="2" style="position:absolute;right:50px;top:1130px;z-index:15">
        <div style="font-family:Anton;font-size:88px;line-height:1;color:#22C55E;padding:4px 24px;border:8px solid #22C55E;border-radius:28px;background:rgba(0,0,0,.6);transform:rotate(-8deg)">RM0</div></div>

      <!-- CLONE WALL -> #2 -->
      <div id="wall" class="clip" {span(B["M7"] - 0.05, B["WALL_OUT"])} data-track-index="2"><div id="wallInner">
{chr(10).join(tiles)}
      </div></div>
      <div id="sec2" class="clip topui" {span(B["SEC2"], B["DUIT"] - 0.1)} data-track-index="2">
        <div class="chip">#2 PAMPASAN <small>SAKIT KRITIKAL</small></div></div>

      <!-- ORBIT -->
      <div id="orbit" class="clip" {span(B["ORBIT"], B["ORBIT_END"])} data-track-index="2"><div id="orbitPos"><div id="ring">
{orbit_items}
      </div></div></div>

      <!-- DUIT PAMPASAN -->
      <div id="duit" class="clip topui" {span(B["DUIT"] - 0.05, B["SUM"])} data-track-index="2">
        <div class="big">DUIT PAMPASAN</div>
        <div class="rm" style="left:60px;top:140px">RM</div><div class="rm" style="right:60px;top:140px">RM</div></div>

      <!-- SUM COVER slider -->
      <div id="slider" class="clip topui" {span(B["SUM"], B["M9"])} data-track-index="2">
        <div class="lbl"><b>SUM COVER</b></div>
        <div class="track"><div class="fill"></div><div class="knob"></div></div>
        <div class="sub">Ikut berapa yang anda nak</div></div>

      <!-- NAME + CTA -->
      <div id="name" class="clip topui" {span(B["NAME"], DUR)} data-track-index="2">
        <div class="nm"><div class="a">CEK MAZ</div><div class="b">AIA &#8226; JOHOR BAHRU</div></div>
        <div class="cta">Nak tahu lebih <b>DETAIL?</b> Refer saya!</div></div>

      <!-- captions -->
{caps_html}

      <div id="flash" class="clip" {span(0, DUR)} data-track-index="4"></div>
      <div id="progress" class="clip" {span(0, DUR)} data-track-index="4"></div>

      <audio id="music" src="assets/sfx/music.wav" data-start="0" data-duration="{DUR}" data-volume="0.07" data-fade-in="0.3" data-fade-out="0.5" data-track-index="5"></audio>
{sfx_html}
    </div>

    <script>
      const B = {json.dumps(B)};
      const CAM = {json.dumps(CAM)};
      const CAPW = {json.dumps([[w[1] for w in g["words"]] for g in CAPS])};
      const tl = gsap.timeline({{ paused: true }});
      const qa = (s) => Array.from(document.querySelectorAll(s));

      // digital zoom (alternating punch-ins hide the jump cuts)
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
      shake(0, 16, 0.3); shake(B.CANCER_H, 10, 0.2); shake(B.HWALL, 12, 0.25); shake(B.CANCER, 8, 0.2); shake(B.DUIT, 10, 0.25);

      // flashes + progress; loop seam (ends white like it starts)
      tl.fromTo("#flash", {{ opacity: 0.8 }}, {{ opacity: 0, duration: 0.22 }}, 0);
      for (const at of [B.MAIN, B.HWALL, B.WALL_OUT]) tl.fromTo("#flash", {{ opacity: 0.65 }}, {{ opacity: 0, duration: 0.2, immediateRender: false }}, at);
      tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.8, duration: 0.3, ease: "power2.in", immediateRender: false }}, B.DUR - 0.3);
      tl.fromTo("#progress", {{ scaleX: 0 }}, {{ scaleX: 1, duration: B.DUR, ease: "none" }}, 0);

      // hook
      tl.fromTo("#hookA .a1", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.18 }}, 0);
      tl.fromTo("#hookA .a2", {{ scale: 2.4, opacity: 0, rotation: -5 }}, {{ scale: 1, opacity: 1, rotation: 0, duration: 0.2, ease: "back.out(2.2)" }}, 0.12);
      tl.fromTo("#hookA .a2", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.25, ease: "back.out(3)", immediateRender: false }}, B.CANCER_H);
      tl.fromTo("#hookB .b1", {{ x: -500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.22, ease: "power3.out" }}, B.H2);
      tl.fromTo("#hookB .b2", {{ x: 500, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.22, ease: "power3.out" }}, B.H2 + 0.12);
      tl.fromTo("#rm0 .stamp", {{ scale: 3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "power4.in" }}, B.BAYAR_H);
      tl.to(["#hookB", "#rm0"], {{ opacity: 0, y: -60, duration: 0.18, ease: "power2.in" }}, B.MAIN - 0.18);
      tl.to("#hookShade", {{ opacity: 0, duration: 0.18 }}, B.MAIN - 0.18);

      // headline wall
      qa(".hrow").forEach((row, r) => {{
        const dir = r % 2 ? 1 : -1;
        tl.set(row, {{ y: -60 + r * 190, xPercent: -50 }}, B.HWALL);
        tl.fromTo(row, {{ x: dir * 700, opacity: 0 }}, {{ x: dir * -60, opacity: 1, duration: 0.25 + Math.abs(r - 5) * 0.02, ease: "power3.out" }}, B.HWALL + Math.abs(r - 5) * 0.03);
        tl.to(row, {{ x: dir * -200, duration: B.HWALL_END - B.HWALL - 0.3, ease: "none" }}, B.HWALL + 0.3);
      }});
      tl.fromTo(".hrow.solid", {{ scale: 1.6 }}, {{ scale: 1.08, duration: 0.22, ease: "back.out(2)", immediateRender: false }}, B.HWALL);
      tl.to("#hwall", {{ opacity: 0, scale: 1.2, duration: 0.14, ease: "power2.in" }}, B.HWALL_END - 0.14);
      tl.fromTo("#title", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "power3.out" }}, B.HWALL_END - 0.05);

      // 2 cards
      tl.fromTo("#card1", {{ x: -600, rotationY: 40, opacity: 0 }}, {{ x: 0, rotationY: 0, opacity: 1, duration: 0.3, ease: "back.out(1.5)" }}, B.DUA);
      tl.fromTo("#card2", {{ x: 600, rotationY: -40, opacity: 0 }}, {{ x: 0, rotationY: 0, opacity: 1, duration: 0.3, ease: "back.out(1.5)" }}, B.DUA + 0.22);
      tl.to("#card1", {{ scale: 1.08, duration: 0.2, ease: "back.out(3)" }}, B.PERTAMA);
      tl.to("#card2", {{ scale: 0.9, opacity: 0.35, duration: 0.2 }}, B.PERTAMA);

      // definition
      tl.fromTo("#def .chip", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }}, B.M3);
      tl.fromTo("#def .box", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2.2)" }}, B.DEF);

      // checklist
      [["#c1", B.CHK1], ["#c2", B.CHK2], ["#c3", B.CHK3]].forEach(([s, at]) => {{
        tl.fromTo(s, {{ x: -700, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.28, ease: "back.out(1.6)" }}, at);
        tl.fromTo(s + " i", {{ scale: 0 }}, {{ scale: 1, duration: 0.2, ease: "back.out(3)" }}, at + 0.18);
      }});
      tl.fromTo("#rm0b > div", {{ scale: 3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "power4.in" }}, B.RM0);

      // clone wall
      const tiles = qa(".tile"), order = [4, 1, 3, 5, 7, 0, 2, 6, 8];
      order.forEach((idx, n) => tl.fromTo(tiles[idx], {{ scale: 0.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "back.out(2)" }}, B.M7 - 0.05 + n * 0.025));
      order.forEach((idx, n) => {{
        const at = B.M7 + 0.45 + n * 0.04, tile = tiles[idx];
        tl.to(tile, {{ scaleX: 0, duration: 0.06, ease: "power1.in" }}, at);
        tl.set(tile.querySelectorAll(".tb, .tlb"), {{ opacity: 1 }}, at + 0.06);
        tl.set(tile.querySelectorAll(".ta, .tla"), {{ opacity: 0 }}, at + 0.06);
        tl.to(tile, {{ scaleX: 1, duration: 0.07, ease: "power1.out" }}, at + 0.06);
      }});
      tl.fromTo("#wallInner", {{ scale: 1 }}, {{ scale: 3.05, duration: 0.3, ease: "power3.in", immediateRender: false }}, B.WALL_OUT - 0.32);
      tl.to("#wall", {{ opacity: 0, duration: 0.08 }}, B.WALL_OUT - 0.08);
      tl.fromTo("#sec2 .chip", {{ y: -60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25, ease: "back.out(2)" }}, B.SEC2);

      // orbit around her
      tl.fromTo("#ring", {{ rotationX: -12, rotationY: 0 }}, {{ rotationX: -12, rotationY: -320, duration: B.ORBIT_END - B.ORBIT, ease: "power1.inOut" }}, B.ORBIT);
      tl.fromTo("#orbitPos", {{ scale: 0.3, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }}, B.ORBIT);
      tl.to("#orbitPos", {{ scale: 1.5, opacity: 0, duration: 0.2, ease: "power2.in" }}, B.ORBIT_END - 0.2);

      // duit pampasan
      tl.fromTo("#duit .big", {{ scale: 2.2, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2)" }}, B.DUIT - 0.05);
      qa("#duit .rm").forEach((el, i) => tl.fromTo(el, {{ y: -260, opacity: 0, rotation: (i - 1) * 14 }}, {{ y: 0, opacity: 1, rotation: (i - 1) * -8, duration: 0.35, ease: "bounce.out" }}, B.DUIT + 0.1 + i * 0.08));

      // sum cover slider: knob sweeps, "ikut pilihan anda"
      tl.fromTo("#slider", {{ y: -40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25 }}, B.SUM);
      tl.fromTo("#slider .knob", {{ x: 50 }}, {{ keyframes: [{{ x: 470, duration: 0.6 }}, {{ x: 210, duration: 0.45 }}, {{ x: 410, duration: 0.45 }}], ease: "power2.inOut", immediateRender: false }}, B.SUM + 0.2);
      tl.fromTo("#slider .fill", {{ scaleX: 50 / 600 }}, {{ keyframes: [{{ scaleX: 470 / 600, duration: 0.6 }}, {{ scaleX: 210 / 600, duration: 0.45 }}, {{ scaleX: 410 / 600, duration: 0.45 }}], ease: "power2.inOut", immediateRender: false }}, B.SUM + 0.2);

      // name + CTA
      tl.fromTo("#name .nm", {{ y: -80, opacity: 0, scale: 0.8 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, B.NAME);
      tl.fromTo("#name .cta", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.25 }}, B.M10 + 0.15);
      tl.fromTo("#name .cta b", {{ scale: 1 }}, {{ scale: 1.15, duration: 0.35, yoyo: true, repeat: 5, ease: "sine.inOut", immediateRender: false }}, B.M10 + 0.5);

      // captions
      qa(".cap").forEach((cap, gi) => {{
        tl.fromTo(cap, {{ scale: 0.82 }}, {{ scale: 1, duration: 0.15, ease: "back.out(2.5)" }}, CAPW[gi][0]);
        cap.querySelectorAll(".w").forEach((w, wi) => {{
          tl.fromTo(w, {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.1 }}, CAPW[gi][wi]);
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
lines = [f"DURATION {DUR}s (asal 47.5s, suara x{SPEED})", "", "EDL (output -> source):"]
lines += [f"  {c['start']:6.2f}-{c['start']+c['dur']:6.2f}  src {c['src']:5.2f}-{c['src_out']:5.2f}  {c['id']:4s} {c['note']}" for c in CLIPS]
lines += ["", "BEATS:"] + [f"  {k:10s} {v}" for k, v in B.items()]
lines += ["", "CAPTIONS:"] + [f"  {g['start']:6.2f}-{g['end']:6.2f}  " + " ".join(w for w, _ in g["words"]) for g in CAPS]
(HERE / "EDIT_PLAN.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
