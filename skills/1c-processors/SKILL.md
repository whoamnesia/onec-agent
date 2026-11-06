---
name: 1c-processors
description: 'astudio external data processors and reports for 1C:Enterprise 8.3 (.epf / .erf): design, create the XML source, write the object and form modules, connect to БСП "Дополнительные отчёты и обработки" (СведенияОВнешнейОбработке), build the binary and dump it back to files with Designer batch commands, test on a copy, and keep sources in Git. Use for "внешняя обработка", "внешний отчёт", "epf", "erf", "собрать обработку", "загрузка данных обработкой", "печатная форма", "дополнительная обработка БСП".'
argument-hint: "[what it must do] [configuration and version]"
---

# astudio · External processors and reports

`<root>` = two levels above this skill's base dir. Build: `<root>/scripts/designer.py build-epf | dump-epf`.

## Workflow
1. **Spec**: what it does, for whom, input (file, selection), output (data changes, report, print form), where it is
   registered (БСП «Дополнительные отчёты и обработки» or opened via File → Open), rights needed.
2. **Source**: keep the processor as files (`dump-epf` of an existing one, or start from an empty processor created in
   the configurator and dumped). Folder: `src/epf/<Имя>/<Имя>.xml` + `Ext/ObjectModule.bsl` + `Forms/…`.
3. **BSP registration** (when the configuration has БСП): export function `СведенияОВнешнейОбработке()` in the object
   module using `ДополнительныеОтчетыИОбработки.СведенияОВнешнейОбработке(<версия БСП>)`: kind, version, safe mode,
   commands, purpose (objects for print forms and fill commands).
4. **Code**: form module UI only; data work in the object module on the server; queries by `1c-queries`; writes in
   transactions with locks by `1c-code`. Long operations through `ДлительныеОперации` (БСП).
5. **Check**: `bsl_check.py src/epf/<Имя>`.
6. **Build**: `designer.py build-epf --xml src/epf/<Имя>/<Имя>.xml --epf build/<Имя>.epf --base File=<empty or test base>`.
7. **Test on a copy**: run, check the result against data, run the failure case. For data-changing processors make a
   dry-run mode (show what would change) and default to it.
8. **Deliver**: `.epf/.erf`, sources, a short instruction for the user (where to open, what to fill, what happens).

## Rules
- Safe mode on when registering in БСП unless the processor needs files/COM/network; say why if it does.
- A processor that changes data logs what it changed (ЗаписьЖурналаРегистрации) and can be run twice without harm.
- No hardcoded paths, bases, users or passwords.
