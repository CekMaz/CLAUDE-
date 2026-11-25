"""Synthesize royalty-free SFX + a light background beat for the sinki edit."""
import sys, os, wave
import numpy as np
from scipy import signal

SR = 48000
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def save(name, x, gain_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    peak = np.max(np.abs(x)) or 1.0
    x = x / peak * (10 ** (gain_db / 20))
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, name), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

def t(d): return np.arange(int(SR * d)) / SR
def env_adsr(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e
def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)
def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)

def sweep_noise(d, f0, f1, q=0.35, block=256):
    """Noise through a moving band-pass (time-varying), for whooshes/risers."""
    n = int(SR * d); x = rng.standard_normal(n); y = np.zeros(n)
    zi = None
    for i in range(0, n, block):
        frac = i / n
        fc = f0 * (f1 / f0) ** frac
        lo, hi = fc * (1 - q), min(fc * (1 + q), SR / 2 - 100)
        sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
        if zi is None: zi = signal.sosfilt_zi(sos) * 0
        y[i:i+block], zi = signal.sosfilt(sos, x[i:i+block], zi=zi)
    return y

# whoosh: swell up then down, stereo pan L->R
def whoosh(d, f0, f1):
    y = sweep_noise(d, f0, f1)
    tt = np.linspace(0, 1, len(y))
    e = np.sin(np.pi * tt) ** 1.6
    pan = tt
    return np.stack([y * e * (1 - 0.6 * pan), y * e * (0.4 + 0.6 * pan)], axis=1)
save("whoosh.wav", whoosh(0.55, 300, 4500), -3)
save("whoosh_small.wav", whoosh(0.28, 800, 6000), -6)
save("whoosh_down.wav", whoosh(0.5, 5000, 250), -3)

# impact / boom
d = 1.4; tt = t(d)
f = 38 + 90 * np.exp(-tt * 18)
sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
click = hp(rng.standard_normal(len(tt)), 1500) * np.exp(-tt * 60) * 0.5
body = lp(rng.standard_normal(len(tt)), 400) * np.exp(-tt * 9) * 0.6
save("impact.wav", np.tanh(1.8 * (sub + click + body)), -1)

# riser: noise sweep up + rising tone
d = 1.6; tt = t(d)
nz = sweep_noise(d, 200, 9000, q=0.5)
tone = signal.chirp(tt, 180, d, 1200, method="logarithmic") * 0.25
e = (tt / d) ** 2.2
save("riser.wav", (nz + tone) * e, -4)

# pop: short sine with pitch drop
d = 0.16; tt = t(d)
f = 900 * np.exp(-tt * 25) + 300
save("pop.wav", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30), -5)

# dings (bell partials) at 3 pitches for mod 1/2/3
def bell(f0, d=1.2):
    tt = t(d); x = np.zeros_like(tt)
    for k, (m, a, dec) in enumerate([(1, 1, 4), (2.0, .5, 6), (2.76, .35, 7), (5.4, .2, 10), (8.9, .08, 14)]):
        x += a * np.sin(2 * np.pi * f0 * m * tt) * np.exp(-tt * dec)
    return x * env_adsr(len(tt), 0.002, 0.05)
save("ding1.wav", bell(1046.5), -6)  # C6
save("ding2.wav", bell(1318.5), -6)  # E6
save("ding3.wav", bell(1568.0), -6)  # G6

# tick (UI click)
d = 0.05; tt = t(d)
save("tick.wav", bp(rng.standard_normal(len(tt)), 2500, 7000) * np.exp(-tt * 140), -8)

# camera shutter: two quick mechanical clicks
d = 0.22; tt = t(d); x = np.zeros_like(tt)
for off, a in [(0.0, 1), (0.085, .7)]:
    i = int(off * SR); seg = tt[: len(tt) - i]
    x[i:] += a * bp(rng.standard_normal(len(seg)), 1200, 6000) * np.exp(-seg * 90)
save("shutter.wav", x, -4)

