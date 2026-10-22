"""Voiced versions of the WebLab Reels: scenes retimed to the ElevenLabs voiceover (vo/<slug>.mp3).

Voice starts at VO_DELAY s; every scene/fx time below is placed on the spoken phrase it illustrates
(phrase boundaries measured with ffmpeg silencedetect).

    python3 reels_vo.py [--preview] [<slug>…]   → out-reels-vo/<slug>/reel.mp4, cover.jpg, reel-vo.mp4
"""
import pathlib
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

from reel_engine import endcard, fx, kicker, mask, render, scene
from reels import BARS, FIELDS, TICK, num, quote, row

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out-reels-vo"
VO = HERE / "vo"
VO_DELAY = 0.3

R = {}

# voice: 0.3 Чатбот відповідає · 1.9 Агент — робить · 3.56 Бот скаже · 4.57 залиште номер ·
#        5.9 Агент перевірить календар… · 9.1 надішле запрошення… · 12.1 Будуємо… · 14.5 Напишіть «Агент» · end 16.0
R["reel-agent"] = dict(duration=17.0, cover=2.9, sweeps=[12.15], scenes=[
    scene(0, 3.25, mask(['Чатбот <span class="dim">відповідає.</span>'], at=.1, style="font-size:112px")
          + mask(['Агент — <span class="am">робить.</span>'], at=1.7, style="font-size:112px"),
          tin="cut", tout="zoom"),
    scene(3.1, 5.9, kicker("Чатбот")
          + fx('<div class="bubble me">Запишіть мене на дзвінок у четвер</div>', "rise", .05)
          + fx('<div class="bubble bot" style="margin-top:36px; width:max-content; max-width:820px">Звісно! Залиште номер — менеджер передзвонить.</div>', "rise", .45)
          + fx('<p class="p" style="margin-top:56px">Відповів — і все. Решту робить людина.</p>', "rise", 1.5),
          tin="zoom", tout="zoom"),
    scene(5.75, 12.15, kicker("ШІ-агент")
          + fx('<div class="bubble me">Запишіть мене на дзвінок у четвер</div>', "rise", .1)
          + '<div class="card" style="margin-top:40px">'
          + row(TICK, "Перевірив календар: четвер, 14:00", .75, 44) + row(TICK, "Створив угоду в CRM", 1.95, 44)
          + row(TICK, "Надіслав запрошення на пошту", 3.4, 44) + row(TICK, "Нагадає за годину до дзвінка", 4.6, 44) + "</div>",
          tin="zoom", tout="cut"),
    endcard(12.15, 17.0, ["Будуємо і ботів,", '<span class="am">і агентів</span>'],
            "З обмеженими правами, журналом дій і підтвердженням людиною.", None, btn_at=.8),
])

# voice: 0.3 У вас є бекап? · 1.8 А ви хоч раз з нього відновлювались? · 3.9 Дізнатися, що він битий,
#        5.5 у день аварії — найдорожче · 7.9 Тримайте копії окремо · 9.5 кілька версій · 10.6 тестуйте… · 12.9 Напишіть · end 14.75
R["reel-backup"] = dict(duration=17.0, cover=3.0, sweeps=[7.75, 12.85], scenes=[
    scene(0, 3.75, kicker("Безпека") + mask(["У вас є бекап?"], at=.1, style="font-size:100px")
          + mask(['<span class="am">А відновлювались</span>', '<span class="am">з нього?</span>'], at=1.6, style="font-size:100px"),
          tin="cut", tout="zoom"),
    scene(3.6, 7.75, '<div class="term">'
          + '<div><span class="am">$ </span><span class="fx" data-fx="type" data-at=".1" data-d=".9" data-text="restore backup-2026-10.tar.gz"></span></div>'
          + fx('<div class="dim">unpacking…</div>', "show", 1.05)
          + fx('<div><div class="rd fx" data-fx="shake" data-at="1.45">ERROR: archive is corrupted</div></div>', "show", 1.45)
          + fx('<div class="rd">ERROR: no valid copy found</div>', "show", 1.75) + "</div>"
          + mask(["Дізнатися це", '<span class="rd">в день аварії</span> —', "найдорожче."], "h3", 1.95, "margin-top:56px; font-size:64px"),
          tin="zoom", tout="cut"),
    scene(7.75, 12.85, mask(["Бекап, з якого ніхто", "не відновлювався, —", '<span class="am">не бекап.</span>'], "h2", .1, "font-size:84px")
          + row(TICK, "Копії окремо від сайту", .45) + row(TICK, "Кілька версій, а не одна", 1.8) + row(TICK, "Тест відновлення щомісяця", 2.85),
          tin="cut", tout="cut"),
    endcard(12.85, 17.0, ["Беремо сайти", '<span class="am">на підтримку</span>'],
            "Оновлення, бекапи, моніторинг — і перевірене відновлення.", None, btn_at=.8),
])


