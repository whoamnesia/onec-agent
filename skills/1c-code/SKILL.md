---
name: 1c-code
description: 'astudio BSL code for 1C:Enterprise 8.3 by the ITS standards: compilation directives and minimal server calls, asynchronous dialogs instead of modal ones, transactions in Попытка with ОтменитьТранзакцию and ВызватьИсключение, managed locks before reading changed data, document posting with register records and balance control, error logging, БСП messaging, safe storage of secrets, privileged mode - with a static checker. Use for "напиши код 1С", "процедура", "проведение документа", "модуль формы", "обработчик", "блокировки", "транзакция", "BSL код", "доработать 1С".'
argument-hint: "[what the code must do] [module path] [object]"
---

# astudio · BSL code

`<root>` = two levels above this skill's base dir. Rules and patterns: `<root>/reference/code-standards.md`.
Check: `<root>/scripts/bsl_check.py <module or folder>`; then BSL Language Server if installed (recommended:
the official `1c-syntax/claude-code-bsl-lsp` plugin for Claude Code).

## Workflow
1. Read the module and its object (`meta_index.py --object`). Find where the logic belongs: object module (data rules,
   posting), manager module (queries, print, functions without an instance), form module (UI only), common module
   (shared logic; server/client/call-server flags by name).
2. Reuse БСП and the configuration's own functions before writing new ones (search the dump for similar names).
3. Write the code: Russian identifiers in the configuration's style, `НСтр` for user strings, one procedure per
   responsibility, no magic constants (use `Перечисление`/`ПредопределенноеЗначение`).
4. Client/server: count server calls per user action (target: one). No server calls in loops.
5. Data changes: transaction pattern, managed lock before reading what you change, no dialogs inside transactions.
6. Run `bsl_check.py`; fix errors; explain any remaining warnings.
7. Test on a copy: the main case, an empty case, a case that must fail (insufficient balance, missing rights). Write
   down what you ran and what happened.

## Style
- Procedures ≤ ~60 lines; a comment block above exported methods: purpose, parameters, return value (БСП format).
- Areas: `#Область ПрограммныйИнтерфейс`, `#Область СлужебныйПрограммныйИнтерфейс`, `#Область СлужебныеПроцедурыИФункции`.
- Do not catch exceptions you cannot handle. Do not leave commented-out code.
