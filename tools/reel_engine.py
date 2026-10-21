"""Reel engine: 1080x1920 kinetic-type videos in the WebLab look.

A reel is a list of scenes on one timeline. Each frame is render(t) in the page →
Playwright screenshot → ffmpeg. Transitions:
  * scene in/out: 'zoom' (scale + blur + fade), 'up' (slide up), 'cut'
  * 'sweep': an amber panel with the flask mark wipes the screen between scenes
Element effects (class fx, data-fx, data-at = seconds from scene start):
  mask (line-by-line reveal from below), rise, pop, wipe, draw (bar grows), type,
  count, strike, collapse, shake, glow
"""
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_posts as bp  # noqa: E402

FPS = 30
F = "node_modules/@fontsource"
DEFS = bp.defs.replace('<symbol id="flask" viewBox="68 16 344 396">',
                       '<symbol id="flask" viewBox="68 16 344 396" overflow="visible">')
INK_FLASK = (DEFS.replace('id="flask"', 'id="flask-ink"').replace('id="fl"', 'id="fl-i"')
             .replace('url(#fl)', 'url(#fl-i)').replace('id="liq"', 'id="liq-i"').replace('url(#liq)', 'url(#liq-i)')
             .replace('stroke="#F0E2C8"', 'stroke="#141413"').replace('stroke="#E8A54B"', 'stroke="#141413"')
             .replace('fill="rgba(20,153,140,.16)"', 'fill="rgba(20,19,19,.12)"'))