def form_card(strikes, collapse_at):
    out, k = [], 0
    for name, drop in FIELDS:
        if drop:
            out.append(f'<div class="field fx" data-fx="collapse" data-at="{collapse_at + k*.07:.2f}" data-d=".4">{name}'
                       f'<i class="strike-line fx" data-fx="draw" data-at="{strikes[k]:.2f}" data-d=".3" style="transform-origin:left"></i></div>')
            k += 1
        else:
            out.append(f'<div class="field" style="color:#F3EEE6; border-color:rgba(232,165,75,.6)">{name}</div>')
    return ('<div class="card" style="padding:30px 36px 34px"><p style="font-size:38px; font-weight:600; margin-bottom:20px">Заявка</p>'
            + "".join(out) + '<div class="btn" style="min-height:76px; font-size:34px; margin-top:6px">Надіслати</div></div>')


# voice: 0.3 Ваша форма вбиває заявки · 2.7 Ім'я, прізвище, пошта, компанія, посада… · 6.5 Для першого контакту досить двох полів ·
#        9.05 Напишіть «Форма» — подивимось на ваш сайт · end 11.85
R["reel-form-fields"] = dict(duration=13.9, cover=1.6, sweeps=[8.85], scenes=[
    scene(0, 2.75, kicker("UX") + mask(["Ваша форма", '<span class="rd">вбиває</span>', "заявки"], at=.1), tin="cut", tout="zoom"),
    scene(2.6, 8.85, fx(form_card([.75, 1.35, 2.05, 2.8, 3.05, 3.25, 3.45], 3.7), "rise", .1)
          + mask(["Для першого контакту", '<span class="am">досить двох полів.</span>'], "h3", 3.95, "margin-top:48px; font-size:62px"),
          tin="zoom", tout="cut"),
    endcard(8.85, 13.9, ["Робимо сайти,", "які збирають", '<span class="am">заявки</span>'],
            "Пройдемо шлях клієнта від першого екрана до форми.", None, btn_at=.8),
])

# voice (seo-fix take): 0.3 Після цих фраз сайт переробляють · 3.05 «SEO зробимо потім» · 4.7 «Головне — щоб було красиво» ·
#        6.8 «Мобільна — це зменшений десктоп» · 9.25 SEO, швидкість і мобільну версію закладають на старті · 13.3 Напишіть «Старт» · end 14.9
R["reel-site-myths"] = dict(duration=19.1, cover=2.4, sweeps=[9.15, 13.2], scenes=[
    scene(0, 2.95, kicker("Три фрази") + mask(["Після цих фраз", 'сайт <span class="rd">переробляють</span>'], at=.1, style="font-size:116px"),
          tin="cut", tout="zoom"),
    scene(2.8, 9.15, quote("«SEO зробимо потім»", .2, 1.4) + quote("«Головне — щоб було красиво»", 1.9, 3.5)
          + quote("«Мобільна — це зменшений десктоп»", 4.0, 5.9), tin="zoom", tout="cut", style="justify-content:center"),
    scene(9.15, 13.2, mask(["SEO, швидкість", "і мобільну версію", "закладають", '<span class="am">на старті.</span>'], "h2", .15),
          tin="cut", tout="cut"),
    endcard(13.2, 19.1, ["Будуємо сайти", '<span class="am">без переробок</span>'],
            "SEO-база, швидкість і мобільна версія — з першого дня.", None, btn_at=.8),
])

