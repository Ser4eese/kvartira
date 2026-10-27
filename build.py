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


# цвет, название, где — реальные отделки из проекта
SW = {
    "olive": ("#8E9078", "Олива"), "greige": ("#E4DED5", "Тёплый грейдж"), "wall": ("#ECE7E0", "Светлый грейдж"),
    "white": ("#F4F2EE", "Белая матовая"), "oak": ("#C9A57A", "Светлый дуб"), "sage": ("#A9B39A", "Шалфей"),
    "sofa": ("#7D8B6A", "Зелёный шалфей"), "tv": ("#A6A199", "Серо-бежевая"), "graphite": ("#4A4D50", "Графит"),
    "black": ("#26272A", "Чёрный металл"), "concrete": ("#B9BAB8", "Плитка под бетон"), "stone": ("#8F8D88", "Тёмный камень"),
}
ROOMS = [
    ("Спальня", "14,4 м²", ["bed-1", "bed-2"],
     [("olive", "стена за кроватью"), ("greige", "стены"), ("white", "стена под проектор"), ("oak", "пол, тумбочки"),
      ("sage", "кресло, шторы")],
     "Кровать 160 стоит изголовьем к оливковой стене, по бокам тумбочки и бра. У окна — кресло и столик. "
     "Шкаф до потолка у двери. Телевизора нет: проектор стоит на тумбочке и показывает на белую стену напротив кровати. "
     "Шторы плотные, на электрокарнизе — открываются сами утром."),
    ("Гостиная", "26,7 м² вместе с кухней", ["living-1", "living-2"],
     [("wall", "стены"), ("tv", "стена с телевизором"), ("sofa", "диван"), ("oak", "пол, рейки, тумба"),
      ("black", "светильники, ножки")],
     "Диван цвета шалфея, перед ним журнальный стол, который поднимается и становится обеденным. "
     "Телевизор на стене, под ним подвесная тумба. У окна рабочее место — кондиционер дует вдоль стены, а не в спину. "
     "Кухню от комнаты отделяют деревянные рейки до потолка."),
    ("Кухня", "", ["kitchen"],
     [("graphite", "фасады, матовые"), ("stone", "столешница"), ("black", "мойка, смеситель"), ("oak", "пол, рейки")],
     "Графитовые фасады до потолка. В высоком шкафу-пенале — духовка, посудомойка и микроволновка. "
     "Индукционная плита, вытяжка спрятана в шкаф. Холодильник у реек."),
    ("Прихожая", "", ["hall-1", "hall-2"],
     [("wall", "стены и двери в цвет стен"), ("white", "шкаф во всю стену"), ("oak", "пол"), ("black", "рама зеркала")],
     "Вдоль стены шкаф до потолка: одежда, отдельная секция для пылесоса и гладильной доски, и полка для роутера. "
     "Обувница и большое зеркало. Двери в спальню и санузел скрытые — без наличников, в цвет стены."),
    ("Санузел", "6,3 м²", ["bath-1", "bath-2"],
     [("concrete", "стены и пол, плиты 90×180"), ("oak", "тумба, шкафы"), ("black", "смесители, сушитель, профиль душа")],
     "Душ без поддона — слив прямо в полу, стеклянная перегородка. Подвесной унитаз, тумба с раковиной. "
     "Стиральная и сушильная машины стоят друг на друге. Плоский бойлер спрятан в шкаф над унитазом. "
     "Пол с подогревом, полотенцесушитель, робот-мойщик полов со своей станцией."),
]
PALETTE = ["olive", "sofa", "sage", "greige", "oak", "tv", "concrete", "graphite", "black"]

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
    def chips(items):
        return "".join(f'<li><span class="chip" style="--c:{SW[k][0]}"></span><b>{SW[k][1]}</b><small>{w}</small></li>'
                       for k, w in items)
    rooms = "".join(
        f'<section class="room"><header><h3>{n}</h3><span class="area">{a}</span></header>'
        f'<div class="shots n{len(imgs)}">{"".join(f"<img src=img/{i}.jpg alt=\"{n}\" loading=lazy>" for i in imgs)}</div>'
        f'<div class="room-text"><ul class="swatches">{chips(sw)}</ul><p>{d}</p></div></section>'
        for n, a, imgs, sw, d in ROOMS)
    palette = "".join(f'<li style="--c:{SW[k][0]}"><span>{SW[k][1]}</span></li>' for k in PALETTE)
    plans = "".join(f'<figure><img src="img/{f}.jpg" alt="{t}" loading="lazy"><figcaption>{t}</figcaption></figure>'
                    for f, t in PLANS)
    how = "".join(f"<div><h3>{t}</h3><p>{d}</p></div>" for t, d in HOW)
    stages = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in STAGES)
    today = datetime.date.today().strftime("%d.%m.%Y")
    out = TEMPLATE
    for k, v in dict(ROOMS=rooms, PALETTE=palette, PLANS=plans, HOW=how, STAGES=stages, SHOP=shopping(), TODAY=today,
                     VER=str(int(os.path.getmtime(os.path.join(HERE, 'model.js'))))).items():
        out = out.replace(f"%%{k}%%", v)
    return out


TEMPLATE = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page())
print("index.html готов")