CSS = f"""
@font-face {{ font-family: GS; font-weight: 400; src: url({F}/google-sans/files/google-sans-cyrillic-400-normal.woff2); unicode-range: U+0400-04FF; }}
@font-face {{ font-family: GS; font-weight: 400; src: url({F}/google-sans/files/google-sans-latin-400-normal.woff2); unicode-range: U+0000-00FF, U+2000-206F, U+2190-21FF, U+2713; }}
@font-face {{ font-family: GS; font-weight: 500; src: url({F}/google-sans/files/google-sans-cyrillic-500-normal.woff2); unicode-range: U+0400-04FF; }}
@font-face {{ font-family: GS; font-weight: 500; src: url({F}/google-sans/files/google-sans-latin-500-normal.woff2); unicode-range: U+0000-00FF, U+2000-206F, U+2190-21FF; }}
@font-face {{ font-family: GS; font-weight: 600; src: url({F}/google-sans/files/google-sans-cyrillic-600-normal.woff2); unicode-range: U+0400-04FF; }}
@font-face {{ font-family: GS; font-weight: 600; src: url({F}/google-sans/files/google-sans-latin-600-normal.woff2); unicode-range: U+0000-00FF, U+2000-206F, U+2190-21FF; }}
@font-face {{ font-family: JBM; font-weight: 500; src: url({F}/jetbrains-mono/files/jetbrains-mono-cyrillic-500-normal.woff2); unicode-range: U+0400-04FF; }}
@font-face {{ font-family: JBM; font-weight: 500; src: url({F}/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2); unicode-range: U+0000-00FF; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0B0A08; }}
#stage {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: GS, sans-serif; color: #F3EEE6; background: #0B0A08; }}
#glow {{ position: absolute; inset: -200px; background:
   radial-gradient(700px 600px at 80% 12%, rgba(232,165,75,.16), transparent 62%),
   radial-gradient(700px 700px at 12% 92%, rgba(20,153,140,.10), transparent 60%); }}
#grid {{ position: absolute; inset: -120px 0; background-image: linear-gradient(rgba(232,165,75,.05) 1px, transparent 1px),
   linear-gradient(90deg, rgba(232,165,75,.05) 1px, transparent 1px); background-size: 60px 60px; }}
#logo {{ position: absolute; left: 96px; top: 250px; font-size: 52px; }}
.scene {{ position: absolute; left: 96px; right: 120px; top: 0; bottom: 0; display: flex; flex-direction: column; justify-content: center;
   padding: 340px 0 440px; opacity: 0; will-change: transform, opacity, filter; }}
.mark {{ display: inline-flex; align-items: baseline; font-weight: 600; letter-spacing: -0.02em; }}
.mark svg {{ width: .66em; height: .76em; margin: 0 .07em; transform: translateY(.015em); overflow: visible; }}
.kicker {{ display: flex; align-items: center; gap: 16px; color: #E8A54B; font-size: 30px; font-weight: 500; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 40px; }}
.kicker::before {{ content: ""; width: 52px; height: 2px; background: currentColor; opacity: .6; }}
.h1 {{ font-size: 128px; font-weight: 600; line-height: 1.0; letter-spacing: -0.045em; }}
.h2 {{ font-size: 96px; font-weight: 600; line-height: 1.04; letter-spacing: -0.035em; }}
.h3 {{ font-size: 68px; font-weight: 600; line-height: 1.1; letter-spacing: -0.025em; }}
.p {{ font-size: 46px; line-height: 1.38; color: #C4B8A8; }}
.ln {{ display: block; overflow: hidden; padding-bottom: .1em; margin-bottom: -.1em; }}
.ln > span {{ display: inline-block; transform: translateY(115%); }}
.am {{ color: #E8A54B; }} .rd {{ color: #FF7B7B; }} .tl {{ color: #14998C; }} .dim {{ color: #9C9082; }}
.mono {{ font-family: JBM, monospace; }}
.bubble {{ border-radius: 36px; padding: 30px 40px; font-size: 46px; line-height: 1.32; max-width: 820px; }}
.me {{ margin-left: auto; background: #1E1A15; border: 2px solid rgba(232,214,186,.14); border-bottom-right-radius: 10px; }}
.bot {{ background: rgba(20,153,140,.13); border: 2px solid rgba(20,153,140,.45); border-bottom-left-radius: 10px; position: relative; }}
.card {{ border: 2px solid rgba(232,214,186,.14); background: rgba(232,196,120,.05); border-radius: 32px; padding: 36px 44px; }}
.row {{ display: flex; align-items: center; gap: 28px; }}
.chip {{ display: inline-flex; align-items: center; min-height: 92px; padding: 0 36px; border-radius: 24px; background: #161310;
   border: 2px solid rgba(232,214,186,.14); font-size: 44px; font-weight: 500; }}
.tick {{ width: 72px; height: 72px; flex: none; border-radius: 20px; display: grid; place-items: center; background: #E8A54B; color: #141413; font-size: 44px; font-weight: 600; }}
.cross {{ background: #FF7B7B; }}
.num {{ width: 96px; height: 96px; flex: none; border-radius: 26px; display: grid; place-items: center; font-size: 44px; font-weight: 600; background: #161310;
   border: 2px solid rgba(232,214,186,.14); color: #E8A54B; }}
.bar {{ height: 92px; border-radius: 22px; background: #E8A54B; transform-origin: left center; display: flex; align-items: center; padding: 0 30px;
   color: #141413; font-size: 40px; font-weight: 600; white-space: nowrap; }}
.field {{ border: 2px solid rgba(232,214,186,.18); border-radius: 20px; padding: 0 28px; height: 62px; display: flex; align-items: center;
   font-size: 32px; color: #9C9082; margin-bottom: 10px; position: relative; overflow: hidden; }}
.strike-line {{ position: absolute; left: 20px; right: 20px; top: 50%; height: 6px; background: #FF7B7B; transform-origin: left; transform: scaleX(0); border-radius: 3px; }}
.strike {{ position: relative; display: inline-block; }}
.term {{ background: #0F0D0B; border: 2px solid rgba(232,214,186,.14); border-radius: 28px; padding: 36px 40px; font-family: JBM, monospace; font-size: 36px; line-height: 1.6; }}
.btn {{ display: inline-flex; align-items: center; min-height: 120px; padding: 0 60px; border-radius: 999px; background: #E8A54B; color: #141413; font-size: 46px; font-weight: 600; }}
.stamp {{ position: absolute; padding: 14px 26px; border: 5px solid #FF7B7B; border-radius: 16px; color: #FF7B7B; font-size: 46px; font-weight: 600;
   letter-spacing: .12em; background: rgba(11,10,8,.88); }}
#sweep {{ position: absolute; left: -40px; right: -40px; top: -160px; height: 2240px; transform: translateY(100%);
   background: linear-gradient(180deg, rgba(243,238,230,.16) 0%, rgba(243,238,230,.07) 7%, rgba(243,238,230,.05) 93%, rgba(243,238,230,.14) 100%);
   backdrop-filter: blur(34px) saturate(1.25) brightness(.9); -webkit-backdrop-filter: blur(34px) saturate(1.25) brightness(.9);
   border-top: 2px solid rgba(243,238,230,.28); border-bottom: 2px solid rgba(243,238,230,.18);
   box-shadow: 0 -30px 80px rgba(0,0,0,.35), 0 30px 80px rgba(0,0,0,.35); }}
#sweep::after {{ content: ""; position: absolute; inset: 0; opacity: .5;
   background: radial-gradient(900px 500px at 30% 20%, rgba(232,165,75,.10), transparent 60%),
               radial-gradient(800px 600px at 80% 80%, rgba(20,153,140,.08), transparent 60%); }}
"""

