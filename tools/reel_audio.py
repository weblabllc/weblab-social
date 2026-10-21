"""Original soundtrack for WebLab Reels: lo-fi bed + transition sound design, synced to the reel timeline.

Everything is synthesised here (no samples, no licensed music):
  * bed: FM electric-piano chords, soft detuned pad, sub bass, brushed drums with swing,
    sidechain-style ducking on the kick, convolution reverb
  * SFX: airy whoosh under each frosted-glass wipe, softer whoosh on zoom cuts,
    a low "hook" hit at 0.1 s, gentle fade-out
Then the track is muxed onto the existing video (video stream copied) and normalised to -14 LUFS.

    python3 reel_audio.py <slug> [<slug>…]   (no args = all reels in reels.py)
"""
import pathlib
import re
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reels import REELS, OUT  # noqa: E402

SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
RNG = np.random.default_rng(7)

A3, B3, C4, D4, E4, F3, G3, G4, A4, B4, C5, D5, E5 = (220.0, 246.94, 261.63, 293.66, 329.63, 174.61, 196.0,
                                                      392.0, 440.0, 493.88, 523.25, 587.33, 659.25)
# Am9 – Fmaj7 – Cadd9 – G6 : warm, unresolved, loops cleanly
CHORDS = [(A3, C4, E4, G4, B4), (F3, A3, C4, E4, A4), (C4, E4, G4, D5), (G3, B3, D4, E4, B4)]
ROOTS = [55.0, 43.65, 65.41, 49.0]


def t_axis(n):
    return np.arange(n) / SR


def lp(x, hz, order=2):
    return sosfilt(butter(order, hz, "low", fs=SR, output="sos"), x)


def hp(x, hz, order=2):
    return sosfilt(butter(order, hz, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def epiano(f, dur=1.8, vel=1.0):
    t = t_axis(int(dur * SR))
    idx = 2.8 * np.exp(-t * 3.0) + 0.4
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.18 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    env = np.exp(-t * 1.4) * (1 - np.exp(-t * 400))
    return vel * s * env


def pad(freqs, dur):
    t = t_axis(int(dur * SR))
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0.0, 0.004):
            ff = f * (1 + det)
            for k in range(1, 7):
                s += np.sin(2 * np.pi * ff * k * t + RNG.uniform(0, 6.28)) / k
    s = lp(s, 1400)
    a = np.minimum(1, t / 0.35)
    r = np.minimum(1, (dur - t) / 0.35)
    return s * a * r / (len(freqs) * 6)


def kick():
    t = t_axis(int(0.32 * SR))
    f = 46 + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * (1 - np.exp(-t * 900))


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = t_axis(n)
    return lp(hp(RNG.standard_normal(n), 6500), 11000) * np.exp(-t * (22 if open_ else 70)) * 0.3


def clap():
    n = int(0.22 * SR)
    t = t_axis(n)
    s = bp(RNG.standard_normal(n), 900, 2600) * np.exp(-t * 18)
    return s * 0.5


def sub(f, dur):
    t = t_axis(int(dur * SR))
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 1.2) * (1 - np.exp(-t * 300)) * 0.9


def whoosh(dur=0.9, lo=300, hi=5000, gain=1.0):
    """Filtered-noise sweep: band centre rises then falls, peak in the middle."""
    n = int(dur * SR)
    t = t_axis(n)
    noise = RNG.standard_normal(n)
    out = np.zeros(n)
    bands = np.geomspace(lo, hi, 9)
    centre = np.sin(np.pi * t / dur)  # 0→1→0
    for i in range(len(bands) - 1):
        seg = bp(noise, bands[i], bands[i + 1])
        pos = i / (len(bands) - 2)
        w = np.exp(-((centre - pos) ** 2) / 0.06)
        out += seg * w
    env = np.sin(np.pi * t / dur) ** 1.6
    return out * env * gain * 0.6


def boom():
    t = t_axis(int(0.9 * SR))
    f = 38 + 30 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * (1 - np.exp(-t * 600))
    return s * 0.8 + lp(RNG.standard_normal(len(t)), 300) * np.exp(-t * 14) * 0.15


def reverb(x, secs=2.2, mix=0.22):
    n = int(secs * SR)
    t = t_axis(n)
    ir = RNG.standard_normal((n, 2)) * np.exp(-t * 3.0)[:, None]
    ir[:, 0] = lp(ir[:, 0], 5000)
    ir[:, 1] = lp(ir[:, 1], 5000)
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    wet /= np.max(np.abs(wet)) + 1e-9
    dry = x / (np.max(np.abs(x)) + 1e-9)
    return dry * (1 - mix) + wet * mix