# rewind: tape-like warble, pitch descending fast with noise
d = 0.7; tt = t(d)
f = 1400 * np.exp(-tt * 2.5) + 250 + 120 * np.sin(2 * np.pi * 18 * tt)
saw = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.35
nz = bp(rng.standard_normal(len(tt)), 1500, 6000) * 0.25
save("rewind.wav", lp(saw + nz, 5000) * env_adsr(len(tt), 0.02, 0.15), -6)

# metallic ting / clang (inharmonic) for "warna metal"
d = 1.8; tt = t(d); x = np.zeros_like(tt)
for m, a, dec in [(1, 1, 2.2), (2.32, .7, 2.8), (4.25, .5, 3.5), (6.63, .35, 4.5), (9.38, .2, 6)]:
    x += a * np.sin(2 * np.pi * 620 * m * tt + m) * np.exp(-tt * dec)
x += hp(rng.standard_normal(len(tt)), 3000) * np.exp(-tt * 80) * 0.4
save("metal_ting.wav", x, -5)

# glitch stutter (for clone wall)
d = 0.45; tt = t(d); x = np.zeros_like(tt)
for k in range(6):
    i = int(k * 0.07 * SR); n = int(0.035 * SR)
    seg = signal.square(2 * np.pi * (300 + 180 * k) * tt[:n]) * 0.4 + rng.standard_normal(n) * 0.3
    x[i:i+n] += seg * np.hanning(n)
save("glitch.wav", lp(x, 7000), -8)

# ---- background beat: 112 BPM, light pop groove with plucks ----
bpm = 112; beat = 60 / bpm; total = float(sys.argv[2]) if len(sys.argv) > 2 else 24.0
n = int(SR * total); mix = np.zeros((n, 2))
def add(x, at, pan=0.0, g=1.0):
    i = int(at * SR)
    if i >= n: return
    x = x[: n - i]
    mix[i:i+len(x), 0] += x * g * (1 - max(0, pan))
    mix[i:i+len(x), 1] += x * g * (1 + min(0, pan))
kt = t(0.35); kick = np.sin(2*np.pi*np.cumsum(50 + 110*np.exp(-kt*35))/SR) * np.exp(-kt*9)
ct = t(0.25); clap = bp(rng.standard_normal(len(ct)), 900, 5000) * (np.exp(-ct*25) + 0.6*np.exp(-np.maximum(ct-0.012,0)*30)*(ct>0.012))
ht = t(0.06); hat = hp(rng.standard_normal(len(ht)), 7000) * np.exp(-ht*90)
def pluck(freq, d=0.45):
    tt = t(d); x = signal.sawtooth(2*np.pi*freq*tt) * 0.5 + np.sin(2*np.pi*freq*2*tt)*0.3
    return lp(x, 2600) * np.exp(-tt * 7) * env_adsr(len(tt), 0.004, 0.05)
def bass(freq, d):
    tt = t(d); return lp(np.sin(2*np.pi*freq*tt) + 0.3*signal.square(2*np.pi*freq*tt), 600) * env_adsr(len(tt), 0.01, 0.08)
prog = [(220.0, [440.0, 523.25, 659.25]), (174.61, [349.23, 440.0, 523.25]), (261.63, [392.0, 523.25, 659.25]), (196.0, [392.0, 493.88, 587.33])]  # Am F C G
bar = 4 * beat; step = beat / 2
b = 0
while b * bar < total:
    root, chord = prog[b % 4]
    for s in range(8):
        at = b * bar + s * step
        if s in (0, 3, 4): add(kick, at, g=0.9)
        if s in (2, 6): add(clap, at, g=0.35)
        add(hat, at + (0.012 if s % 2 else 0), pan=0.3, g=0.18 if s % 2 else 0.12)
        note = chord[[0, 1, 2, 1, 0, 2, 1, 2][s]]
        add(pluck(note), at, pan=-0.25 if s % 2 else 0.25, g=0.16)
    add(bass(root / 2, bar * 0.95), b * bar, g=0.35)
    b += 1
fade = int(SR * 0.6); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
save("music.wav", np.tanh(mix * 1.2), -3)
print("ok")
