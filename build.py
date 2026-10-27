"""Собирает index.html. Список покупок берётся из Obsidian.
Запуск: python3 build.py"""
import html, os, re, datetime

VAULT = "/Users/denis/Desktop/projects/Vault/🏠Дом"
HERE = os.path.dirname(os.path.abspath(__file__))
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def inline(s):
    """markdown-ссылки и ~~зачёркивание~~ → html, остальное экранируем."""
    out, pos = [], 0
    for m in LINK.finditer(s):
        out.append(html.escape(s[pos:m.start()]))
        out.append(f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{html.escape(m.group(1))}</a>')
        pos = m.end()
    out.append(html.escape(s[pos:]))
    return re.sub(r"~~(.+?)~~", r"<s>\1</s>", "".join(out))


def shopping():
    sections, cur = [], None
    for line in open(os.path.join(VAULT, "Список покупок.md"), encoding="utf-8"):
        line = line.rstrip()
        if line.startswith("## "):
            cur = (line[3:], []); sections.append(cur)
        elif cur and line.startswith("- ["):
            done = line[3] == "x"
            text = line[6:].replace(" — ссылка: ", " — ").replace("ссылка: ", "")
            name, _, rest = text.partition(" — ")
            alt = ""
            if " · альт: " in rest:
                rest, _, alt = rest.partition(" · альт: ")
            cur[1].append((done, name, rest, alt))
    parts = []
    for title, items in sections:
        lis = []
        for done, name, rest, alt in items:
            cls = ' class="have"' if done else ""
            alt_html = f'<span class="alt">Запасной вариант: {inline(alt)}</span>' if alt else ""
            lis.append(f'<li{cls}><span class="what">{inline(name)}</span>'
                       f'<span class="pick">{inline(rest) or "подбирается"}</span>{alt_html}</li>')
        parts.append(f'<details><summary>{html.escape(title)} <span class="count">{len(items)}</span></summary>'
                     f'<ul class="buy">{"".join(lis)}</ul></details>')
    return "\n".join(parts)


ROOMS = [
    ("Спальня", "14,4 м²", ["bed-1", "bed-2"],
     "Кровать 160 стоит изголовьем к оливковой стене, по бокам тумбочки и бра. У окна — кресло и столик. "
     "Шкаф до потолка у двери. Телевизора нет: проектор стоит на тумбочке и показывает на белую стену напротив кровати. "
     "Шторы плотные, на электрокарнизе — открываются сами утром."),
    ("Гостиная", "26,7 м² вместе с кухней", ["living-1", "living-2"],
     "Диван цвета шалфея, перед ним журнальный стол, который поднимается и становится обеденным. "
     "Телевизор на стене, под ним подвесная тумба. У окна рабочее место — кондиционер дует вдоль стены, а не в спину. "
     "Кухню от комнаты отделяют деревянные рейки до потолка."),
    ("Кухня", "", ["kitchen"],
     "Графитовые фасады, тёмная столешница. В высоком шкафу-пенале — духовка, посудомойка и микроволновка. "
     "Индукционная плита, вытяжка спрятана в шкаф. Холодильник у реек."),
    ("Прихожая", "", ["hall-1", "hall-2"],
     "Вдоль стены шкаф до потолка: одежда, отдельная секция для пылесоса и гладильной доски, и полка для роутера. "
     "Обувница и большое зеркало. Двери в спальню и санузел скрытые — без наличников, в цвет стены."),
    ("Санузел", "6,3 м²", ["bath-1", "bath-2"],
     "Душ без поддона — слив прямо в полу, стеклянная перегородка. Подвесной унитаз, тумба с раковиной. "
     "Стиральная и сушильная машины стоят друг на друге. Плоский бойлер спрятан в шкаф над унитазом. "
     "Пол с подогревом, полотенцесушитель, робот-мойщик полов со своей станцией."),
]

PLANS = [("top-plan", "План с мебелью"), ("plan-1", "План с размерами"), ("plan-2", "Розетки"), ("plan-3", "Свет и выключатели"),
         ("plan-4", "Вода и канализация"), ("plan-5", "Климат и умный дом")]

HOW = [
    ("Тёплый пол", "Электрический мат под плиткой в санузле. Регулятор с Wi-Fi у двери: можно включить с телефона "
     "или по расписанию — например, утром на час."),
    ("Если протечёт", "На полу под стиралкой, раковиной, мойкой и у душа лежат датчики. Если намокнет — краны на входе "
     "воды закроются сами, на телефон придёт сообщение. Соседей не зальёт."),
    ("Свет и шторы", "Всё слушается Алису. В прихожей и санузле свет включается сам, когда заходишь, а ночью горит "
     "тускло. Утром шторы открываются и свет плавно разгорается."),
    ("Воздух", "В каждой комнате кондиционер. В спальне бризер — тихо подаёт уличный воздух через фильтр и подогревает "
     "его, окно открывать не нужно. Датчик показывает, когда душно."),
    ("Тишина", "Стены, общие с соседями, закрыты шумоизоляцией, под полом звукопоглощающая подложка."),
]

STAGES = [
    ("Черновые работы", "Перегородки, электрика, трубы, трассы кондиционеров, шумоизоляция."),
    ("Отделка", "Гидроизоляция и плитка в санузле, стены, натяжные потолки, пол, двери."),
    ("Кухня и санузел", "Кухня, техника, сантехника, свет. После этого можно жить."),
    ("Мебель", "Шкафы, диван, шторы и всё остальное — постепенно."),
]


def page():
    rooms = "".join(
        f'<section class="room"><h3>{n} <span>{a}</span></h3><p>{d}</p>'
        f'<div class="shots">{"".join(f"<img src=img/{i}.jpg alt=\"{n}\" loading=lazy>" for i in imgs)}</div></section>'
        for n, a, imgs, d in ROOMS)
    plans = "".join(f'<figure><img src="img/{f}.jpg" alt="{t}" loading="lazy"><figcaption>{t}</figcaption></figure>'
                    for f, t in PLANS)
    how = "".join(f"<div><h3>{t}</h3><p>{d}</p></div>" for t, d in HOW)
    stages = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in STAGES)
    today = datetime.date.today().strftime("%d.%m.%Y")
    out = TEMPLATE
    for k, v in dict(ROOMS=rooms, PLANS=plans, HOW=how, STAGES=stages, SHOP=shopping(), TODAY=today,
                     VER=str(int(os.path.getmtime(os.path.join(HERE, 'model.js'))))).items():
        out = out.replace(f"%%{k}%%", v)
    return out


TEMPLATE = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page())
print("index.html готов")
