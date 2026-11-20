"""PRO-133: EN-страницы без кириллицы + честные пороги/оценки.

Механика: пары токенов {{page.ru.kXXX}}{{page.en.kXXX}} — build_pages оставляет
токен текущего языка (значение из i18n) и стирает чужой. Заголовочные aria/
плейсхолдеры — через {{ui.*}}.

Запуск: python3 scripts/pro133_fixes.py  (до build_pages; идемпотентно)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "site" / "i18n"

def load(lang):
    return json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))

def save(lang, data):
    (I18N / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def put(data, page, key, value):
    dst = data["ui"] if page == "ui" else data[page]
    dst[key] = value

def sub(path_rel, old, new):
    p = ROOT / path_rel
    t = p.read_text(encoding="utf-8")
    if old in t:
        p.write_text(t.replace(old, new), encoding="utf-8")
        return 1
    if new in t:
        return 0  # уже применено
    raise SystemExit(f"PRO-133: фрагмент не найден в {path_rel}: {old[:80]!r}")

def main():
    ru, en = load("ru"), load("en")

    # ── 1. Заголовок (шапка) — все страницы ─────────────────────────────
    put(ru, "ui", "brand_aria", "Стратег Фабрики продуктов")
    put(en, "ui", "brand_aria", "Product Factory Strategist")
    put(ru, "ui", "menu_aria", "Меню")
    put(en, "ui", "menu_aria", "Menu")
    put(ru, "ui", "lang_aria", "Язык")
    put(en, "ui", "lang_aria", "Language")
    put(ru, "ui", "search_aria", "Поиск по справке")
    put(en, "ui", "search_aria", "Search the help")
    put(ru, "ui", "search_ph", "Поиск по справке…")
    put(en, "ui", "search_ph", "Search the help…")

    # ── 2. demo_page ────────────────────────────────────────────────────
    put(ru, "demo_page", "k130", "Вайрфрейм кабинета семьи с предупреждениями: низкий остаток участника и предстоящий платёж (S004)")
    put(en, "demo_page", "k130", "Wireframe of the family dashboard with alerts: a low member balance and an upcoming charge (S004)")
    put(ru, "demo_page", "k131", "Схема архитектуры агента: ядро pfs, реестры источников/утверждений/решений, знания и субагенты")
    put(en, "demo_page", "k131", "Agent architecture: the pfs core, source/claim/decision registries, knowledge and subagents")
    put(ru, "demo_page", "k132", "эффект ≥ −3 п.п. · ложные <20% · повторные списания = 0")
    put(en, "demo_page", "k132", "effect ≥ −3 pp · false alerts <20% · double charges = 0")
    put(ru, "demo_page", "k133", "S001 · бриф → C013 (гипотеза)")
    put(en, "demo_page", "k133", "S001 · brief → C013 (hypothesis)")
    put(ru, "demo_page", "k134", "Связь<em> для близких</em>")
    put(en, "demo_page", "k134", "Connection<em> for Loved Ones</em>")
    put(ru, "demo_page", "k135", "учебный бриф: услуги мобильного оператора")
    put(en, "demo_page", "k135", "a training brief: mobile carrier services")

    # ── 3. materials_page ───────────────────────────────────────────────
    put(ru, "materials_page", "k130", "Схема архитектуры агента: ядро pfs, реестры источников/утверждений/решений, знания и субагенты")
    put(en, "materials_page", "k130", "Agent architecture: the pfs core, source/claim/decision registries, knowledge and subagents")
    put(ru, "materials_page", "k131", "Вайрфрейм кабинета семьи с предупреждениями (S004)")
    put(en, "materials_page", "k131", "Wireframe of the family dashboard with alerts (S004)")

    save("ru", ru); save("en", en)
    print("i18n: ui + k130–k135 записаны (ru/en)")

    # ── 4. Шаблоны ──────────────────────────────────────────────────────
    n = 0
    for page in ("demo", "help", "materials"):
        p = ROOT / "site_src" / f"{page}.html"
        t = p.read_text(encoding="utf-8")
        t2 = t
        t2 = t2.replace('aria-label="Стратег Фабрики продуктов"', 'aria-label="{{ui.brand_aria}}"')
        t2 = t2.replace('aria-label="Меню"', 'aria-label="{{ui.menu_aria}}"')
        t2 = t2.replace('aria-label="Язык / Language"', 'aria-label="{{ui.lang_aria}}"')
        t2 = t2.replace('placeholder="Поиск по справке… / Search the help…"', 'placeholder="{{ui.search_ph}}"')
        t2 = t2.replace('aria-label="Поиск по справке / Search the help"', 'aria-label="{{ui.search_aria}}"')
        if t2 != t:
            p.write_text(t2, encoding="utf-8"); n += 1
    print(f"шаблоны шапки: {n}/3 обновлено")

    # ── 5. site_src/demo.html: карточки и подписи → токены ─────────────
    p = ROOT / "site_src" / "demo.html"
    t = p.read_text(encoding="utf-8")
    t2 = t
    t2 = t2.replace(
        'alt="Вайрфрейм кабинета семьи с предупреждениями: низкий остаток участника и предстоящий платёж (S004)"',
        'alt="{{demo.ru.k130}}{{demo.en.k130}}"')
    t2 = t2.replace(
        'alt="Схема архитектуры агента: ядро pfs, реестры источников/утверждений/решений, знания и субагенты"',
        'alt="{{demo.ru.k131}}{{demo.en.k131}}"')
    t2 = t2.replace(
        "<p><b>эффект ≥ −3 п.п. · ложные <20% · повторные списания = 0</b></p>",
        "<p><b>{{demo.ru.k132}}{{demo.en.k132}}</b></p>")
    t2 = t2.replace(
        "<i>S001 · бриф → C013 (гипотеза)</i>",
        "<i>{{demo.ru.k133}}{{demo.en.k133}}</i>")
    t2 = t2.replace(
        '<div class="cv-name">Связь<em> для близких</em></div><div class="cv-tag">учебный бриф: услуги мобильного оператора</div>',
        '<div class="cv-name">{{demo.ru.k134}}{{demo.en.k134}}</div><div class="cv-tag">{{demo.ru.k135}}{{demo.en.k135}}</div>')
    if t2 != t:
        p.write_text(t2, encoding="utf-8"); print("demo.html: карточки/подписи → токены")
    else:
        print("demo.html: уже токенизировано")

    # ── 6. site_src/materials.html: alt → токены (materials-ключи) ─────
    p = ROOT / "site_src" / "materials.html"
    t = p.read_text(encoding="utf-8")
    t2 = t
    t2 = t2.replace(
        'alt="Схема архитектуры агента: ядро pfs, реестры источников/утверждений/решений, знания и субагенты"',
        'alt="{{materials.ru.k130}}{{materials.en.k130}}"')
    t2 = t2.replace(
        'alt="Вайрфрейм кабинета семьи с предупреждениями (S004)"',
        'alt="{{materials.ru.k131}}{{materials.en.k131}}"')
    if t2 != t:
        p.write_text(t2, encoding="utf-8"); print("materials.html: alt → токены")
    else:
        print("materials.html: уже токенизировано")

    # ── 7. «100/100» и «Три порога» не должны вернуться ────────────────
    for page in ("demo", "help", "materials"):
        t = (ROOT / "site_src" / f"{page}.html").read_text(encoding="utf-8")
        for bad in ("100/100", "Три порога", "Three thresholds"):
            if bad in t:
                raise SystemExit(f"PRO-133 gate: {page}.html содержит {bad!r}")
    print("гейт: 100/100 и «Три порога» отсутствуют в шаблонах ✅")

if __name__ == "__main__":
    main()
