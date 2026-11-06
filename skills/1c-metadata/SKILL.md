---
name: 1c-metadata
description: 'astudio 1C configuration metadata: dump a configuration or extension to XML files (Designer /DumpConfigToFiles, ibcmd, EDT), index it, and read it correctly - catalogs, documents and their register records, accumulation (balance vs turnover), information (periodic, subordinate to recorder), accounting and calculation registers, enums, characteristic types, subsystems, roles and RLS - and keep the dump in Git. Use for "выгрузить конфигурацию", "структура конфигурации", "какие реквизиты у документа", "куда пишет документ", "метаданные 1С", "XML выгрузка", "1C metadata".'
argument-hint: "[base or dump path] [object]"
---

# astudio · 1C metadata

`<root>` = two levels above this skill's base dir. Tools: `<root>/scripts/designer.py` (dump), `<root>/scripts/meta_index.py` (index).

## Get the files
- Preferred: the team's Git repository with the configuration XML (Designer hierarchical format or EDT project).
- Otherwise dump from a **test copy**: `designer.py dump-config --base File=… --out src/cf` (extensions: `dump-ext`).
  Designer executes only the last batch command on a command line, so one operation per call.
- Commit the dump to Git; diffs of XML are the change log the team can review.

## Read it
- `meta_index.py src/cf` — what is there; `--object Документ.X` — attributes, tabular sections, posting, register
  records; `--find Контрагент` — where a name or a type is used.
- Object types to know:
  | Type | What to remember |
  |---|---|
  | Справочник | reference data; hierarchy, owners, predefined items |
  | Документ | `Проведение` allowed or not; `RegisterRecords` = registers it writes on posting |
  | РегистрНакопления | balance type → `Остатки`, `ОстаткиИОбороты`; turnover type → only `Обороты` |
  | РегистрСведений | periodic (СрезПоследних/СрезПервых) or not; independent or subordinate to a recorder |
  | РегистрБухгалтерии | chart of accounts, subdimensions (субконто), `ОборотыДтКт` |
  | ПланВидовХарактеристик | additional attributes and subdimension types |
  | Роль | rights and RLS templates: why a user sees fewer rows |
- Modules live next to the XML: `Ext/ObjectModule.bsl`, `Ext/ManagerModule.bsl`, `Forms/<Форма>/Ext/Form/Module.bsl`.

## Explain to a person
Draw the path: document → its register records → the register → the report that reads it. Name objects by synonym
and by name ("документ «Реализация товаров и услуг» (Документ.РеализацияТоваровУслуг)").
