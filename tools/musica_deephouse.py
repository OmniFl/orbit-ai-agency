"""Kalifai — pista deep house original (generada por síntesis, sin muestras de terceros).
122 BPM, La menor, 64 compases, bucle sin cortes."""
import numpy as np
from scipy import signal

SR = 44100
BPM = 122
BEAT = 60 / BPM
BAR = 4 * BEAT
NBARS = 64
N = int(round(NBARS * BAR * SR))
rng = np.random.default_rng(7)

L = np.zeros(N); R = np.zeros(N)          # pista seca
RVB_L = np.zeros(N); RVB_R = np.zeros(N)  # envío a reverb
SC = np.ones(N)                            # sidechain (compresión con el bombo)


def t_of(bar, beat=0.0):
    return int(round((bar * BAR + beat * BEAT) * SR))


def add(buf, start, x):
    start %= N
    end = start + len(x)
    if end <= N:
        buf[start:end] += x
    else:  # se envuelve al principio: bucle perfecto
        k = N - start
        buf[start:] += x[:k]
        buf[:end - N] += x[k:]


def put(x, start, pan=0.0, rev=0.0):
    gl = np.cos((pan + 1) * np.pi / 4); gr = np.sin((pan + 1) * np.pi / 4)
    add(L, start, x * gl); add(R, start, x * gr)
    if rev:
        add(RVB_L, start, x * gl * rev); add(RVB_R, start, x * gr * rev)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'low'); return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high'); return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band'); return signal.lfilter(b, a, x)


def env(n, a=0.005, d=0.2, s=0.0, r=0.05, hold=None):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    if hold is not None:
        rel = t > hold
        e[rel] *= np.exp(-(t[rel] - hold) / max(r, 1e-6))
    return e


# ---------- Batería ----------
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.28)
    click = hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.004) * 0.15
    return np.tanh(1.6 * (body + click)) * 0.55


def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 900, 3200)
    e = np.zeros(n)
    for off in (0, 0.011, 0.022):
        tt = t - off; e += np.where(tt >= 0, np.exp(-np.clip(tt, 0, None) / 0.012), 0)
    e += np.exp(-t / 0.13) * 0.6
    return nz * e * 0.22


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR); t = np.arange(n) / SR
    nz = hp(rng.standard_normal(n), 7500, 4)
    return nz * np.exp(-t / (0.07 if open_ else 0.014)) * (0.08 if open_ else 0.05)


def shaker():
    n = int(0.06 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 5000, 11000)
    a = np.minimum(t / 0.008, 1)
    return nz * a * np.exp(-t / 0.02) * 0.04


def rim():
    n = int(0.08 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.012) + bp(rng.standard_normal(n), 1500, 4000) * np.exp(-t / 0.006) * .5
    return x * 0.10


K, CL, HO, HC, SH, RM = kick(), clap(), hat(True), hat(False), shaker(), rim()

# ---------- Armonía: Am9 – Fmaj9 – Dm9 – Em7(9) ----------
CHORDS = [
    (45, [57, 60, 64, 67, 71]),   # Am9
    (41, [57, 60, 64, 65, 67]),   # Fmaj9 (voz cercana)
    (38, [57, 60, 62, 65, 69]),   # Dm9
    (40, [55, 59, 62, 64, 66]),   # Em7(9)
]


def epiano(freq, dur, vel=1.0):
    n = int((dur + 1.2) * SR); t = np.arange(n) / SR
    idx = 1.6 * np.exp(-t / 0.35) + 0.25
    mod = np.sin(2 * np.pi * freq * t)
    car = np.sin(2 * np.pi * freq * t + idx * mod)
    tine = np.sin(2 * np.pi * freq * 14 * t) * np.exp(-t / 0.02) * 0.05
    e = np.exp(-t / 1.4) * np.where(t > dur, np.exp(-(t - dur) / 0.12), 1)
    e *= np.minimum(t / 0.003, 1)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.1 * t)
    return (car + tine) * e * trem * 0.11 * vel


