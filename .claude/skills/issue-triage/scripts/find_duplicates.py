#!/usr/bin/env python3
"""Deterministic duplicate-candidate search (TF-IDF cosine, stdlib only).

Usage: python3 find_duplicates.py <issue.json> [corpus.json] [--top 3] [--min 0.25]
- issue.json: object with number, title, body, createdAt
- corpus.json: list of issues (default: evals/golden/hoppscotch-issues.json)
Only issues created BEFORE the target are considered, so no future information leaks.
Prints JSON list of {number, title, score}. The model decides whether a candidate
is a true duplicate; this script only narrows the search.
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_CORPUS = Path("evals/golden/hoppscotch-issues.json")
STOP = set("""a an the and or of to in on for is it this that with as be are was
i we you my our not no can when from by at if but have has do does there
issue bug feature existing searched description platform browser operating system
version deployment type response""".split())


def tokens(text):
    words = re.findall(r"[a-z][a-z0-9_\-]{2,}", (text or "").lower())
    return [w for w in words if w not in STOP]


def doc(issue):
    # Title counts double: titles carry most of the signal.
    return tokens(issue.get("title", "")) * 2 + tokens(issue.get("body", ""))


def main(argv):
    args, opts, it = [], {}, iter(argv)
    for a in it:
        if a.startswith("--"):
            opts[a] = next(it)
        else:
            args.append(a)
    top = int(opts.get("--top", 3))
    min_score = float(opts.get("--min", 0.25))
    target = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    corpus_path = Path(args[1]) if len(args) > 1 else DEFAULT_CORPUS
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

    cutoff = target.get("createdAt", "9999")
    # Golden replays carry the ORIGINAL creation time in a harness marker, so the
    # search only sees issues that existed when the original issue was opened.
    m = re.search(r"golden-cutoff:\s*(\S+)", target.get("body") or "")
    if m:
        cutoff = m.group(1)
    title = (target.get("title") or "").strip().lower()
    pool = [c for c in corpus
            if c["number"] != target["number"]
            and (c.get("title") or "").strip().lower() != title
            and c.get("createdAt", "") < cutoff]
    docs = [Counter(doc(c)) for c in pool]
    n = len(docs) + 1
    df = Counter(w for d in docs for w in d)
    idf = {w: math.log(n / (1 + df[w])) + 1 for w in df}

    def vec(counter):
        return {w: c * idf.get(w, math.log(n) + 1) for w, c in counter.items()}

    def cos(a, b):
        dot = sum(v * b.get(k, 0) for k, v in a.items())
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    tv = vec(Counter(doc(target)))
    scored = [(cos(tv, vec(d)), c) for d, c in zip(docs, pool)]
    scored.sort(key=lambda x: -x[0])
    out = [{"number": c["number"], "title": c["title"], "score": round(s, 3)}
           for s, c in scored[:top] if s >= min_score]
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
