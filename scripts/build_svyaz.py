#!/usr/bin/env python3
"""PRO-127: demo/help/materials под демо «Связь для близких» + index proof/demo.

build_site.py парсит старый прогон projects/демо (MRR-воронка беты, Pro $/Unlimited $,
рынок resume builders, C011) — на новом демо он падает громко. Этот скрипт повторяет
конвейер build_pages (шаги 0–7: токены страниц → head → LANGSWITCH → фильтр языка →
../ для EN-ассетов) с числами нового демо в VALUES и строками site/i18n/{ru,en}.json.

Правки контента заданы парами (старое → новое) и применяются идемпотентно: если
«старое» не найдено, но «новое» уже в файле — шаг пропускается, иначе BuildError.

Запуск: python3 scripts/build_svyaz.py
Пишет: site/{demo,help,materials}.html, site/en/{demo,help,materials}.html,
       site/i18n/{ru,en}.json, site/index.html, site/en/index.html.
Копирование в корень (деплой) — командами cp в shell, как в PRO-66.
"""
from __future__ import annotations

import json
import re
import sys
import html as html_mod
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site as bs  # filter_lang, LANGSWITCH, I18N_DIR, SITE_SRC, PAGE_DICT, BuildError

PROJ = "связь-для-близких-и-собственных-устройств"
GH = "https://github.com/Fighter90/product-factory-strategist"
GH_BLOB = GH + "/blob/main"
P = quote(PROJ)

DEMO_NAME_RU = "«Связь для близких»"
DEMO_NAME_EN = "Connection for Loved Ones"

TITLE_RU = f"Демо-разбор: {DEMO_NAME_RU} — от задачи руководителя до six-pager"
TITLE_EN = f"Demo walkthrough: {DEMO_NAME_EN} — from a director's brief to a six-pager"
DESC_RU = ("Сквозной 12-шаговый прогон ИИ-агента на брифе заказчика «Связь для близких и "
           "собственных устройств» (мобильный оператор): 26 утверждений с источниками, "
           "5 вариантов и red team — 20 ударов, решение D001 «Предупреждение до перебоя» — "
           "пилот 600 групп с порогом −3 п.п.")
DESC_EN = ("An end-to-end 12-step run of the AI agent on a client brief, Connection for Loved "
           "ones and personal devices (a mobile operator): 26 claims with sources, 5 options "
           "and a red team — 20 hits, decision D001 \"Warn before the outage\" — a 600-group "
           "pilot with a −3 pp threshold.")

# ---------------------------------------------------------------- i18n updates

U: dict = {"ru": {"demo_page": {}, "help_page": {}, "materials_page": {}, "ui": {}},
           "en": {"demo_page": {}, "help_page": {}, "materials_page": {}, "ui": {}}}

def u(page: str, key: str, ru: str, en: str):
    U["ru"][page][key] = ru
    U["en"][page][key] = en

# --- demo_page: шапка -------------------------------------------------------
u("demo_page", "title", TITLE_RU, TITLE_EN)
u("demo_page", "og_title", TITLE_RU, TITLE_EN)
u("demo_page", "description", DESC_RU, DESC_EN)
u("demo_page", "lead",
  '<p class="sub" lang="ru">Сквозной прогон агента на брифе заказчика — услуги вымышленного '
  'мобильного оператора для семейных групп и владельцев нескольких номеров. Ниже — сама задача, '
  '12 шагов, доказательная база, 5 вариантов с red team и решение с пилотом.</p>',
  '<p class="sub" lang="en">An end-to-end run on a client brief — services of a fictional mobile '
  'operator for family groups and owners of several numbers. Below: the task itself, 12 steps, '
  'the evidence base, 5 options with a red team, and the decision with a pilot.</p>')
u("demo_page", "k008",
  f'<h1 lang="ru">Демо-разбор: <span class="grad">{DEMO_NAME_RU}</span> — от задачи руководителя до six-pager</h1>',
  f'<h1 lang="en">Demo walkthrough: <span class="grad">{DEMO_NAME_EN}</span> — from a director\'s brief to a six-pager</h1>')
u("demo_page", "k016",
  '<span lang="ru"> six-pager × 2 формата</span>',
  '<span lang="en"> six-pager × 2 formats</span>')

# --- demo_page: карточка продукта + задание ---------------------------------
u("demo_page", "k018",
  '<p lang="ru">Учебный бриф заказчика: вымышленный мобильный оператор; одни клиенты помогают '
  'близким со связью, другие обслуживают несколько собственных номеров. Цель планового года — '
  'валовая прибыль ≥285 млн ₽; разрыв к прогнозу «без изменений» — 6 млн ₽ = 12 000 доп. '
  'оплаченных месяцев × 500 ₽.</p>',
  '<p lang="en">A teaching brief from a client: a fictional mobile operator; some customers help '
  'loved ones stay connected, others run several numbers of their own. The planned-year goal is '
  'gross profit ≥ 285M ₽; the gap to the "no change" forecast is 6M ₽ = 12,000 extra paid '
  'months × ₽500.</p>')
u("demo_page", "k019",
  '<p lang="ru">Прогон полный: 12 шагов, 3 обязательные паузы человека. Реестр: 26 утверждений — '
  '10 фактов, 8 допущений, 4 гипотезы, 4 вывода; 4 источника (бриф, 2 ИИ-респондента — только '
  'гипотезы, вайрфрейм); расчёты воспроизводимы: economics.py и 4 книги Excel на формулах.</p>',
  '<p lang="en">A complete run: 12 steps, 3 mandatory human pauses. The registry: 26 claims — '
  '10 facts, 8 assumptions, 4 hypotheses, 4 inferences; 4 sources (the brief, 2 AI respondents — '
  'hypotheses only, a wireframe); calculations are reproducible: economics.py and 4 formula-based '
  'Excel workbooks.</p>')
u("demo_page", "k021",
  '<p lang="ru"><b>Задание агенту (дословно из project.json):</b> «Ваша команда отвечает за услуги '
  'вымышленного мобильного оператора. Одни клиенты помогают близким со связью. Другие обслуживают '
  'несколько собственных номеров. Решите, кому помочь в первую очередь, что именно изменить и '
  'почему оператору стоит вложить в это деньги. Подготовьте план на ближайший год и задайте '
  'ориентир на конец третьего года работы…»</p>',
  '<p lang="en"><b>Brief to the agent (verbatim from project.json):</b> "Your team runs the services '
  'of a fictional mobile operator. Some customers help loved ones stay connected. Others manage '
  'several numbers of their own. Decide who to help first, what exactly to change, and why the '
  'operator should invest money in it. Prepare a plan for the coming year and set a benchmark for '
  'the end of year three…"</p>')
u("demo_page", "k022",
  '<p lang="ru"><b>Ось сравнения:</b> вклад в валовую прибыль планового года (доп. оплаченные '
  'месяцы × 500 ₽) и активные группы (цель 8 000).</p>',
  '<p lang="en"><b>Comparison axis:</b> contribution to the planned-year gross profit (extra paid '
  'months × ₽500) and active groups (goal: 8,000).</p>')
u("demo_page", "k023",
  '<p lang="ru"><b>Ограничения:</b> числа учебные, заданы брифом; два решения руководителя — конец '
  'Q1 (запускать ли пилот) и конец Q2 (расширять ли охват); согласия участников гранулярные: '
  'остаток / платежи / оплата за меня.</p>',
  '<p lang="en"><b>Constraints:</b> all numbers are teaching numbers set by the brief; two decisions '
  'for the lead — end of Q1 (run the pilot?) and end of Q2 (expand?); participant consents are '
  'granular: balance / payments / pay on my behalf.</p>')

# --- demo_page: обзор — видео и материалы -----------------------------------
# PRO-133/правка руководителя: секция «Обзор демо» удалена со страницы демо (видео — на materials и главной)
u("demo_page", "k024", "", "")
u("demo_page", "k025", "", "")
u("demo_page", "k026",
  '<span lang="ru">svyaz-overview — видео · RU · 4:20</span>',
  '<span lang="en">svyaz-overview — video · RU · 4:20</span>')
u("demo_page", "k027",
  '<div class="shot-cap" lang="ru">Сквозной прогон «Связь для близких» за 4 минуты: задача, реестр '
  'утверждений, red team, решение D001 с пилотом 600 групп.</div>',
  '<div class="shot-cap" lang="en">The end-to-end run in 4 minutes: the task, the claim registry, '
  'the red team, decision D001 with the 600-group pilot.</div>')
u("demo_page", "k028",
  '<span lang="ru">svyaz-overview — видео · EN · 4:14</span>',
  '<span lang="en">svyaz-overview — video · EN · 4:14</span>')
u("demo_page", "k029",
  '<div class="shot-cap" lang="ru">Тот же прогон на английском — six-pager, Excel и реестры '
  'существуют в двух языках.</div>',
  '<div class="shot-cap" lang="en">The same run in English — the six-pager, Excel and registries '
  'exist in two languages.</div>')
u("demo_page", "k030",
  '<span lang="ru">Вайрфрейм: кабинет семьи · S004</span>',
  '<span lang="en">Wireframe: family dashboard · S004</span>')
u("demo_page", "k031",
  '<div class="shot-cap" lang="ru">Макет кабинета с предупреждениями: низкий остаток участника и '
  'предстоящий платёж — ровно то, что разбирает UX-ревью 06_ux_review_S004.md.</div>',
  '<div class="shot-cap" lang="en">The dashboard mock with warnings: a participant\'s low balance and '
  'an upcoming payment — exactly what 06_ux_review_S004.md reviews.</div>')
u("demo_page", "k032",
  '<span lang="ru">Архитектура агента</span>',
  '<span lang="en">Agent architecture</span>')
u("demo_page", "k033",
  '<div class="shot-cap" lang="ru">Схема архитектуры: CLI/MCP-ядро pfs, реестры источников, '
  'утверждений и решений, знания и субагенты — гарантии в коде, не в промптах.</div>',
  '<div class="shot-cap" lang="en">The architecture diagram: the pfs CLI/MCP core, source/claim/'
  'decision registries, knowledge and subagents — guarantees in code, not in prompts.</div>')
u("demo_page", "k034",
  '<span lang="ru">Реестр утверждений</span>',
  '<span lang="en">Claim registry</span>')
u("demo_page", "k035",
  '<div class="shot-cap" lang="ru">26 утверждений с типом и силой A–D: факты — только с источником, '
  'синтетика — только гипотезы.</div>',
  '<div class="shot-cap" lang="en">26 claims with type and A–D strength: facts always carry a source, '
  'synthetic data yields hypotheses only.</div>')

# --- demo_page: 12 шагов ----------------------------------------------------
u("demo_page", "k038",
  '<span lang="ru">бриф заказчика, {{SOURCES_COUNT}} источника (бриф, ИИ-респонденты — гипотезы, '
  'вайрфрейм), {{CLAIMS_COUNT}} утверждений, учебные числа из задания</span>',
  '<span lang="en">the client brief, {{SOURCES_COUNT}} sources (the brief, AI respondents — '
  'hypotheses, a wireframe), {{CLAIMS_COUNT}} claims, teaching numbers from the task</span>')
u("demo_page", "k039",
  '<span lang="ru">ситуация с пробелами, {{OPT_COUNT}} варианта A–E, red team: {{D_OBJ}} возражений '
  '+ {{D_ASM}} скрытых допущений — пороги записаны до данных</span>',
  '<span lang="en">the situation with gaps, {{OPT_COUNT}} options A–E, red team: {{D_OBJ}} objections '
  '+ {{D_ASM}} hidden assumptions — thresholds written before data</span>')
u("demo_page", "k040",
  '<span lang="ru">продуктовая + коммуникационная стратегии, план проверки, ревью 98/100 '
  '(check --strict: 0 ошибок), six-pager RU+EN + 4 книги Excel</span>',
  '<span lang="en">product + communication strategies, a validation plan, a 98/100 review '
  '(check --strict: 0 errors), a RU+EN six-pager + 4 Excel workbooks</span>')
u("demo_page", "k041",
  '<span lang="ru">решение D001 «Предупреждение до перебоя» с основаниями и датой пересмотра, '
  'мониторинг обязательств открыт</span>',
  '<span lang="en">decision D001 "Warn before the outage" with grounds and a review date, commitment '
  'monitoring open</span>')

# --- demo_page: факты -------------------------------------------------------
u("demo_page", "k042",
  '<h2 class="rv" lang="ru">Что известно: цифры брифа с источниками</h2>',
  '<h2 class="rv" lang="en">What is known: the brief\'s numbers with sources</h2>')
u("demo_page", "k043",
  '<p class="lead rv d1" lang="ru">Каждое число — с типом, силой A–D и источником S001 (бриф '
  'заказчика). Цепочка S001 → C### → решение D001 проверяется командой pfs impact.</p>',
  '<p class="lead rv d1" lang="en">Every number carries a type, an A–D strength and source S001 (the '
  'client brief). The chain S001 → C### → decision D001 is checkable with pfs impact.</p>')
u("demo_page", "k044",
  '<b lang="ru">285 млн ₽</b>', '<b lang="en">285M ₽</b>')
u("demo_page", "k045",
  '<span lang="ru">цель валовой прибыли планового года; прогноз «без изменений» — 279 млн ₽; '
  'разрыв 6 млн ₽</span>',
  '<span lang="en">the planned-year gross profit goal; the "no change" forecast is 279M ₽; the gap '
  'is 6M ₽</span>')
u("demo_page", "k046",
  '<b lang="ru">12 000 мес</b>', '<b lang="en">12,000 mo</b>')
u("demo_page", "k047",
  '<span lang="ru">доп. оплаченных месяцев × 500 ₽ закрывают разрыв 6 млн ₽ — граница решения '
  'из брифа</span>',
  '<span lang="en">extra paid months × ₽500 close the 6M ₽ gap — the decision boundary set by the '
  'brief</span>')
u("demo_page", "k048",
  '<span lang="ru">S001 · бриф заказчика → C003</span>',
  '<span lang="en">S001 · the client brief → C003</span>')
