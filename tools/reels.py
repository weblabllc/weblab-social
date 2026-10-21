"""WebLab Reels, week of 23–30.10. Usage: python3 reels.py <slug> [<slug>…]  (no args = all)."""
import pathlib
import sys

from reel_engine import endcard, fx, kicker, mask, render, scene

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out-reels"

TICK = ('<span class="tick"><svg viewBox="0 0 24 24" width="44" height="44"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" '
        'stroke="#141413" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')


def row(lead, text, at, size=54):
    return fx(f'<div class="row" style="margin-top:36px">{lead}<p style="font-size:{size}px; font-weight:500; line-height:1.2; letter-spacing:-.015em">{text}</p></div>', "rise", at)


def num(n):
    return f'<span class="num">{n}</span>'


REELS = {}

# 1 — the approved trial, rebuilt on the engine
REELS["reel-rag-chatbot"] = dict(duration=17.2, cover=1.9, sweeps=[7.9, 14.6], scenes=[
    scene(0, 2.6, kicker("ШІ · під капотом") + mask(
        ["Ваш ШІ-чатбот", '<span class="rd fx" data-fx="shake" data-at="1.3" style="display:inline-block">бреше</span> клієнтам'], at=.1),
        tin="cut", tout="zoom"),
    scene(2.45, 7.9,
          '<p class="dim" style="font-size:28px; text-align:right; margin:0 8px 14px 0">Клієнт</p>'
          + '<div class="bubble me"><span class="fx" data-fx="type" data-at=".3" data-d="1.1" '
            'data-text="Скільки коштує доставка до Львова?"></span></div>'
          + fx('<p class="dim" style="font-size:28px; margin:56px 0 14px 8px">Чатбот</p>', "rise", 1.4, .3)
          + fx('<div style="width:max-content">', "rise", 1.45, .3)
          + '<div class="bubble bot fx" data-fx="recolor" data-at="3.5" data-b2="rgba(255,123,123,.85)" data-bg2="rgba(255,123,123,.10)">'
          + fx('<span class="mono" style="font-size:40px">• • •</span>', "hide", 2.3)
          + '<span class="fx" data-fx="type" data-at="2.3" data-d=".8" data-text="Безкоштовно від 500 грн, буде завтра!"></span>'
          + fx('<div class="stamp" style="right:-24px; bottom:-64px">ВИГАДАНО</div>', "pop", 3.5, extra='data-rot="-8"')
          + "</div></div>"
          + fx('<p class="mono rd" style="font-size:34px; margin-top:104px">// в умовах доставки такого немає</p>', "rise", 3.8),
          tin="zoom", tout="cut"),
    scene(7.9, 10.6, kicker("Чому так", .25) + mask(["Модель не знає", "ваших цін і умов."], "h2", .3)
          + mask(["Тож пише", '<span class="am">найправдо­подібніше.</span>'], "h2", 1.2, "margin-top:56px; color:#C4B8A8; font-size:80px"),
          tin="cut", tout="zoom"),
    scene(10.45, 14.6, kicker("Як це лікується") + mask(["RAG: спершу знайти,", "потім відповісти"], "h2", .1, "font-size:86px")
          + '<div style="margin-top:40px">' + row(num(1), "Питання клієнта", .9) + row(num(2), "Пошук у вашій базі знань", 1.2)
          + row(num(3), "Відповідь з джерелом", 1.5) + "</div>"
          + fx('<div class="bubble bot" style="margin-top:56px; font-size:40px">Доставка до Львова — за тарифами перевізника, 1–2 дні.'
               '<p class="mono tl" style="margin-top:14px; font-size:28px">Джерело: «Доставка і оплата»</p></div>', "rise", 2.1),
          tin="zoom", tout="cut"),
    endcard(14.6, 17.2, ["Будуємо ШІ-асистентів,", "які відповідають", '<span class="am">з ваших даних</span>'],
            "RAG, агенти, інтеграції з CRM та ERP.", "Напишіть «RAG» у дірект"),
])