# voice: 0.3 «Скільки коштує сайт?» · 2.1 — неправильне питання · 3.9 Ціна — це дизайн, розробка, інтеграції, контент, запуск і підтримка ·
#        9.75 Правильне питання: що входить у ціну? · 12.75 Напишіть «Кошторис» — розпишемо за етапами · end 15.6
R["reel-site-price"] = dict(duration=16.9, cover=2.8, sweeps=[9.75, 12.65], scenes=[
    scene(0, 3.75, kicker("Ціни") + mask(["«Скільки коштує", "сайт?»"], at=.1)
          + fx('<p class="h3 rd" style="margin-top:32px">— неправильне питання.</p>', "rise", 1.8), tin="cut", tout="zoom"),
    scene(3.6, 9.75, kicker("З чого складається ціна", .1)
          + "".join(fx(f'<div class="bar" style="margin-top:20px; {"" if i % 2 == 0 else "background:#2A241D; color:#F3EEE6"}">{b}</div>',
                       "draw", 1.15 + i * .78, .4) for i, b in enumerate(BARS)),
          tin="zoom", tout="cut"),
    scene(9.75, 12.65, mask(["Правильне питання:", '<span class="am">що входить</span>', '<span class="am">у ціну?</span>'], "h2", .15)
          + fx('<p class="p" style="margin-top:44px">І що не входить — це теж має бути в кошторисі.</p>', "rise", 1.5),
          tin="cut", tout="cut"),
    endcard(12.65, 16.9, ["Кошторис", '<span class="am">з розбивкою</span>', '<span class="am">за етапами</span>'],
            "Щоб ви бачили, за що платите.", None, btn_at=.8),
])

# voice: 0.3 Ваш сайт вантажиться шість секунд? · 2.8 За даними Google, більше половини… після трьох ·
#        7.9 Найчастіше винні важкі фото, чужі скрипти і сторінки… · 13.55 Перевірте свій сайт — і напишіть нам «Швидкість» · end 16.7
R["reel-site-speed"] = dict(duration=17.8, cover=2.3, sweeps=[13.45], scenes=[
    scene(0, 2.9, kicker("Швидкість") + mask(["Ваш сайт", "вантажиться"], at=.1)
          + '<div class="h1 am fx" data-fx="count" data-at=".4" data-d="1.1" data-from="0" data-to="6" data-dec="1" data-suffix=" с" '
            'style="font-size:240px; margin-top:24px">0,0 с</div>',
          tin="cut", tout="zoom"),
    scene(2.75, 7.85, kicker("За даними Google", .1)
          + '<div class="h1 am fx" data-fx="count" data-at=".3" data-d="1.2" data-from="0" data-to="53" data-suffix="%" style="font-size:230px">0%</div>'
          + mask(["мобільних відвідувань", "обриваються, якщо сторінка", 'вантажиться <span class="am">довше 3 с</span>'], "h3", 1.0, "margin-top:28px; font-size:62px"),
          tin="zoom", tout="zoom"),
    scene(7.7, 13.45, kicker("Що гальмує") + mask(["Три причини", "з нашого досвіду"], "h2", .1, "font-size:84px")
          + row(num(1), "Важкі фото без стиснення", .9) + row(num(2), "Чужі скрипти: чати, пікселі, віджети", 1.9)
          + row(num(3), "Сторінка збирається лише в браузері", 2.85),
          tin="zoom", tout="cut"),
    endcard(13.45, 17.8, ["Робимо сайти,", "що відкриваються", '<span class="am">швидко</span>'],
            "Перевірте свій сайт у PageSpeed Insights — це безкоштовно.", None, btn_at=.8),
])

