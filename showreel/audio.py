"""Synthesised 15s soundtrack for the showreel, locked to the picture's cut list.
120 BPM (beat = 0.5s). Writes showreel.wav (48 kHz, 16-bit stereo)."""
import wave
import numpy as np

SR, DUR = 48000, 15.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * np.sqrt((1 - pan) / 2)
    R[i:i + len(sig)] += sig * gain * np.sqrt((1 + pan) / 2)


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def noise(d):
    return rng.standard_normal(int(d * SR))


def kick(g=1.0):
    t = t_arr(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = band(noise(0.45), 2000, 8000) * np.exp(-t * 300) * 0.3
    return (np.sin(ph) * np.exp(-t * 7) + click) * g


def hat(d=0.06):
    t = t_arr(d)
    return band(noise(d), 7000, 16000) * np.exp(-t * 70)


def clap():
    t = t_arr(0.25)
    env = sum(np.exp(-np.maximum(t - o, 0) * 90) * (t >= o) for o in (0, 0.011, 0.023))
    return band(noise(0.25), 900, 5000) * (env + 0.4 * np.exp(-t * 18)) * 0.8


def impact(size=1.0):
    t = t_arr(1.8)
    f = 30 + 70 * np.exp(-t * 10)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.2 / size))
    crash = band(noise(1.8), 300, 12000) * np.exp(-t * 6)
    return boom * 1.2 + crash * 0.35


def whoosh(d, lo=400, hi=5000, rise=True):
    t = t_arr(d)
    x = band(noise(d), lo, hi)
    env = (t / d) ** 2.2 if rise else np.exp(-t * 8)
    return x * env


def riser(d, f0=200, f1=1600):
    t = t_arr(d)
    f = f0 * (f1 / f0) ** (t / d)
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.12
    return (tone + band(noise(d), 1500, 9000) * 0.5) * (t / d) ** 2


def blip(freq, d=0.12, shape='sine'):
    t = t_arr(d)
    s = np.sin(2 * np.pi * freq * t)
    if shape == 'square':
        s = np.sign(s) * 0.5
    return s * np.exp(-t * 30)


def pluck(freq, d=0.3):
    t = t_arr(d)
    s = sum(np.sin(2 * np.pi * freq * h * t) / h ** 1.3 for h in (1, 2, 3, 4))
    return s * np.exp(-t * 14) * 0.35


def saw(freq, d, detune=(0.0,)):
    t = t_arr(d)
    return sum(2 * ((t * freq * (1 + dt)) % 1) - 1 for dt in detune) / len(detune)


def note(n):  # MIDI → Hz
    return 440 * 2 ** ((n - 69) / 12)


# ---- 0–2s  OPEN ----------------------------------------------------------
t = t_arr(2.0)
drone = sum(np.sin(2 * np.pi * note(n) * t) for n in (45, 52, 57, 60)) / 4
add(drone * np.minimum(1, t / 1.4) * 0.22, 0)
add(blip(1320, 0.25), 0.15, 0.35)                              # dot pop
add(whoosh(0.55, 800, 7000), 0.5, 0.5)                          # line stretch
for i in range(0, 31, 5):
    add(blip(2400, 0.03, 'square'), 1.0 + i * 0.008, 0.08, pan=(i / 15 - 1))  # ruler ticks
add(riser(0.45, 300, 2400), 1.55, 0.7)

# ---- rhythm bed 2–12s -----------------------------------------------------
for b in np.arange(2.0, 12.0, 0.5):
    add(kick(), b, 0.9)
for b in np.arange(4.25, 12.0, 0.5):
    add(hat(), b, 0.25, pan=0.3)
for b in np.arange(4.0, 12.0, 0.125):
    if (b * 8) % 2:
        add(hat(0.03), b, 0.09, pan=-0.35)
for b in np.arange(4.5, 12.0, 1.0):
    add(clap(), b, 0.55)

# word stabs 2–4
for i, b in enumerate((2.0, 2.5, 3.0, 3.5)):
    ch = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)][i]
    stab = sum(saw(note(n), 0.35, (-.006, .006)) for n in ch) / 3
    add(band(stab, 80, 3500) * np.exp(-t_arr(0.35) * 9), b, 0.35)