REELS["reel-site-speed"] = dict(duration=14.2, cover=2.3, sweeps=[11.4], scenes=[
    scene(0, 3.6, kicker("Швидкість") + mask(["Ваш сайт", "вантажиться"], at=.1)
          + '<div class="h1 am fx" data-fx="count" data-at=".6" data-d="1.8" data-from="0" data-to="6" data-dec="1" data-suffix=" с" '
            'style="font-size:240px; margin-top:24px">0,0 с</div>',
          tin="cut", tout="zoom"),
    scene(3.45, 7.2, kicker("За даними Google", .15)
          + '<div class="h1 am fx" data-fx="count" data-at=".3" data-d="1.2" data-from="0" data-to="53" data-suffix="%" style="font-size:230px">0%</div>'
          + mask(["мобільних відвідувань", "обриваються, якщо сторінка", 'вантажиться <span class="am">довше 3 с</span>'], "h3", .7, "margin-top:28px; font-size:62px"),
          tin="zoom", tout="zoom"),
    scene(7.05, 11.4, kicker("Що гальмує") + mask(["Три причини", "з нашого досвіду"], "h2", .1, "font-size:84px")
          + row(num(1), "Важкі фото без стиснення", .8) + row(num(2), "Чужі скрипти: чати, пікселі, віджети", 1.2)
          + row(num(3), "Сторінка збирається лише в браузері", 1.6),
          tin="zoom", tout="cut"),
    endcard(11.4, 14.2, ["Робимо сайти,", "що відкриваються", '<span class="am">швидко</span>'],
            "Перевірте свій у PageSpeed Insights. Червоні цифри — пишіть.", "Напишіть «ШВИДКІСТЬ»"),
])

FIELDS = [("Ім’я", False), ("Прізвище", True), ("Email", True), ("Телефон або Telegram", False), ("Компанія", True),
          ("Посада", True), ("Місто", True), ("Бюджет", True), ("Як ви про нас дізналися?", True)]


def form_card():
    out, k = [], 0
    for name, drop in FIELDS:
        if drop:
            out.append(f'<div class="field fx" data-fx="collapse" data-at="{3.6 + k*.07:.2f}" data-d=".4">{name}'
                       f'<i class="strike-line fx" data-fx="draw" data-at="{1.2 + k*.22:.2f}" data-d=".3" style="transform-origin:left"></i></div>')
            k += 1
        else:
            out.append(f'<div class="field" style="color:#F3EEE6; border-color:rgba(232,165,75,.6)">{name}</div>')
    return ('<div class="card" style="padding:30px 36px 34px"><p style="font-size:38px; font-weight:600; margin-bottom:20px">Заявка</p>'
            + "".join(out) + '<div class="btn" style="min-height:76px; font-size:34px; margin-top:6px">Надіслати</div></div>')


REELS["reel-form-fields"] = dict(duration=11.2, cover=1.6, sweeps=[8.4], scenes=[
    scene(0, 2.4, kicker("UX") + mask(["Ваша форма", '<span class="rd">вбиває</span>', "заявки"], at=.1), tin="cut", tout="zoom"),
    scene(2.25, 8.4, fx(form_card(), "rise", .1)
          + mask(["Для першого контакту", '<span class="am">досить двох полів.</span>'], "h3", 4.4, "margin-top:48px; font-size:62px"),
          tin="zoom", tout="cut"),
    endcard(8.4, 11.2, ["Робимо сайти,", "які збирають", '<span class="am">заявки</span>'],
            "Пройдемо шлях клієнта від першого екрана до форми.", "Напишіть «ФОРМА» у дірект"),
])