# voice: 0.3 Ваш ШІ-чатбот бреше клієнтам · 2.86 Клієнт питає про доставку · 4.6 а бот впевнено вигадує ·
#        6.5 Бо модель не знає… · 9.0 Вона просто пише найправдоподібніше · 11.5 Рішення — RAG: спершу знайти… ·
#        15.7 потім відповісти · 17.2 З джерелом · 18.3 ВебЛеб. Довірте нам розробку вашого ШІ-асистента · end 22.0
R["reel-rag-chatbot"] = dict(duration=22.8, cover=1.9, sweeps=[6.45, 18.1], scenes=[
    scene(0, 2.85, kicker("ШІ · під капотом") + mask(
        ["Ваш ШІ-чатбот", '<span class="rd fx" data-fx="shake" data-at="1.3" style="display:inline-block">бреше</span> клієнтам'], at=.1),
        tin="cut", tout="zoom"),
    scene(2.7, 6.45,
          '<p class="dim" style="font-size:28px; text-align:right; margin:0 8px 14px 0">Клієнт</p>'
          + '<div class="bubble me"><span class="fx" data-fx="type" data-at=".2" data-d="1.1" '
            'data-text="Скільки коштує доставка до Львова?"></span></div>'
          + fx('<p class="dim" style="font-size:28px; margin:56px 0 14px 8px">Чатбот</p>', "rise", 1.35, .3)
          + fx('<div style="width:max-content">', "rise", 1.4, .3)
          + '<div class="bubble bot fx" data-fx="recolor" data-at="2.9" data-b2="rgba(255,123,123,.85)" data-bg2="rgba(255,123,123,.10)">'
          + fx('<span class="mono" style="font-size:40px">• • •</span>', "hide", 1.9)
          + '<span class="fx" data-fx="type" data-at="1.9" data-d=".8" data-text="Безкоштовно від 500 грн, буде завтра!"></span>'
          + fx('<div class="stamp" style="right:-24px; bottom:-64px">ВИГАДАНО</div>', "pop", 2.9, extra='data-rot="-8"')
          + "</div></div>"
          + fx('<p class="mono rd" style="font-size:34px; margin-top:104px">// в умовах доставки такого немає</p>', "rise", 3.2),
          tin="zoom", tout="cut"),
    scene(6.45, 11.45, kicker("Чому так", .1) + mask(["Модель не знає", "ваших цін і умов."], "h2", .2)
          + mask(["Тож пише", '<span class="am">найправдо\u00adподібніше.</span>'], "h2", 2.55, "margin-top:56px; color:#C4B8A8; font-size:80px"),
          tin="cut", tout="zoom"),
    scene(11.3, 18.1, kicker("Як це лікується") + mask(["RAG: спершу знайти,", "потім відповісти"], "h2", .2, "font-size:86px")
          + '<div style="margin-top:40px">' + row(num(1), "Питання клієнта", 1.2) + row(num(2), "Пошук у вашій базі знань", 2.6)
          + row(num(3), "Відповідь з джерелом", 4.4) + "</div>"
          + fx('<div class="bubble bot" style="margin-top:56px; font-size:40px">Доставка до Львова — за тарифами перевізника, 1–2 дні.'
               '<p class="mono tl" style="margin-top:14px; font-size:28px">Джерело: «Доставка і оплата»</p></div>', "rise", 5.85),
          tin="zoom", tout="cut"),
    endcard(18.1, 22.8, ["Будуємо ШІ-асистентів,", "які відповідають", '<span class="am">з ваших даних</span>'],
            "RAG, агенти, інтеграції з CRM та ERP.", None),
])

