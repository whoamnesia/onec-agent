---
name: 1c-review
description: 'astudio code review for 1C: static checks (bsl_check.py plus BSL Language Server diagnostics), a checklist by ITS standards (queries, transactions and locks, client-server calls, modal calls, security, extensions vs vendor objects, БСП usage), impact on posting and rights, and a findings report with severity and fixes. Use for "проверь код 1С", "ревью доработки", "code review 1С", "проверь обработку", "найди ошибки в модуле".'
argument-hint: "[path to modules / diff]"
---

# astudio · 1C code review

`<root>` = two levels above this skill's base dir. Map of standards: `<root>/reference/standards-map.md`.

## Steps
1. `bsl_check.py <changed modules>`; if BSL LS is installed, add its diagnostics.
2. Checklist (each finding: file:line, standard, why it matters, fix):
   - queries: source, virtual-table parameters, joins, loops, `РАЗРЕШЕННЫЕ`, `ПЕРВЫЕ`+order;
   - data changes: transaction pattern, managed locks before reads, posting writes all registers it should, balance control;
   - client/server: directives, server calls per action, no server calls in loops, no modal/sync calls;
   - security: privileged mode, `Выполнить`, secrets, rights checks, external data validation;
   - maintainability: vendor objects edited directly?, БСП reused?, `НСтр`, areas, comments on exported methods;
   - impact: which documents, registers, reports, exchanges and roles are affected.
3. Severity: **blocker** (data corruption, wrong totals, security), **major** (performance, update-ability), **minor** (style).
4. Report: summary, findings table sorted by severity, what was not checked (no base, no BSL LS), suggested tests.