JS = r"""
const $ = id => document.getElementById(id);
const clamp = (x, a=0, b=1) => Math.min(b, Math.max(a, x));
const prog = (t, a, d) => clamp((t - a) / d);
const eo = x => 1 - Math.pow(1 - clamp(x), 3);
const eio = x => { x = clamp(x); return x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3) / 2; };
const eback = x => { x = clamp(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3*Math.pow(x-1,3) + c1*Math.pow(x-1,2); };
const scenes = [...document.querySelectorAll('.scene')];
const fxs = [...document.querySelectorAll('.fx')];
fxs.forEach(el => { if (el.dataset.fx === 'collapse') el.dataset.h = el.offsetHeight; });

function sceneOf(el) { return el.closest('.scene'); }

function render(t) {
  $('glow').style.transform = `translate(${Math.sin(t*.35)*40}px, ${Math.cos(t*.3)*30}px)`;
  $('grid').style.transform = `translateY(${(t*14) % 60}px)`;
  scenes.forEach(sc => {
    const a = +sc.dataset.a, b = +sc.dataset.b, tin = sc.dataset.tin, tout = sc.dataset.tout;
    if (t < a - .001 || t > b + .001) { sc.style.opacity = 0; return; }
    let op = 1, s = 1, ty = 0, blur = 0;
    const pi = eo(prog(t, a, .55));
    if (tin === 'zoom') { s *= 1.08 - .08*pi; blur += 18*(1 - pi); op *= pi; }
    if (tin === 'up') { ty += 160*(1 - pi); op *= pi; }
    const po = eio(prog(t, b - .4, .4));
    if (tout === 'zoom') { s *= 1 - .06*po; blur += 14*po; op *= 1 - po; }
    if (tout === 'up') { ty -= 160*po; op *= 1 - po; }
    sc.style.opacity = op;
    sc.style.transform = `translateY(${ty}px) scale(${s})`;
    sc.style.filter = blur > .2 ? `blur(${blur}px)` : 'none';
  });
  fxs.forEach(el => {
    const sc = sceneOf(el), at = (sc ? +sc.dataset.a : 0) + (+el.dataset.at || 0), k = el.dataset.fx;
    const d = +(el.dataset.d || .5);
    const p = prog(t, at, d);
    if (k === 'mask') {
      [...el.querySelectorAll('.ln > span')].forEach((s, i) => {
        const q = eo(prog(t, at + i*.09, .55)); s.style.transform = `translateY(${115*(1-q)}%)`; });
    } else if (k === 'rise') { const q = eo(p); el.style.opacity = q; el.style.transform = `translateY(${60*(1-q)}px)`; }
    else if (k === 'pop') { const q = eback(prog(t, at, .45)); el.style.opacity = clamp(p*3); el.style.transform = `scale(${.5 + .5*q}) rotate(${el.dataset.rot||0}deg)`; }
    else if (k === 'wipe') { const q = eio(p); el.style.clipPath = `inset(0 ${100*(1-q)}% 0 0 round 22px)`; }
    else if (k === 'draw') { const q = eo(p); el.style.transform = `scaleX(${q})`; el.style.opacity = q > 0 ? 1 : 0; }
    else if (k === 'type') { const s = el.dataset.text, n = Math.round(s.length*clamp((t-at)/d));
      el.textContent = s.slice(0, n) + ((t >= at && n < s.length && Math.floor(t*4)%2===0) ? '▍' : ''); }
    else if (k === 'count') { const v = (+el.dataset.from) + ((+el.dataset.to) - (+el.dataset.from))*eio(p);
      el.textContent = v.toFixed(+(el.dataset.dec||0)).replace('.', ',') + (el.dataset.suffix||''); }
    else if (k === 'strike') { el.querySelector('.strike-line').style.transform = `scaleX(${eo(p)})`; }
    else if (k === 'collapse') { const q = eio(p), h = +el.dataset.h;
      el.style.height = `${h*(1-q)}px`; el.style.marginBottom = `${10*(1-q)}px`; el.style.opacity = 1 - q;
      if (q > 0) el.style.borderWidth = `${2*(1-q)}px`; }
    else if (k === 'shake') { const j = prog(t, at, .45); el.style.transform = `translateX(${j>0&&j<1 ? Math.sin(j*Math.PI*7)*14*(1-j) : 0}px)`; }
    else if (k === 'show') { el.style.opacity = t >= at ? 1 : 0; }
    else if (k === 'hide') { el.style.display = t >= at ? 'none' : ''; }
    else if (k === 'recolor') { const on = t >= at; el.style.borderColor = on ? el.dataset.b2 : ''; el.style.background = on ? el.dataset.bg2 : ''; }
  });
  const sw = $('sweep');
  let y = 100;
  SWEEPS.forEach(s => {
    if (t >= s - .4 && t < s) y = 100 * (1 - eio(prog(t, s - .4, .4)));
    else if (t >= s && t < s + .4) y = -100 * eio(prog(t, s, .4));
  });
  sw.style.transform = `translateY(${y}%)`;
}
"""


