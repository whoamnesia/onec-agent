#!/usr/bin/env python3
"""astudio-1c · designer.py — build (and optionally run) 1C Designer batch commands safely.

  python3 designer.py dump-config  --base File=C:/bases/test --out src/cf
  python3 designer.py dump-ext     --base File=C:/bases/test --ext МоёРасширение --out src/cfe
  python3 designer.py build-epf    --xml src/epf/Отчёт/Отчёт.xml --epf build/Отчёт.epf --base File=C:/bases/empty
  python3 designer.py dump-epf     --epf Отчёт.epf --out src/epf --base File=C:/bases/empty
  python3 designer.py load-config  --base File=C:/bases/test --src src/cf --test-base   (+ --update-db)
  python3 designer.py check-config --base File=C:/bases/test

Prints the command by default; --run executes it and shows the /Out log. Rules built in:
- one batch command per Designer call (Designer runs only the LAST batch command on a line);
- commands that change a base (load-config, load-ext, update-db) refuse to run without --test-base,
  which you pass only for a test copy, never for production;
- the password comes from the V8_PASSWORD environment variable and is masked in output;
- platform: --v8 path or V8_PATH (e.g. "C:/Program Files/1cv8/8.3.25.1374/bin/1cv8.exe").
--base accepts File=<dir> or Srvr=<server>;Ref=<base>.
"""
import argparse, os, shlex, subprocess, sys, tempfile, pathlib

def base_args(base, user):
    if base.startswith("File="): a = ["/F", base[5:]]
    elif base.startswith("Srvr="):
        srv, _, ref = base[5:].partition(";Ref=")
        a = ["/S", f"{srv}\\{ref}"]
    else: sys.exit("--base must be File=<dir> or Srvr=<server>;Ref=<base>")
    if user: a += ["/N", user]
    if os.environ.get("V8_PASSWORD"): a += ["/P", os.environ["V8_PASSWORD"]]
    return a

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["dump-config", "dump-ext", "build-epf", "dump-epf", "load-config", "load-ext", "update-db", "check-config"])
    ap.add_argument("--base", required=True); ap.add_argument("--user", default=os.environ.get("V8_USER", ""))
    ap.add_argument("--out"); ap.add_argument("--src"); ap.add_argument("--ext"); ap.add_argument("--xml"); ap.add_argument("--epf")
    ap.add_argument("--update-db", action="store_true"); ap.add_argument("--test-base", action="store_true")
    ap.add_argument("--v8", default=os.environ.get("V8_PATH", "1cv8")); ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    mutating = a.cmd in ("load-config", "load-ext", "update-db")
    if mutating and not a.test_base:
        sys.exit("refused: this changes the base. Work on a test copy and pass --test-base (never production).")
    log = str(pathlib.Path(tempfile.gettempdir()) / "astudio-1c-designer.log")
    c = [a.v8, "DESIGNER"] + base_args(a.base, a.user) + ["/DisableStartupDialogs", "/DisableStartupMessages"]
    if a.cmd == "dump-config": c += ["/DumpConfigToFiles", a.out or sys.exit("--out"), "-Format", "Hierarchical"]
    elif a.cmd == "dump-ext": c += ["/DumpConfigToFiles", a.out or sys.exit("--out"), "-Extension", a.ext or sys.exit("--ext"), "-Format", "Hierarchical"]
    elif a.cmd == "build-epf": c += ["/LoadExternalDataProcessorOrReportFromFiles", a.xml or sys.exit("--xml"), a.epf or sys.exit("--epf")]
    elif a.cmd == "dump-epf": c += ["/DumpExternalDataProcessorOrReportToFiles", a.out or sys.exit("--out"), a.epf or sys.exit("--epf"), "-Format", "Hierarchical"]
    elif a.cmd == "load-config": c += ["/LoadConfigFromFiles", a.src or sys.exit("--src")]
    elif a.cmd == "load-ext": c += ["/LoadConfigFromFiles", a.src or sys.exit("--src"), "-Extension", a.ext or sys.exit("--ext")]
    elif a.cmd == "update-db": c += ["/UpdateDBCfg"]
    elif a.cmd == "check-config": c += ["/CheckConfig", "-ConfigLogIntegrity", "-IncorrectReferences", "-Server", "-ThinClient", "-WebClient", "-ExternalConnection"]
    c += ["/Out", log]
    shown = " ".join("****" if (i > 0 and c[i - 1] == "/P") else shlex.quote(x) for i, x in enumerate(c))
    print(shown)
    if a.cmd == "load-config" and a.update_db:
        print("then: python3 designer.py update-db --base … --test-base   (separate call: one batch command per run)")
    if not a.run:
        print("(not run: add --run to execute)"); return 0
    r = subprocess.run(c)
    if os.path.exists(log):
        print(open(log, encoding="utf-8-sig", errors="replace").read()[-4000:])
    print("exit code", r.returncode)
    return r.returncode

if __name__ == "__main__":
    sys.exit(main())
