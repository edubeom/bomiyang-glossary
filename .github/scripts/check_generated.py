#!/usr/bin/env python3
"""CI: after `generate_glossary.py generate`, the generated files must equal the committed ones.

Only the build time differs between runs (GLOSSARY.md '> 생성:' line, terms*.json "generated_at" and the
"checksum" that covers it) -- those lines are ignored. Any other difference means the dictionary was
changed without regenerating (or generate is no longer deterministic). Exit 1 with the file list.
"""
import re
import subprocess
import sys

VOLATILE = re.compile(r'^\s*(> 생성: |"generated_at": |"checksum": )')


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def stable(text: str) -> list:
    return [line for line in text.replace("\r", "").split("\n") if not VOLATILE.match(line)]


def main() -> int:
    changed = [p for p in git("diff", "--name-only", "-z").decode("utf-8").split("\0") if p]
    new = [p for p in git("ls-files", "--others", "--exclude-standard", "-z").decode("utf-8").split("\0") if p]
    bad = []
    for path in changed:
        old = git("show", f"HEAD:{path}").decode("utf-8", "replace")
        with open(path, encoding="utf-8", errors="replace") as fh:
            cur = fh.read()
        if stable(old) != stable(cur):
            bad.append(path)
    bad += new
    if bad:
        for path in bad:
            print(f"::error file={path}::generated file differs from the commit -- run `python generate_glossary.py generate` and commit")
        print("FAIL: generated files are out of date: " + ", ".join(bad))
        return 1
    print(f"OK: generated files match ({len(changed)} differ only in build time)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
