#!/usr/bin/env python3
"""astudio-1c · bsl_check.py — static checks for 1C queries and BSL code (RU and EN keywords).

  python3 bsl_check.py Module.bsl [more files or folders]
  python3 bsl_check.py --query query.txt
  python3 bsl_check.py src/ --json

Reads text only; never runs 1C code. Complements (does not replace) BSL Language Server.
Each finding names the ITS standard (its.1c.ru/db/v8std) or BSL LS diagnostic it follows.
Query checks: VT filters in ГДЕ instead of VT parameters (657/733), commas between conditions
inside a VT parameter, joins with subqueries or VTs (655), OR in WHERE (658), ПЕРВЫЕ without
УПОРЯДОЧИТЬ (412), chained dereference «.Поле.Поле» (654), ПОДОБНО «%…» (726), temp tables joined
without ИНДЕКСИРОВАТЬ, ОБЪЕДИНИТЬ without ВСЕ (434), no РАЗРЕШЕННЫЕ (info).
Code checks: query executed in a loop (436), transactions not paired with Попытка (783), modal and
synchronous calls (703), Выполнить/Вычислить (770), privileged mode (485), hardcoded secrets (740),
Сообщить() (use ОбщегоНазначения.СообщитьПользователю), empty Исключение block (499).
"""
import argparse, json, pathlib, re, sys

I = re.I | re.U
FIND = []

def add(level, code, std, line, msg, path):
    FIND.append({"level": level, "code": code, "std": std, "file": path, "line": line, "message": msg})

def line_of(text, pos): return text.count("\n", 0, pos) + 1

VT_NAMES = r"(Остатки|Обороты|ОстаткиИОбороты|СрезПоследних|СрезПервых|Balance|Turnovers|BalanceAndTurnovers|SliceLast|SliceFirst|ДвиженияССубконто|ОборотыДтКт)"

