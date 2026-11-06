# ITS development standards most used by astudio-1c

Numbers and titles from its.1c.ru page titles and BSL Language Server diagnostic docs (checked 2026-11-06).
The standards' texts are on its.1c.ru/db/v8std (ITS subscription); verify the wording before quoting.

| № | Title (short) | BSL LS diagnostics |
|---|---|---|
| 412 | Упорядочивание результатов запроса | SelectTopWithoutOrderBy |
| 434 | ОБЪЕДИНИТЬ и ОБЪЕДИНИТЬ ВСЕ | UnionAll |
| 435 | ПОЛНОЕ ВНЕШНЕЕ СОЕДИНЕНИЕ | FullOuterJoinQuery |
| 436 | Многократное выполнение однотипных запросов (запросы в цикле) | CreateQueryInCycle |
| 437 | Оформление текстов запросов | — |
| 439 | Директивы компиляции и инструкции препроцессора | CompilationDirectiveLost |
| 455 / 456 | Структура модуля / Тексты модулей | CodeOutOfRegion |
| 460 | Использование управляемого режима блокировки | — |
| 469 | Правила создания общих модулей | CommonModuleNameServerCall и др. |
| 485 | Использование привилегированного режима | SetPrivilegedMode |
| 487 | Минимизация количества серверных вызовов | ServerCallsInFormEvents |
| 498 | Использование Журнала регистрации | — |
| 499 | Перехват исключений в коде | — |
| 654 | Разыменование ссылочных полей составного типа | QueryNestedFieldsByDot, RefOveruse |
| 655 | Соединения с вложенными запросами и виртуальными таблицами | JoinWithSubQuery, JoinWithVirtualTable |
| 656 | Вложенные запросы в условии соединения | — |
| 657 | Обращения к виртуальным таблицам | VirtualTableCallWithoutParameters |
| 658 | Эффективные условия запросов | LogicalOrInTheWhereSectionOfQuery |
| 669 / 770 | Выполнение «внешнего» кода, Выполнить и Вычислить на сервере | ExecuteExternalCode |
| 703 | Модальные окна и синхронные вызовы | UsingModalWindows, UsingSynchronousCalls |
| 726 | Оператор ПОДОБНО | UsingLikeInQuery |
| 733 | Эффективное обращение к виртуальной таблице «Остатки» | VirtualTableCallWithoutParameters |
| 737 | Проверка прав доступа | — |
| 740 | Безопасное хранение паролей | UsingHardcodeSecretInformation |
| 783 | Транзакции: правила использования | BeginTransactionBeforeTryCatch, CommitTransactionOutsideTryCatch, PairingBrokenTransaction |

BSL Language Server (1c-syntax, LGPL-3.0) has about 190 diagnostics; suppress one in code with `// BSLLS:Ключ-выкл`.
