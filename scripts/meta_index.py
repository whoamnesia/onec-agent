#!/usr/bin/env python3
"""astudio-1c · meta_index.py — index a configuration dumped to XML files so the agent never
invents object, attribute or register names.

  python3 meta_index.py <dump dir>                         # summary by type
  python3 meta_index.py <dump dir> --object Документ.РеализацияТоваровУслуг
  python3 meta_index.py <dump dir> --find Контрагент       # where a name or type is used
  python3 meta_index.py <dump dir> --json > meta.json

<dump dir> is the output of  1cv8 DESIGNER ... /DumpConfigToFiles <dir>  (hierarchical format,
also ibcmd and EDT-exported Designer XML). Reads XML only; namespace-agnostic; writes nothing.
"""
import argparse, json, pathlib, re, sys, xml.etree.ElementTree as ET

RU = {"Catalog": "Справочник", "Document": "Документ", "AccumulationRegister": "РегистрНакопления",
      "InformationRegister": "РегистрСведений", "AccountingRegister": "РегистрБухгалтерии", "CalculationRegister": "РегистрРасчета",
      "Enum": "Перечисление", "ChartOfAccounts": "ПланСчетов", "ChartOfCharacteristicTypes": "ПланВидовХарактеристик",
      "ChartOfCalculationTypes": "ПланВидовРасчета", "BusinessProcess": "БизнесПроцесс", "Task": "Задача", "ExchangePlan": "ПланОбмена",
      "DataProcessor": "Обработка", "Report": "Отчет", "Constant": "Константа", "CommonModule": "ОбщийМодуль",
      "DocumentJournal": "ЖурналДокументов", "Subsystem": "Подсистема", "Role": "Роль", "HTTPService": "HTTPСервис", "WebService": "WebСервис",
      "CommonForm": "ОбщаяФорма", "ScheduledJob": "РегламентноеЗадание", "EventSubscription": "ПодпискаНаСобытие", "FunctionalOption": "ФункциональнаяОпция",
      "DefinedType": "ОпределяемыйТип", "Sequence": "Последовательность", "DocumentNumerator": "НумераторДокументов", "SessionParameter": "ПараметрСеанса"}

def local(tag): return tag.rsplit("}", 1)[-1]

def child(el, name):
    for c in el:
        if local(c.tag) == name: return c
    return None

def text_of(el, name):
    c = child(el, name) if el is not None else None
    return (c.text or "").strip() if c is not None and c.text else ""

def synonym(props):
    s = child(props, "Synonym") if props is not None else None
    if s is None: return ""
    for item in s.iter():
        if local(item.tag) == "content" and item.text: return item.text.strip()
    return ""

def types(props):
    t = child(props, "Type") if props is not None else None
    if t is None: return []
    out = []
    for x in t.iter():
        if local(x.tag) in ("Type", "TypeSet") and x.text and x is not t:
            v = x.text.strip()
            v = re.sub(r"^cfg:", "", v).replace("CatalogRef.", "СправочникСсылка.").replace("DocumentRef.", "ДокументСсылка.").replace("EnumRef.", "ПеречислениеСсылка.")
            v = {"xs:string": "Строка", "xs:decimal": "Число", "xs:boolean": "Булево", "xs:dateTime": "Дата"}.get(v, v)
            out.append(v)
    return out

def fields(container, kinds=("Attribute", "Dimension", "Resource", "AddressingAttribute", "AccountingFlag", "ExtDimensionAccountingFlag")):
    res = []
    for el in container:
        k = local(el.tag)
        if k in kinds:
            p = child(el, "Properties")
            res.append({"kind": k, "name": text_of(p, "Name"), "synonym": synonym(p), "type": types(p)})
    return res

