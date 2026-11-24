import os, glob, ast, py_compile
from datetime import datetime

BASE = os.path.expanduser("~/job-hunter")
EXPORT_PATHS = [
    "/sdcard/Download/job_hunter_full_export.txt",
    os.path.join(BASE, "latest_export.txt"),
]

def refresh_export(quiet=True):
    py_files = sorted(glob.glob(os.path.join(BASE, "**", "*.py"), recursive=True))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = [f"=== JOB-HUNTER LIVE CODE SNAPSHOT | Updated: {now} | Files: {len(py_files)} ===\n"]
    summary = []

    for f in py_files:
        rel = os.path.relpath(f, BASE)
        with open(f, encoding="utf-8", errors="replace") as _sf:
            src = _sf.read()
        issues = []
        try:
            tree = ast.parse(src)
            py_compile.compile(f, doraise=True)
        except Exception as e:
            issues.append(f"COMPILE_ERROR: {e}")
            tree = None

        if tree:
            with_opens = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.With):
                    for item in node.items:
                        if isinstance(item.context_expr, ast.Call) and getattr(item.context_expr.func, "id", "") == "open":
                            with_opens.add(id(item.context_expr))
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(f"L{node.lineno}: bare except")
                if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open" and id(node) not in with_opens:
                    issues.append(f"L{node.lineno}: unclosed open()")

        status = "CLEAN" if not issues else "; ".join(issues)
        summary.append(f"  [{status}] {rel} ({len(src.splitlines())} lines)")
        report.append(f"\n{'='*70}\nFILE: {rel} | STATUS: {status}\n{'='*70}\n")
        for idx, line in enumerate(src.splitlines(), 1):
            report.append(f"{idx:4d}: {line}\n")

    text = "".join(report)
    for out_p in EXPORT_PATHS:
        try:
            with open(out_p, "w", encoding="utf-8") as out:
                out.write(text)
        except Exception:
            pass

    if not quiet:
        print(f"[Sync] Refreshed export at {now} ({len(text)/1024:.1f} KB)")
        print("\n".join(summary))

if __name__ == "__main__":
    refresh_export(quiet=False)
