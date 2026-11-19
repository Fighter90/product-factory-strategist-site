#!/usr/bin/env python3
"""PRO-129: регресс-чекер сайта strategyproduct.ru одним прогоном.

Проверки по pages/*.html под --root (по умолчанию — корень сайта рядом со скриптом):
  1. Битые внутренние ссылки (href/src): файла нет, фрагмента #id нет,
     выход за корень сайта.
  2. <meta name="viewport"> на каждой странице.
  3. Запрещённые бренды (мегафон, магистрат, ВШЭ, НИУ, авито) в тексте страниц.
  4. Секреты: ключи/токены (api_key, secret, token, sk-/AKIA/ghp-), id счётчика
     Метрики (политика site/ANALYTICS.md: id в git не попадает), личные пути.
  5. Риски «разъезда» на 375px: фиксированные ширины >=400px вне min()/процентов;
     страница без брейкпоинтов @media.
  6. Счётчики на страницах против vendor/meta.json (N_MAPS, N_TESTS, ...).
  7. Баланс тегов HTML (незакрытые/лишние закрывающие).
  8. Демо-раздел: название проекта в demo.html; если не «Связь для близких» —
     предупреждение pending (--strict-demo переводит в ошибку).

Код возврата: 0 — чисто (pending-предупреждение не влияет), 1 — есть находки.
Вывод: человекочитаемый текст или --json (только JSON в stdout).

Запуск:  python3 scripts/check_site.py [--root DIR] [--repo DIR] [--json] [--strict-demo]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BRANDS = ["мегафон", "магистрат", "вшэ", "ниу", "авито"]

SECRET_PATTERNS = [
    ("api_key", re.compile(r"(?i)api[_-]?key\s*[=:]\s*[\"']?[^\s\"']{6,}")),
    ("token/secret", re.compile(r"(?i)\b(secret|token|password)\s*[=:]\s*[\"']?[^\s\"']{8,}")),
    ("openai-style key", re.compile(r"sk-[a-zA-Z0-9]{10,}")),
    ("aws key", re.compile(r"AKIA[A-Z0-9]{8,}")),
    ("github token", re.compile(r"ghp_[a-zA-Z0-9]{15,}")),
    ("metrika id", re.compile(r"(?:YM_ID\s*=\s*\d+|mc\.yandex\.ru/watch/\d+|ym\(\s*\d{4,})")),
    ("personal path", re.compile(r"/Users/[A-Za-z0-9_.-]+")),
]

# фиксированная ширина >= 400px (только width; min-/max-width сжимаются и не риск);
# min()/проценты/overflow-контейнеры не риск
FIXED_WIDTH = re.compile(r"(?<![\w-])width\s*:\s*(\d{3,})px")
MEDIA_COND = re.compile(r"@media[^{]*?\)")

COUNTER_PATTERNS = [
    ("N_MAPS", re.compile(r"(\d+)\s*(?:методическ\w+\s+)?карт\b")),
    ("N_MAPS_EN", re.compile(r"(\d+)\s+method\s+cards\b", re.I)),
    ("N_TESTS", re.compile(r"[Aа]втотест\w*\s*CLI\s*\((\d+)\)|CLI\s+autotests\s*\((\d+)\)", re.I)),
    ("N_SKILLS", re.compile(r"навыков:\s*(\d+)|skills:\s*(\d+)", re.I)),
    ("N_AGENTS", re.compile(r"субагентов:\s*(\d+)|subagents:\s*(\d+)", re.I)),
    ("N_HOOKS", re.compile(r"хуков:\s*(\d+)|hooks:\s*(\d+)", re.I)),
    ("N_MCP", re.compile(r"MCP[-\s]*(?:инструмент\w*|tools)?[:\s]*(\d+)", re.I)),
]

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}

TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:\"[^\"]*\"|'[^']*'|[^>])*?)(/?)>")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def html_text(raw: str) -> str:
    """HTML → текст: без script/style, комментариев и тегов."""
    raw = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style\b.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    return re.sub(r"<[^>]+>", " ", raw)


def strip_media_conditions(css: str) -> str:
    """Убрать условия @media (...), чтобы max-width: 980px не считался шириной элемента."""
    return MEDIA_COND.sub(" ", css)


def css_scope(raw: str) -> str:
    """CSS-текст страницы: содержимое <style> + инлайновые style=\"...\"."""
    blocks = re.findall(r"<style\b.*?</style>", raw, flags=re.S | re.I)
    inline = re.findall(r"style\s*=\s*[\"']([^\"']*)[\"']", raw, flags=re.I)
    return strip_media_conditions(" ".join(blocks + inline))