def parse(f):
    root = ET.parse(f).getroot()
    obj = next((c for c in root if local(c.tag) in RU), None)
    if obj is None: return None
    kind = local(obj.tag); props = child(obj, "Properties"); kids = child(obj, "ChildObjects")
    o = {"type": kind, "ru": RU[kind], "name": text_of(props, "Name"), "synonym": synonym(props), "file": str(f)}
    if kids is not None:
        o["fields"] = fields(kids)
        o["tabular_sections"] = []
        for ts in kids:
            if local(ts.tag) == "TabularSection":
                p = child(ts, "Properties"); tk = child(ts, "ChildObjects")
                o["tabular_sections"].append({"name": text_of(p, "Name"), "synonym": synonym(p), "fields": fields(tk) if tk is not None else []})
        vals = [text_of(child(v, "Properties"), "Name") for v in kids if local(v.tag) == "EnumValue"]
        if vals: o["values"] = vals
    if props is not None:
        rr = child(props, "RegisterRecords")
        if rr is not None:
            o["register_records"] = [x.text.strip() for x in rr.iter() if x is not rr and x.text and x.text.strip()]
        for flag in ("Posting", "RegisterType", "Periodicity", "WriteMode", "Hierarchical", "CodeLength", "DescriptionLength", "Owners"):
            v = child(props, flag)
            if v is not None:
                o[flag] = (v.text or "").strip() or [x.text.strip() for x in v.iter() if x is not v and x.text and x.text.strip()]
    return o

def load(d):
    out = []
    for f in sorted(pathlib.Path(d).rglob("*.xml")):
        if f.name in ("Configuration.xml", "ConfigDumpInfo.xml") or "Ext" in f.parts or "Forms" in f.parts or "Templates" in f.parts:
            continue
        try:
            o = parse(f)
        except ET.ParseError:
            continue
        if o and o["name"]: out.append(o)
    return out

def show(o):
    print(f"{o['ru']}.{o['name']}  «{o['synonym']}»")
    for k in ("Posting", "RegisterType", "Periodicity", "WriteMode", "Hierarchical", "Owners"):
        if o.get(k): print(f"  {k}: {o[k]}")
    if o.get("register_records"): print("  Движения: " + ", ".join(o["register_records"]))
    if o.get("values"): print("  Значения: " + ", ".join(o["values"]))
    for f in o.get("fields", []):
        print(f"  {f['kind']:<10} {f['name']:<32} {', '.join(f['type'])}")
    for ts in o.get("tabular_sections", []):
        print(f"  ТЧ {ts['name']}  «{ts['synonym']}»")
        for f in ts["fields"]: print(f"     {f['name']:<30} {', '.join(f['type'])}")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir"); ap.add_argument("--object"); ap.add_argument("--find"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    objs = load(a.dir)
    if a.json:
        print(json.dumps(objs, ensure_ascii=False, indent=1)); return 0
    if a.object:
        t, _, n = a.object.partition(".")
        hit = [o for o in objs if o["name"].lower() == n.lower() and t.lower() in (o["ru"].lower(), o["type"].lower())]
        if not hit: print(f"нет объекта {a.object} в выгрузке — не выдумывайте имя, найдите его через --find"); return 1
        for o in hit: show(o)
        return 0
    if a.find:
        q = a.find.lower()
        for o in objs:
            if q in o["name"].lower() or q in o["synonym"].lower(): print(f"{o['ru']}.{o['name']}  «{o['synonym']}»")
            for f in o.get("fields", []):
                if q in f["name"].lower() or any(q in t.lower() for t in f["type"]): print(f"  {o['ru']}.{o['name']}.{f['name']}  ({', '.join(f['type'])})")
            for ts in o.get("tabular_sections", []):
                for f in ts["fields"]:
                    if q in f["name"].lower() or any(q in t.lower() for t in f["type"]): print(f"  {o['ru']}.{o['name']}.{ts['name']}.{f['name']}  ({', '.join(f['type'])})")
        return 0
    from collections import Counter
    c = Counter(o["ru"] for o in objs)
    print(f"{len(objs)} объектов в {a.dir}")
    for k, v in c.most_common(): print(f"  {k:<28} {v}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
