"""Build carousel slides for the next WebLab posts, reusing the RAG carousel's CSS and flask symbol."""
import pathlib, re, sys
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
base = (HERE / "rag.html").read_text()
head = base.split("</head>")[0] + """
<style>
.chk { margin: 48px 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; }
.chk li { display: grid; grid-template-columns: 60px 1fr; gap: 24px; align-items: start; padding: 32px 0; border-top: 1px solid var(--hair); }
.chk li:last-child { border-bottom: 1px solid var(--hair); }
.box { width: 44px; height: 44px; margin-top: 4px; border-radius: 10px; border: 2px solid var(--amber); display: grid; place-items: center; }
.box svg { width: 24px; height: 24px; }
.chk h3 { margin: 0 0 8px; font-size: 40px; font-weight: 600; letter-spacing: -0.02em; }
.chk p { margin: 0; color: var(--paper-dim); font-size: 30px; line-height: 1.45; }
.vs { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 56px; }
.vs .card h3 { margin: 0 0 18px; font-size: 34px; font-weight: 600; }
.vs .card p { margin: 0 0 12px; color: var(--paper-dim); font-size: 27px; line-height: 1.4; }
.metric { display: grid; grid-template-columns: 270px 1fr; gap: 28px; align-items: center; padding: 30px 0; border-top: 1px solid var(--hair); }
.metric:last-child { border-bottom: 1px solid var(--hair); }
.metric .v { white-space: nowrap; font-size: 60px; font-weight: 600; letter-spacing: -0.03em; color: var(--teal); }
.metric h3 { margin: 0 0 8px; font-size: 38px; font-weight: 600; }
.metric p { margin: 0; color: var(--paper-dim); font-size: 29px; line-height: 1.4; }
.big-n { font-size: 200px; font-weight: 600; line-height: .9; letter-spacing: -0.05em; color: var(--teal); margin: 0 0 24px; }
.tag { display: inline-flex; align-items: center; min-height: 60px; padding: 0 26px; border-radius: 999px; border: 1px solid var(--hair); color: var(--paper-dim); font-size: 27px; }
.list li { padding: 34px 0; }
.list h3 { font-size: 40px; margin-bottom: 8px; }
.list p { font-size: 30px; }
.tight .list { margin-top: 36px; }
.tight .list li { padding: 22px 0; }
.tight .list p { font-size: 28px; }
</style>
</head>"""
defs = re.search(r'<svg width="0" height="0".*?</svg>', base, re.S).group(0)

MARK = '<span class="mark">WebL<svg><use href="#flask"/></svg>b</span>'
ARROW = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>'
TICK = '<svg viewBox="0 0 24 24" fill="none" stroke="#E8A54B" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'


def slide(sid, n, total, inner, foot_right="Далі →", foot_left="weblab.llc"):
    return f"""<section class="slide" id="{sid}"><div class="grid"></div>
<div class="top">{MARK}<div class="idx">{n:02d}<span class="l"></span><span class="t">{total:02d}</span></div></div>
{inner}
<div class="foot"><span>{foot_left}</span><span class="swipe">{foot_right}</span></div></section>"""


def cover(kicker, title, lead, extra=""):
    return f'<p class="kicker">{kicker}</p><h1>{title}</h1><p class="lead">{lead}</p>{extra}'


def body(kicker, title, html):
    return f'<p class="kicker">{kicker}</p><h2>{title}</h2>{html}'


def cta(title, lead, button):
    return f"""<div style="position:relative; margin: auto 0; display:flex; flex-direction:column; align-items:flex-start;">
<svg width="140" height="162" style="margin-bottom: 48px; overflow: visible;"><use href="#flask" width="140" height="162"/></svg>
<p class="kicker">WebLab · Київ</p><h2 style="font-size: 72px;">{title}</h2><p class="lead">{lead}</p>
<div style="display:flex; gap: 20px; margin-top: 56px; flex-wrap: wrap;"><span class="btn">{button} {ARROW}</span><span class="ghost">weblab.llc</span></div></div>"""