u("demo_page", "k049",
  '<b lang="ru">12% → 9%</b>', '<b lang="en">12% → 9%</b>')
u("demo_page", "k050",
  '<span lang="ru">целевое снижение доли ограничений из-за исчерпания объёма (−3 п.п. = четверть) — '
  'гипотеза эффекта, проверяет пилот</span>',
  '<span lang="en">the target drop in exhaustion-driven restrictions (−3 pp = a quarter) — the effect '
  'hypothesis the pilot tests</span>')
u("demo_page", "k051",
  '<span lang="ru">домохозяйств доступны оператору из 300 тыс., которым нужна помощь со связью; '
  'владельцев нескольких номеров — 40 тыс. из 180 тыс.</span>',
  '<span lang="en">households available to the operator out of 300K needing connection help; owners '
  'of several numbers — 40K out of 180K</span>')
u("demo_page", "k052",
  '<span lang="ru">целевой сценар: 5 500 номеров × 3 мес × 500 ₽ − 1,5 млн прямых расходов → '
  '285,8 млн ₽ — цель достигается с запасом</span>',
  '<span lang="en">the target scenario: 5,500 numbers × 3 mo × ₽500 − 1.5M direct costs → '
  '285.8M ₽ — the goal met with margin</span>')
u("demo_page", "k053",
  '<b lang="ru">8 000</b>', '<b lang="en">8,000</b>')
u("demo_page", "k054",
  '<span lang="ru">активных групп — цель года; сейчас 5 000 из 8 000 подключённых (62,5%): '
  'работать должны две трети групп</span>',
  '<span lang="en">active groups — the yearly goal; now 5,000 of 8,000 connected (62.5%): two thirds '
  'of groups must act</span>')
u("demo_page", "k055",
  '<div class="note rv" lang="ru">Рынок учебный — все числа заданы брифом [S001]. Частоты причин '
  'перебоя — допущение [C011], проверка выгрузкой пилота. ИИ-респонденты дали только гипотезы '
  '[C019,C020] — синтетика не доказательство.</div>',
  '<div class="note rv" lang="en">The market is a teaching one — every number is set by the brief '
  '[S001]. The frequencies of outage causes are an assumption [C011] checked against pilot data. '
  'AI respondents produced hypotheses only [C019,C020] — synthetic data is not proof.</div>')

# --- demo_page: варианты ----------------------------------------------------
u("demo_page", "k056",
  '<h2 class="rv" lang="ru">Варианты и red team: {{OPT_COUNT}} путей, {{RT_HITS}} ударов</h2>',
  '<h2 class="rv" lang="en">Options and red team: {{OPT_COUNT}} paths, {{RT_HITS}} hits</h2>')
u("demo_page", "k057",
  '<p class="lead rv d1" lang="ru">Red team — отдельный субагент: {{D_OBJ}} возражений + '
  '{{D_ASM}} скрытых допущений по выбранному варианту. Вердикт — «требует доработки до пилота»; '
  'удары встроены порогами [C021–C026].</p>',
  '<p class="lead rv d1" lang="en">The red team is a separate subagent: {{D_OBJ}} objections + '
  '{{D_ASM}} hidden assumptions on the chosen option. Verdict: "needs rework before the pilot"; '
  'the hits are built into thresholds [C021–C026].</p>')
u("demo_page", "k060",
  '<th lang="ru">Вклад в прибыль планового года</th>',
  '<th lang="en">Planned-year profit contribution</th>')
u("demo_page", "k062",
  '<td lang="ru"><b>A</b> · оставить как есть</td>',
  '<td lang="en"><b>A</b> · keep as is</td>')
u("demo_page", "k063",
  '<td lang="ru">текущее обслуживание: группы и переключение номеров уже работают, предупреждений нет</td>',
  '<td lang="en">current service: groups and number switching already work, no warnings</td>')
u("demo_page", "k064",
  '<td lang="ru">цели года не достигнуты по всем пяти строкам: −6 млн ₽ к плану, 5 000 активных '
  'из 8 000</td>',
  '<td lang="en">yearly goals missed on all five lines: −6M ₽ to plan, 5,000 active out of 8,000</td>')
u("demo_page", "k065",
  '<td lang="ru"><b>B</b> · «Предупреждение до перебоя» <span style="color:var(--accent)">← выбран</span></td>',
  '<td lang="en"><b>B</b> · "Warn before the outage" <span style="color:var(--accent)">← chosen</span></td>')
u("demo_page", "k066",
  '<td lang="ru">сообщение организатору: низкий остаток участника (~20% на 3 дня) и предстоящий '
  'платёж (напоминание плательщику; гранулярные согласия)</td>',
  '<td lang="en">a message to the organizer: a participant\'s low balance (~20% for 3 days) and an '
  'upcoming payment (a reminder to the payer; granular consents)</td>')
u("demo_page", "k067",
  '<td lang="ru"><b>+6,75 млн ₽</b> нетто → 285,8 млн (осн. ход: 5 500 номеров × 3 мес − 1,5 млн); '
  'неблагоприятный +1,5 млн → 280,5 млн</td>',
  '<td lang="en"><b>+6.75M ₽</b> net → 285.8M (base case: 5,500 numbers × 3 mo − 1.5M); downside '
  '+1.5M → 280.5M</td>')
u("demo_page", "k068",
  '<td lang="ru">инкрементальность платежей не доказана — сдвиги >30% при окне 90 дней обнуляют '
  'эффект [C021]; конверсия согласий неизвестна [C019]</td>',
  '<td lang="en">payment incrementality is unproven — shifts >30% in a 90-day window nullify the '
  'effect [C021]; consent conversion unknown [C019]</td>')
u("demo_page", "k069",
  '<td lang="ru"><b>C</b> · «Семейный кабинет»</td>',
  '<td lang="en"><b>C</b> · "Family dashboard"</td>')
u("demo_page", "k070",
  '<td lang="ru">сводная карточка остатков семьи + передача интернета в один клик</td>',
  '<td lang="en">a family balance card + one-click data sharing</td>')
u("demo_page", "k071",
  '<td lang="ru">прямой вклад не оценивается: боль в осведомлённости, не в UX [C005]</td>',
  '<td lang="en">direct contribution not estimable: the pain is awareness, not UX [C005]</td>')
u("demo_page", "k072",
  '<td lang="ru">≥4–5 чел.-мес — перебор ресурса Q2 [C010]; организатор всё равно узнаёт о перебое '
  'от близкого [C005]</td>',
  '<td lang="en">≥4–5 person-months — over the Q2 budget [C010]; the organizer learns of outages from '
  'loved ones anyway [C005]</td>')
u("demo_page", "k073",
  '<td lang="ru"><b>D</b> · «Не думай о роутере»</td>',
  '<td lang="en"><b>D</b> · "Never think about the router"</td>')
u("demo_page", "k074",
  '<td lang="ru">предупреждения по номерам устройств — владельцы первой очередью</td>',
  '<td lang="en">warnings for device numbers — device owners served first</td>')
u("demo_page", "k075",
  '<td lang="ru">вклад меньше B: база 40 тыс. против 100 тыс. [C004]</td>',
  '<td lang="en">contribution below B: a 40K base vs 100K [C004]</td>')
u("demo_page", "k076",
  '<td lang="ru">интеграция состояния устройства требует данных от вендоров [C006]; автоплатёж '
  'закрывает большинство случаев [C020]</td>',
  '<td lang="en">device-state integration needs vendor data [C006]; autopay already covers most cases '
  '[C020]</td>')
u("demo_page", "k077",
  '<td lang="ru"><b>E</b> · закрыть направление</td>',
  '<td lang="en"><b>E</b> · shut the track down</td>')
u("demo_page", "k078",
  '<td lang="ru">не финансировать услуги «близких» в плановом году, пересмотреть цели с руководством</td>',
  '<td lang="en">do not fund the "loved ones" services in the planned year; revise goals with '
  'management</td>')
u("demo_page", "k079",
  '<td lang="ru">0 → 279 млн: цели не достигнуты осознанно; разрыв 6 млн достижим по формуле '
  'брифа [C003] — отказ без пилота преждевременен</td>',
  '<td lang="en">0 → 279M: goals missed knowingly; the 6M gap is reachable per the brief\'s formula '
  '[C003] — quitting without a pilot is premature</td>')

# --- demo_page: вердикт -----------------------------------------------------
u("demo_page", "k081",
  '<p class="lead rv d1" lang="ru">Рекомендация — не «лучший вариант вообще», а лучший при '
  'ограничениях брифа: существующие данные и механика [C005,C006], ресурс 3 чел.-мес [C010], '
  'измеримый порог отката. D — вторая очередь Q3–Q4, C — кандидат на вторую итерацию B.</p>',
  '<p class="lead rv d1" lang="en">The recommendation is not "the best option overall" but the best '
  'under the brief\'s constraints: existing data and mechanics [C005,C006], a 3 person-month budget '
  '[C010], a measurable fallback threshold. D moves to Q3–Q4; C is a candidate for B\'s second '
  'iteration.</p>')
u("demo_page", "k083",
  '<p lang="ru"><b>«Предупреждение до перебоя»:</b> своевременное сообщение организатору — «у '
  'участника N остаток ~20% на 3 дня» и «по номеру M 5-го спишется X руб. — отправь напоминание '
  'плательщику». Данные уже у оператора [C005,C006]; добавляется только информирование + UI '
  'согласий [C009].</p>',
  '<p lang="en"><b>"Warn before the outage":</b> a timely message to the organizer — "participant N '
  'has ~20% balance left for 3 days" and "number M will be charged X on the 5th — send the payer a '
  'reminder". The data already exists at the operator [C005,C006]; only notifications + a consent UI '
  'are added [C009].</p>')
u("demo_page", "k084",
  '<p lang="ru">Пилот — к концу Q1: решение руководителя по порогам, записанным до данных; первые '
  'оценки эффекта — к концу Q2 [C013].</p>',
  '<p lang="en">The pilot starts by end of Q1: the lead decides by thresholds written before data; '
  'first effect estimates by end of Q2 [C013].</p>')
u("demo_page", "k085",
  '<p lang="ru">Экономика: основной ход +6,75 млн нетто → 285,8 млн ₽ (цель с запасом); '
  'неблагоприятный +1,5 млн → 280,5 млн; сценарии «ноль» и «минус» — в economics.py [C021].</p>',
  '<p lang="en">Economics: base case +6.75M net → 285.8M ₽ (goal met with margin); downside +1.5M → '
  '280.5M; "zero" and "minus" scenarios live in economics.py [C021].</p>')
u("demo_page", "k087",
  '<p lang="ru"><b>Инкрементальность</b> — расчёт по датам платежей против контроля, окно '
  'каннибализации 90 дней; сдвиги >30% → эффект обнуляется [C021].</p>',
  '<p lang="en"><b>Incrementality</b> — computed from payment dates against control, a 90-day '
  'cannibalization window; shifts >30% nullify the effect [C021].</p>')
u("demo_page", "k088",
  '<p lang="ru"><b>Гранулярные согласия</b> — 3 раздельных (остаток / платежи / оплата за меня); '
  '«подтвердите» убрано из текста; отзывы >15% — стоп-метрика [C009,C022].</p>',
  '<p lang="en"><b>Granular consents</b> — 3 separate ones (balance / payments / pay for me); '
  '"confirm" removed from the copy; withdrawal >15% is a stop metric [C009,C022].</p>')
u("demo_page", "k089",
  '<p lang="ru"><b>Каннибализация</b> — раздельный лог реакций (перевод ГБ / оплата / ничего); '
  'вклад считается только по оплаченным месяцам [C023].</p>',
  '<p lang="en"><b>Cannibalization</b> — reactions logged separately (share GB / pay / nothing); '
  'contribution counts paid months only [C023].</p>')
u("demo_page", "k090",
  '<p lang="ru"><b>Точность канала</b> — precision ≥80%, ≤2 алерта/нед, «тихий режим» новых '
  'номеров, сверка автоплатежа при отправке [C026].</p>',
  '<p lang="en"><b>Channel precision</b> — precision ≥80%, ≤2 alerts/week, a quiet mode for new '
  'numbers, autopay status checked on send [C026].</p>')
u("demo_page", "k092",
  '<p lang="ru"><b>C — «Семейный кабинет»:</b> ≥4–5 чел.-мес — перебор ресурса; кандидат на вторую '
  'итерацию B, если пилот покажет потребность в контексте всей семьи.</p>',
  '<p lang="en"><b>C — "Family dashboard":</b> ≥4–5 person-months — over budget; a candidate for B\'s '
  'second iteration if the pilot shows a need for whole-family context.</p>')
u("demo_page", "k093",
  '<p lang="ru"><b>D — «Не думай о роутере»:</b> отложено на Q3–Q4 — интеграция с устройствами '
  '[C006], отодвигает семейную цель 8 000 [C002].</p>',
  '<p lang="en"><b>D — "Never think about the router":</b> moved to Q3–Q4 — device integration [C006], '
  'delays the family goal of 8,000 [C002].</p>')
u("demo_page", "k094",
  '<p lang="ru"><b>E — закрыть направление:</b> осознанный отказ от цели; правомерен только при '
  'пересмотре целей руководством.</p>',
  '<p lang="en"><b>E — shut the track down:</b> a conscious放弃 of the goal; legitimate only if '
  'management revises the goals.</p>'.replace("放弃", "waiving"))
u("demo_page", "k095",
  '<p lang="ru"><b>A — оставить как есть:</b> разрыв −6 млн ₽ и отставание базового года [C001] '
  'скорее усилятся.</p>',
  '<p lang="en"><b>A — keep as is:</b> the −6M ₽ gap and last year\'s shortfall [C001] will likely '
  'worsen.</p>')
