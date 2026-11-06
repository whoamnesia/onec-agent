---
name: 1c-extensions
description: 'astudio configuration extensions (.cfe) for typical 1C configurations on vendor support: borrow objects, add attributes and forms, intercept methods with &Перед, &После, &Вместо and &ИзменениеИКонтроль, keep the typical configuration updatable, check compatibility after vendor updates, and dump/load extensions with Designer. Use for "расширение 1С", "доработать типовую", "не снимая с поддержки", "cfe", "заимствовать объект", "перехват метода".'
argument-hint: "[change needed] [typical configuration and version]"
---

# astudio · Extensions

`<root>` = two levels above this skill's base dir. Dump/load: `<root>/scripts/designer.py dump-ext | load-ext`.

## Why
Editing a vendor-supported typical configuration makes every vendor update a manual merge. An extension keeps the
typical configuration intact and survives updates when it is written carefully.

## Workflow
1. Confirm the configuration is on support and its version; find the exact typical method to change (dump + search).
2. Choose the interception:
   | Need | Annotation |
   |---|---|
   | add actions before/after typical logic | `&Перед("Метод")`, `&После("Метод")` |
   | change a few lines inside a method | `&ИзменениеИКонтроль("Метод")` with `#Вставка`/`#Удаление` (the platform warns when the vendor changes the method) |
   | replace the method completely | `&Вместо("Метод")`, call `ПродолжитьВызов()` if the typical logic must still run — last resort |
3. Borrow only what you need; own attributes and forms get the extension prefix (e.g. `аст_`).
4. Set the extension's purpose (Исправление / Адаптация / Дополнение) and safe mode according to its needs.
5. Check, build into a test copy (`load-ext … --test-base`), test the typical scenario and yours.
6. After each vendor update: run the configurator's extension compatibility check; `&ИзменениеИКонтроль` breaks
   loudly by design — fix the insertion, do not switch to `&Вместо`.