add(whoosh(0.22, 300, 3000), 3.78, 0.6)

# bass 4–12 (8th pulse, note per bar)
for bar, root in zip((4, 6, 8, 10), (33, 29, 36, 31)):
    for b in np.arange(bar, bar + 2, 0.25):
        s = band(saw(note(root), 0.24, (-.004, .004)), 30, 700)
        add(s * np.exp(-t_arr(0.24) * 6), b + 0.0, 0.32)

# grid arps 4–6
scale = [69, 72, 74, 76, 79, 81, 84]
for i, b in enumerate(np.arange(4.0, 5.5, 0.125)):
    add(pluck(note(scale[(i * 3) % 7])), b, 0.35, pan=np.sin(i) * 0.6)
add(whoosh(0.5, 100, 2500), 5.5, 0.9)                           # suck into collapse

# particles 6–8.5
add(impact(1.2), 6.0, 0.9)
t = t_arr(1.2)
add(band(noise(1.2), 5000, 15000) * np.exp(-t * 3) * 0.3, 6.0)  # sparkle
for i, b in enumerate(np.arange(6.5, 8.0, 0.125)):
    add(pluck(note(scale[(i * 2 + 1) % 7] + 12), 0.25), b, 0.22, pan=-np.sin(i) * 0.6)
add(whoosh(0.5, 300, 9000), 7.95, 1.0)                          # wind blow

# 3D 8.5–10.5
add(impact(0.8), 8.5, 0.6)
t = t_arr(2.0)
add(np.sin(2 * np.pi * note(64) * t + 2 * np.sin(2 * np.pi * 3 * t)) * np.exp(-t * 1.2) * 0.12, 8.5)
add(whoosh(0.3, 500, 6000), 9.25, 0.5)                          # morph
add(whoosh(0.4, 200, 3000), 10.1, 0.7)                          # flatten

# shape / timing 10.5–12
add(impact(0.7), 10.5, 0.5)
for i, b in enumerate((10.75, 11.0, 11.25, 11.5, 11.75)):
    add(blip(note(72 + i * 2), 0.15), b, 0.4)
for b in np.arange(10.5, 12.0, 0.25):
    add(blip(180, 0.05), b, 0.25)                               # ball contact
add(riser(0.5, 200, 1800), 11.5, 0.6)

# montage 12–13
for i, b in enumerate(np.arange(12.0, 13.0, 0.25)):
    add(kick(1.1), b, 1.0)
    add(clap(), b, 0.5)
    add(band(noise(0.06), 2000, 12000) * 0.5, b, 0.5)           # glitch burst
for i, b in enumerate(np.arange(12.0, 13.0, 1 / 16)):
    add(clap(), b, 0.12 + 0.25 * (b - 12))                      # roll
add(riser(1.0, 150, 3000), 12.0, 0.6)

# title 13–15
add(impact(1.6), 13.0, 1.1)
t = t_arr(2.0)
pad = sum(saw(note(n), 2.0, (-.008, 0, .008)) for n in (45, 52, 57, 60, 64, 71)) / 6
pad = band(pad, 60, 2500) * np.minimum(1, t / 0.05) * np.exp(-t * 0.9)
add(pad * 0.3, 13.0, pan=0.0)
for i in range(18):
    add(blip(1500 + (i * 397) % 1800, 0.04, 'square'), 13.55 + i * 0.03, 0.05, pan=(i % 3 - 1) * 0.5)
add(whoosh(0.25, 200, 4000), 14.6, 0.6)                          # letterbox close
add(blip(note(81), 0.5), 14.9, 0.35)                             # final dot

# ---- master ---------------------------------------------------------------
mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.8) / np.tanh(1.8)
fade = np.ones(N); fade[-int(0.05 * SR):] = np.linspace(1, 0, int(0.05 * SR))
mix *= fade[:, None] * 0.92
pcm = (mix * 32767).astype('<i2')
with wave.open('showreel.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote showreel.wav')