u("demo_page", "k096",
  '<div class="note rv" lang="ru"><b>Решение D001 — «Предупреждение до перебоя» (вариант B):</b> '
  'A/B-пилот на 600 семейных группах (6 недель набора + 14 дней наблюдения, ITT, рандомизация '
  'по семьям). Расширение планового года — только при эффекте ≥−3 п.п. по ограничениям из-за '
  'исчерпания [C013]. Владельцы нескольких номеров — вторая очередь Q3–Q4 [C016]. Пересмотр — '
  '2027-04-30.</div>',
  '<div class="note rv" lang="en"><b>Decision D001 — "Warn before the outage" (option B):</b> an A/B '
  'pilot on 600 family groups (6 weeks of intake + 14 days of observation, ITT, cluster '
  'randomization by family). Planned-year expansion only if the effect is ≥−3 pp on exhaustion-driven '
  'restrictions [C013]. Owners of several numbers — the second wave, Q3–Q4 [C016]. Review: '
  '2027-04-30.</div>')

# --- demo_page: экономика ---------------------------------------------------
u("demo_page", "k097",
  '<h2 class="rv" lang="ru">Экономика: от доп. месяцев к прибыли года</h2>',
  '<h2 class="rv" lang="en">Economics: from extra months to yearly profit</h2>')
u("demo_page", "k098",
  '<p class="lead rv d1" lang="ru">Граница решения задана брифом: 500 ₽ валовой прибыли за один '
  'доп. оплаченный месяц [C003]. 12 000 месяцев закрывают разрыв 6 млн ₽; целевой сценар — '
  '5 500 номеров × 3 мес = 16 500 мес × 500 ₽ − 1,5 млн расходов = <b>+6,75 млн ₽</b>.</p>',
  '<p class="lead rv d1" lang="en">The decision boundary is set by the brief: ₽500 of gross profit '
  'per extra paid month [C003]. 12,000 months close the 6M ₽ gap; the target scenario — 5,500 '
  'numbers × 3 mo = 16,500 mo × ₽500 − 1.5M costs = <b>+6.75M ₽</b>.</p>')
u("demo_page", "k099",
  '<div class="note rv" lang="ru">Сценарии — модель до данных, расчёт воспроизводим: '
  'analysis/economics.py демо-проекта. Фактический вклад решает пилот: считаются только оплаченные '
  'месяцы, окно каннибализации 90 дней [C021,C023].</div>',
  '<div class="note rv" lang="en">The scenarios are a pre-data model, reproducible via analysis/'
  'economics.py in the demo project. The pilot decides the actual contribution: paid months only, '
  'a 90-day cannibalization window [C021,C023].</div>')

# --- demo_page: six-pager ---------------------------------------------------
u("demo_page", "k101",
  '<p class="lead rv d1" lang="ru">Отчёт для комитета — в формате референса стратегии: FAQ-1…6, '
  'расчёты рядом с решениями, приложения Excel. Ниже — суть каждого раздела.</p>',
  '<p class="lead rv d1" lang="en">The committee report follows the growth-strategy reference format: '
  'FAQ-1…6, calculations next to decisions, Excel appendices. Below is the gist of each section.</p>')

# --- demo_page: план проверки ----------------------------------------------
u("demo_page", "k105",
  '<h2 class="rv" lang="ru">План проверки: пороги и контр-метрики</h2>',
  '<h2 class="rv" lang="en">Validation plan: thresholds and counter-metrics</h2>')
u("demo_page", "k106",
  '<p class="lead rv d1" lang="ru">A/B-пилот на 600 семейных группах: 6 недель набора (темп ≥100 '
  'впервые подходящих групп/нед [C012]) + до 14 дней наблюдения. ITT: в расчёте все включённые. '
  'Рандомизация по семьям — участники делят пакет.</p>',
  '<p class="lead rv d1" lang="en">An A/B pilot on 600 family groups: 6 weeks of intake (≥100 newly '
  'eligible groups/week [C012]) + up to 14 days of observation. ITT: everyone included counts. '
  'Randomization by family — participants share the data plan.</p>')
u("demo_page", "k107",
  '<h3 lang="ru">Расширять</h3>', '<h3 lang="en">Expand</h3>')
u("demo_page", "k108",
  '<p lang="ru">→ расширение планового года: цель 285 млн ₽ остаётся, владельцы номеров — Q3–Q4.</p>',
  '<p lang="en">→ expand the planned year: the 285M ₽ goal stands, device owners come in Q3–Q4.</p>')
u("demo_page", "k109",
  '<h3 lang="ru">Продлить наблюдение</h3>', '<h3 lang="en">Extend observation</h3>')
u("demo_page", "k110",
  '<p lang="ru">→ расширяем набор (темп <50/нед 2 недели подряд — сузить вопрос проверки), решение '
  'откладывается, дата пересмотра фиксируется.</p>',
  '<p lang="en">→ extend intake (pace <50/week for 2 straight weeks — narrow the question), the '
  'decision is postponed, a review date is fixed.</p>')
u("demo_page", "k112",
  '<b lang="ru">эффект ≈0 · ложные >20% · повторные списания ≥1</b>',
  '<b lang="en">effect ≈0 · false alerts >20% · repeat charges ≥1</b>')
u("demo_page", "k113",
  '<p lang="ru">→ предложение не расширяется; разбор с заказчиком системы расчётов [S001].</p>',
  '<p lang="en">→ the service is not expanded; a review with the billing system\'s owner [S001].</p>')
u("demo_page", "k114",
  '<b lang="ru">600 групп</b>', '<b lang="en">600 groups</b>')
u("demo_page", "k115",
  '<span lang="ru">A/B-пилот: 6 недель набора + 14 дней наблюдения, ITT</span>',
  '<span lang="en">A/B pilot: 6 weeks of intake + 14 days of observation, ITT</span>')
u("demo_page", "k116",
  '<span lang="ru">порог расширения: доля ограничений из-за исчерпания 12% → 9% [C013]</span>',
  '<span lang="en">expansion threshold: exhaustion-driven restrictions 12% → 9% [C013]</span>')
u("demo_page", "k117",
  '<span lang="ru">consent rate включённых групп — условие масштабирования [C024]</span>',
  '<span lang="en">the consent rate of enrolled groups — the scaling condition [C024]</span>')
u("demo_page", "k118",
  '<span lang="ru">решение утверждено 2026-11-19 · пересмотр D001</span>',
  '<span lang="en">decision approved 2026-11-19 · D001 review</span>')
u("demo_page", "k119",
  '<div class="note rv" lang="ru">Контр-метрики: отключения опции >10% за 4 недели; ложные '
  'предупреждения >20% сработавших — стоп расширения; повторные списания ≥1 — стоп спорных '
  'операций; consent rate <50% за первые 4 недели — доработка приглашения; нагрузка на поддержку '
  'растёт — пересмотр текстов [C019,C022,C024].</div>',
  '<div class="note rv" lang="en">Counter-metrics: opt-outs >10% in 4 weeks; false alerts >20% of '
  'triggers — stop expansion; repeat charges ≥1 — stop disputed operations; consent rate <50% in '
  'the first 4 weeks — rework the invitation; support load rising — rework the copy '
  '[C019,C022,C024].</div>')
u("demo_page", "k127",
  '<b lang="ru">эффект в диапазоне −1…−3 п.п.</b>',
  '<b lang="en">the effect lands in −1…−3 pp</b>')

# --- demo_page: артефакты ---------------------------------------------------
u("demo_page", "k121",
  f'<p class="lead rv d1" lang="ru">Всё лежит в открытом репозитории: <code lang="ru">projects/{PROJ}/outputs/</code>. '
  'Главный документ — <b>BRIEF_RESPONSE.md</b>: ответ на бриф одним документом из пяти частей, '
  'как требует заказчик; DEMO_README.md — чтение пакета за 60 секунд.</p>',
  f'<p class="lead rv d1" lang="en">Everything lives in the open repository: <code lang="en">projects/{PROJ}/outputs/</code>. '
  'The key document is <b>BRIEF_RESPONSE.md</b> — the answer to the brief as a single five-part '
  'document, as the client requires; DEMO_README.md reads the package in 60 seconds.</p>')
u("demo_page", "k103",
  '<span lang="ru">SIX_PAGER.md — черновик от генератора</span>',
  '<span lang="en">SIX_PAGER.md — the generator\'s draft</span>')

# --- ui ---------------------------------------------------------------------
u("ui", "aria_econ",
  "Сценарии экономики: вклад в прибыль планового года",
  "Economics scenarios: planned-year profit contribution")

# --- help_page k083 / materials k028 k037: Excel и рынок старого демо --------
u("help_page", "k083",
  '<p lang="ru"><b>Что смотреть (по порядку):</b> <code>00_brief.md</code> → '
  '<code>01_research_plan.md</code> → <code>02_situation.md</code> → <code>03_options.md</code> '
  '({{OPT_COUNT}} вариантов + {{RT_HITS}} ударов red team) → <code>04/05</code> (стратегии) → '
  '<code>06_validation_plan.md</code> (пороги пилота, ~8–10 недель) → <code>BRIEF_RESPONSE.md</code> '
  '(ответ на бриф из 5 частей), <code>REPORT.md</code> и <b>SIX_PAGER / SIX_PAGER_EN</b> в '
  '.md / .docx; Excel — <code>outputs/attachments/</code>; вайрфрейм кабинета — '
  '<code>sources/raw/</code>; журнал шагов — <code>log.jsonl</code>.</p>',
  '<p lang="en"><b>What to look at (in order):</b> 00_brief → 01_research_plan → 02_situation → '
  '03_options ({{OPT_COUNT}} options + {{RT_HITS}} red-team hits) → 04/05 (strategies) → '
  '06_validation_plan (pilot thresholds, ~8–10 weeks) → BRIEF_RESPONSE.md (the 5-part answer to '
  'the brief), REPORT.md and SIX_PAGER / SIX_PAGER_EN in .md/.docx; Excel in outputs/attachments/; '
  'the dashboard wireframe in sources/raw/; the step log is log.jsonl.</p>')
u("materials_page", "k028",
  '<p lang="ru">Четыре книги на формулах: unit-economics (500 ₽ × 12 000 мес = +6 млн ₽), growth '
  '(группы 6 500 → 12 000), cohort (пилот 600 групп), market (300 тыс. домохозяйств → SOM 11,5%). '
  'Входные значения можно менять — книги пересчитаются.</p>',
  '<p lang="en">Four formula-based workbooks: unit-economics (₽500 × 12,000 mo = +₽6M), growth '
  '(groups 6,500 → 12,000), cohort (the 600-group pilot), market (300K households → SOM 11.5%). '
  'Change the inputs and the books recalculate.</p>')
u("materials_page", "k037",
  '<p lang="ru">PAM→TAM→SAM→SOM: 300 тыс. домохозяйств, оператору доступны 100 тыс. [C004]; SOM '
  'основного хода — 11 500 подключённых групп (11,5% базы), ориентир 3-го года ≥25% [C004].</p>',
  '<p lang="en">PAM→TAM→SAM→SOM: 300K households, 100K available to the operator [C004]; the base '
  'case SOM is 11,500 connected groups (11.5% of the base), the year-3 benchmark ≥25% [C004].</p>')

# --- help_page --------------------------------------------------------------
u("help_page", "k016",
  '<a href="#h-demo" lang="ru">Демо «Связь для близких» ★</a>',
  '<a href="#h-demo" lang="en">Connection for Loved Ones demo ★</a>')
u("help_page", "k081",
  '<h3 lang="ru">Демо «Связь для близких»: как это сделано и что посмотреть</h3>',
  '<h3 lang="en">Connection for Loved Ones demo: how it was made and what to look at</h3>')
u("help_page", "k082",
  '<p lang="ru">Полный сквозной прогон агента на брифе заказчика — <b>«Связь для близких и '
  'собственных устройств»</b> (услуги вымышленного мобильного оператора): 12 шагов, '
  '{{OPT_COUNT}} вариантов, {{RT_HITS}} ударов red team (15 возражений + 5 скрытых допущений), '
  'обе стратегии, six-pager в 4 форматах (RU/EN × MD/DOCX), {{XLSX_COUNT}} книги Excel, решение '
  'D001 — пилот 600 групп, <b>check --strict: 0 ошибок, ревью 98/100</b>. Проект: '
  f'<code>projects/{PROJ}/</code>; интерактивный разбор: <a href="demo.html">demo.html</a>.</p>',
  '<p lang="en">A complete end-to-end run on a client brief — <b>Connection for Loved Ones and '
  'personal devices</b> (services of a fictional mobile operator): 12 steps, {{OPT_COUNT}} options, '
  '{{RT_HITS}} red-team hits (15 objections + 5 hidden assumptions), both strategies, a six-pager '
  'in 4 formats (RU/EN × MD/DOCX), {{XLSX_COUNT}} Excel workbooks, decision D001 — a 600-group '
  'pilot, <b>check --strict: 0 errors, a 98/100 review</b>. Project: '
  f'<code>projects/{PROJ}/</code>; interactive walkthrough: <a href="demo.html">demo.html</a>.</p>')
u("help_page", "k085",
  '<p lang="ru"><b>Сверка с заданием:</b> обязательный минимум (задача · материалы · исследование · '
  '≥3 варианта с возражениями · обе стратегии · план проверки · workflow · порядок в знаниях · '
  'продолжение после перерыва · прозрачность) и дополнительный уровень (синтетика · медиа · данные · '
  'решения · пересмотр · маршрутизация · субагенты/хуки · MCP/CLI · устойчивость · переносимость · '
  'сравнение с чатом) — закрыты; полная таблица соответствия — в '
  '<a href="https://github.com/Fighter90/product-factory-strategist/blob/main/README.md">README</a> '
  'и <a href="https://github.com/Fighter90/product-factory-strategist/blob/main/docs/COMPLIANCE.md">'
  'docs/COMPLIANCE.md</a>.</p>',
  '<p lang="en"><b>Compliance check:</b> the mandatory minimum (task · materials · research · ≥3 '
  'options with objections · both strategies · validation plan · workflow · knowledge order · '
  'continuation after a break · transparency) and the extra level (synthetic data · media · data · '
  'decisions · review · routing · subagents/hooks · MCP/CLI · robustness · portability · comparison '
  'with a chat) — all closed; the full mapping is in '
  '<a href="https://github.com/Fighter90/product-factory-strategist/blob/main/README.md">README</a> '
  'and <a href="https://github.com/Fighter90/product-factory-strategist/blob/main/docs/COMPLIANCE.md">'
  'docs/COMPLIANCE.md</a>.</p>')