def check_query(q, path, base_line=1):
    def ln(pos): return base_line + q.count("\n", 0, pos)
    # VT used + WHERE refers to VT alias
    for m in re.finditer(r"\.\s*" + VT_NAMES + r"\s*(\((?P<args>[^()]*(\([^()]*\)[^()]*)*)\))?\s*(КАК|AS)\s+(?P<alias>[\wА-Яа-яЁё]+)", q, I):
        alias, args = m.group("alias"), m.group("args")
        where = re.search(r"\b(ГДЕ|WHERE)\b(.*?)(\b(СГРУППИРОВАТЬ|УПОРЯДОЧИТЬ|ОБЪЕДИНИТЬ|ИТОГИ|GROUP|ORDER|UNION|TOTALS|ИНДЕКСИРОВАТЬ)\b|;|$)", q[m.end():], I | re.S)
        if where and re.search(r"\b" + re.escape(alias) + r"\.[\wА-Яа-яЁё]+\s*(=|В\s*\(|IN\s*\(|<|>)", where.group(2), I):
            if not re.search(r"(Остаток|Оборот|Приход|Расход|Balance|Turnover|Receipt|Expense)\s*(=|<|>)", where.group(2), I):
                add("error", "vt_filter_in_where", "ITS 657, 733; BSL LS VirtualTableCallWithoutParameters", ln(m.start()),
                    f"filter on virtual table «{alias}» is in ГДЕ: pass dimension conditions in the table's parameters", path)
        if args is None or not args.strip():
            add("warn", "vt_without_params", "ITS 657", ln(m.start()), f"virtual table «{alias}» called without parameters: set the period/moment and the condition", path)
        elif args:
            parts = [p.strip() for p in re.split(r",(?![^()]*\))", args)]
            conds = [p for p in parts if re.search(r"\s(=|В|IN)\s*[&(]|\s=\s", p, I)]
            if len(conds) >= 2:
                add("error", "vt_condition_commas", "ITS 657", ln(m.start()),
                    f"«{alias}»: several conditions separated by commas; the condition is ONE parameter, join predicates with И (AND)", path)
    for m in re.finditer(r"\b(СОЕДИНЕНИЕ|JOIN)\s*\(\s*(ВЫБРАТЬ|SELECT)\b", q, I):
        add("error", "join_subquery", "ITS 655; BSL LS JoinWithSubQuery", ln(m.start()), "join with a subquery: put it into an indexed temporary table first", path)
    for m in re.finditer(r"\b(СОЕДИНЕНИЕ|JOIN)\s+[\wА-Яа-яЁё]+\.[\wА-Яа-яЁё]+\.\s*" + VT_NAMES, q, I):
        add("warn", "join_vt", "ITS 655; BSL LS JoinWithVirtualTable", ln(m.start()), "join with a virtual table: read it into a temporary table, then join", path)
    for m in re.finditer(r"\b(ГДЕ|WHERE)\b(.*?)(\b(СГРУППИРОВАТЬ|УПОРЯДОЧИТЬ|ОБЪЕДИНИТЬ|GROUP|ORDER|UNION|ИНДЕКСИРОВАТЬ|ПОМЕСТИТЬ)\b|;|$)", q, I | re.S):
        if re.search(r"\s(ИЛИ|OR)\s", m.group(2), I):
            add("warn", "or_in_where", "ITS 658; BSL LS LogicalOrInTheWhereSectionOfQuery", ln(m.start()), "ИЛИ in ГДЕ can stop index use: use В(...) or split with ОБЪЕДИНИТЬ ВСЕ", path)
    for m in re.finditer(r"\b(ВЫБРАТЬ|SELECT)\b(\s+(РАЗЛИЧНЫЕ|РАЗРЕШЕННЫЕ|DISTINCT|ALLOWED))*\s+(ПЕРВЫЕ|TOP)\s+\d+", q, I):
        tail = q[m.end():]
        stop = re.search(r";|\b(ОБЪЕДИНИТЬ|UNION)\b", tail, I)
        seg = tail[: stop.start()] if stop else tail
        if not re.search(r"\b(УПОРЯДОЧИТЬ|ORDER)\b", seg, I):
            add("warn", "top_without_order", "ITS 412; BSL LS SelectTopWithoutOrderBy", ln(m.start()), "ПЕРВЫЕ without УПОРЯДОЧИТЬ ПО returns an arbitrary row", path)
    for m in re.finditer(r"[\wА-Яа-яЁё]+\.[\wА-Яа-яЁё]+\.[\wА-Яа-яЁё]+\.[\wА-Яа-яЁё]+", q):
        s = m.group(0)
        if not re.match(r"(Справочник|Документ|РегистрНакопления|РегистрСведений|РегистрБухгалтерии|Перечисление|ПланСчетов|ПланВидовХарактеристик|Catalog|Document|AccumulationRegister|InformationRegister|AccountingRegister|Enum|ChartOf)", s, I):
            add("warn", "deep_dereference", "ITS 654; BSL LS QueryNestedFieldsByDot", ln(m.start()), f"«{s}»: each dot is an implicit join; select the needed fields in a temporary table", path)
    for m in re.finditer(r"\.Ссылка\.Ссылка|\.Ref\.Ref", q, I):
        add("warn", "ref_overuse", "BSL LS RefOveruse", ln(m.start()), "«.Ссылка» on a reference adds a join and no value", path)
    for m in re.finditer(r"\b(ПОДОБНО|LIKE)\s+\"%", q, I):
        add("warn", "like_leading_percent", "ITS 726", ln(m.start()), "ПОДОБНО with a leading % cannot use an index", path)
    temp = set(x.lower() for x in re.findall(r"\b(?:ПОМЕСТИТЬ|INTO)\s+([\wА-Яа-яЁё]+)", q, I))
    for t in temp:
        if re.search(r"\b(СОЕДИНЕНИЕ|JOIN)\s+" + re.escape(t) + r"\b", q, I) or re.search(r"\b(ИЗ|FROM)\s+" + re.escape(t) + r"\b.*?\b(СОЕДИНЕНИЕ|JOIN)\b", q, I | re.S):
            block = re.search(r"\b(?:ПОМЕСТИТЬ|INTO)\s+" + re.escape(t) + r"\b(.*?)(;|$)", q, I | re.S)
            if block and not re.search(r"\b(ИНДЕКСИРОВАТЬ|INDEX)\b", block.group(1), I):
                add("info", "temp_not_indexed", "comol-style pre-flight; ITS 655", ln(block.start()), f"temporary table «{t}» is joined: add ИНДЕКСИРОВАТЬ ПО <join keys> if it is large", path)
    for m in re.finditer(r"\b(ОБЪЕДИНИТЬ|UNION)\b(?!\s+(ВСЕ|ALL)\b)", q, I):
        add("info", "union_distinct", "ITS 434", ln(m.start()), "ОБЪЕДИНИТЬ removes duplicates (slower); use ОБЪЕДИНИТЬ ВСЕ if duplicates are impossible or wanted", path)

def extract_queries(code):
    """Yield (start_line, text) for string literals that look like queries ("ВЫБРАТЬ ... with | continuation)."""
    for m in re.finditer(r"\"((?:[^\"]|\"\")*?)\"", code, re.S):
        s = m.group(1)
        if re.search(r"\b(ВЫБРАТЬ|SELECT)\b", s, I):
            text = re.sub(r"(?m)^\s*\|", "", s).replace('""', '"')
            yield line_of(code, m.start()), text

