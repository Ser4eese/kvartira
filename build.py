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

PLANS = [("top-3d", "Вид сверху"), ("top-plan", "План с мебелью"), ("plan-1", "План с размерами"), ("plan-2", "Розетки"), ("plan-3", "Свет и выключатели"),
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



# --- план квартиры (метры; x вправо, y вниз от окон) ---------------------------
ZONES = {  # id: (прямоугольники зоны, заливка, цвет подписи, центр подписи, площадь)
    "bed": ([(0, 0, 3.23, 4.45)], "#8E9078", "#fff", (1.62, 2.1), "14,4 м²"),
    "living": ([(3.43, 0, 6.5, 4.45)], "#A9B39A", "#2f3133", (4.97, 2.1), "26,7 м² с кухней"),
    "kitchen": ([(3.84, 4.45, 6.5, 6.41)], "#4A4D50", "#fff", (5.2, 5.38), ""),
    "hall": ([(2.17, 4.45, 3.84, 9.3)], "#E4DED5", "#2f3133", (3.0, 7.1), ""),
    "bath": ([(4.04, 6.61, 6.5, 9.3)], "#B9BAB8", "#2f3133", (5.27, 7.85), "6,3 м²"),
}
ZNAME = {"bed": "Спальня", "living": "Гостиная", "kitchen": "Кухня", "hall": "Прихожая", "bath": "Санузел"}
WALLS = [((-0.1, -0.1), (6.6, -0.1)), ((-0.1, -0.1), (-0.1, 4.55)), ((-0.1, 4.55), (3.33, 4.55)),
         ((3.33, -0.1), (3.33, 4.55)), ((2.07, 4.55), (2.07, 9.4)), ((2.07, 9.4), (6.6, 9.4)),
         ((6.6, -0.1), (6.6, 9.4)), ((3.94, 6.51), (6.6, 6.51)), ((3.94, 6.51), (3.94, 9.4))]


def plan_svg(focus=None, full=True):
    k = 100
    v = lambda a: f"{a * k:.0f}"
    out = [f'<svg viewBox="-70 -75 830 1090" class="plan" role="img" aria-label="План квартиры">']
    for zid, (rects, fill, ink, (lx, ly), area) in ZONES.items():
        on = focus in (None, zid)
        body = "".join(f'<rect x="{v(x0)}" y="{v(y0)}" width="{v(x1 - x0)}" height="{v(y1 - y0)}"/>' for x0, y0, x1, y1 in rects)
        g = f'<g class="zone" style="fill:{fill if on else "transparent"}">{body}'
        if full:
            rot = f' transform="rotate(-90 {v(lx)} {v(ly)})"' if zid == "hall" else ""
            g += (f'<text x="{v(lx)}" y="{v(ly)}" fill="{ink}" class="zn"{rot}>{ZNAME[zid]}</text>'
                  + (f'<text x="{v(lx)}" y="{ly * k + 42:.0f}" fill="{ink}" class="za">{area}</text>' if area else ""))
        g += "</g>"
        out.append(f'<a href="#{zid}" aria-label="{ZNAME[zid]}">{g}</a>' if full else g)
    for (a, b) in WALLS:
        out.append(f'<line x1="{v(a[0])}" y1="{v(a[1])}" x2="{v(b[0])}" y2="{v(b[1])}" class="wall"/>')
    # проёмы: окна, двери (закрашиваем стену фоном)
    for x, w in [(1.43, 1.95), (4.78, 1.95)]:
        out.append(f'<rect x="{v(x - w / 2)}" y="-20" width="{v(w)}" height="20" class="gap"/>'
                   f'<line x1="{v(x - w / 2)}" y1="-10" x2="{v(x + w / 2)}" y2="-10" class="glass"/>')
    out.append('<rect x="223" y="444" width="90" height="22" class="gap"/>'
               '<path d="M223,455 L223,545 A90,90 0 0 0 313,455" class="door"/>')
    out.append('<rect x="383" y="691" width="22" height="90" class="gap"/>'
               '<path d="M384,781 L294,781 A90,90 0 0 1 384,691" class="door"/>')
    out.append('<rect x="280" y="929" width="96" height="22" class="gap"/>'
               '<path d="M280,950 L280,1010" class="door"/>')
    if full:  # размеры
        for x0, x1, t in [(0, 3.23, "3230"), (3.43, 6.5, "3070")]:
            out.append(f'<line x1="{v(x0)}" y1="-45" x2="{v(x1)}" y2="-45" class="dim"/>'
                       f'<text x="{v((x0 + x1) / 2)}" y="-55" class="dt">{t}</text>')
        out.append('<line x1="-45" y1="0" x2="-45" y2="445" class="dim"/>'
                   '<text x="-55" y="222" class="dt" transform="rotate(-90 -55 222)">4450</text>')
        out.append('<line x1="705" y1="0" x2="705" y2="930" class="dim"/>'
                   '<text x="735" y="465" class="dt" transform="rotate(-90 735 465)">9300</text>')
    out.append("</svg>")
    return "".join(out)


def page():
    def chips(items):
        return "".join(f'<li tabindex="0" data-hex="{SW[k][0].upper()}"><span class="chip" style="--c:{SW[k][0]}"></span><b>{SW[k][1]}</b><small>{w}</small></li>'
                       for k, w in items)
    ids = ["bed", "living", "kitchen", "hall", "bath"]
    rooms = "".join(
        f'<section class="room" id="{rid}"><div class="room-head">{plan_svg(rid, full=False)}'
        f'<h3>{n}</h3><p class="area">{a}</p></div><div class="room-body">'
        f'<div class="shots n{len(imgs)}">{"".join(f"<img src=img/{i}.jpg alt=\"{n}\" loading=lazy>" for i in imgs)}</div>'
        f'<p class="desc">{d}</p><ul class="swatches">{chips(sw)}</ul></div></section>'
        for rid, (n, a, imgs, sw, d) in zip(ids, ROOMS))
    plans = "".join(f'<figure><img src="img/{f}.jpg" alt="{t}" loading="lazy"><figcaption>{t}</figcaption></figure>'
                    for f, t in PLANS)
    how = "".join(f"<div><h3>{t}</h3><p>{d}</p></div>" for t, d in HOW)
    stages = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in STAGES)
    today = datetime.date.today().strftime("%d.%m.%Y")
    out = TEMPLATE
    for k, v in dict(ROOMS=rooms, PLAN=plan_svg(), PLANS=plans, HOW=how, STAGES=stages, SHOP=shopping(), TODAY=today,
                     VER=str(int(os.path.getmtime(os.path.join(HERE, 'model.js'))))).items():
        out = out.replace(f"%%{k}%%", v)
    return out


TEMPLATE = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(page())
print("index.html готов")