u("help_page", "k102",
  '<p lang="ru"><b>Агент:</b> показывает сравнение вариантов (критерии, экономика, риски) и одну '
  'рекомендацию, затем спрашивает — <code>pfs ask "Какой вариант принимаем?" --options "A,B,C"</code>. '
  '<b>Человек:</b> <span class="pause">выбирает вариант</span> — ответ сохраняется в state.json и '
  'становится основанием стратегий и решения D### (как в демо «Связь для близких»: выбор B '
  '«Предупреждение до перебоя»). Никакие стратегии не пишутся до выбора.</p>',
  '<p lang="en"><b>Agent:</b> shows the option comparison (criteria, economics, risks) and a single '
  'recommendation, then asks — <code>pfs ask "Which option do we take?" --options "A,B,C"</code>. '
  '<b>Human:</b> <span class="pause">picks the option</span> — the answer is stored in state.json and '
  'grounds the strategies and the D### decision (as in the Connection for Loved Ones demo: option B '
  '"Warn before the outage" chosen). No strategies are written before the choice.</p>')

# --- materials_page ---------------------------------------------------------
u("materials_page", "title",
  f"Материалы демо {DEMO_NAME_RU} — Стратег Фабрики продуктов",
  f"{DEMO_NAME_EN} demo materials — Product Factory Strategist")
u("materials_page", "og_title",
  f"Материалы демо {DEMO_NAME_RU} — Стратег Фабрики продуктов",
  f"{DEMO_NAME_EN} demo materials — Product Factory Strategist")
u("materials_page", "description",
  f"Материалы демонстрационного проекта {DEMO_NAME_RU} (бриф заказчика: услуги мобильного "
  "оператора): six-pager комитета RU/EN (MD · DOCX), четыре Excel-модели, видео-обзор прогона, "
  "доказательная база — источники S001–S004, утверждения C001–C027, решение D001 с пилотом "
  "600 групп.",
  f"Materials of the {DEMO_NAME_EN} demo project (a client brief: mobile operator services): "
  "the committee six-pager in RU/EN (MD · DOCX), four Excel models, a run overview video, and the "
  "evidence base — sources S001–S004, claims C001–C027, decision D001 with a 600-group pilot.")
u("materials_page", "k006",
  f'<h1 lang="ru">Материалы демо <span class="grad">{DEMO_NAME_RU}</span></h1>',
  f'<h1 lang="en"><span class="grad">{DEMO_NAME_EN}</span> demo materials</h1>')
u("materials_page", "k008",
  '<span lang="ru">файлов six-pager (RU · EN × MD/DOCX)</span>',
  '<span lang="en">six-pager files (RU · EN × MD/DOCX)</span>')
u("materials_page", "k010",
  '<span lang="ru">видео и схем демо</span>',
  '<span lang="en">demo videos and diagrams</span>')
u("materials_page", "k040",
  '<h2 class="rv" lang="ru">Видео-обзор и схемы</h2>',
  '<h2 class="rv" lang="en">Overview video and diagrams</h2>')
u("materials_page", "k041",
  '<p class="lead rv d1" lang="ru">Видео-обзор прогона на двух языках, вайрфрейм кабинета семьи '
  '(S004) и схема архитектуры агента.</p>',
  '<p class="lead rv d1" lang="en">The run overview video in two languages, the family dashboard '
  'wireframe (S004), and the agent architecture diagram.</p>')
u("materials_page", "k042",
  '<span lang="ru">svyaz-overview — видео · RU · 4:20</span>',
  '<span lang="en">svyaz-overview — video · RU · 4:20</span>')
u("materials_page", "k043",
  '<div class="shot-cap" lang="ru">Сквозной прогон за 4 минуты: задача, реестр утверждений, '
  'red team, решение D001 с пилотом 600 групп.</div>',
  '<div class="shot-cap" lang="en">The run in 4 minutes: the task, the claim registry, the red team, '
  'decision D001 with the 600-group pilot.</div>')
u("materials_page", "k044",
  '<span lang="ru">svyaz-overview — видео · EN · 4:14</span>',
  '<span lang="en">svyaz-overview — video · EN · 4:14</span>')
u("materials_page", "k045",
  '<div class="shot-cap" lang="ru">Тот же прогон на английском: six-pager и реестры существуют '
  'в двух языках.</div>',
  '<div class="shot-cap" lang="en">The same run in English: the six-pager and registries exist in '
  'two languages.</div>')
u("materials_page", "k046",
  '<span lang="ru">Вайрфрейм: кабинет семьи · S004</span>',
  '<span lang="en">Wireframe: family dashboard · S004</span>')
u("materials_page", "k047",
  '<div class="shot-cap" lang="ru">Макет кабинета с предупреждениями: низкий остаток участника и '
  'предстоящий платёж — материал UX-ревью 06_ux_review_S004.md.</div>',
  '<div class="shot-cap" lang="en">The dashboard mock with warnings: a participant\'s low balance and '
  'an upcoming payment — the material of 06_ux_review_S004.md.</div>')
u("materials_page", "k048",
  '<span lang="ru">Архитектура агента</span>',
  '<span lang="en">Agent architecture</span>')
u("materials_page", "k049",
  '<div class="shot-cap" lang="ru">Схема архитектуры: ядро pfs, реестры источников/утверждений/'
  'решений, знания и субагенты.</div>',
  '<div class="shot-cap" lang="en">The architecture diagram: the pfs core, source/claim/decision '
  'registries, knowledge and subagents.</div>')
u("materials_page", "k050",
  '<span lang="ru">Реестр утверждений</span>',
  '<span lang="en">Claim registry</span>')
u("materials_page", "k051",
  '<div class="shot-cap" lang="ru">26 утверждений: факты — с источником, синтетика — только '
  'гипотезы, сила A–D.</div>',
  '<div class="shot-cap" lang="en">26 claims: facts carry sources, synthetic data yields hypotheses '
  'only, A–D strength.</div>')
u("materials_page", "k052",
  '<span lang="ru">Сценарии экономики</span>',
  '<span lang="en">Economics scenarios</span>')
u("materials_page", "k053",
  '<div class="shot-cap" lang="ru">5 сценариев вклада в прибыль года: от +6,75 до −3,5 млн ₽ — '
  'воспроизводимы в economics.py.</div>',
  '<div class="shot-cap" lang="en">5 scenarios of yearly profit contribution: +6.75M to −3.5M ₽ — '
  'reproducible in economics.py.</div>')
u("materials_page", "k054",
  '<div class="note rv" lang="ru">Видео и схемы лежат в репозитории проекта: '
  f'<a href="{GH}/tree/main/projects/{P}" target="_blank" rel="noopener">projects/{PROJ}</a> '
  '(assets — постеры, video — исходники монтажа).</div>',
  '<div class="note rv" lang="en">Videos and diagrams live in the project repository: '
  f'<a href="{GH}/tree/main/projects/{P}" target="_blank" rel="noopener">projects/{PROJ}</a> '
  '(assets — posters, video — editing sources).</div>')
u("materials_page", "k060",
  '<h3 lang="ru">sources/ — бриф, синтетика и вайрфрейм</h3>',
  '<h3 lang="en">sources/ — the brief, synthetic data and the wireframe</h3>')
u("materials_page", "k061",
  '<p lang="ru">{{SOURCES_COUNT}} источника с сохранённым текстом: бриф заказчика (все числа '
  'учебные), 2 ИИ-респондента (семейный организатор и владелец номеров — только гипотезы), '
  'вайрфрейм кабинета семьи.</p>',
  '<p lang="en">{{SOURCES_COUNT}} sources with preserved text: the client brief (all numbers are '
  'teaching numbers), 2 AI respondents (a family organizer and a multi-number owner — hypotheses '
  'only), the family dashboard wireframe.</p>')
u("materials_page", "k064",
  '<p lang="ru">2 ИИ-респондента — семейный организатор и владелец нескольких номеров (S002, '
  'S003). Помечено origin=synthetic: такие ответы порождают только гипотезы [C014,C019,C020] и '
  'не доказывают спрос. Реальные интервью — работа человека.</p>',
  '<p lang="en">2 AI respondents — a family organizer and a multi-number owner (S002, S003). '
  'Flagged origin=synthetic: such answers yield hypotheses only [C014,C019,C020] and prove no '
  'demand. Real interviews are human work.</p>')
u("materials_page", "k066",
  '<p class="lead rv d1" lang="ru">Демо-проект — учебный бриф «Связь для близких и собственных '
  'устройств»: услуги вымышленного мобильного оператора для семейных групп и владельцев '
  'нескольких номеров.</p>',
  '<p class="lead rv d1" lang="en">The demo project is the teaching brief "Connection for Loved '
  'Ones and personal devices": services of a fictional mobile operator for family groups and '
  'owners of several numbers.</p>')
u("materials_page", "k067",
  '<h3 lang="ru">Видео-обзор прогона</h3>',
  '<h3 lang="en">The run overview video</h3>')
u("materials_page", "k068",
  '<p lang="ru">Обзор на русском (4:20) и английском (4:14): задача, реестр утверждений, red team, '
  'решение с пилотом 600 групп. Видео лежат в репозитории и смотрятся прямо со страницы.</p>',
  '<p lang="en">An overview in Russian (4:20) and English (4:14): the task, the claim registry, the '
  'red team, the decision with the 600-group pilot. The videos live in the repository and play '
  'right on the page.</p>')
u("materials_page", "k069",
  '<span lang="ru">svyaz-overview-ru.mp4 · svyaz-overview-en.mp4 · постеры PNG</span>',
  '<span lang="en">svyaz-overview-ru.mp4 · svyaz-overview-en.mp4 · PNG posters</span>')
u("materials_page", "k070",
  '<span lang="ru">Открыть папку проекта на GitHub</span>',
  '<span lang="en">Open the project folder on GitHub</span>')
u("materials_page", "k071",
  f'<h3 lang="ru">projects/{PROJ} — полный пакет</h3>',
  f'<h3 lang="en">projects/{PROJ} — the full package</h3>')
u("materials_page", "k072",
  '<p lang="ru">12 шагов прогона: бриф, план исследования, ситуация, 5 вариантов с red team, '
  'стратегии, план проверки, ревью 98/100, решение D001. Главный документ — BRIEF_RESPONSE.md '
  '(ответ на бриф из 5 частей).</p>',
  '<p lang="en">The 12-step run: brief, research plan, situation, 5 options with a red team, '
  'strategies, validation plan, a 98/100 review, decision D001. The key document is '
  'BRIEF_RESPONSE.md (a 5-part answer to the brief).</p>')
u("materials_page", "k073",
  '<span lang="ru">12 шагов · 26 утверждений · решение D001</span>',
  '<span lang="en">12 steps · 26 claims · decision D001</span>')
u("materials_page", "k074",
  '<span lang="ru">Открыть на GitHub</span>',
  '<span lang="en">Open on GitHub</span>')

# ------------------------------------------------------------- template fixes

def gh_blob(path: str) -> str:
    return f"{GH_BLOB}/projects/{P}/{path}"

def gh_raw(path: str) -> str:
    return f"https://raw.githubusercontent.com/Fighter90/product-factory-strategist/main/projects/{P}/{path}"

VIDEO_CARD_RU = (
    '<div class="shot-card">\n'
    '      <div class="shot-bar"><i></i><i></i><i></i><span>{{demo.ru.k026}}{{demo.en.k026}}</span></div>\n'
    '      <video controls preload="metadata" poster="assets/svyaz-poster-ru.png" src="assets/svyaz-overview-ru.mp4" style="width:100%;display:block;background:#000"></video>\n'
    '      {{demo.ru.k027}}\n'
    '      {{demo.en.k027}}\n'
    '    </div>'
)
VIDEO_CARD_EN = (
    '<div class="shot-card">\n'
    '      <div class="shot-bar"><i></i><i></i><i></i><span>{{demo.ru.k028}}{{demo.en.k028}}</span></div>\n'
    '      <video controls preload="metadata" poster="assets/svyaz-poster-en.png" src="assets/svyaz-overview-en.mp4" style="width:100%;display:block;background:#000"></video>\n'
    '      {{demo.ru.k029}}\n'
    '      {{demo.en.k029}}\n'
    '    </div>'
)
FIG_CARD_STATUS = (
    '<div class="shot-card">\n'
    '      <div class="shot-bar"><i></i><i></i><i></i><span>{{demo.ru.k030}}{{demo.en.k030}}</span></div>\n'
    '      <div class="shot-crop"><img src="assets/svyaz-screenshot-status.png?v=10" alt="{{demo.ru.k130}}{{demo.en.k130}}"></div>\n'
    '      {{demo.ru.k031}}\n'
    '      {{demo.en.k031}}\n'
    '    </div>'
)
FIG_CARD_ARCH = (
    '<div class="shot-card">\n'
    '      <div class="shot-bar"><i></i><i></i><i></i><span>{{demo.ru.k032}}{{demo.en.k032}}</span></div>\n'
    '      <div class="shot-crop"><img src="assets/svyaz-architecture.png?v=10" alt="{{demo.ru.k131}}{{demo.en.k131}}"></div>\n'
    '      {{demo.ru.k033}}\n'
    '      {{demo.en.k033}}\n'
    '    </div>'
)