# публикуемая поверхность: корень + языковые зеркала; вложенные копии и
# приложения (vendor, projects, site, assets) — не страницы сайта
EXCLUDED_DIRS = {"vendor", "projects", "site", "assets", "site_src"}


def iter_pages(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.html")
                  if not (set(p.parts) & EXCLUDED_DIRS or any(
                      part.startswith(".") for part in p.parts)))


def rel(page: Path, root: Path) -> str:
    return page.relative_to(root).as_posix()


def check_links(page: Path, root: Path, raw: str) -> list[dict]:
    found: list[dict] = []
    ids_here = set(re.findall(r"id\s*=\s*[\"']([^\"']+)[\"']", raw))
    for attr, url in re.findall(r"(href|src)\s*=\s*[\"']([^\"']+)[\"']", raw, flags=re.I):
        u = url.strip()
        if not u or u.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "#!" )):
            continue
        path_part, _, frag = u.partition("#")
        path_part = path_part.partition("?")[0]  # cache-buster вида ?v=10 не часть пути
        if not path_part:
            if frag and frag not in ids_here:
                found.append({"page": rel(page, root), "url": url, "why": "fragment"})
            continue
        target = (page.parent / path_part).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            found.append({"page": rel(page, root), "url": url, "why": "escapes-root"})
            continue
        if not target.exists():
            found.append({"page": rel(page, root), "url": url, "why": "missing"})
            continue
        if frag:
            target_ids = set(re.findall(r"id\s*=\s*[\"']([^\"']+)[\"']", read_text(target)))
            if frag not in target_ids:
                found.append({"page": rel(page, root), "url": url, "why": "fragment"})
    return found


def check_tag_balance(page: Path, root: Path, raw: str) -> list[dict]:
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    stack: list[str] = []
    problems: list[dict] = []
    for close, name, _attrs, self_close in TAG_RE.findall(raw):
        name = name.lower()
        if name in VOID_TAGS or self_close:
            continue
        if close:
            if stack and stack[-1] == name:
                stack.pop()
            elif name in stack:
                while stack and stack[-1] != name:
                    problems.append({"page": rel(page, root),
                                     "problem": f"незакрыт <{stack.pop()}> перед </{name}>"})
                if stack:
                    stack.pop()
            else:
                problems.append({"page": rel(page, root), "problem": f"лишний </{name}>"})
        else:
            stack.append(name)
    for leftover in stack:
        problems.append({"page": rel(page, root), "problem": f"незакрыт <{leftover}> до конца файла"})
    return problems


def parse_counters(root: Path) -> dict[str, list[int]]:
    counters: dict[str, list[int]] = {}
    for page in iter_pages(root):
        text = html_text(read_text(page))
        for name, pat in COUNTER_PATTERNS:
            for m in pat.finditer(text):
                value = next((g for g in m.groups() if g), None)
                if value is not None:
                    counters.setdefault(name, []).append(int(value))
    return {k: sorted(set(v)) for k, v in counters.items()}


