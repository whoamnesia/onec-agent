# BSL code: the rules an agent breaks most often

Standard numbers per BSL Language Server docs (2026-11-06); read the ITS text before quoting it.

## Client and server (ITS 439, 487, 703)
- Every procedure in a form module has a compilation directive: `&НаКлиенте`, `&НаСервере`,
  `&НаСервереБезКонтекста`, `&НаКлиентеНаСервереБезКонтекста`.
- Minimise server calls: one server call per user action that gets everything needed. Prefer
  `&НаСервереБезКонтекста` when the form's data is not needed (the form is not sent to the server).
- Never call the server in a loop on the client; never pass the whole form object when two values are enough.
- No modal windows and synchronous calls: use `ПоказатьВопрос`/`ВопросАсинх`, `ПоказатьПредупреждение`,
  `ОписаниеОповещения`, `Ждать` with async functions (8.3.18+).
- Common modules: name and flags by role — `…Сервер`, `…Клиент`, `…КлиентСервер`, `…ВызовСервера` (server call
  allowed), `…Повтисп` (cached). (ITS 469)

## Transactions and locks (ITS 460, 783)
- Explicit transaction pattern (nothing between НачатьТранзакцию and Попытка):
  ```
  НачатьТранзакцию();
  Попытка
  	// блокировка, чтение, запись
  	ЗафиксироватьТранзакцию();
  Исключение
  	ОтменитьТранзакцию();
  	ЗаписьЖурналаРегистрации(НСтр("ru = 'Обмен'"), УровеньЖурналаРегистрации.Ошибка,,, ПодробноеПредставлениеОшибки(ИнформацияОбОшибке()));
  	ВызватьИсключение;
  КонецПопытки;
  ```
- Managed lock mode (ITS 460). Lock **before** reading data you will change: `БлокировкаДанных` →
  `ЭлементБлокировкиДанных` with `Режим = РежимБлокировкиДанных.Исключительный` (or `Разделяемый` for read-only
  consistency), `ИсточникДанных` + `ИспользоватьИзИсточникаДанных` for a table of keys.
- Keep transactions short; no user interaction, no HTTP calls, no file I/O inside a transaction.
- Document posting already runs in a transaction; do not open another one in `ОбработкаПроведения`.

## Posting a document (pattern)
```
Процедура ОбработкаПроведения(Отказ, РежимПроведения)
	Движения.ТоварыНаСкладах.Записывать = Истина;

	Блокировка = Новый БлокировкаДанных;
	Элемент = Блокировка.Добавить("РегистрНакопления.ТоварыНаСкладах");
	Элемент.Режим = РежимБлокировкиДанных.Исключительный;
	Элемент.ИсточникДанных = Товары;
	Элемент.ИспользоватьИзИсточникаДанных("Номенклатура", "Номенклатура");
	Элемент.УстановитьЗначение("Склад", Склад);
	Блокировка.Заблокировать();

	Для Каждого Стр Из Товары Цикл
		Движение = Движения.ТоварыНаСкладах.ДобавитьРасход();
		Движение.Период = Дата;
		Движение.Склад = Склад;
		Движение.Номенклатура = Стр.Номенклатура;
		Движение.Количество = Стр.Количество;
	КонецЦикла;
	Движения.Записать();

	// контроль остатков после записи: одним запросом по всем строкам, без запросов в цикле
	Если РежимПроведения = РежимПроведенияДокумента.Оперативный Тогда
		ПроверитьОтрицательныеОстатки(Отказ);
	КонецЕсли;
КонецПроцедуры
```
(The loop builds records in memory only; the single query that checks balances runs after `Движения.Записать()`.)

## Errors and logging (ITS 498, 499)
- Never an empty `Исключение` block. Log with `ЗаписьЖурналаРегистрации` and re-raise, or handle meaningfully.
- Messages to users: `ОбщегоНазначения.СообщитьПользователю` / `ОбщегоНазначенияКлиентСервер.СообщитьПользователю`
  (БСП) to bind the message to a field; `НСтр("ru = '…'; en = '…'")` for every user-facing string.

## Security (ITS 485, 669, 740, 770)
- Privileged mode only where justified, smallest scope, switched off in the same procedure.
- No `Выполнить`/`Вычислить` on data from outside; if unavoidable, safe mode.
- No passwords or tokens in code: `ОбщегоНазначения.ЗаписатьДанныеВБезопасноеХранилище`.
- Check rights before actions on behalf of a user (`ПравоДоступа`, ITS 737).

## Vendor-supported configurations
Do not edit objects of a typical configuration that is "на поддержке": every edit makes vendor updates harder. Use an
extension (`&Перед`, `&После`, `&ИзменениеИКонтроль`, `&Вместо` on borrowed methods) or a separate subsystem.