ECON_SVG_NEW = '''<div class="wf-wrap rv d2"><svg class="wf-svg" viewBox="0 0 860 300" role="img" aria-label="{{ui.aria_econ}}">
    <g font-size="12.5">
      <line x1="30" y1="150" x2="830" y2="150" stroke="rgba(214,210,204,.25)" stroke-dasharray="4 4"/>
      <g class="bar-g"><rect x="60"  y="20" width="110" height="130" rx="8" fill="#EE8A3C" opacity=".95"/><text x="115" y="14" text-anchor="middle" fill="#F1EEE9" font-weight="700">+6,75</text></g>
      <g class="bar-g"><rect x="215" y="65" width="110" height="85"  rx="8" fill="#EE8A3C" opacity=".6"/><text x="270" y="59" text-anchor="middle" fill="#F1EEE9" font-weight="700">+4,5</text></g>
      <g class="bar-g"><rect x="370" y="122" width="110" height="28" rx="8" fill="#EE8A3C" opacity=".35"/><text x="425" y="116" text-anchor="middle" fill="#F1EEE9" font-weight="700">+1,5</text></g>
      <g class="bar-g"><rect x="525" y="150" width="110" height="28" rx="8" fill="#E8B34B" opacity=".7"/><text x="580" y="192" text-anchor="middle" fill="#E8B34B" font-weight="700">−1,5</text></g>
      <g class="bar-g"><rect x="680" y="150" width="110" height="66" rx="8" fill="#f472b6" opacity=".8"/><text x="735" y="230" text-anchor="middle" fill="#f472b6" font-weight="700">−3,5</text></g>
      <text x="115" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">основной ход</tspan><tspan lang="en">base case</tspan></text>
      <text x="270" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">сдержанный</tspan><tspan lang="en">conservative</tspan></text>
      <text x="425" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">неблагоприятный</tspan><tspan lang="en">downside</tspan></text>
      <text x="580" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">«ноль»</tspan><tspan lang="en">"zero"</tspan></text>
      <text x="735" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">«минус» с оттоком</tspan><tspan lang="en">"minus" with churn</tspan></text>
    </g>
    <g font-size="12.5">
      <rect x="30" y="268" width="180" height="24" rx="7" fill="rgba(238,138,60,.1)" stroke="rgba(238,138,60,.35)"/><text x="120" y="284" text-anchor="middle" fill="#EE8A3C"><tspan lang="ru">цель ≥ 285 млн ₽</tspan><tspan lang="en">target ≥ 285M ₽</tspan></text>
      <rect x="226" y="268" width="200" height="24" rx="7" fill="rgba(238,138,60,.1)" stroke="rgba(238,138,60,.35)"/><text x="326" y="284" text-anchor="middle" fill="#EE8A3C"><tspan lang="ru">порог расширения −3 п.п.</tspan><tspan lang="en">scale-up threshold −3 pp</tspan></text>
      <rect x="442" y="268" width="240" height="24" rx="7" fill="rgba(232,179,75,.1)" stroke="rgba(232,179,75,.35)"/><text x="562" y="284" text-anchor="middle" fill="#E8B34B"><tspan lang="ru">12 000 мес × 500 ₽ = +6 млн</tspan><tspan lang="en">12,000 mo × ₽500 = +6M</tspan></text>
      <rect x="698" y="268" width="132" height="24" rx="7" fill="rgba(154,167,189,.08)" stroke="rgba(154,167,189,.3)"/><text x="764" y="284" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">модель [C021]</tspan><tspan lang="en">model [C021]</tspan></text>
    </g>
  </svg></div>'''

SIXPAGER_RU_NEW = '''<div class="colcard" lang="ru">
      <h3>{{demo.ru.k102}}{{demo.en.k102}}</h3>
      <div class="faq6">
        <div class="f6"><b>FAQ-1</b><span><b>Текущее состояние:</b> цель ≥285 млн ₽ при «без изменений» 279; разрыв 6 млн = 12 000 мес × 500 ₽ [C003]; база 6 500 групп, активных 4 000 [C001] · <i>S001</i></span></div>
        <div class="f6"><b>FAQ-2</b><span><b>Аудитория:</b> семейные организаторы (доступны 100 тыс.) и владельцы номеров (40 тыс.) [C004]; барьер — «о перебое узнаёт из просьбы о помощи» [C005,C006]</span></div>
        <div class="f6"><b>FAQ-3</b><span><b>Инициативы:</b> 5 вариантов A–E по одной оси; рекомендация B «Предупреждение до перебоя»: +6,75 млн → 285,8 млн ₽ [C003,C021]; D — вторая очередь Q3–Q4 [C016]</span></div>
        <div class="f6"><b>FAQ-4</b><span><b>Тактики:</b> предупреждение о низком остатке (~20% на 3 дня), напоминание плательщику, 3 гранулярных согласия [C009,C022]; precision ≥80%, ≤2 алерта/нед [C026]</span></div>
        <div class="f6"><b>FAQ-5</b><span><b>План:</b> Q1 — запуск пилота 600 групп (решение по порогам), Q2 — расширение/изменение/наблюдение; ориентир 3-го года ≥25% базы [C004]</span></div>
        <div class="f6"><b>FAQ-6</b><span><b>KPI:</b> бизнес — валовая прибыль ≥285 млн ₽, доп. месяцы ≥15 000 [C003]; продукт — ограничения 12%→9% [C013], активные 8 000 [C002]</span></div>
      </div>
    </div>'''

SIXPAGER_EN_NEW = '''<div class="colcard" lang="en">
      <h3>Six-pager — English</h3>
      <div class="faq6">
        <div class="f6"><b>FAQ-1</b><span><b>Current state:</b> the goal is ≥285M ₽ vs "no change" 279; the gap is 6M = 12,000 mo × ₽500 [C003]; the base is 6,500 groups, 4,000 active [C001] · <i>S001</i></span></div>
        <div class="f6"><b>FAQ-2</b><span><b>Audience:</b> family organizers (100K available) and number owners (40K) [C004]; the barrier — "they learn of outages from a loved one\'s request" [C005,C006]</span></div>
        <div class="f6"><b>FAQ-3</b><span><b>Initiatives:</b> 5 options A–E on one axis; the recommendation B "Warn before the outage": +6.75M → 285.8M ₽ [C003,C021]; D — the second wave Q3–Q4 [C016]</span></div>
        <div class="f6"><b>FAQ-4</b><span><b>Tactics:</b> a low-balance warning (~20% for 3 days), a payer reminder, 3 granular consents [C009,C022]; precision ≥80%, ≤2 alerts/week [C026]</span></div>
        <div class="f6"><b>FAQ-5</b><span><b>Plan:</b> Q1 — start the 600-group pilot (decision by thresholds), Q2 — expand/change/observe; the year-3 benchmark ≥25% of the base [C004]</span></div>
        <div class="f6"><b>FAQ-6</b><span><b>KPIs:</b> business — gross profit ≥285M ₽, extra months ≥15,000 [C003]; product — restrictions 12%→9% [C013], 8,000 active groups [C002]</span></div>
      </div>
    </div>'''