def pad(freqs, dur):
    n = int((dur + 1.5) * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for d in (-0.08, 0.0, 0.08):
            x += signal.sawtooth(2 * np.pi * f * (2 ** (d / 12)) * t + rng.uniform(0, 6.28))
    x = lp(x, 1100, 2)
    a = np.minimum(t / 0.6, 1)
    e = a * np.where(t > dur, np.exp(-(t - dur) / 0.6), 1)
    return x * e * 0.018


def bass(freq, dur):
    n = int((dur + 0.08) * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t) + 0.1 * signal.sawtooth(2 * np.pi * freq * t)
    x = lp(x, 420, 2)
    e = np.minimum(t / 0.006, 1) * np.where(t > dur, np.exp(-(t - dur) / 0.02), 1) * (0.75 + 0.25 * np.exp(-t / 0.15))
    return x * e * 0.38


def sax(freq, dur, vel=1.0):
    """Voz tipo saxo: diente de sierra con vibrato, formantes y soplo."""
    n = int((dur + 0.35) * SR); t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.18) / 0.25, 0, 1)
    scoop = 1 - 0.02 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(freq * vib * scoop) / SR
    x = signal.sawtooth(ph) * 0.6 + signal.square(ph, 0.35) * 0.25
    breath = rng.standard_normal(n) * 0.05
    x = x + breath
    f1 = bp(x, 450, 1100); f2 = bp(x, 1300, 2900) * 0.7; f3 = bp(x, 3000, 4200) * 0.18
    y = f1 + f2 + f3
    e = np.minimum(t / 0.045, 1) * np.where(t > dur, np.exp(-(t - dur) / 0.09), 1) * (0.85 + 0.15 * np.exp(-t / 0.3))
    return np.tanh(y * 2.2) * e * 0.13 * vel


# ---------- Patrones ----------
CHORD_HITS = [(0.0, 0.35), (0.75, 0.25), (1.5, 0.45), (2.75, 0.25), (3.5, 0.4)]
BASS_HITS = [(0.5, 0.35, 0), (1.5, 0.3, 0), (2.25, 0.2, 12), (2.5, 0.35, 0), (3.5, 0.35, 7)]

# Melodía (compases de 2 por acorde, 8 compases), en semitonos MIDI, (beat_en_frase, duración, nota)
MEL = [
    (0.5, 1.0, 76), (1.75, 0.5, 74), (2.5, 2.0, 72), (5.0, 0.5, 69), (5.5, 0.5, 72), (6.0, 1.5, 74),
    (8.5, 1.0, 72), (9.75, 0.5, 74), (10.5, 2.5, 76), (13.5, 0.5, 79), (14.0, 1.5, 76),
    (16.5, 1.0, 77), (17.75, 0.5, 76), (18.5, 1.5, 74), (20.5, 0.5, 72), (21.0, 2.0, 74),
    (24.5, 0.75, 71), (25.5, 0.75, 72), (26.5, 1.0, 74), (28.0, 3.0, 76),
]


def section_flags(bar):
    # 0-15 groove | 16-23 + saxo | 24-31 respiro sin bombo | 32-47 todo + saxo | 48-63 groove que vuelve al inicio
    kick_on = not (24 <= bar < 31)
    sax_on = (16 <= bar < 24) or (32 <= bar < 48)
    pad_on = bar >= 8 and bar < 56 or bar >= 60
    clap_on = not (24 <= bar < 28)
    shaker_on = bar >= 4 and not (24 <= bar < 28)
    return kick_on, sax_on, pad_on, clap_on, shaker_on