def extract_demo_title(demo_page: Path) -> str:
    if not demo_page.exists():
        return ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", read_text(demo_page), re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def run(root: Path, repo: Path | None, strict_demo: bool) -> tuple[dict, int]:
    broken: list[dict] = []
    forbidden: list[dict] = []
    secrets: list[dict] = []
    missing_viewport: list[str] = []
    css_issues: list[dict] = []
    tag_problems: list[dict] = []

    pages = iter_pages(root)
    for page in pages:
        raw = read_text(page)
        broken.extend(check_links(page, root, raw))
        if not re.search(r"<meta\s+name\s*=\s*[\"']viewport[\"']", raw, re.I):
            missing_viewport.append(rel(page, root))
        text = html_text(raw).lower()
        for brand in BRANDS:
            if brand in text:
                forbidden.append({"page": rel(page, root), "brand": brand, "match": brand})
        for kind, pat in SECRET_PATTERNS:
            for m in pat.finditer(raw):
                secrets.append({"page": rel(page, root), "kind": kind, "match": m.group(0)[:60]})
        css = css_scope(raw)
        for m in FIXED_WIDTH.finditer(css):
            ctx = css[max(0, m.start() - 60):m.end() + 60]
            if int(m.group(1)) >= 400 and "min(" not in ctx and "overflow" not in ctx:
                css_issues.append({"page": rel(page, root), "why": "fixed-width",
                                   "detail": m.group(0)})
        if css and not re.search(r"@media", raw, re.I):
            css_issues.append({"page": rel(page, root), "why": "no-breakpoints",
                               "detail": "нет @media-брейкпоинтов"})
        tag_problems.extend(check_tag_balance(page, root, raw))

    counters = parse_counters(root)
    mismatches: list[dict] = []
    vendor_path = root / "vendor" / "meta.json"
    vendor: dict = {}
    if vendor_path.exists():
        try:
            vendor = json.loads(vendor_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            vendor = {}
    for name, shown in counters.items():
        if name in vendor:
            for value in shown:
                if int(value) != int(vendor[name]):
                    mismatches.append({"name": name, "shown": value,
                                       "vendor": vendor[name], "page": "*"})

    demo_title = extract_demo_title(root / "demo.html")
    demo_pending = "Связь для близких" not in demo_title

    report = {
        "pages_scanned": len(pages),
        "broken_links": broken,
        "forbidden": forbidden,
        "secrets": secrets,
        "missing_viewport": sorted(set(missing_viewport)),
        "css_issues": css_issues,
        "tag_balance": tag_problems,
        "counters": counters,
        "counter_mismatches": mismatches,
        "demo": {"title": demo_title, "pending": demo_pending},
    }
    if repo and (repo / "vendor" / "meta.json").exists():
        try:
            report["repo_counters"] = json.loads(
                (repo / "vendor" / "meta.json").read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass

    errors = (broken or forbidden or secrets or report["missing_viewport"]
              or css_issues or mismatches or tag_problems
              or (strict_demo and demo_pending))
    return report, (1 if errors else 0)


def print_human(report: dict) -> None:
    ok = lambda cond: "✓" if not cond else "✗"
    print(f"Страниц просканировано: {report['pages_scanned']}")
    print(f"{ok(report['broken_links'])} битых внутренних ссылок: {len(report['broken_links'])}")
    for b in report["broken_links"][:10]:
        print(f"  ✗ {b['page']}: {b['url']} ({b['why']})")
    print(f"{ok(report['forbidden'])} запрещённые бренды: {len(report['forbidden'])}")
    for f in report["forbidden"][:10]:
        print(f"  ✗ {f['page']}: {f['match']} ({f['brand']})")
    print(f"{ok(report['secrets'])} секреты: {len(report['secrets'])}")
    for s in report["secrets"][:10]:
        print(f"  ✗ {s['page']}: {s['match']} ({s['kind']})")
    print(f"{ok(report['missing_viewport'])} без viewport: {len(report['missing_viewport'])}"
          + (f" → {', '.join(report['missing_viewport'][:8])}" if report["missing_viewport"] else ""))
    print(f"{ok(report['css_issues'])} риски 375px: {len(report['css_issues'])}")
    for c in report["css_issues"][:10]:
        print(f"  ✗ {c['page']}: {c['why']} — {c.get('detail', '')}")
    print(f"{ok(report['tag_balance'])} проблемы баланса тегов: {len(report['tag_balance'])}")
    for t in report["tag_balance"][:10]:
        print(f"  ✗ {t['page']}: {t['problem']}")
    print(f"{ok(report['counter_mismatches'])} расхождения счётчиков: {len(report['counter_mismatches'])}")
    for m in report["counter_mismatches"][:10]:
        print(f"  ✗ {m['name']}: на сайте {m['shown']}, в vendor {m['vendor']}")
    for name, values in sorted(report["counters"].items()):
        print(f"  · {name}: {values}")
    demo = report["demo"]
    if demo["pending"]:
        print(f"⚠ демо-проект снапшота: «{demo['title'] or '?'}» — ожидается «Связь для близких»")
    else:
        print(f"✓ демо-проект: «{demo['title']}»")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Регресс-чекер сайта (PRO-129)")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--root", default=str(default_root), help="корень сайта")
    parser.add_argument("--repo", default=None, help="корень основного репо (для repo_counters)")
    parser.add_argument("--json", action="store_true", help="вывод JSON")
    parser.add_argument("--strict-demo", action="store_true",
                        help="pending-предупреждение демо считать ошибкой")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    repo = Path(args.repo).resolve() if args.repo else None
    report, code = run(root, repo, args.strict_demo)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
        print(f"Итог: {'есть находки' if code else 'чисто'} (код {code})")
    return code


if __name__ == "__main__":
    sys.exit(main())