def demo_template_fixes() -> list:
    f = "site_src/demo.html"
    sixpager_links_new = (
        f'<a href="{gh_raw("outputs/SIX_PAGER.docx")}" target="_blank" rel="noopener" class="pbtn">SIX_PAGER.docx</a>\n'
        f'    <a href="{gh_blob("outputs/SIX_PAGER_EN.docx")}" target="_blank" rel="noopener" class="pbtn ghost2">SIX_PAGER_EN.docx</a>\n'
        f'    <a href="{gh_blob("outputs/SIX_PAGER.md")}" target="_blank" rel="noopener" class="pbtn ghost2">{{{{demo.ru.k103}}}}{{{{demo.en.k103}}}}</a>\n'
        '    <a href="materials.html?v=10" class="pbtn ghost2">{{demo.ru.k104}}{{demo.en.k104}}</a>'
    )
    artifacts_links_new = (
        f'<a class="btn ghost" href="{gh_blob("outputs/BRIEF_RESPONSE.md")}" target="_blank" rel="noopener">BRIEF_RESPONSE.md</a>\n'
        f'    <a class="btn ghost" href="{gh_blob("outputs/SIX_PAGER.docx")}" target="_blank" rel="noopener">SIX_PAGER.docx</a>\n'
        f'    <a class="btn ghost" href="{gh_blob("outputs/SIX_PAGER_EN.docx")}" target="_blank" rel="noopener">SIX_PAGER_EN.docx</a>\n'
        f'    <a class="btn ghost" href="{gh_blob("outputs/REPORT.md")}" target="_blank" rel="noopener">REPORT.md</a>\n'
        f'    <a class="btn ghost" href="{gh_blob("outputs/03_options.md")}" target="_blank" rel="noopener">03_options.md</a>'
    )
    return [
        (f, '<span class="chip"><b>100/100</b> check --strict</span>',
            '<span class="chip"><b>98/100</b> review · check --strict: 0</span>'),
        (f, '<div><div class="cv-name">CV<em>Start</em></div><div class="cv-tag">open-source AI resume builder · cvstart.org</div></div>',
            '<div><div class="cv-name">{{demo.ru.k134}}{{demo.en.k134}}</div><div class="cv-tag">{{demo.ru.k135}}{{demo.en.k135}}</div></div>'),
        (f, '<p><a href="https://cvstart.org/" target="_blank" rel="noopener">cvstart.org</a> · <a href="https://github.com/Fighter90/career-ops-ui" target="_blank" rel="noopener">github.com/Fighter90/career-ops-ui</a></p>',
            f'<p><a href="{GH}/tree/main/projects/{P}" target="_blank" rel="noopener">projects/{PROJ}</a> · <a href="{GH}" target="_blank" rel="noopener">github.com/Fighter90/product-factory-strategist</a></p>'),
        (f, '<a class="pill pill-a pill-sm" href="https://github.com/Fighter90/product-factory-strategist-agent" data-goal="github_click">',
            f'<a class="pill pill-a pill-sm" href="{GH}" data-goal="github_click">'),
        # PRO-133: секция shots удалена из шаблона demo (пары замен не нужны)
        # PRO-133: старая пара замен shots-блока удалена (секция удалена из шаблона)
        (f, '<div class="fact rv">{{demo.ru.k044}}{{demo.en.k044}}{{demo.ru.k045}}{{demo.en.k045}}<i>S006 · Wiseguy Reports → C005</i></div>',
            '<div class="fact rv">{{demo.ru.k044}}{{demo.en.k044}}{{demo.ru.k045}}{{demo.en.k045}}<i>S001 · бриф → C002</i></div>'),
        (f, '<div class="fact rv d2">{{demo.ru.k049}}{{demo.en.k049}}{{demo.ru.k050}}{{demo.en.k050}}<i>S004 · Rezi/Kickresume pricing → C006</i></div>',
            '<div class="fact rv d2">{{demo.ru.k049}}{{demo.en.k049}}{{demo.ru.k050}}{{demo.en.k050}}<i>{{demo.ru.k133}}{{demo.en.k133}}</i></div>'),
        (f, '<div class="fact rv d3"><b>98%</b>{{demo.ru.k051}}{{demo.en.k051}}<i>S007 · SkyQuest/Jobscan → C008</i></div>',
            '<div class="fact rv d3"><b>100 тыс.</b>{{demo.ru.k051}}{{demo.en.k051}}<i>S001 · бриф → C004</i></div>'),
        (f, '<div class="fact rv"><b>31–74%</b>{{demo.ru.k052}}{{demo.en.k052}}<i>S005 · Kickresume Press → C009</i></div>',
            '<div class="fact rv"><b>+6,75 млн ₽</b>{{demo.ru.k052}}{{demo.en.k052}}<i>S001 · economics.py → C021</i></div>'),
        (f, '<div class="fact rv d1">{{demo.ru.k053}}{{demo.en.k053}}{{demo.ru.k054}}{{demo.en.k054}}<i>S007 · SkyQuest → C011</i></div>',
            '<div class="fact rv d1">{{demo.ru.k053}}{{demo.en.k053}}{{demo.ru.k054}}{{demo.en.k054}}<i>S001 · бриф → C002/C008</i></div>'),
        # таблица вариантов: статические ячейки $
        (f, '''    <tr>
      {{demo.ru.k062}}{{demo.en.k062}}
      {{demo.ru.k063}}{{demo.en.k063}}
      <td>$0</td>
      {{demo.ru.k064}}{{demo.en.k064}}
    </tr>''',
            '''    <tr>
      {{demo.ru.k062}}{{demo.en.k062}}
      {{demo.ru.k063}}{{demo.en.k063}}
      <td>0 → 279 млн ₽</td>
      {{demo.ru.k064}}{{demo.en.k064}}
    </tr>'''),
        (f, '''    <tr>
      {{demo.ru.k077}}{{demo.en.k077}}
      {{demo.ru.k078}}{{demo.en.k078}}
      <td>$0</td>
      {{demo.ru.k079}}{{demo.en.k079}}
    </tr>''',
            '''    <tr>
      {{demo.ru.k077}}{{demo.en.k077}}
      {{demo.ru.k078}}{{demo.en.k078}}
      <td>0 → 279 млн ₽</td>
      {{demo.ru.k079}}{{demo.en.k079}}
    </tr>'''),
        # экономика: SVG → сценарии
        (f, '''  <div class="wf-wrap rv d2"><svg class="wf-svg" viewBox="0 0 860 300" role="img" aria-label="{{ui.aria_econ}}">
    <defs><linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2dd4bf"/><stop offset="1" stop-color="#818cf8"/></lineargradient></defs>
    <g font-size="13">
      <g class="bar-g"><rect x="40"  y="170" width="120" height="60"  rx="8" fill="url(#wg)" opacity=".9"/><text x="100" y="162" text-anchor="middle" fill="#eef2ff" font-weight="700">{{ARPU}}</text></g>
      <g class="bar-g"><rect x="230" y="200" width="120" height="30" rx="8" fill="#f472b6" opacity=".75"/><text x="290" y="192" text-anchor="middle" fill="#f472b6" font-weight="700">{{VC_NEG}}</text></g>
      <g class="bar-g"><rect x="420" y="170" width="120" height="60" rx="8" fill="url(#wg)" opacity=".9"/><text x="480" y="162" text-anchor="middle" fill="#eef2ff" font-weight="700">{{CM}}</text></g>
      <g class="bar-g"><rect x="610" y="80" width="120" height="150" rx="8" fill="#818cf8" opacity=".6"/><text x="670" y="72" text-anchor="middle" fill="#eef2ff" font-weight="700">{{LTV}}</text></g>
      <text x="100" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">ARPU платящего / мес</tspan><tspan lang="en">payer ARPU / mo</tspan></text>
      <text x="290" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">инференс + инфра ~{{VC_PCT}}%</tspan><tspan lang="en">inference + infra ~{{VC_PCT}}%</tspan></text>
      <text x="480" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">вклад (CM) платящего</tspan><tspan lang="en">payer contribution margin (CM)</tspan></text>
      <text x="670" y="252" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">LTV платящего (модель)</tspan><tspan lang="en">payer LTV (model)</tspan></text>
    </g>
    <g font-size="12.5">
      <rect x="40" y="270" width="160" height="24" rx="7" fill="rgba(238,138,60,.1)" stroke="rgba(238,138,60,.35)"/><text x="120" y="286" text-anchor="middle" fill="#2dd4bf"><tspan lang="ru">LTV / CAC ≈ {{LTV_CAC}}</tspan><tspan lang="en">LTV / CAC ≈ {{LTV_CAC}}</tspan></text>
      <rect x="212" y="270" width="185" height="24" rx="7" fill="rgba(232,179,75,.1)" stroke="rgba(232,179,75,.35)"/><text x="304" y="286" text-anchor="middle" fill="#818cf8"><tspan lang="ru">окупаемость CAC ≈ {{PAYBACK}} мес</tspan><tspan lang="en">CAC payback ≈ {{PAYBACK}} mo</tspan></text>
      <rect x="409" y="270" width="200" height="24" rx="7" fill="rgba(238,138,60,.1)" stroke="rgba(238,138,60,.35)"/><text x="509" y="286" text-anchor="middle" fill="#f472b6"><tspan lang="ru">брейк-евен ≈ {{BREAKEVEN}} платящих</tspan><tspan lang="en">break-even ≈ {{BREAKEVEN}} payers</tspan></text>
      <rect x="621" y="270" width="199" height="24" rx="7" fill="rgba(154,167,189,.08)" stroke="rgba(154,167,189,.3)"/><text x="720" y="286" text-anchor="middle" fill="#9aa7bd"><tspan lang="ru">допущения помечены [C016]</tspan><tspan lang="en">assumptions tagged [C016]</tspan></text>
    </g>
  </svg></div>''', ECON_SVG_NEW),
        # six-pager: статические фрагменты RU+EN
        (f, '''    <div class="colcard" lang="ru">
      <h3>{{demo.ru.k102}}{{demo.en.k102}}</h3>
      <div class="faq6">
        <div class="f6"><b>1.1</b><span><b>Обзор рынка:</b> resume builders $1,2–2,4 млрд (диапазон — агрегаторы расходятся ×2, считаем по консервативной границе); AI-сегмент CAGR 13,1%; тренды: ATS-гейт найма, подписочная усталость, GenAI-стандарт · <i>S004–S007</i></span></div>
        <div class="f6"><b>1.2</b><span><b>Конкуренты (таблица):</b> Mass-market SaaS / ATS-specialists / OSS — преимущества, стратегии роста и промо-механики, риски с оценкой Высокий–Средний–Низкий; окно возможностей — 2–3 квартала · <i>C005–C007</i></span></div>
        <div class="f6"><b>2.1–2.2</b><span><b>Персоны и барьеры:</b> таблицы «Кто они / Что используют сегодня / Трудности» по трём сегментам + барьеры по этапам пути (поиск → выбор → резюме → постоплата) и «что сдерживает от старта» · <i>C017/C018 — гипотезы, синтетика</i></span></div>
        <div class="f6"><b>3.1–3.3</b><span><b>Драйверы:</b> «Первый драйвер — честная монетизация» (BYOK-free), «Второй драйвер — путь „вакансия → ATS-резюме“», глобальное покрытие; UE пошагово: CM = 29 × 0,75 = 21,75 → LTV = 271,88 → LTV/CAC = 4,53 → брейк-евен 69 · <i>C016</i></span></div>
        <div class="f6"><b>FAQ-4</b><span><b>Матрица тактик</b> «Инициатива | Фокус | Потребности | Решения»: BYOK-free-тир, страница цены без автопродлений, CV Studio (тюминг + ATS-буллеты), трекер с follow-up, волны локалей, OSS-дистрибуция</span></div>
        <div class="f6"><b>FAQ-5–6</b><span><b>План и KPI:</b> вклад инициатив 50/30/20%; тайминг к январскому пику найма; KPI в двух плоскостях (бизнес: MRR ≥ $1 500, LTV/CAC ≥ 3 · продукт: активация ≥ 50%, churn ≤ 10%); сноски S001–S011 · <i>D001</i></span></div>
      </div>
    </div>''', SIXPAGER_RU_NEW),
        (f, '''    <div class="colcard" lang="en">
      <h3>Six-pager — English</h3>
      <div class="faq6">
        <div class="f6"><b>1.1</b><span><b>Market overview:</b> resume builders $1.2–2.4B (a range — aggregators diverge ×2, we use the conservative floor); AI segment CAGR 13.1%; trends: the ATS gate, subscription fatigue, GenAI as standard · <i>S004–S007</i></span></div>
        <div class="f6"><b>1.2</b><span><b>Competitors (table):</b> Mass-market SaaS / ATS-specialists / OSS — advantages, growth strategies and promo mechanics, risks rated High–Medium–Low; the window — 2–3 quarters · <i>C005–C007</i></span></div>
        <div class="f6"><b>2.1–2.2</b><span><b>Personas and barriers:</b> "Who they are / What they use today / Difficulties" tables across three segments + stage-by-stage barriers (search → selection → resume → post-payment) and "what blocks them from starting" · <i>C017/C018 — hypotheses, synthetic</i></span></div>
        <div class="f6"><b>3.1–3.3</b><span><b>Drivers:</b> "The first driver — honest monetization" (BYOK-free), "The second driver — the vacancy → ATS-ready resume path", global coverage; step-by-step UE: CM = 29 × 0.75 = 21.75 → LTV 271.88 → LTV/CAC 4.53 → break-even 69 · <i>C016</i></span></div>
        <div class="f6"><b>FAQ-4</b><span><b>Tactic matrix</b> "Initiative | Focus | Needs | Solutions": BYOK-free tier, a no-auto-renewal pricing page, CV Studio (JD tuning + ATS bullets), follow-up tracker, locale waves, OSS distribution</span></div>
        <div class="f6"><b>FAQ-5–6</b><span><b>Plan &amp; KPIs:</b> initiative contribution 50/30/20%; timing to the January hiring peak; KPIs in two planes (business: MRR ≥ $1,500, LTV/CAC ≥ 3 · product: activation ≥ 50%, churn ≤ 10%); footnotes S001–S011 · <i>D001</i></span></div>
      </div>
    </div>''', SIXPAGER_EN_NEW),
        # ссылки на six-pager файлы (PDF → DOCX нового демо)
        (f, '''    <a href="https://raw.githubusercontent.com/Fighter90/product-factory-strategist/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_RU.pdf" target="_blank" rel="noopener" class="pbtn">SIX_PAGER_RU.pdf</a>
    <a href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_RU.docx" target="_blank" rel="noopener" class="pbtn ghost2">SIX_PAGER_RU.docx</a>
    <a href="https://raw.githubusercontent.com/Fighter90/product-factory-strategist/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_EN.pdf" target="_blank" rel="noopener" class="pbtn">SIX_PAGER_EN.pdf</a>
    <a href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_EN.docx" target="_blank" rel="noopener" class="pbtn ghost2">SIX_PAGER_EN.docx</a>
    <a href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER.md" target="_blank" rel="noopener" class="pbtn ghost2">{{demo.ru.k103}}{{demo.en.k103}}</a>
    <a href="materials.html?v=9" class="pbtn ghost2">{{demo.ru.k104}}{{demo.en.k104}}</a>''',
        sixpager_links_new),
        # план проверки: пороги
        (f, '      <p><b>paid ≥ {{PAID_TARGET}} · activation ≥ {{ACT_TARGET}}% · churn ≤ {{CHURN_MAX}}%</b></p>',
            '      <p><b>{{demo.ru.k132}}{{demo.en.k132}}</b></p>'),
        (f, '<div class="mgrid" style="margin-top:18px">\n    <div class="fact rv">{{demo.ru.k114}}{{demo.en.k114}}{{demo.ru.k115}}{{demo.en.k115}}</div>\n    <div class="fact rv d1"><b>{{TARGET_LO}}–{{TARGET_HI}}</b>{{demo.ru.k116}}{{demo.en.k116}}</div>\n    <div class="fact rv d2"><b>≥ $1 500</b>{{demo.ru.k117}}{{demo.en.k117}}</div>\n    <div class="fact rv d3"><b>2026-12-15</b>{{demo.ru.k118}}{{demo.en.k118}}</div>\n  </div>',
            '<div class="mgrid" style="margin-top:18px">\n    <div class="fact rv">{{demo.ru.k114}}{{demo.en.k114}}{{demo.ru.k115}}{{demo.en.k115}}</div>\n    <div class="fact rv d1"><b>−3 п.п.</b>{{demo.ru.k116}}{{demo.en.k116}}</div>\n    <div class="fact rv d2"><b>≥70%</b>{{demo.ru.k117}}{{demo.en.k117}}</div>\n    <div class="fact rv d3"><b>2027-04-30</b>{{demo.ru.k118}}{{demo.en.k118}}</div>\n  </div>'),
        # артефакты: ссылки на новое демо
        (f, '''    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_RU.pdf" target="_blank" rel="noopener">SIX_PAGER_RU.pdf</a>
    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_EN.pdf" target="_blank" rel="noopener">SIX_PAGER_EN.pdf</a>
    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_RU.docx" target="_blank" rel="noopener">SIX_PAGER_RU.docx</a>
    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/SIX_PAGER_EN.docx" target="_blank" rel="noopener">SIX_PAGER_EN.docx</a>
    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/REPORT.md" target="_blank" rel="noopener">REPORT.md</a>
    <a class="btn ghost" href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/03_options.md" target="_blank" rel="noopener">03_options.md</a>''',
        artifacts_links_new),
        (f, '<a class="btn primary" href="materials.html?v=9">{{demo.ru.k122}}{{demo.en.k122}}</a>',
            '<a class="btn primary" href="materials.html?v=10">{{demo.ru.k122}}{{demo.en.k122}}</a>'),
    ]

def materials_template_fixes() -> list:
    f = "site_src/materials.html"
    shots_new = f'''  <div class="shot-grid rv d2">
    {VIDEO_CARD_RU.replace("demo.", "materials.").replace("{{demo.", "{{materials.").replace("{{materials.", "{{materials.")}
  </div>'''
    # материаловская сетка: 2 видео + 2 схемы теми же карточками
    m_video_ru = VIDEO_CARD_RU.replace("{{demo.", "{{materials.")
    m_video_en = VIDEO_CARD_EN.replace("{{demo.", "{{materials.")
    m_fig1 = FIG_CARD_STATUS.replace("{{demo.", "{{materials.")
    m_fig2 = FIG_CARD_ARCH.replace("{{demo.", "{{materials.")
    shots_block_new = ('  <div class="shot-grid rv d2">\n    ' + m_video_ru + '\n    ' + m_video_en +
                       '\n    ' + m_fig1 + '\n    ' + m_fig2 + '\n  </div>')
    fixes = []
    tmpl = (ROOT / "site_src" / "materials.html").read_text(encoding="utf-8")
    if 'assets/cv_landing_ru.jpg' in tmpl:  # PRO-133: замена уже применена — не повторять
        fixes.append(
        (f, '''  <div class="shot-grid rv d2">
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.ru.k042}}{{materials.en.k042}}</span></div>
      <div class="shot-crop"><img src="assets/cv_landing_ru.jpg?v=9" alt="Лендинг cvstart.org (русский): AI-конструктор резюме, скан ~129 джоб-бордов, 19 языков"></div>
      {{materials.ru.k043}}
      {{materials.en.k043}}
    </div>
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.en.k044}}{{materials.ru.k044}}</span></div>
      <div class="shot-crop"><img src="assets/cv_landing_en.jpg?v=9" alt="Лендинг cvstart.org (English): open-source AI resume builder"></div>
      {{materials.ru.k045}}
      {{materials.en.k045}}
    </div>
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.ru.k046}}{{materials.en.k046}}</span></div>
      <div class="shot-crop"><img src="assets/cv_dash_ru.jpg?v=9" alt="Дашборд поиска работы CVStart (русский): AI-скоринг вакансий 0.0–5.0"></div>
      {{materials.ru.k047}}
      {{materials.en.k047}}
    </div>
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.en.k048}}{{materials.ru.k048}}</span></div>
      <div class="shot-crop"><img src="assets/cv_dash_en.jpg?v=9" alt="Job-search dashboard CVStart (English): vacancy fit scoring"></div>
      {{materials.ru.k049}}
      {{materials.en.k049}}
    </div>
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.ru.k050}}{{materials.en.k050}}</span></div>
      <div class="shot-crop"><img src="assets/cv_map_en.jpg?v=9" alt="Карта вакансий CVStart (English): job map"></div>
      {{materials.ru.k051}}
      {{materials.en.k051}}
    </div>
    <div class="shot-card">
      <div class="shot-bar"><i></i><i></i><i></i><span>{{materials.ru.k052}}{{materials.en.k052}}</span></div>
      <div class="shot-crop"><img src="assets/cv_tracker_en.jpg?v=9" alt="Трекер заявок CVStart (English): application tracker with follow-up"></div>
      {{materials.ru.k053}}
      {{materials.en.k053}}
    </div>
  </div>''', shots_block_new))
        # поток доказательств: подписи узлов
    fixes.extend([
        (f, '<text x="60" y="106" fill="#9aa7bd" font-weight="400"><tspan lang="ru">{{SOURCES_COUNT}} · сайт + дайджесты</tspan><tspan lang="en">{{SOURCES_COUNT}} · site + digests</tspan></text>',
            '<text x="60" y="106" fill="#9aa7bd" font-weight="400"><tspan lang="ru">{{SOURCES_COUNT}} · бриф, синтетика, вайрфрейм</tspan><tspan lang="en">{{SOURCES_COUNT}} · brief, synthetic, wireframe</tspan></text>'),
        (f, '<text x="945" y="22" fill="#9aa7bd" font-weight="400">check 100/100</text>',
            '<text x="945" y="22" fill="#9aa7bd" font-weight="400">check --strict: 0 · 98/100</text>'),
        # карточки материалов: ссылки нового демо
        (f, '<div class="pdf-meta"><code lang="ru">projects/демо/outputs/REPORT.md</code></div>',
            f'<div class="pdf-meta"><code lang="ru">projects/{PROJ}/outputs/REPORT.md</code></div>'),
        (f, f'<div class="pdf-btns"><a href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/outputs/REPORT.md" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k059}}}}{{{{materials.en.k059}}}}</a></div>',
            f'<div class="pdf-btns"><a href="{gh_blob("outputs/REPORT.md")}" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k059}}}}{{{{materials.en.k059}}}}</a></div>'),
        (f, '<div class="pdf-meta"><code lang="ru">projects/демо/sources/</code> · S001–S011</div>',
            f'<div class="pdf-meta"><code lang="ru">projects/{PROJ}/sources/</code> · S001–S004</div>'),
        (f, f'<div class="pdf-btns"><a href="https://github.com/Fighter90/product-factory-strategist-agent/tree/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/sources" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k062}}}}{{{{materials.en.k062}}}}</a></div>',
            f'<div class="pdf-btns"><a href="{GH}/tree/main/projects/{P}/sources" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k062}}}}{{{{materials.en.k062}}}}</a></div>'),
        (f, '''      <div class="pdf-btns">
        <a href="https://github.com/Fighter90/product-factory-strategist-agent/tree/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/interviews/synthetic" target="_blank" rel="noopener" class="pbtn">interviews/synthetic/</a>
        <a href="https://github.com/Fighter90/product-factory-strategist-agent/blob/main/projects/%D0%B4%D0%B5%D0%BC%D0%BE/analysis/synthetic_funnel.csv" target="_blank" rel="noopener" class="pbtn ghost2">synthetic_funnel.csv</a>
      </div>''',
            f'''      <div class="pdf-btns">
        <a href="{GH}/tree/main/projects/{P}/interviews/synthetic" target="_blank" rel="noopener" class="pbtn">interviews/synthetic/</a>
        <a href="{GH}/tree/main/projects/{P}/sources" target="_blank" rel="noopener" class="pbtn ghost2">S002 · S003</a>
      </div>'''),
        (f, '<div class="pdf-meta">interviews/synthetic/ · analysis/synthetic_funnel.csv</div>',
            f'<div class="pdf-meta">projects/{PROJ}/interviews/synthetic/</div>'),
        (f, '<div class="pdf-btns"><a href="https://cvstart.org/" target="_blank" rel="noopener" class="pbtn">{{materials.ru.k070}}{{materials.en.k070}}</a></div>',
            f'<div class="pdf-btns"><a href="{GH}/tree/main/projects/{P}" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k070}}}}{{{{materials.en.k070}}}}</a></div>'),
        (f, '<div class="pdf-btns"><a href="https://github.com/Fighter90/career-ops-ui" target="_blank" rel="noopener" class="pbtn">{{materials.ru.k074}}{{materials.en.k074}}</a></div>',
            f'<div class="pdf-btns"><a href="{GH_BLOB}/projects/{P}/outputs/BRIEF_RESPONSE.md" target="_blank" rel="noopener" class="pbtn">{{{{materials.ru.k074}}}}{{{{materials.en.k074}}}}</a></div>'),
        # k043/k045/k047/k049/k051/k053 больше не нужны (слоты заняты видео/схемами) —
        # i18n-ключи перезаписаны, здесь шаблон чист.
    ])
    return fixes

