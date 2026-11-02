#!/usr/bin/env python3
"""Self-contained OpenCC s2tw (Simplified -> Traditional, Taiwan variants).
Forward maximum-matching over STPhrases+STCharacters, then TWVariants chars.
Dictionaries are the OpenCC project data files placed next to this script."""
import os, sys

_DIR = os.path.dirname(os.path.abspath(__file__))

def _load(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            k, v = line.split("\t", 1)
            d[k] = v.split(" ")[0].strip()
    return d

class S2TW:
    def __init__(self, dict_dir=None):
        dd = dict_dir or os.path.join(_DIR, "dict")
        self.phrases = _load(os.path.join(dd, "STPhrases.txt"))
        self.chars = _load(os.path.join(dd, "STCharacters.txt"))
        self.tw = _load(os.path.join(dd, "TWVariants.txt"))
        self.maxlen = max(len(k) for k in self.phrases)

    def _s2t(self, text):
        out = []
        i = 0
        n = len(text)
        ph = self.phrases
        ch = self.chars
        ml = self.maxlen
        while i < n:
            matched = False
            hi = min(ml, n - i)
            for L in range(hi, 1, -1):
                seg = text[i:i+L]
                r = ph.get(seg)
                if r is not None:
                    out.append(r)
                    i += L
                    matched = True
                    break
            if matched:
                continue
            c = text[i]
            out.append(ch.get(c, c))
            i += 1
        return "".join(out)

    def convert(self, text):
        t = self._s2t(text)
        tw = self.tw
        if tw:
            t = "".join(tw.get(c, c) for c in t)
        return t

if __name__ == "__main__":
    cc = S2TW()
    data = sys.stdin.read()
    sys.stdout.write(cc.convert(data))