REELS["reel-backup"] = dict(duration=13.4, cover=1.9, sweeps=[6.6, 10.6], scenes=[
    scene(0, 2.6, kicker("Безпека") + mask(["У вас є бекап?", '<span class="am">А відновлювались</span>', '<span class="am">з нього?</span>'], at=.1,
                                           style="font-size:112px"), tin="cut", tout="zoom"),
    scene(2.45, 6.6, '<div class="term">'
          + '<div><span class="am">$ </span><span class="fx" data-fx="type" data-at=".3" data-d="1.1" data-text="restore backup-2026-10.tar.gz"></span></div>'
          + fx('<div class="dim">unpacking…</div>', "show", 1.5)
          + fx('<div><div class="rd fx" data-fx="shake" data-at="2.0">ERROR: archive is corrupted</div></div>', "show", 2.0)
          + fx('<div class="rd">ERROR: no valid copy found</div>', "show", 2.4) + "</div>"
          + mask(["Дізнатися це", '<span class="rd">в день аварії</span> —', "найдорожче."], "h3", 2.7, "margin-top:56px; font-size:64px"),
          tin="zoom", tout="cut"),
    scene(6.6, 10.6, mask(["Бекап, з якого ніхто", "не відновлювався, —", '<span class="am">не бекап.</span>'], "h2", .25, "font-size:84px")
          + row(TICK, "Копії окремо від сайту", 1.3) + row(TICK, "Кілька версій, а не одна", 1.6) + row(TICK, "Тест відновлення щомісяця", 1.9),
          tin="cut", tout="cut"),
    endcard(10.6, 13.4, ["Беремо сайти", '<span class="am">на підтримку</span>'],
            "Оновлення, бекапи, моніторинг — і перевірене відновлення.", "Напишіть «БЕКАП» у дірект"),
])

REELS["reel-agent"] = dict(duration=13.8, cover=1.8, sweeps=[10.8], scenes=[
    scene(0, 2.5, mask(['Чатбот <span class="dim">відповідає.</span>', 'Агент — <span class="am">робить.</span>'], at=.1, style="font-size:112px"),
          tin="cut", tout="zoom"),
    scene(2.35, 6.4, kicker("Чатбот")
          + fx('<div class="bubble me">Запишіть мене на дзвінок у четвер</div>', "rise", .2)
          + fx('<div class="bubble bot" style="margin-top:36px; width:max-content; max-width:820px">Звісно! Залиште номер — менеджер передзвонить.</div>', "rise", .9)
          + fx('<p class="p" style="margin-top:56px">Відповів — і все. Решту робить людина.</p>', "rise", 1.8),
          tin="zoom", tout="zoom"),
    scene(6.25, 10.8, kicker("ШІ-агент")
          + fx('<div class="bubble me">Запишіть мене на дзвінок у четвер</div>', "rise", .2)
          + '<div class="card" style="margin-top:40px">'
          + row(TICK, "Перевірив календар: четвер, 14:00", .9, 44) + row(TICK, "Створив угоду в CRM", 1.5, 44)
          + row(TICK, "Надіслав запрошення на пошту", 2.1, 44) + row(TICK, "Нагадає за годину до дзвінка", 2.7, 44) + "</div>",
          tin="zoom", tout="cut"),
    endcard(10.8, 13.8, ["Будуємо і ботів,", '<span class="am">і агентів</span>'],
            "З обмеженими правами, журналом дій і підтвердженням людиною.", "Напишіть «АГЕНТ» у дірект"),
])