def timeline(slug):
    html = "".join(REELS[slug]["scenes"])
    scenes = [(float(a), b, tin) for a, b, tin in re.findall(r'data-a="([\d.]+)" data-b="([\d.]+)" data-tin="(\w+)"', html)]
    zooms = [a for a, _, tin in scenes if tin == "zoom"]
    return REELS[slug]["duration"], REELS[slug]["sweeps"], zooms


def soundtrack(slug):
    dur, sweeps, zooms = timeline(slug)
    n = int((dur + 2.5) * SR)
    music = np.zeros((n, 2))
    drums = np.zeros(n)
    duck = np.ones(n)
    bars = int(np.ceil(dur / BAR)) + 1
    for b in range(bars):
        t0 = b * BAR
        ch = CHORDS[b % 4]
        p = pad(ch, BAR + 0.4) * 1.6
        add(music[:, 0], p * 0.9, t0)
        add(music[:, 1], p * 0.9, t0)
        for k, f in enumerate(ch):  # spread the e-piano voices across the stereo field
            pan = (k / max(1, len(ch) - 1)) * 0.6 + 0.2
            for when, vel in ((0.0, 0.55), (1.5 * BEAT, 0.32), (3.0 * BEAT + BEAT * 0.5, 0.22)):
                note = epiano(f, 1.6, vel)
                add(music[:, 0], note * (1 - pan) * 0.95, t0 + when + k * 0.012)
                add(music[:, 1], note * pan * 0.95, t0 + when + k * 0.012)
        s = sub(ROOTS[b % 4], BAR)
        add(music[:, 0], s * 0.22, t0)
        add(music[:, 1], s * 0.22, t0)
        for beat in range(4):
            tb = t0 + beat * BEAT
            if beat in (0, 2) or (beat == 3 and b % 2 == 1):
                kt = tb + (0.5 * BEAT if beat == 3 else 0)
                add(drums, kick() * 0.5, kt)
                i = int(kt * SR)
                m = min(n, i + int(0.28 * SR))
                if m <= i:
                    continue
                duck[i:m] = np.minimum(duck[i:m], 0.55 + 0.45 * np.linspace(0, 1, m - i) ** 0.6)
            if beat in (1, 3):
                add(drums, clap() * 0.3, tb)
            for eighth in (0, 1):
                swing = 0.09 * BEAT if eighth else 0
                add(drums, hat(open_=(beat == 3 and eighth == 1)) * (0.5 if eighth else 0.7), tb + eighth * BEAT / 2 + swing)
    # bed: duck the tonal parts under the kick, soften the drums, warm everything
    music *= duck[:, None]
    bed = music + np.stack([drums * 0.9, drums * 0.85], axis=1)
    bed = np.stack([lp(hp(bed[:, c], 35), 10000) for c in range(2)], axis=1)
    bed = reverb(bed, 2.4, 0.25)
    # intro: drums enter after the hook lands, pad from the start
    t = t_axis(n)[:, None]
    bed *= np.minimum(1, 0.35 + t / 1.2)
    sfx = np.zeros((n, 2))
    b = boom()
    add(sfx[:, 0], b * 0.7, 0.05)
    add(sfx[:, 1], b * 0.7, 0.05)
    for s in sweeps:
        w = whoosh(0.95, 250, 5000, 0.5)
        add(sfx[:, 0], w, s - 0.5)
        add(sfx[:, 1], np.roll(w, 240), s - 0.5)  # slight width
        # dip the bed under the glass, like passing behind it
        i, j = int((s - 0.4) * SR), int((s + 0.4) * SR)
        bed[i:j] *= (1 - 0.45 * np.sin(np.linspace(0, np.pi, j - i)))[:, None]
    for z in zooms:
        w = whoosh(0.6, 400, 3000, 0.22)
        add(sfx[:, 0], w, z - 0.2)
        add(sfx[:, 1], w, z - 0.2)
    sfx = reverb(sfx, 1.2, 0.18) * 0.55
    mix = bed * 0.9 + sfx * 0.8
    total = int(dur * SR)
    mix = mix[:total]
    fade = int(0.9 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    mix = mix / (np.max(np.abs(mix)) + 1e-9)
    mix = np.tanh(mix * 1.05) / np.tanh(1.05)
    return (mix * 0.89).astype(np.float32)


def mux(slug):
    d = OUT / slug
    wav = d / "soundtrack.wav"
    wavfile.write(str(wav), SR, soundtrack(slug))
    src = d / "reel.mp4"
    dst = d / "reel-audio.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(dst)], check=True)
    return dst


if __name__ == "__main__":
    for slug in sys.argv[1:] or list(REELS):
        print(mux(slug), flush=True)