LOOP = r"(?is)\b(Для|Пока|For|While)\b.*?\b(Цикл|Do)\b(?P<body>.*?)\b(КонецЦикла|EndDo)\b"

def check_code(code, path):
    for ln, q in extract_queries(code):
        check_query(q, path, ln)
    for m in re.finditer(LOOP, code):
        if re.search(r"\.(Выполнить|Execute|ВыполнитьПакет|ExecuteBatch)\s*\(", m.group("body"), I):
            add("error", "query_in_loop", "ITS 436; BSL LS CreateQueryInCycle", line_of(code, m.start()), "query executed inside a loop: read all data with one query before the loop", path)
    for m in re.finditer(r"\b(НачатьТранзакцию|BeginTransaction)\s*\(\s*\)\s*;", code, I):
        after = code[m.end(): m.end() + 200]
        if not re.match(r"\s*(//[^\n]*\n\s*)*(Попытка|Try)\b", after, I):
            add("error", "transaction_not_in_try", "ITS 783; BSL LS BeginTransactionBeforeTryCatch", line_of(code, m.start()), "НачатьТранзакцию() must be followed immediately by Попытка … Исключение ОтменитьТранзакцию(); ВызватьИсключение; КонецПопытки", path)
    for m in re.finditer(r"\b(Предупреждение|Вопрос|ОткрытьФормуМодально|ВвестиЗначение|ВвестиЧисло|ВвестиДату|ВвестиСтроку|DoMessageBox|DoQueryBox|OpenFormModal)\s*\(", code, I):
        add("warn", "modal_call", "ITS 703; BSL LS UsingModalWindows", line_of(code, m.start()), f"{m.group(1)}(): modal/synchronous call; use the asynchronous variant (…Асинх / ОписаниеОповещения)", path)
    for m in re.finditer(r"(?<![\wА-Яа-яЁё.])(Выполнить|Вычислить|Execute|Eval)\s*\(", code, I):
        add("warn", "execute_external", "ITS 770; BSL LS ExecuteExternalCode", line_of(code, m.start()), f"{m.group(1)}() runs arbitrary code; avoid, or use safe mode with a whitelist", path)
    for m in re.finditer(r"\b(УстановитьПривилегированныйРежим|SetPrivilegedMode)\s*\(\s*(Истина|True)", code, I):
        add("warn", "privileged_mode", "ITS 485", line_of(code, m.start()), "privileged mode: justify it, keep the scope minimal, switch it off in the same procedure", path)
    for m in re.finditer(r"(Пароль|Password|Токен|Token|Секрет|Secret)\s*=\s*\"[^\"]{4,}\"", code, I):
        add("error", "hardcoded_secret", "ITS 740; BSL LS UsingHardcodeSecretInformation", line_of(code, m.start()), "secret in code: store it in a safe storage (БезопасноеХранилищеДанных)", path)
    for m in re.finditer(r"(?<![\wА-Яа-яЁё.])(Сообщить|Message)\s*\(", code, I):
        add("info", "message_call", "БСП practice", line_of(code, m.start()), "Сообщить(): prefer ОбщегоНазначенияКлиентСервер.СообщитьПользователю (БСП) to bind messages to fields", path)
    for m in re.finditer(r"\b(Исключение|Except)\s*(//[^\n]*)?\s*\b(КонецПопытки|EndTry)\b", code, I):
        add("error", "empty_except", "ITS 499", line_of(code, m.start()), "empty exception handler hides errors: log (ЗаписьЖурналаРегистрации) and re-raise or handle", path)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*"); ap.add_argument("--query"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.query:
        check_query(pathlib.Path(a.query).read_text(encoding="utf-8-sig"), a.query)
    for p in a.paths:
        pp = pathlib.Path(p)
        files = [pp] if pp.is_file() else list(pp.rglob("*.bsl")) + list(pp.rglob("*.os"))
        for f in files:
            check_code(f.read_text(encoding="utf-8-sig", errors="replace"), str(f))
    if a.json:
        print(json.dumps(FIND, ensure_ascii=False, indent=2))
    else:
        for f in sorted(FIND, key=lambda x: (x["file"], x["line"])):
            mark = {"error": "✗", "warn": "!", "info": "·"}[f["level"]]
            print(f"{mark} {f['file']}:{f['line']} [{f['code']}] {f['message']}  ({f['std']})")
        e = sum(f["level"] == "error" for f in FIND)
        print(f"\n{e} error(s), {sum(f['level'] == 'warn' for f in FIND)} warning(s), {sum(f['level'] == 'info' for f in FIND)} note(s)")
    return 1 if any(f["level"] == "error" for f in FIND) else 0

if __name__ == "__main__":
    sys.exit(main())
