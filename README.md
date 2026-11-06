# astudio-1c — 1C:Enterprise 8.3 agent for Claude Code

**English** · [Русский](README.ru.md)

Author: **astudio.one** — [astudio.one](https://astudio.one) · License: MIT · Version 1.0.0

A plugin that makes an agent a careful 1C architect: it reads the configuration from its XML dump instead of guessing names, writes queries and BSL code by the ITS development standards, builds external data processors and reports, changes typical configurations only through extensions, and explains to non-programmers why a figure in the base is what it is. Live bases are read-only; changes happen on a test copy after the user agrees.

## What it does

- Work modes: explain, query, quick fix, full cycle, processor, extension, review — with escalation to the full cycle when posting, transactions or rights are touched
- Configuration index from a Designer/EDT XML dump: objects, attributes, tabular sections, register records — no invented names
- Query rules with ITS references: virtual-table parameters joined with И, indexed temporary tables, no queries in loops, no joins with subqueries
- BSL patterns: client/server, async dialogs, transactions, managed locks, posting with balance control, logging, security
- External processors and reports (.epf/.erf) with БСП registration, built and dumped by Designer batch commands
- Extensions with &Перед/&После/&ИзменениеИКонтроль instead of editing vendor objects
- Plain-language investigation of balances, debts and report figures, event log and rights — read-only

## Install

In Claude Code:

```
/plugin marketplace add whoamnesia/astudio-1c
/plugin install astudio-1c@astudio-1c
```

Restart Claude Code. Skills appear in the `/` menu as `astudio-1c:astudio-1c` …

Pinned install (what aiocenter.ru does): clone the repository, check out the published commit, then `/plugin marketplace add ~/.aiocenter/packages/astudio-1c`.

Other agents (Cursor, Codex, Gemini CLI): every skill is a plain `skills/<name>/SKILL.md` with references; point the agent at the folder or copy it into the agent's rules.

## Skills

| Skill | What it does |
|---|---|
| `astudio-1c` | Main skill: mode selection, ground truth from metadata, safety rules, deliverable |
| `1c-queries` | Queries and DCS by the ITS standards, with a linter |
| `1c-code` | BSL modules: client/server, transactions, locks, posting |
| `1c-metadata` | Dump, index and read configuration metadata |
| `1c-processors` | External processors and reports, БСП registration, build |
| `1c-extensions` | Extensions for vendor-supported configurations |
| `1c-explain` | Explain balances, figures, posting, event log and rights to a user |
| `1c-review` | Code review by the ITS checklist |

## Tools

Python 3.9+, standard library only. They read what you pass them and write nothing unless you redirect the output.

| Script | Purpose |
|---|---|
| `scripts/meta_index.py` | Index of an XML configuration dump: summary, object card, name search |
| `scripts/bsl_check.py` | Static checks of queries and BSL code with ITS references |
| `scripts/designer.py` | Designer batch commands with safety rails (one command per run, --test-base for changes, masked password) |

## Safety

- Production bases are read-only: queries only, no writes, posting or deletion.
- designer.py refuses to load a configuration or update a database without --test-base; one batch command per run.
- Never edits vendor-supported objects directly; extensions instead.
- Credentials only from environment variables; personal data masked in reports; execution results are never invented.

## Layout

```
astudio-1c/
  .claude-plugin/plugin.json, marketplace.json
  skills/<8 skills>/SKILL.md
  reference/   query-language.md · code-standards.md · standards-map.md
  scripts/     meta_index.py · bsl_check.py · designer.py
  README.md · README.ru.md · LICENSE · NOTICE.md
```

## Training track

This plugin is the package of the aiocenter.ru track «Агент для 1С»: digests, agent memo and an exam with a signed certificate — https://aiocenter.ru/tracks/onec-agent/

## Credits

Built by astudio.one on ideas from the best open-source projects in this field; see [NOTICE.md](NOTICE.md) for sources and licences.
