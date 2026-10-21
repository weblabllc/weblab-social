"""'Paper' theme: light editorial variant of the WebLab carousels.

Same content model and markup as build_posts.py; the dark theme is remapped by
CSS and the flask mark is swapped for its on-light version (ink glass, darker
amber lip — as in the logo's inversion on the brand canvas).

    python3 build_paper.py <slug> [<slug>…]     # renders to out-paper/<slug>/NN.png
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_posts as bp  # noqa: E402
from build_posts import body, chk, cover, cta, nlist, slide, SAVE, SWIPE  # noqa: E402,F401

PAPER_CSS = """
<style>
:root {
  --ink: #F3EEE6;          /* slide ground */
  --ink-soft: #E9E2D6;
  --paper: #141413;        /* main text */
  --paper-dim: #3D372F;    /* body text, 10:1 */
  --paper-faint: #6E6457;  /* captions, 5:1 */
  --hair: rgba(20, 19, 19, 0.14);
  --amber: #8C5416;        /* small accent text, 5.4:1 */
  --amber-big: #B9762A;    /* large accent only, 3.2:1 */
  --teal: #0D7A70;
}
body { background: #ccc; color: var(--paper); }
.slide { background: var(--ink) !important; }
.grid { background-image:
    linear-gradient(rgba(20,19,19,.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(20,19,19,.05) 1px, transparent 1px) !important;
  mask-image: none !important; -webkit-mask-image: none !important; opacity: .9; }
.tl { color: var(--amber-big) !important; }
.kicker, .idx, .swipe, .list .k { color: var(--amber) !important; }
.idx span.l { background: rgba(140, 84, 22, .45) !important; }
.card { background: rgba(255,255,255,.55) !important; border-color: var(--hair) !important; }
.step .n { background: #fff !important; color: var(--amber) !important; }
.step .n.hl { background: var(--paper) !important; color: var(--ink) !important; }
.box { border-color: var(--paper) !important; }
.box svg path { stroke: var(--paper) !important; }
.tag { border-color: rgba(20,19,19,.28) !important; color: var(--paper-dim) !important; background: rgba(255,255,255,.5); }
.btn { background: var(--paper) !important; color: var(--ink) !important; }
.ghost { border-color: rgba(20,19,19,.35) !important; color: var(--paper) !important; }
.metric .v { color: var(--paper) !important; }
/* outlined index numbers instead of filled teal */
.big-n { color: transparent !important; -webkit-text-stroke: 3px var(--paper); }
/* pros/cons signs were inline-coloured for the dark theme */
[style*="#14998C"] { color: var(--teal) !important; }
[style*="#FF9D9D"] { color: #B4232C !important; }
/* cover: bigger headline and a solid ink footer band */
.slide:has(h1) h1 { font-size: 112px; letter-spacing: -0.04em; }
.slide:has(h1) .foot { margin: auto -96px -88px; padding: 44px 96px 48px; background: var(--paper); color: var(--ink); }
.slide:has(h1) .foot .swipe { color: #E8A54B !important; }
/* last slide: ink background, paper text */
.slide:has(.btn) { background: #141413 !important; color: #F3EEE6; }
.slide:has(.btn) .grid { display: none; }
.slide:has(.btn) h2, .slide:has(.btn) .mark { color: #F3EEE6; }
.slide:has(.btn) .lead { color: #C4B8A8; }
.slide:has(.btn) .kicker, .slide:has(.btn) .idx, .slide:has(.btn) .swipe { color: #E8A54B !important; }
.slide:has(.btn) .foot { color: #9C9082; }
.slide:has(.btn) .btn { background: #E8A54B !important; color: #141413 !important; }
.slide:has(.btn) .ghost { border-color: rgba(232,165,75,.5) !important; color: #F3EEE6 !important; }
.slide:has(.btn) .idx span.l { background: rgba(232,165,75,.45) !important; }
</style>
"""

# On-light flask for the content slides; the dark CTA slide keeps the original via #flask-dark.
DEFS = bp.defs.replace('<symbol id="flask" viewBox="68 16 344 396">', '<symbol id="flask" viewBox="68 16 344 396" overflow="visible">')
assert 'overflow="visible"' in DEFS
DEFS_DARK = DEFS.replace('id="flask"', 'id="flask-dark"').replace('id="fl"', 'id="fl-d"').replace(
    'url(#fl)', 'url(#fl-d)').replace('id="liq"', 'id="liq-d"').replace('url(#liq)', 'url(#liq-d)')
DEFS_LIGHT = DEFS.replace('stroke="#F0E2C8"', 'stroke="#141413"').replace(
    'stroke="#E8A54B"', 'stroke="#B9762A"').replace('stroke-width="30"', 'stroke-width="32"')


def cta_dark(title, lead, button):
    return cta(title, lead, button).replace('href="#flask"', 'href="#flask-dark"')


def note(text):
    return f'<div class="card" style="margin-top:44px"><p style="margin:0; font-size:30px; line-height:1.45;">{text}</p></div>'


def tags(*names):
    return ('<div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:72px;">'
            + "".join(f'<span class="tag">{n}</span>' for n in names) + "</div>")


NEW = {
    "2026-10-27-ux-mistakes": [
        ("cover", cover("UX", '6 помилок, через які сайт <span class="tl">втрачає заявки</span>',
                        "Відвідувач уже хотів написати — і пішов. Ось де це зазвичай стається."), SWIPE),
        ("b", body("Помилки 1–3", "На першому екрані", nlist([
            ("Незрозуміло, що ви робите", "Гасло замість простого речення: що, для кого і де."),
            ("Немає головної кнопки", "Або їх п’ять, і жодна не виглядає головною."),
            ("Попап через дві секунди", "Людина ще не прочитала заголовок, а її вже просять підписатись."),
        ])), None),
        ("b", body("Помилки 4–6", "На шляху до заявки", nlist([
            ("Форма на десять полів", "Для першого контакту досить імені й способу зв’язку."),
            ("Ані слова про ціну", "Хоча б вилка «від» знімає половину сумнівів."),
            ("Телефон не натискається", "На мобільному номер має одразу відкривати дзвінок."),
        ], 4)), None),
        ("cta", cta_dark("Знайдемо, де ваш сайт губить заявки", "Пройдемо шлях клієнта від першого екрана до форми.", "Написати в дірект"), SAVE),
    ],
    "2026-10-28-site-support": [
        ("cover", cover("Після запуску", 'Підтримка сайту: <span class="tl">за що ви платите</span> щомісяця',
                        "Сайт після релізу — як авто після покупки. Його треба обслуговувати, а не лише заправляти."), SWIPE),
        ("b", body("Що входить", "Регулярна робота, яку не видно", chk([
            ("Оновлення", "Залежності, CMS і плагіни — до того, як у них знайдуть діри."),
            ("Резервні копії", "Регулярні й перевірені: бекап, з якого ніхто не відновлювався, — не бекап."),
            ("Моніторинг", "Дізнаємося про падіння раніше за клієнтів."),
        ])), None),
        ("b", body("І ще", "Те, що дає результат", chk([
            ("Дрібні правки", "Тексти, банери, ціни — без окремого кошторису на кожну дрібницю."),
            ("Швидкість і SEO", "Слідкуємо, щоб сайт не «обростав» і не просідав у пошуку."),
            ("Звіт", "Раз на місяць: що зроблено, що змінилось у цифрах."),
        ]) + note("Без підтримки сайт не ламається одразу. Він повільно старіє, поки одного дня не впаде.")), None),
        ("cta", cta_dark("Беремо сайти на підтримку", "Зокрема ті, які робили не ми. Почнемо з аудиту.", "Обговорити підтримку"), SAVE),
    ],
    "2026-10-29-agent-vs-chatbot": [
        ("cover", cover("ШІ", 'Чатбот чи <span class="tl">ШІ-агент</span>: у чому різниця',
                        "Обидва спілкуються текстом. Але один лише відповідає, а другий — робить."), SWIPE),
        ("b", body("Чатбот", "Відповідає на питання", chk([
            ("Що вміє", "Пояснити умови, знайти відповідь у базі знань, передати людині."),
            ("Де корисний", "Підтримка, FAQ, перша лінія продажів."),
            ("Ризик", "Мінімальний: він нічого не змінює у ваших системах."),
        ])), None),
        ("b", body("Агент", "Виконує дії", chk([
            ("Що вміє", "Створити угоду в CRM, записати на зустріч, надіслати лист, оновити таблицю."),
            ("Де корисний", "Процеси з багатьма кроками й системами."),
            ("Що потрібно", "Обмежені права, журнал дій і підтвердження людиною для важливих кроків."),
        ])), None),
        ("cta", cta_dark("Будуємо і ботів, і агентів", "Підкажемо, що потрібно саме вам — часто вистачає бота.", "Написати в дірект"), SAVE),
    ],
    "2026-10-30-site-security": [
        ("cover", cover("Безпека", 'Безпека сайту: <span class="tl">6 базових речей</span>',
                        "Не про хакерів з фільмів. Про те, через що сайти ламають насправді.",
                        tags("HTTPS", "Оновлення", "Бекапи", "Доступи", "Форми", "Логи")), SWIPE),
        ("b", body("01–03", "Фундамент", nlist([
            ("HTTPS скрізь", "Сертифікат, редирект з http і жодного «змішаного» контенту."),
            ("Оновлення", "Більшість зламів — через відомі вразливості в застарілих плагінах."),
            ("Бекапи окремо від сайту", "Копія на тому ж сервері зникне разом із ним."),
        ])), None),
        ("b", body("04–06", "Доступи й контроль", nlist([
            ("Доступи й 2FA", "Окремий акаунт кожному, двофакторний вхід, без спільних паролів."),
            ("Захищені форми", "Перевірка даних і захист від ботів та спаму."),
            ("Логи й моніторинг", "Щоб помітити підозріле до того, як стане пізно."),
        ], 4)), None),
        ("cta", cta_dark("Зробимо аудит безпеки сайту", "Перевіримо базу і дамо список, що виправити першим.", "Замовити аудит"), SAVE),
    ],
}

# The five queued posts, re-rendered in this theme. Their CTA slides get the dark flask.
QUEUED = ["2026-10-22-ecommerce-sells", "2026-10-23-website-myths", "2026-10-24-first-call-prep",
          "2026-10-25-ai-glossary", "2026-10-26-selfhosted-vs-api"]

POSTS = {}
for s in QUEUED:
    POSTS[s] = [(k, inner.replace('href="#flask"', 'href="#flask-dark"') if k == "cta" else inner, r)
                for k, inner, r in bp.POSTS[s]]
POSTS.update(NEW)


def render(slugs, out_root):
    head = bp.head.replace("</head>", PAPER_CSS + "</head>")
    parts = []
    for slug in slugs:
        slides = POSTS[slug]
        for i, (kind, inner, right) in enumerate(slides, 1):
            html = slide(f"{slug}--{i:02d}", i, len(slides), inner, right or "Далі →")
            if kind == "cta":  # dark slide: header mark and big flask need the light-glass version
                html = html.replace('href="#flask"', 'href="#flask-dark"')
            parts.append(html)
    page = head + "<body>" + DEFS_LIGHT + DEFS_DARK + "\n".join(parts) + "</body></html>"
    path = HERE / "paper.html"
    path.write_text(page)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(path.resolve().as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(700)
        for slug in slugs:
            d = out_root / slug
            d.mkdir(parents=True, exist_ok=True)
            for f in d.glob("*.png"):
                f.unlink()
            for i in range(1, len(POSTS[slug]) + 1):
                sid = f"{slug}--{i:02d}"
                ov = pg.evaluate(f"""(()=>{{const s=document.getElementById('{sid}');
                    return s.scrollHeight>s.clientHeight+2}})()""")
                pg.locator(f'[id="{sid}"]').screenshot(path=str(d / f"{i:02d}.png"))
                if ov:
                    print("OVERFLOW", sid)
        b.close()


if __name__ == "__main__":
    slugs = sys.argv[1:] or list(POSTS)
    render(slugs, HERE / "out-paper")
    print("done", len(slugs))