def chk(items):
    return '<ul class="chk">' + "".join(
        f'<li><span class="box">{TICK}</span><div><h3>{h}</h3><p>{p}</p></div></li>' for h, p in items) + "</ul>"


def nlist(items, start=1):
    return '<ul class="list">' + "".join(
        f'<li><span class="k">{i:02d}</span><div><h3>{h}</h3><p>{p}</p></div></li>' for i, (h, p) in enumerate(items, start)) + "</ul>"


SWIPE = f"Гортайте {ARROW}"
SAVE = "Збережіть, щоб не загубити"

POSTS = {
    "2026-10-16-launch-checklist": [
        ("cover", cover("Чекліст", 'Перед запуском сайту: <span class="tl">20 пунктів</span>, які часто забувають',
                        "Збережіть і пройдіться перед релізом. Кожен пункт — реальна втрата заявок або позицій, якщо його пропустити.",
                        '<div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:72px;"><span class="tag">SEO</span><span class="tag">Прев\'ю в соцмережах</span><span class="tag">Швидкість</span><span class="tag">Надійність</span><span class="tag">Аналітика</span></div>'), SWIPE),
        ("b", body("01 · SEO-база", "Щоб пошуковик зрозумів сторінку", chk([
            ("Унікальні title і description", "На кожній сторінці свої, а не одні на весь сайт."),
            ("Canonical на правильний домен", "Після переїзду домену його часто забувають оновити."),
            ("sitemap.xml і robots.txt", "Карта сайту актуальна, robots нічого зайвого не закриває."),
            ("Контент без JavaScript", "Пошуковик і прев'ю бачать текст, а не порожню заглушку."),
        ])), None),
        ("b", body("02 · Прев'ю", "Як посилання виглядає в Telegram та Instagram", chk([
            ("og:image 1200×630", "Обкладинка, а не випадкова картинка зі сторінки."),
            ("og:title і og:description", "Короткі, без обрізаних посеред слова фраз."),
            ("twitter:card = summary_large_image", "Інакше прев'ю буде маленьким квадратиком."),
            ("Фавікон і іконка для телефона", "SVG для вкладки й PNG для домашнього екрана."),
        ])), None),
        ("b", body("03 · Швидкість", "Core Web Vitals у зеленій зоні", chk([
            ("Картинки у WebP або AVIF", "З правильними розмірами під екран і lazy-loading нижче першого екрана."),
            ("Шрифти: лише потрібні накреслення", "Плюс font-display: swap, щоб текст не зникав."),
            ("Сторонні скрипти — на аудит", "Кожен віджет, піксель і чат коштує швидкості."),
            ("Перевірка на слабкому телефоні", "А не лише на ноутбуці розробника."),
        ])), None),
        ("b", body("04 · Надійність", "Щоб нічого не впало в день запуску", chk([
            ("HTTPS і єдиний домен", "www і без www, http і https — усе редиректить в одне місце."),
            ("Сторінка 404", "Корисна, з навігацією, а не біла сторінка хостингу."),
            ("Форма заявки протестована", "Відправили тестову заявку й переконались, що вона дійшла."),
            ("Бекапи й доступи", "Домен, хостинг і репозиторій оформлені на вас."),
        ])), None),
        ("b", body("05 · Аналітика", "Щоб знати, звідки приходять клієнти", chk([
            ("Аналітика підключена", "І перевірено, що вона справді збирає дані."),
            ("Подія на кожну заявку", "Кнопка, форма, дзвінок, месенджер — усе як окремі цілі."),
            ("UTM-мітки на всіх посиланнях", "Біо в Instagram, розсилки, реклама."),
            ("Search Console", "Підтверджено домен і надіслано sitemap."),
        ])), None),
        ("cta", cta("Запускаємо сайти, які проходять цей чекліст", "Сайти, інтернет-магазини та AI-інтеграції під ключ.", "Обговорити проєкт"), SAVE),
    ],
    "2026-10-20-builder-vs-custom": [
        ("cover", cover("Чесно", 'Конструктор чи <span class="tl">кастомна розробка</span>?',
                        "Не завжди потрібен кастом. Розбираємо, коли конструктора досить, а коли він почне коштувати дорожче за розробку."), SWIPE),
        ("b", body("Конструктор", "Коли конструктор — нормальний вибір", chk([
            ("Перевірити ідею", "Потрібен лендинг за тиждень, щоб зрозуміти, чи є попит."),
            ("Немає інтеграцій", "Заявки на пошту чи в Telegram, без CRM і складу."),
            ("Сайт-візитка", "Кілька сторінок, які рідко змінюються."),
            ("Мінімальний бюджет на старті", "І ви готові до обмежень платформи."),
        ])), None),
        ("b", body("Кастом", "Коли варто писати код", chk([
            ("Інтеграції", "CRM, облікова система, склад, оплата, доставка, власні API."),
            ("Нестандартна логіка", "Калькулятори, кабінети, передзамовлення, ролі користувачів."),
            ("Пошук — основний канал", "Потрібен повний контроль над швидкістю, розміткою й рендером."),
            ("Продукт росте", "Важливо масштабуватися без переїзду на іншу платформу."),
        ])), None),
        ("b", body("Про що мовчать", "Неочевидна ціна конструктора", nlist([
            ("Підписка назавжди", "Сайт живе, поки ви платите. Плюс платні плагіни й шаблони."),
            ("Стеля шаблону", "Рано чи пізно потрібна функція, якої платформа не вміє."),
            ("Переїзд = переписування", "Код і дані не завжди можна просто забрати з собою."),
        ])), None),
        ("b", body("Як вирішити", "Три питання перед вибором", nlist([
            ("Що сайт має робити через рік?", "Якщо відповідь «те саме» — конструктор, найімовірніше, підійде."),
            ("З якими системами він має говорити?", "Кожна інтеграція — аргумент на користь кастому."),
            ("Звідки прийдуть клієнти?", "Якщо з пошуку, швидкість і рендер стають бізнес-питанням."),
        ])), None),
        ("cta", cta("Підкажемо, що підходить саме вам", "Інколи наша порада — взяти конструктор. І це нормально.", "Написати в дірект"), SAVE),
    ],
    "2026-10-22-slow-site": [
        ("cover", cover("Швидкість", 'Чому ваш сайт <span class="tl">повільний</span>: 5 причин',
                        "Повільний сайт втрачає відвідувачів ще до того, як вони побачать ваш продукт. Ось що зазвичай його гальмує."), SWIPE),
        ("b", body("Метрики Google", "Core Web Vitals: що міряти", '<div style="margin-top:52px">' + "".join(
            f'<div class="metric"><span class="v">{v}</span><div><h3>{h}</h3><p>{p}</p></div></div>' for v, h, p in [
                ("≤ 2,5 с", "LCP — головний контент", "За скільки з'являється найбільший елемент першого екрана."),
                ("≤ 200 мс", "INP — реакція на дії", "Як швидко сторінка відповідає на натискання."),
                ("≤ 0,1", "CLS — стабільність", "Наскільки «стрибає» верстка під час завантаження."),
            ]) + '</div><p class="body" style="font-size:27px">Пороги «добре» за Google. Перевірити свій сайт можна в PageSpeed Insights.</p>'), None),
        ("b", body("Причини 1–3", "Що найчастіше гальмує", nlist([
            ("Важкі картинки", "Фото на кілька мегабайт без стиснення й без адаптивних розмірів."),
            ("Сторонні скрипти", "Чати, пікселі, віджети. Кожен вантажиться й виконується на телефоні клієнта."),
            ("Шрифти", "Десяток накреслень, які блокують показ тексту."),
        ])), None),
        ("b", body("Причини 4–5", "І те, що не видно в коді сторінки", nlist([
            ("Рендер лише в браузері", "Поки не завантажиться весь JavaScript, користувач і пошуковик бачать порожнечу."),
            ("Немає CDN і кешу", "Кожен запит їде на один сервер, хоч би де був відвідувач."),
        ], 4) + '<div class="card" style="margin-top:44px"><p style="margin:0; font-size:30px; line-height:1.45;">Швидкість — це не «оптимізуємо колись». Її закладають в архітектуру з першого дня.</p></div>'), None),
        ("cta", cta("Робимо швидкі сайти за замовчуванням", "Міряємо Core Web Vitals на кожному етапі, а не перед здачею.", "Написати в дірект"), SAVE),
    ],
    "2026-10-27-how-we-work": [
        ("cover", cover("Як працюємо", 'Від брифу <span class="tl">до релізу</span>',
                        "Кожен етап закінчується результатом, який можна подивитись і перевірити. Без «чорної скриньки» на два місяці."), SWIPE),
        ("b", '<div style="position:relative; margin-top: 20px;"><p class="big-n">01</p>' + body("Дослідження", "Розбираємо задачу",
            '<p class="body">Вивчаємо продукт, конкурентів і аудиторію.</p><div class="card" style="margin-top:44px"><p class="kicker" style="margin-bottom:14px; font-size:20px;">На виході</p><p style="margin:0; font-size:30px; line-height:1.45;">Структура сайту, список сторінок і сценарії, за якими користувач дійде до заявки.</p></div>') + "</div>", None),
        ("b", '<div style="position:relative; margin-top: 20px;"><p class="big-n">02</p>' + body("Дизайн", "Малюємо інтерфейс",
            '<p class="body">Прототип, макети під десктоп і мобільний, типографіка та стани елементів.</p><div class="card" style="margin-top:44px"><p class="kicker" style="margin-bottom:14px; font-size:20px;">Важливо</p><p style="margin:0; font-size:30px; line-height:1.45;">Узгоджуємо все до того, як почнемо писати код. Правки в макеті коштують у рази менше, ніж у коді.</p></div>') + "</div>", None),
        ("b", '<div style="position:relative; margin-top: 20px;"><p class="big-n">03</p>' + body("Розробка", "Пишемо код",
            '<p class="body">Адаптивна верстка, анімації та інтеграції з CRM і платіжними системами.</p><div class="card" style="margin-top:44px"><p class="kicker" style="margin-bottom:14px; font-size:20px;">Як контролюємо</p><p style="margin:0; font-size:30px; line-height:1.45;">Швидкість завантаження міряємо на кожному кроці, а не перед здачею.</p></div>') + "</div>", None),
        ("b", '<div style="position:relative; margin-top: 20px;"><p class="big-n">04</p>' + body("Запуск", "Вмикаємо трафік",
            '<p class="body">Переносимо на хостинг, підключаємо аналітику, запускаємо рекламу.</p><div class="card" style="margin-top:44px"><p class="kicker" style="margin-bottom:14px; font-size:20px;">Далі</p><p style="margin:0; font-size:30px; line-height:1.45;">Підтримка й правки за метриками, а не за відчуттями.</p></div>') + "</div>", None),
        ("cta", cta("Кожен етап закривається артефактом", "Структура, макет, збірка, звіт. Ви завжди бачите, де проєкт.", "Обговорити проєкт"), "Сайти · e-commerce · AI"),
    ],
    "2026-10-17-dev-glossary": [
        ("cover", cover("Словник", 'Що кажуть розробники <span class="tl">і що це означає</span>',
                        "8 слів, які ви почуєте на першому ж дзвінку зі студією. Пояснюємо без жаргону.",
                        '<div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:72px;"><span class="tag">API</span><span class="tag">CMS</span><span class="tag">MVP</span><span class="tag">Деплой</span><span class="tag">CDN</span><span class="tag">SSR</span><span class="tag">Рефакторинг</span><span class="tag">RAG</span></div>'), SWIPE),
        ("b", '<div class="tight">' + body("Словник · 1–4", "Про продукт і процес", nlist([
            ("API", "Спосіб, яким дві програми обмінюються даними. Наприклад, сайт і ваша CRM."),
            ("CMS", "Адмінка, де ви самі змінюєте тексти, товари й картинки без програміста."),
            ("MVP", "Перша версія з мінімумом функцій, щоб перевірити ідею на реальних людях."),
            ("Деплой", "Викладка нової версії сайту на сервер, тобто туди, де її бачать відвідувачі."),
        ])) + "</div>", None),
        ("b", '<div class="tight">' + body("Словник · 5–8", "Про швидкість, код і AI", nlist([
            ("CDN", "Мережа серверів по світу. Сайт віддається з найближчого до відвідувача."),
            ("SSR", "Сторінку збирає сервер, тож пошуковик і користувач одразу бачать текст."),
            ("Рефакторинг", "Переписування коду без зміни поведінки, щоб далі було легше розвивати."),
            ("RAG", "Підхід, коли AI спершу шукає відповідь у ваших документах, а потім формулює її."),
        ], 5)) + "</div>", None),
        ("cta", cta("Пояснюємо людською мовою", "Без жаргону на дзвінках, у кошторисах і звітах.", "Поставити питання"), SAVE),
    ],
    "2026-10-18-automation-signs": [
        ("cover", cover("Автоматизація", '5 ознак, що бізнесу <span class="tl">пора автоматизувати</span> процеси',
                        "Якщо впізнали у себе хоча б дві — частину рутини вже можна віддати системі."), SWIPE),
        ("b", body("Ознаки 1–3", "Де губиться час", nlist([
            ("Дані переносять руками", "Заявку з сайту копіюють у таблицю, потім у CRM, потім у месенджер."),
            ("Одні й ті самі питання", "Менеджери щодня відповідають на те, що вже є в FAQ чи прайсі."),
            ("Звіти збирають годинами", "Щотижня хтось зводить цифри з кількох систем вручну."),
        ])), None),
        ("b", body("Ознаки 4–5", "Де губляться гроші", nlist([
            ("Заявки «випадають»", "Частина звернень губиться між каналами, і ніхто не помічає."),
            ("Знання в головах", "Пішов співробітник — і разом з ним пішло, як усе працює."),
        ], 4) + '<div class="card" style="margin-top:44px"><p style="margin:0; font-size:30px; line-height:1.45;">Почати можна з одного процесу: той, що забирає найбільше годин щотижня.</p></div>'), None),
        ("cta", cta("Знайдемо, що автоматизувати першим", "Інтеграції з CRM, месенджерами й таблицями, AI-асистенти для рутини.", "Написати в дірект"), SAVE),
    ],
}