for bar in range(NBARS):
    kick_on, sax_on, pad_on, clap_on, shaker_on = section_flags(bar)
    root, notes = CHORDS[(bar // 2) % 4]
    for b in range(4):
        if kick_on:
            s = t_of(bar, b); put(K, s, 0, 0.02)
            dl = int(0.38 * SR); sc = 1 - 0.32 * np.exp(-np.arange(dl) / SR / 0.11)
            idx = (np.arange(dl) + s) % N; SC[idx] = np.minimum(SC[idx], sc)
        if clap_on and b in (1, 3):
            put(CL, t_of(bar, b), 0.05, 0.35)
        put(HO * (0.9 if kick_on else 0.6), t_of(bar, b + 0.5), 0.2, 0.08)
        if shaker_on:
            for k in range(4):
                sw = 0.06 if k % 2 else 0.0
                v = (0.6, 1.0, 0.7, 1.1)[k]
                put(SH * v, t_of(bar, b + k * 0.25 + sw), -0.35, 0.05)
    if bar % 2 == 1:
        put(RM, t_of(bar, 3.75), 0.4, 0.3)
    # Acordes tipo Rhodes (2 compases por acorde: el patrón se repite en cada compás)
    for (pos, dur) in CHORD_HITS:
        for i, m in enumerate(notes):
            put(epiano(mtof(m), dur * BEAT, 0.9 + 0.1 * (pos == 0)), t_of(bar, pos) + i * 40, (i - 2) * 0.15, 0.35)
    if pad_on and bar % 2 == 0:
        put(pad([mtof(m) for m in notes[:4]], 2 * BAR), t_of(bar), 0, 0.5)
    # Bajo
    if not (24 <= bar < 28):
        for (pos, dur, iv) in BASS_HITS:
            put(bass(mtof(root + iv), dur * BEAT), t_of(bar, pos), 0, 0)
    # Saxo
    if sax_on and bar % 8 == 0:
        for (pos, dur, m) in MEL:
            put(sax(mtof(m - 12 + 12), dur * BEAT), t_of(bar, pos), -0.1, 0.45)

# ---------- Mezcla ----------
# Sidechain a todo menos bombo: aproximación — aplicamos a la mezcla total y devolvemos el bombo seco
kk_l = np.zeros(N); kk_r = np.zeros(N)
for bar in range(NBARS):
    if section_flags(bar)[0]:
        for b in range(4):
            g = np.cos(np.pi / 4)
            add(kk_l, t_of(bar, b), K * g); add(kk_r, t_of(bar, b), K * g)
mixL = (L - kk_l) * SC + kk_l
mixR = (R - kk_r) * SC + kk_r

# Reverb: respuesta al impulso de ruido con caída de 2,4 s, convolución circular (cola que entra al inicio del bucle)
ir_n = int(2.4 * SR); ti = np.arange(ir_n) / SR
irL = rng.standard_normal(ir_n) * np.exp(-ti / 0.55); irR = rng.standard_normal(ir_n) * np.exp(-ti / 0.55)
irL = lp(hp(irL, 250), 6000); irR = lp(hp(irR, 250), 6000)
irL /= np.sqrt(np.sum(irL ** 2)); irR /= np.sqrt(np.sum(irR ** 2))


def circ_conv(x, ir):
    y = signal.fftconvolve(x, ir)
    out = y[:N].copy(); tail = y[N:]
    out[:len(tail)] += tail
    return out


wetL = circ_conv(RVB_L * SC, irL) * 0.5
wetR = circ_conv(RVB_R * SC, irR) * 0.5
mixL += wetL; mixR += wetR

# Delay de 3/16 en el saxo y acordes (ping-pong suave) — incluido en el envío
d = int(0.75 * BEAT * SR)
mixL += np.roll(wetR, d) * 0.25; mixR += np.roll(wetL, d) * 0.25

# Masterización suave
mix = np.stack([mixL, mixR], 1)
mix = lp(hp(mix.T, 28), 14500).T
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix *= 0.89  # ~ -1 dBFS
out = (mix * 32767).astype(np.int16)

import wave, sys
path = sys.argv[1]
with wave.open(path, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', N / SR, 's')
