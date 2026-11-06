# 1C query language: rules that matter

Every rule names the ITS development standard (its.1c.ru/db/v8std) or the BSL Language Server diagnostic that
implements it. Standard numbers were taken from the BSL LS documentation and ITS page titles on 2026-11-06; read the
standard itself on ITS before quoting its wording to a client.

## 0. Before the first ВЫБРАТЬ
1. Confirm every object, attribute, dimension and resource name in the metadata (`scripts/meta_index.py --object …`
   or the live base). Never invent names.
2. Pick the right source; a wrong source is a design defect, not a tuning problem:
   | Question | Source |
   |---|---|
   | balance at a moment | `РегистрНакопления.X.Остатки(&Момент, <условие>)` |
   | turnover for a period | `РегистрНакопления.X.Обороты(&Начало, &Конец, <периодичность>, <условие>)` |
   | opening, receipts, issues, closing | `…ОстаткиИОбороты(&Начало, &Конец, <периодичность>, <метод дополнения>, <условие>)` |
   | latest value of a periodic info register | `РегистрСведений.X.СрезПоследних(&Период, <условие>)` (periodic registers only) |
   | accounting balance / turnover | `РегистрБухгалтерии.X.Остатки(&Момент, <счета>, <виды субконто>, <условие>)`, `.Обороты(…)`, `.ОборотыДтКт(…)` |
   | the records of one document | `РегистрНакопления.X` (real table) `ГДЕ Регистратор = &Документ` |
3. Look for a proven pattern in the configuration (БСП and typical modules) before writing a new one.

## 1. Virtual tables (ITS 657, 733)
- All conditions on the table go into its **parameters**, not into ГДЕ:
  ✓ `РегистрНакопления.ТоварыНаСкладах.Остатки(&Момент, Склад = &Склад И Номенклатура В (&Товары)) КАК Ост`
  ✗ `…Остатки(&Момент) КАК Ост ГДЕ Ост.Склад = &Склад`
- The condition is **one parameter**: predicates inside it are joined with **И**. A comma starts the next parameter:
  ✗ `Остатки(&Момент, Склад = &Склад, Номенклатура = &Номенклатура)`
- Conditions on resources (`КоличествоОстаток > 0`) stay in ГДЕ or ИМЕЮЩИЕ: the parameter filters records before totals.
- Resource fields are derived names: `<Ресурс>Остаток`, `<Ресурс>Оборот`, `<Ресурс>Приход`, `<Ресурс>Расход`,
  `<Ресурс>НачальныйОстаток`, `<Ресурс>КонечныйОстаток`.

## 2. Joins (ITS 655, 656)
- Join only tables of metadata objects and temporary tables. A subquery or a virtual table in a join → put it into a
  temporary table (`ПОМЕСТИТЬ ВТ_…`) first.
- Index a temporary table that is joined and can be large: `ИНДЕКСИРОВАТЬ ПО <ключи соединения>`.
- No subqueries in the join condition.
- Fields from the outer side of ЛЕВОЕ/ПРАВОЕ/ПОЛНОЕ joins can be NULL: wrap them in `ЕСТЬNULL(…, 0)` or check `ЕСТЬ NULL`.

## 3. Conditions and dereferencing (ITS 654, 658, 726)
- Every dot after a reference field is an implicit join; for composite types it is a join per type. Read only the
  fields you need, cast composite fields: `ВЫРАЗИТЬ(Т.Регистратор КАК Документ.РеализацияТоваровУслуг).Контрагент`.
- `Поле.Ссылка` on a reference field adds a join and nothing else.
- `ИЛИ` in ГДЕ can stop the DBMS from using an index: use `В (&Список)` or split into parts with `ОБЪЕДИНИТЬ ВСЕ`.
- `ПОДОБНО "%…"` with a leading % cannot use an index.
- Use `ПРЕДСТАВЛЕНИЕ(Поле)` for display, not a dereference to Наименование.

## 4. Results (ITS 412, 434)
- `ПЕРВЫЕ N` is the only row limit; without `УПОРЯДОЧИТЬ ПО` it returns arbitrary rows.
- `ОБЪЕДИНИТЬ` removes duplicates (slower); `ОБЪЕДИНИТЬ ВСЕ` keeps them. No `РАЗЛИЧНЫЕ` inside union parts unless needed.
- `ВЫБРАТЬ РАЗРЕШЕННЫЕ` when the query serves a user under record-level security (RLS) — otherwise the user gets an
  access error instead of a filtered result.
- Constants of the configuration: `ЗНАЧЕНИЕ(Перечисление.СтатусыЗаказов.Закрыт)`, `ЗНАЧЕНИЕ(Справочник.Склады.ПустаяСсылка)`.

## 5. Performance (ITS 436)
- **No queries in loops.** Collect keys first, then one query with `В (&Ключи)` or a join with a temporary table built
  from a value table (`ИЗ &ТаблицаЗначений КАК Т` → `ПОМЕСТИТЬ`).
- Use a batch query (`ПакетЗапросов`) with temporary tables instead of several round trips.
- Period parameters as dates with boundaries: `&НачалоПериода`, `КОНЕЦПЕРИОДА(&Дата, ДЕНЬ)`, or `Новый Граница(…)`.

## Template: stock for a document's lines
```
ВЫБРАТЬ
	Т.Номенклатура КАК Номенклатура,
	СУММА(Т.Количество) КАК Количество
ПОМЕСТИТЬ ВТ_Товары
ИЗ
	&Товары КАК Т
СГРУППИРОВАТЬ ПО
	Т.Номенклатура
ИНДЕКСИРОВАТЬ ПО
	Номенклатура
;
////////////////////////////////////////////////////////////////////////////////
ВЫБРАТЬ
	ВТ.Номенклатура КАК Номенклатура,
	ВТ.Количество КАК Нужно,
	ЕСТЬNULL(Ост.КоличествоОстаток, 0) КАК Есть
ИЗ
	ВТ_Товары КАК ВТ
		ЛЕВОЕ СОЕДИНЕНИЕ РегистрНакопления.ТоварыНаСкладах.Остатки(
				&Момент,
				Склад = &Склад
					И Номенклатура В
						(ВЫБРАТЬ ВТ_Товары.Номенклатура ИЗ ВТ_Товары)) КАК Ост
		ПО ВТ.Номенклатура = Ост.Номенклатура
ГДЕ
	ЕСТЬNULL(Ост.КоличествоОстаток, 0) < ВТ.Количество
```
(The virtual table is filtered by its parameter with a subquery on an indexed temporary table — the pattern ITS
recommends instead of joining an unfiltered virtual table.)
