#!/usr/bin/env python3
"""Convert Simplified Chinese in the firmware source tree to Traditional
(Taiwan, OpenCC s2tw) in place, right before the zh_CN firmware build.

Only CJK code points are remapped; ASCII (identifiers, format specifiers,
escape sequences, paths) is left byte-for-byte unchanged, so converting a
whole source file is safe. Run from the repository root.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zhconv import S2TW

# (root, (extensions...))  -- only these files under each root are touched.
RULES = (
    ("applications", (".c", ".h", ".cpp", ".hpp", ".cc", ".fam")),
    ("lib", (".c", ".h", ".cpp", ".hpp", ".cc")),
    ("furi", (".c", ".h", ".cpp", ".hpp", ".cc")),
    ("targets", (".c", ".h", ".cpp", ".hpp", ".cc")),
    ("localization", (".json",)),
)
# assets/dolphin animation captions live in meta.txt files.
DOLPHIN_ROOT = "assets/dolphin"


def has_cjk(text):
    return any("㐀" <= c <= "鿿" or "豈" <= c <= "﫿" for c in text)


def convert_file(cc, path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (UnicodeDecodeError, OSError):
        return False
    if not has_cjk(text):
        return False
    converted = cc.convert(text)
    if converted == text:
        return False
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(converted)
    return True


def main():
    repo = os.getcwd()
    cc = S2TW()
    changed = 0
    scanned = 0
    for root, exts in RULES:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(exts):
                    scanned += 1
                    if convert_file(cc, os.path.join(dirpath, name)):
                        changed += 1
    dolphin = os.path.join(repo, DOLPHIN_ROOT)
    if os.path.isdir(dolphin):
        for dirpath, _dirs, files in os.walk(dolphin):
            for name in files:
                if name == "meta.txt":
                    scanned += 1
                    if convert_file(cc, os.path.join(dirpath, name)):
                        changed += 1
    print(f"[zh_tw_convert] scanned {scanned} files, converted {changed}")


if __name__ == "__main__":
    main()