def help_template_fixes() -> list:
    return []

# ------------------------------------------------------- index (лендинг) edits

def index_fixes() -> list:
    """site/index.html (RU) и site/en/index.html (EN): секции proof и demo."""
    ru = "site/index.html"
    en = "site/en/index.html"
    quote_ru = ("«Ваша команда отвечает за услуги вымышленного мобильного оператора. Одни клиенты "
                "помогают близким со связью. Другие обслуживают несколько собственных номеров…»")
    return [
        # --- RU ---------------------------------------------------------------
        (ru, '<h2 id="proof-h">Фрагменты реальной работы <span class="acc">демо-проекта CVStart</span></h2>',
            '<h2 id="proof-h">Фрагменты реальной работы <span class="acc">демо-проекта «Связь для близких»</span></h2>'),
        (ru, '''<pre><span class="p">$</span> pfs new "CVStart: платная версия" "Разработать коммерческую версию cvstart.org и стратегию вывода на рынок"
<span class="a">Шаг 1/12 · intake</span> · бриф подтверждён · дальше: sources
<span class="a">Шаг 2/12 · sources</span> · 11 источников · 0 запрещённых доменов · дальше: research
<span class="p">$</span> pfs claim add "Мировой рынок онлайн-рекрутинга: $37,97 млрд (2025), CAGR 7,1% до 2033" --kind fact --source S007 --grade B
<span class="hi">C011 · факт · сила B · цитата сохранена</span>
<span class="a">Шаг 3/12 · research</span> · 20 утверждений в реестре · дальше: discovery
<span class="p">&gt;</span> стоп — пауза: состояние в файлах, новый чат продолжит с шага 3</pre>''',
            '''<pre><span class="p">$</span> pfs new "Связь для близких и собственных устройств" "Ваша команда отвечает за услуги вымышленного мобильного оператора. Одни клиенты помогают близким со связью…"
<span class="a">Шаг 1/12 · intake</span> · бриф подтверждён · дальше: sources
<span class="a">Шаг 2/12 · sources</span> · 4 источника · 0 запрещённых доменов · дальше: research
<span class="p">$</span> pfs claim add "500 ₽ валовой прибыли за доп. оплаченный месяц; +6 млн ₽ = 12 000 мес" --kind fact --source S001 --grade A
<span class="hi">C003 · факт · сила A · цитата сохранена</span>
<span class="a">Шаг 3/12 · research</span> · 26 утверждений в реестре · дальше: discovery
<span class="p">&gt;</span> стоп — пауза: состояние в файлах, новый чат продолжит с шага 3</pre>'''),
        (ru, '''<div class="claim">
          <div class="tags"><span class="tag a">C011 · факт</span><span class="tag">сила B</span><span class="tag">источник S007</span></div>
          <p>Мировой рынок онлайн-рекрутинга: $37,97 млрд (2025), CAGR 7,1% до 2033; Indeed — 60+ стран, 28 языков, 685 млн профилей; Bayt (MENA) — 59+ млн профилей</p>
          <div class="chain">
            <span class="chip a"><em>C011</em> · факт · сила B</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip"><em>S007</em> · skyquestt.com · 2026-11-06</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip">six-pager · FAQ-3 · Стратегические инициативы</span>
          </div>
        </div>''',
            '''<div class="claim">
          <div class="tags"><span class="tag a">C003 · факт</span><span class="tag">сила A</span><span class="tag">источник S001</span></div>
          <p>Учебная ставка: 500 руб. валовой прибыли за один дополнительный оплаченный месяц одного номера; для прибавки 6 млн руб. без новых прямых расходов нужно 12 000 доп. оплаченных месяцев</p>
          <div class="chain">
            <span class="chip a"><em>C003</em> · факт · сила A</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip"><em>S001</em> · бриф заказчика · 2026-11-19</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip">six-pager · FAQ-1 · Анализ текущего состояния</span>
          </div>
        </div>'''),
        (ru, '''<div class="xl">
          <div class="label" style="margin-bottom:10px">Excel · лист «Ввод»</div>
          <table>
            <tr><td>Цена Pro</td><td>$29/мес</td></tr>
            <tr><td>Переменные 25% → вклад на покрытие</td><td>$21,75</td></tr>
            <tr><td>LTV</td><td>≈ $272</td></tr>
            <tr><td>LTV / CAC</td><td>≈ 4,5</td></tr>
          </table>
          <p class="muted" style="margin:10px 0 0;font-size:13px">Значения можно поменять — формулы пересчитаются.</p>
        </div>''',
            '''<div class="xl">
          <div class="label" style="margin-bottom:10px">Excel · unit-econ</div>
          <table>
            <tr><td>Ставка за доп. оплаченный месяц</td><td>500 ₽</td></tr>
            <tr><td>Нужно месяцев (разрыв 6 млн ₽)</td><td>12 000</td></tr>
            <tr><td>Осн. ход: 5 500 × 3 мес − 1,5 млн</td><td>+6,75 млн ₽</td></tr>
            <tr><td>Итог года (осн. ход)</td><td>285,8 млн ₽</td></tr>
          </table>
          <p class="muted" style="margin:10px 0 0;font-size:13px">Значения можно поменять — формулы пересчитаются.</p>
        </div>'''),
        (ru, '<h2 id="demo-h">CVStart: <span class="acc">платная версия</span> и выход на рынок</h2>',
            '<h2 id="demo-h">Демо-разбор: «Связь для близких» — <span class="acc">предупреждение до перебоя</span></h2>'),
        (ru, '<p>Задача руководителя дословно: «Разработать коммерческую версию cvstart.org и стратегию вывода на рынок на весь мир». Числа — из проекта, не руками.</p>',
            f'<p>Задача руководителя дословно: {quote_ru} Числа — из проекта, не руками.</p>'),
        (ru, '''      <dl class="stats">
        <div><dt><span>источников</span></dt><dd style="margin:0"><b>11</b></dd></div>
        <div><dt><span>утверждений, из них факты — 12</span></dt><dd style="margin:0"><b>20</b></dd></div>
        <div><dt><span>вариантов A–E, со статус-кво и закрытием</span></dt><dd style="margin:0"><b>A–E</b></dd></div>
        <div><dt><span>возражений и скрытых допущений red team</span></dt><dd style="margin:0"><b>15 + 5</b></dd></div>
        <div><dt><span>выбор: Hosted freemium SaaS</span></dt><dd style="margin:0"><b>B</b></dd></div>
        <div><dt><span>пересмотр решения D001</span></dt><dd style="margin:0"><b>2027-02-10</b></dd></div>
      </dl>''',
            '''      <dl class="stats">
        <div><dt><span>источников</span></dt><dd style="margin:0"><b>4</b></dd></div>
        <div><dt><span>утверждений, из них факты — 10</span></dt><dd style="margin:0"><b>26</b></dd></div>
        <div><dt><span>вариантов A–E, включая «закрыть»</span></dt><dd style="margin:0"><b>A–E</b></dd></div>
        <div><dt><span>возражений и скрытых допущений red team</span></dt><dd style="margin:0"><b>15 + 5</b></dd></div>
        <div><dt><span>выбор: «Предупреждение до перебоя»</span></dt><dd style="margin:0"><b>B</b></dd></div>
        <div><dt><span>пересмотр решения D001</span></dt><dd style="margin:0"><b>2027-04-30</b></dd></div>
      </dl>'''),
        (ru, '<!-- числа подставляет scripts/build_site.py из projects/demo -->',
            '<!-- числа подставляет scripts/build_svyaz.py из проекта «Связь для близких» -->'),
        # --- EN ---------------------------------------------------------------
        (en, '<h2 id="proof-h">Fragments of the real CVStart <span class="acc">demo project</span></h2>',
            '<h2 id="proof-h">Fragments of the real <span class="acc">Connection for Loved Ones demo project</span></h2>'),
        (en, '''<pre><span class="p">$</span> pfs new "CVStart: paid version" "Build a commercial version of cvstart.org and take it to market worldwide"
<span class="a">Step 1/12 · intake</span> · brief confirmed · next: sources
<span class="a">Step 2/12 · sources</span> · 11 sources · 0 blocked domains · next: research
<span class="p">$</span> pfs claim add "Global online recruitment market: $37.97B in 2025 with a 7.1% CAGR to 2033" --kind fact --source S007 --grade B
<span class="hi">C011 · fact · grade B · quote saved</span>
<span class="a">Step 3/12 · research</span> · 20 claims in the registry · next: discovery
<span class="p">&gt;</span> stop — pause: the state lives in files, a new chat resumes at step 3</pre>''',
            '''<pre><span class="p">$</span> pfs new "Connection for loved ones and personal devices" "Your team runs the services of a fictional mobile operator. Some customers help loved ones stay connected…"
<span class="a">Step 1/12 · intake</span> · brief confirmed · next: sources
<span class="a">Step 2/12 · sources</span> · 4 sources · 0 blocked domains · next: research
<span class="p">$</span> pfs claim add "₽500 of gross profit per extra paid month; +₽6M = 12,000 months" --kind fact --source S001 --grade A
<span class="hi">C003 · fact · grade A · quote saved</span>
<span class="a">Step 3/12 · research</span> · 26 claims in the registry · next: discovery
<span class="p">&gt;</span> stop — pause: the state lives in files, a new chat resumes at step 3</pre>'''),
        (en, '''<div class="claim">
          <div class="tags"><span class="tag a">C011 · fact</span><span class="tag">grade B</span><span class="tag">source S007</span></div>
          <p>Global online recruitment market: $37.97B in 2025 with a 7.1% CAGR to 2033; Indeed — 60+ countries, 28 languages, 685M profiles; Bayt (MENA) — 59M+ profiles</p>
          <div class="chain">
            <span class="chip a"><em>C011</em> · fact · grade B</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip"><em>S007</em> · skyquestt.com · 2026-11-06</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip">six-pager · FAQ-1 · Current state analysis</span>
          </div>
        </div>''',
            '''<div class="claim">
          <div class="tags"><span class="tag a">C003 · fact</span><span class="tag">grade A</span><span class="tag">source S001</span></div>
          <p>Teaching rate: ₽500 of gross profit per one extra paid month of a number; a +₽6M gain with no new direct costs requires 12,000 extra paid months</p>
          <div class="chain">
            <span class="chip a"><em>C003</em> · fact · grade A</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip"><em>S001</em> · the client brief · 2026-11-19</span><span aria-hidden="true" class="muted">→</span>
            <span class="chip">six-pager · FAQ-1 · Current state analysis</span>
          </div>
        </div>'''),
        (en, '''<div class="xl">
          <div class="label" style="margin-bottom:10px">Excel · input sheet</div>
          <table>
            <tr><td>Pro price</td><td>$29/mo</td></tr>
            <tr><td>25% variable costs → contribution margin</td><td>$21.75</td></tr>
            <tr><td>LTV</td><td>≈ $272</td></tr>
            <tr><td>LTV / CAC</td><td>≈ 4.5</td></tr>
          </table>
          <p class="muted" style="margin:10px 0 0;font-size:13px">Change the inputs and the formulas recalculate.</p>
        </div>''',
            '''<div class="xl">
          <div class="label" style="margin-bottom:10px">Excel · unit-econ</div>
          <table>
            <tr><td>Rate per extra paid month</td><td>₽500</td></tr>
            <tr><td>Months needed (the ₽6M gap)</td><td>12,000</td></tr>
            <tr><td>Base case: 5,500 × 3 mo − 1.5M</td><td>+₽6.75M</td></tr>
            <tr><td>Year total (base case)</td><td>₽285.8M</td></tr>
          </table>
          <p class="muted" style="margin:10px 0 0;font-size:13px">Change the inputs and the formulas recalculate.</p>
        </div>'''),
        (en, '<h2 id="demo-h">CVStart: <span class="acc">a paid version</span> and a go-to-market plan</h2>',
            '<h2 id="demo-h">Demo walkthrough: <span class="acc">Connection for Loved Ones</span> — warn before the outage</h2>'),
        (en, '<p>The product lead’s request, word for word: “Build a commercial version of cvstart.org and a strategy to take it to market worldwide.” Numbers come from the project, not from hands.</p>',
            '<p>The product lead’s request, word for word: “Your team runs the services of a fictional mobile operator. Some customers help loved ones stay connected. Others manage several numbers of their own…” Numbers come from the project, not from hands.</p>'),
        (en, '''      <dl class="stats">
        <div><dt><span>sources</span></dt><dd style="margin:0"><b>11</b></dd></div>
        <div><dt><span>claims, of them facts — 12</span></dt><dd style="margin:0"><b>20</b></dd></div>
        <div><dt><span>options A–E, incl. status quo and shut-down</span></dt><dd style="margin:0"><b>A–E</b></dd></div>
        <div><dt><span>red-team objections and hidden assumptions</span></dt><dd style="margin:0"><b>15 + 5</b></dd></div>
        <div><dt><span>chosen: Hosted freemium SaaS</span></dt><dd style="margin:0"><b>B</b></dd></div>
        <div><dt><span>review of decision D001</span></dt><dd style="margin:0"><b>2027-02-10</b></dd></div>
      </dl>''',
            '''      <dl class="stats">
        <div><dt><span>sources</span></dt><dd style="margin:0"><b>4</b></dd></div>
        <div><dt><span>claims, of them facts — 10</span></dt><dd style="margin:0"><b>26</b></dd></div>
        <div><dt><span>options A–E, incl. shut-down</span></dt><dd style="margin:0"><b>A–E</b></dd></div>
        <div><dt><span>red-team objections and hidden assumptions</span></dt><dd style="margin:0"><b>15 + 5</b></dd></div>
        <div><dt><span>chosen: Warn before the outage</span></dt><dd style="margin:0"><b>B</b></dd></div>
        <div><dt><span>review of decision D001</span></dt><dd style="margin:0"><b>2027-04-30</b></dd></div>
      </dl>'''),
        (en, '<!-- numbers are substituted by scripts/build_site.py from the demo project -->',
            '<!-- numbers are substituted by scripts/build_svyaz.py from the Connection for Loved Ones project -->'),
    ]

