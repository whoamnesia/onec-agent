---
name: 1c-explain
description: 'astudio explanation of what is happening in a 1C base for non-programmers: why a balance, debt or report figure is what it is, which documents formed it, what a document does when posted, who changed what (event log), why a user cannot see data (rights and RLS) - investigated read-only with metadata, code, queries and the event log, and answered in plain words with the evidence. Use for "почему такой остаток", "откуда эта сумма", "что делает этот документ", "кто изменил документ", "почему пользователь не видит", "объясни, что происходит в базе 1С".'
argument-hint: "[the question in the user's words] [base access: read-only]"
---

# astudio · Explain the base

`<root>` = two levels above this skill's base dir. Read-only always. Query rules: `<root>/reference/query-language.md`.

## Workflow
1. **Restate** the question with numbers: object, date, expected vs actual ("остаток товара «Чайник» на складе
   «Основной» на 31.10: в отчёте 5, по факту 8").
2. **Trace the figure**: which report → which register and resource → which documents wrote to it in the period
   (physical register table `ГДЕ Регистратор …`, or the configuration's «Движения документа»).
3. **Query** read-only: balances at the start, turnovers by recorder in the period, balances at the end; find the
   records that explain the gap (unposted documents, wrong warehouse or date, reversal, re-posting after the period).
4. **Who and when**: the event log (Журнал регистрации) filtered by object and period; for documents also the
   version history if the configuration keeps it (БСП «Версионирование объектов»).
5. **Rights**: if a user sees less, compare roles and RLS of the two users; do not grant rights yourself.
6. **Answer** in plain words, then the evidence:
   - one-paragraph answer;
   - a table of the documents that explain the figure (date, number, type, amount, effect);
   - what to do (and who should do it: accountant, administrator, developer);
   - the queries used, so a specialist can repeat them.

## Rules
- Do not change anything while investigating: no re-posting, no corrections. Propose them; a person decides.
- Mask personal data in the answer unless the user needs it.
- If you have no access to data, give the exact steps or queries for the user to run and ask for the results.