# ---------- markup helpers ----------
def kicker(text, at=0.0):
    return f'<p class="kicker fx" data-fx="rise" data-at="{at}">{text}</p>'


def mask(lines, cls="h1", at=0.0, style=""):
    inner = "".join(f'<span class="ln"><span>{ln}</span></span>' for ln in lines)
    return f'<div class="{cls} fx" data-fx="mask" data-at="{at}" style="{style}">{inner}</div>'


def fx(html_tag, kind, at, d=None, extra=""):
    """Wrap: html_tag is '<tag attrs>content</tag>'; inject fx attrs into the first tag."""
    dd = f' data-d="{d}"' if d is not None else ""
    i = html_tag.index(">")
    head = html_tag[:i]
    if 'class="' in head:
        head = head.replace('class="', 'class="fx ', 1)
    else:
        head += ' class="fx"'
    return f'{head} data-fx="{kind}" data-at="{at}"{dd} {extra}{html_tag[i:]}'


def scene(a, b, body, tin="zoom", tout="zoom", style=""):
    return f'<div class="scene" data-a="{a}" data-b="{b}" data-tin="{tin}" data-tout="{tout}" style="{style}">{body}</div>'


def endcard(a, b, title, sub, button):
    body = (f'<svg class="fx" data-fx="pop" data-at="0.05" width="170" height="196" style="overflow:visible; margin-bottom:64px">'
            f'<use href="#flask" width="170" height="196"/></svg>'
            + mask(title, "h3", .15, "font-size:76px")
            + f'<p class="p fx" data-fx="rise" data-at=".55" style="margin-top:36px">{sub}</p>'
            + f'<div class="fx" data-fx="pop" data-at=".8" style="margin-top:64px"><span class="btn">{button}</span></div>'
            + '<p class="fx dim" data-fx="rise" data-at="1.0" style="margin-top:40px; font-size:38px">weblab.llc</p>')
    return scene(a, b, body, tin="cut", tout="cut")


def page(scenes_html, sweeps):
    return (f'<!doctype html><html lang="uk"><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div id="stage"><div id="glow"></div><div id="grid"></div>{DEFS}{INK_FLASK}'
            f'<div id="logo"><span class="mark">WebL<svg><use href="#flask"/></svg>b</span></div>'
            f'{"".join(scenes_html)}'
            f'<div id="sweep"></div>'
            f'</div><script>const SWEEPS = {list(sweeps)};{JS}window.render = render; render(0);</script></body></html>')


def render(slug, scenes_html, sweeps, duration, cover_t, out_root):
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    html_path = HERE / f"_reel_{slug}.html"
    html_path.write_text(page(scenes_html, sweeps))
    n = int(duration * FPS)
    mp4 = out / "reel.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
                           "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow",
                           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(html_path.resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        for i in range(n):
            t = i / FPS
            pg.evaluate(f"render({t:.4f})")
            ff.stdin.write(pg.screenshot(type="png"))
        pg.evaluate(f"render({cover_t})")
        pg.screenshot(path=str(out / "cover.jpg"), type="jpeg", quality=92)
        b.close()
    ff.stdin.close()
    ff.wait()
    html_path.unlink()
    return mp4


def preview(slug, scenes_html, sweeps, duration, out_root):
    """Contact sheet of mid-scene frames (no video) for a quick look."""
    from PIL import Image
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)
    html_path = HERE / f"_prev_{slug}.html"
    html_path.write_text(page(scenes_html, sweeps))
    import re
    bounds = [(float(a), float(b)) for a, b in re.findall(r'data-a="([\d.]+)" data-b="([\d.]+)"', "".join(scenes_html))]
    times = [min(b - .45, a + (b - a) * .85) for a, b in bounds] + [sweeps[0] if sweeps else 0]
    shots = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(html_path.resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(400)
        for t in times:
            pg.evaluate(f"render({t:.3f})")
            f = out / f"_p{t:05.2f}.png"
            pg.screenshot(path=str(f))
            shots.append(f)
        b.close()
    html_path.unlink()
    w, h = 432, 768
    sheet = Image.new("RGB", (len(shots) * (w + 12), h), (60, 60, 60))
    for i, f in enumerate(shots):
        sheet.paste(Image.open(f).resize((w, h)), (i * (w + 12), 0))
        f.unlink()
    path = out / "preview.png"
    sheet.save(path)
    return path