# ------------------------------------------------------------------- rendering

VALUES = {
    "SOURCES_COUNT": ("int", 4), "CLAIMS_COUNT": ("int", 26),
    "S_RANGE": ("str", "S001–S004"), "C_RANGE": ("str", "C001–C027"),
    "OPT_COUNT": ("int", 5), "RT_HITS": ("int", 20),
    "D_OBJ": ("int", 15), "D_ASM": ("int", 5),
    "SIX_COUNT": ("int", 4), "XLSX_COUNT": ("int", 4), "SHOTS_COUNT": ("int", 4),
    "N_MAPS": ("int", 111), "N_SKILLS": ("int", 102), "N_AGENTS": ("int", 10),
    "N_HOOKS": ("int", 6), "N_TESTS": ("int", 937), "N_MCP": ("int", 18),
    "REVIEW_RU": ("str", "2027-04-30"), "REVIEW_EN": ("str", "2027-04-30"),
    "FUNNEL_WEEKS": ("int", 6), "PAID_W12": ("int", 600),
}

GROUNDS_RU = [
    ("C013", "гипотеза: предупреждение организатору до критического события снижает долю подходящих номеров с полным ограничением из-за исчерпания объёма с 12% до 9% (−3 п.п.) — проверка A/B-пилотом"),
    ("C016", "вывод: первые клиенты — семьи: доступная база 100 тыс. домохозяйств против 40 тыс. владельцев; владельцы — вторая очередь с переносом механики"),
    ("C017", "вывод: первая услуга — «предупреждение до перебоя»: данные об остатках и платежах уже у оператора, механика передачи интернета есть — добавляется только информирование"),
    ("C003", "факт: 500 руб. валовой прибыли за один доп. оплаченный месяц; для +6 млн руб. нужно 12 000 доп. оплаченных месяцев"),
    ("C015", "вывод: цель +6 млн руб. достижима, например, при 4 000 номерах × 3 мес или 6 000 номерах × 2 мес дополнительного удержания"),
    ("C027", "вывод: 600 групп — объём набора по темпу брифа (~100/нед × 6 недель); достаточность проверяется расчётом MDE до старта (мощность ≥80%, α=5%)"),
]
GROUNDS_EN = [
    ("C013", "hypothesis: a pre-outage warning to the organizer cuts the share of numbers fully restricted due to exhaustion from 12% to 9% (−3 pp) — tested by the A/B pilot"),
    ("C016", "inference: the first customers are families — 100K available households vs 40K device owners; owners come in the second wave with the same warning mechanics"),
    ("C017", "inference: the first service is \"warn before the outage\": balance and payment data already exist at the operator, data-sharing mechanics exist — only notifications are added"),
    ("C003", "fact: ₽500 of gross profit per extra paid month; +₽6M requires 12,000 extra paid months"),
    ("C015", "inference: the +₽6M goal is reachable, e.g. 4,000 numbers × 3 months or 6,000 numbers × 2 months of extra retention"),
    ("C027", "inference: 600 groups — the intake per the brief's rate (~100/week × 6 weeks); sufficiency is checked by an MDE calculation before launch (power ≥80%, α=5%)"),
]
METRIC_RU = ("Первичная метрика: дополнительные оплаченные месяцы на группу (ITT); "
             "клиентский результат: доля ограничений из-за исчерпания 12%→9% (−3 п.п.)")
METRIC_EN = ("Primary metric: extra paid months per group (ITT); client outcome: "
             "exhaustion-driven restrictions 12%→9% (−3 pp)")
TRIGGERS_RU = ("Отзывы согласий >15% [C022] ; повторные списания ≥1 [C026] ; precision прогноза "
               "<80% [C026] ; темп набора <50 групп/нед 2 недели подряд [C012] ; сдвиг платежей "
               ">30% (инкрементальность) [C021]")
TRIGGERS_EN = ("Consent withdrawal >15% [C022] ; repeat charges ≥1 [C026] ; forecast precision "
               "<80% [C026] ; intake pace <50 groups/week for 2 straight weeks [C012] ; payment "
               "shifts >30% (incrementality) [C021]")


def render_value(kind, val, lang: str) -> str:
    if kind == "int":
        return str(val)
    if kind == "str":
        return html_mod.escape(str(val), quote=True)
    raise bs.BuildError(f"неизвестный тип значения {kind!r}")


def apply_i18n_updates() -> None:
    for lang in ("ru", "en"):
        p = bs.I18N_DIR / f"{lang}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for page, keys in U[lang].items():
            dst = data["ui"] if page == "ui" else data[page]
            for k, v in keys.items():
                dst[k] = v
        # cache-bust ссылок на страницы при выкатке нового демо
        def bump(v):
            return v.replace("?v=9", "?v=10") if isinstance(v, str) else v
        n_bump = 0
        for page in data.values():
            if isinstance(page, dict):
                for k, v in page.items():
                    nv = bump(v)
                    if nv != v:
                        page[k] = nv
                        n_bump += 1
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"i18n {lang}.json: обновлено {sum(len(v) for v in U[lang].values())} строк, "
              f"?v=9→?v=10: {n_bump}")


def apply_fixes(fixes: list, base: str) -> None:
    for path, old, new in fixes:
        p = ROOT / path
        text = p.read_text(encoding="utf-8")
        if old in text:
            text = text.replace(old, new)
            p.write_text(text, encoding="utf-8")
            print(f"{path}: замена применена ({len(old)} → {len(new)} симв.)")
        elif new in text:
            print(f"{path}: уже применено, пропуск")
        else:
            raise bs.BuildError(f"{path}: не найден фрагмент для замены ({base}): {old[:90]!r}…")


def build_pages(out: Path) -> list:
    ru_d = json.loads((bs.I18N_DIR / "ru.json").read_text(encoding="utf-8"))
    en_d = json.loads((bs.I18N_DIR / "en.json").read_text(encoding="utf-8"))
    written = []
    for page in bs.PAGES_I18N:
        src = (bs.SITE_SRC / f"{page}.html").read_text(encoding="utf-8")
        for lang in ("ru", "en"):
            d = ru_d if lang == "ru" else en_d
            pd_ = d[bs.PAGE_DICT[page]]
            page_html = src
            for mk in ("title", "description", "og_title", "og_url"):
                page_html = page_html.replace("{{" + page + "." + mk + "}}", pd_[mk])
            page_html = re.sub(r"\{\{" + page + r"\.(ru|en)\.[A-Za-z0-9_]+\}\}",
                               lambda m: "" if m.group(1) != lang else m.group(0), page_html)
            page_html = re.sub(r"\{\{" + page + r"\." + lang + r"\.([A-Za-z0-9_]+)\}\}",
                               lambda m: pd_[m.group(1)], page_html)
            page_html = re.sub(r"\{\{ui\.([a-z_]+)\}\}", lambda m: d["ui"][m.group(1)], page_html)

            def repl(m):
                key = m.group(1)
                if key == "GROUNDS_RU":
                    return " · ".join(f"<b>{cid}</b> — {text}" for cid, text in GROUNDS_RU)
                if key == "GROUNDS_EN":
                    return " · ".join(f"<b>{cid}</b> — {text}" for cid, text in GROUNDS_EN)
                if key == "TRIGGERS_RU":
                    return html_mod.escape(TRIGGERS_RU, quote=False)
                if key == "TRIGGERS_EN":
                    return html_mod.escape(TRIGGERS_EN, quote=False)
                if key == "METRIC_RU":
                    return html_mod.escape(METRIC_RU, quote=False)
                if key == "METRIC_EN":
                    return html_mod.escape(METRIC_EN, quote=False)
                if key in VALUES:
                    kind, val = VALUES[key]
                    return render_value(kind, val, lang)
                raise bs.BuildError(f"{page}/{lang}: неизвестный токен {{{{{key}}}}}")

            page_html = re.sub(r"\{\{([A-Z_0-9]+)\}\}", repl, page_html)
            meta = pd_
            canon = f"{bs.BASE}/{page}.html"
            canon = f"{bs.BASE}/en/{page}.html" if lang == "en" else canon
            head = (f"<title>{html_mod.escape(meta['title'], quote=True)}</title>\n"
                    f'<meta name="description" content="{html_mod.escape(meta["description"], quote=True)}">\n'
                    f'<meta property="og:type" content="website">\n'
                    f'<meta property="og:title" content="{html_mod.escape(meta["og_title"], quote=True)}">\n'
                    f'<meta property="og:description" content="{html_mod.escape(meta["description"], quote=True)}">\n'
                    f'<meta property="og:url" content="{canon}">\n'
                    f'<link rel="canonical" href="{canon}">\n'
                    f'<link rel="alternate" hreflang="ru" href="{bs.BASE}/{page}.html">\n'
                    f'<link rel="alternate" hreflang="en" href="{bs.BASE}/en/{page}.html">\n'
                    f'<link rel="alternate" hreflang="x-default" href="{bs.BASE}/{page}.html">')
            page_html, n_title = re.subn(r"<title>.*?</title>\n?", "", page_html, flags=re.S)
            page_html, n_desc = re.subn(r'<meta name="description"[^>]*>\n?', "", page_html)
            page_html = re.subn(r'<meta property="og:[a-z_]+"[^>]*>\n?', "", page_html)[0]
            if n_title != 1 or n_desc != 1:
                raise bs.BuildError(f"{page}: не ровно одна строка title/description в исходнике")
            mark = '<meta charset="UTF-8">'
            if mark not in page_html:
                raise bs.BuildError(f"{page}: нет {mark}")
            page_html = page_html.replace(mark, mark + "\n" + head, 1)
            page_html = page_html.replace("<!--LANGSWITCH-->", bs.LANGSWITCH[(page, lang)], 1)
            if lang == "en":
                page_html = re.sub(r'((?:src|href)=")assets/', r"\1../assets/", page_html)
            page_html = bs.filter_lang(page_html, lang)
            page_html = re.sub(r"\n{3,}", "\n\n", page_html)
            if "{{" in page_html:
                left = sorted(set(re.findall(r"\{\{([^}]+)\}\}", page_html)))
                raise bs.BuildError(f"{page}/{lang}: неразрешённые токены: {left[:6]}")
            dest = out / (f"en/{page}.html" if lang == "en" else f"{page}.html")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page_html, encoding="utf-8")
            written.append(dest)
    return written


def main() -> int:
    apply_i18n_updates()
    apply_fixes(demo_template_fixes(), "demo")
    apply_fixes(materials_template_fixes(), "materials")
    apply_fixes(help_template_fixes(), "help")
    apply_fixes(index_fixes(), "index")
    out = ROOT / "site"
    written = build_pages(out)
    print("Записано:", ", ".join(str(p.relative_to(ROOT)) for p in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
