import subprocess, sys, numpy as np
from scipy.io import wavfile
SR = 48000
def load(f):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True, stdin=subprocess.DEVNULL).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
def cut(x, a, b, fade=.03):
    y = x[int(max(0, a)*SR):int(b*SR)].copy(); n = int(fade*SR)
    y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n); return y
rms = lambda v: np.sqrt(np.mean(v[np.abs(v) > 0.02]**2))
so = load("signoff.mp3")
SEG = {"reel-agent": (0, 3.73), "reel-backup": (4.17, 7.21), "reel-form-fields": (7.63, 11.44), "reel-site-myths": (11.85, 16.56),
       "reel-site-price": (16.98, 20.04), "reel-site-speed": (20.46, 23.61), "reel-rag-chatbot": (24.02, 27.63), "reel-site-test": (28.04, 30.94)}
BODY = {"reel-agent": ("reel-agent.full.mp3", 11.65), "reel-backup": ("reel-backup.full.mp3", 12.35),
        "reel-form-fields": ("reel-form-fields.full.mp3", 8.5), "reel-site-myths": ("reel-site-myths.full.mp3", 12.8),
        "reel-site-price": ("reel-site-price.full.mp3", 12.2), "reel-site-speed": ("reel-site-speed.full.mp3", 13.0),
        "reel-rag-chatbot": ("reel-rag-chatbot.mp3", 17.62)}
if len(sys.argv) > 2:  # slug file end
    BODY = {sys.argv[1]: (sys.argv[2], float(sys.argv[3]))}
for slug, (f, end) in BODY.items():
    b = cut(load(f), 0, end); s = cut(so, SEG[slug][0] - .05, SEG[slug][1] + .05)
    s *= rms(b) / rms(s)
    out = np.concatenate([b, np.zeros(int(.35*SR)), s])
    wavfile.write(f"{slug}.final.wav", SR, out.astype(np.float32))
    print(slug, f"body {len(b)/SR:.2f}  signoff from {len(b)/SR+.4:.2f}  total {len(out)/SR:.2f}")