ONLY = set(sys.argv[1:])
if ONLY:
    POSTS = {k: v for k, v in POSTS.items() if k in ONLY}

out_root = HERE / "out"
html_parts = []
for slug, slides in POSTS.items():
    total = len(slides)
    for i, (kind, inner, right) in enumerate(slides, 1):
        sid = f"{slug}--{i:02d}"
        foot_right = right if right else "Далі →"
        foot_left = "weblab.llc"
        html_parts.append(slide(sid, i, total, inner, foot_right, foot_left))

page = head + "<body>" + defs + "\n".join(html_parts) + "</body></html>"
(HERE / "posts.html").write_text(page)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.goto((HERE / "posts.html").resolve().as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(700)
    for slug, slides in POSTS.items():
        d = out_root / slug
        d.mkdir(parents=True, exist_ok=True)
        for i in range(1, len(slides) + 1):
            sid = f"{slug}--{i:02d}"
            # overflow check: footer must sit inside the slide
            ov = pg.evaluate(f"""(()=>{{const s=document.getElementById('{sid}');const f=s.querySelector('.foot');
                const sb=s.getBoundingClientRect(), fb=f.getBoundingClientRect(); return fb.bottom>sb.bottom-40}})()""")
            pg.locator(f'[id="{sid}"]').screenshot(path=str(d / f"{i:02d}.png"))
            if ov:
                print("OVERFLOW", sid)
    b.close()
print("done")
