---
name: 1c-queries
description: 'astudio 1C query language: write and optimise queries for 1C:Enterprise 8.3 - correct source (registers, virtual tables Остатки/Обороты/ОстаткиИОбороты/СрезПоследних, accounting registers), conditions in virtual-table parameters joined with И, temporary tables with ИНДЕКСИРОВАТЬ ПО, no queries in loops, no joins with subqueries, ЕСТЬNULL, ВЫРАЗИТЬ for composite types, РАЗРЕШЕННЫЕ, batch queries and DCS (СКД) - checked by a linter that cites ITS standards. Use for "запрос 1С", "язык запросов", "оптимизировать запрос", "медленный отчёт", "остатки на дату", "СКД", "1C query".'
argument-hint: "[what the query must return] [objects or XML dump path]"
---

# astudio · 1C queries

`<root>` = two levels above this skill's base dir. Rules and templates: `<root>/reference/query-language.md`.
Check: `<root>/scripts/bsl_check.py --query q.txt` or on the module.

## Workflow
1. **Restate** the question as data: which rows, which columns, at which moment or for which period, which filters,
   under which user (RLS → `РАЗРЕШЕННЫЕ`).
2. **Confirm names** with `meta_index.py --object` (registers: dimensions, resources, periodicity; documents: attributes
   and tabular sections). Never invent a name; if the dump is not available, ask for it or for the object's structure.
3. **Choose the source** (table in the reference §0). Balances → virtual table with the moment; history → turnovers;
   one document's records → the physical register table with `Регистратор`.
4. **Write** as a batch: input keys into an indexed temporary table → virtual tables filtered by parameters →
   final select. Russian keywords, one clause per line, aliases for every field, parameters `&…` (never string
   concatenation of values).
5. **Check** with `bsl_check.py`; fix every error.
6. **Run** on a test or read-only base (the user's console, `ИнструментыРазработчика`, or a read-only MCP). Show the row
   count and 3–5 sample rows; compare a total with a known figure (ОСВ, report from the configuration).
7. **Explain** the query in 3–5 lines for the user and list the standards it follows.

## DCS (СКД) notes
- Put virtual-table conditions in the parameters using `{ }` blocks so the composer can push user filters down:
  `РегистрНакопления.Продажи.Обороты(&НачалоПериода, &КонецПериода, , {(Номенклатура).* КАК Номенклатура})`.
- Resources are aggregated in the schema, not with СУММА in the query text, unless needed inside the query.
- Use `&НачалоПериода`/`&КонецПериода` with `КОНЕЦПЕРИОДА` handled by the period parameter's settings.

## Never
Queries in loops; joins with subqueries or unfiltered virtual tables; `ИЛИ` across different fields in ГДЕ when `В`
or a union works; `ПЕРВЫЕ` without `УПОРЯДОЧИТЬ`; dereference chains on composite fields without `ВЫРАЗИТЬ`; values
glued into the query text.