# voice: 0.3 Перевірте свій сайт прямо зараз · 2.5 Відкрийте з телефону… · 5.85 Натисніть на номер… · 8.15 Надішліть заявку… ·
#        10.5 Хоч одне «ні» — ви втрачаєте клієнтів · 14.0 ВебЛеб. Довірте нам аудит вашого сайту · end ~17.0
R["reel-site-test"] = dict(duration=17.8, cover=1.9, sweeps=[13.65], scenes=[
    scene(0, 2.5, kicker("Тест на 30 секунд") + mask(["Перевірте", "свій сайт", '<span class="am">прямо зараз</span>'], at=.1),
          tin="cut", tout="zoom"),
    scene(2.35, 10.35, row(num(1), "Відкрийте з телефону.<br><span class='am'>Завантажився за 3 секунди?</span>", .15, 56)
          + row(num(2), "Натисніть на номер.<br><span class='am'>Пішов дзвінок?</span>", 3.5, 56)
          + row(num(3), "Надішліть заявку.<br><span class='am'>Вона дійшла?</span>", 5.8, 56),
          tin="zoom", tout="zoom"),
    scene(10.2, 13.65, mask(["Хоч одне «ні» —", '<span class="rd">ви втрачаєте</span>', '<span class="rd">клієнтів.</span>'], "h2", .3),
          tin="zoom", tout="cut"),
    endcard(13.65, 17.8, ["Знайдемо, де сайт", '<span class="am">губить заявки</span>'],
            "Пройдемо шлях клієнта від першого екрана до форми.", None),
])

REELS = R


# ---------- audio: music bed ducked under the voice ----------
def load_voice(slug, sr):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(VO / f"{slug}.final.wav"), "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    v = sosfilt(butter(2, 80, "high", fs=sr, output="sos"), v)
    return v / (np.max(np.abs(v)) + 1e-9)


def envelope(x, sr, attack=.03, release=.35):
    from scipy.ndimage import maximum_filter1d
    from scipy.signal import lfilter
    # fast attack (running max over the attack window), smooth release (one-pole)
    peak = maximum_filter1d(np.abs(x), size=max(1, int(attack * sr)))
    r = np.exp(-1 / (release * sr))
    rel = lfilter([1 - r], [1, -r], peak)
    return np.maximum(rel, lfilter([1 - r], [1, -r], peak[::-1])[::-1] * 0.0 + rel)


def mix_voice(slug):
    import reel_audio
    reel_audio.REELS = REELS  # soundtrack() reads timings from here
    sr = reel_audio.SR
    music = reel_audio.soundtrack(slug).astype(np.float64)
    n = len(music)
    v = np.zeros(n)
    voice = load_voice(slug, sr)
    i = int(VO_DELAY * sr)
    v[i:i + len(voice)] = voice[: n - i]
    env = envelope(v, sr)
    act = np.clip(env / 0.08, 0, 1)  # 0 = silence, 1 = speech
    duck = 0.42 - 0.24 * act         # bed at ~-7.5 dB in gaps, ~-15 dB under speech
    out = music * duck[:, None] + np.stack([v, v], axis=1) * 0.92
    out /= np.max(np.abs(out)) + 1e-9
    d = OUT / slug
    wav = d / "mix.wav"
    wavfile.write(str(wav), sr, (out * 0.95).astype(np.float32))
    dst = d / "reel-vo.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(d / "reel.mp4"), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(dst)], check=True)
    return dst


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--preview"]:
        from reel_engine import preview
        for slug in args[1:] or list(REELS):
            r = REELS[slug]; print(preview(slug, r["scenes"], r["sweeps"], r["duration"], OUT))
        sys.exit()
    if args[:1] == ["--audio"]:
        for slug in args[1:] or list(REELS):
            print(mix_voice(slug), flush=True)
        sys.exit()
    for slug in args or list(REELS):
        r = REELS[slug]
        render(slug, r["scenes"], r["sweeps"], r["duration"], r["cover"], OUT)
        print(mix_voice(slug), flush=True)