BARS = ["Дизайн", "Розробка", "Інтеграції", "Контент", "Запуск", "Підтримка"]
REELS["reel-site-price"] = dict(duration=13.6, cover=1.9, sweeps=[7.6, 10.6], scenes=[
    scene(0, 2.6, kicker("Ціни") + mask(["«Скільки коштує", "сайт?»"], at=.1)
          + fx('<p class="h3 rd" style="margin-top:32px">— неправильне питання.</p>', "rise", 1.2), tin="cut", tout="zoom"),
    scene(2.45, 7.6, kicker("З чого складається ціна")
          + "".join(fx(f'<div class="bar" style="margin-top:20px; {"" if i % 2 == 0 else "background:#2A241D; color:#F3EEE6"}">{b}</div>',
                       "draw", .4 + i * .45, .4) for i, b in enumerate(BARS)),
          tin="zoom", tout="cut"),
    scene(7.6, 10.6, mask(["Правильне питання:", '<span class="am">що входить</span>', '<span class="am">у ціну?</span>'], "h2", .25)
          + fx('<p class="p" style="margin-top:44px">І що не входить — це теж має бути в кошторисі.</p>', "rise", 1.2),
          tin="cut", tout="cut"),
    endcard(10.6, 13.6, ["Кошторис", '<span class="am">з розбивкою</span>', '<span class="am">за етапами</span>'],
            "Щоб ви бачили, за що платите.", "Напишіть «КОШТОРИС»"),
])

REELS["reel-site-test"] = dict(duration=14.8, cover=1.9, sweeps=[12.0], scenes=[
    scene(0, 2.5, kicker("Тест на 30 секунд") + mask(["Перевірте", "свій сайт", '<span class="am">прямо зараз</span>'], at=.1),
          tin="cut", tout="zoom"),
    scene(2.35, 9.4, row(num(1), "Відкрийте з телефону.<br><span class='am'>Завантажився за 3 секунди?</span>", .3, 56)
          + row(num(2), "Натисніть на номер.<br><span class='am'>Пішов дзвінок?</span>", 2.1, 56)
          + row(num(3), "Надішліть заявку.<br><span class='am'>Вона дійшла?</span>", 3.9, 56),
          tin="zoom", tout="zoom"),
    scene(9.25, 12.0, mask(["Хоч одне «ні» —", '<span class="rd">ви втрачаєте</span>', '<span class="rd">клієнтів.</span>'], "h2", .2),
          tin="zoom", tout="cut"),
    endcard(12.0, 14.8, ["Знайдемо, де сайт", '<span class="am">губить заявки</span>'],
            "Пройдемо шлях клієнта від першого екрана до форми.", "Напишіть «АУДИТ» у дірект"),
])


def quote(text, at_in, at_strike):
    return fx(f'<div class="h3" style="margin-top:56px"><span class="strike fx" data-fx="strike" data-at="{at_strike}" data-d=".45">'
              f'{text}<i class="strike-line"></i></span></div>', "rise", at_in)


REELS["reel-site-myths"] = dict(duration=14.2, cover=1.8, sweeps=[8.6, 11.4], scenes=[
    scene(0, 2.4, kicker("Три фрази") + mask(["Після цих фраз", 'сайт <span class="rd">переробляють</span>'], at=.1, style="font-size:116px"),
          tin="cut", tout="zoom"),
    scene(2.25, 8.6, quote("«SEO зробимо потім»", .3, 1.2) + quote("«Головне — щоб було красиво»", 1.9, 2.8)
          + quote("«Мобільна — це зменшений десктоп»", 3.5, 4.4), tin="zoom", tout="cut", style="justify-content:center"),
    scene(8.6, 11.4, mask(["SEO, швидкість", "і мобільну версію", "закладають", '<span class="am">на старті.</span>'], "h2", .25),
          tin="cut", tout="cut"),
    endcard(11.4, 14.2, ["Будуємо сайти", '<span class="am">без переробок</span>'],
            "SEO-база, швидкість і мобільна версія — з першого дня.", "Напишіть «СТАРТ» у дірект"),
])

if __name__ == "__main__":
    if sys.argv[1:2] == ["--preview"]:
        from reel_engine import preview
        for slug in sys.argv[2:] or list(REELS):
            r = REELS[slug]; print(preview(slug, r["scenes"], r["sweeps"], r["duration"], OUT))
        sys.exit()
    for slug in (sys.argv[1:] or list(REELS)):
        r = REELS[slug]
        print(render(slug, r["scenes"], r["sweeps"], r["duration"], r["cover"], OUT), flush=True)
