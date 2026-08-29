#!/usr/bin/env python3
"""Generate the MASVS throughline source from OWASP's official machine-readable data.

This reads `OWASP_MASVS.yaml` (the whole standard in one file) and emits one throughline
item per category (a `user_requirement`) and per control (a `system_requirement`), grounded
category -> intent and control -> category.

MASVS v2 is deliberately two levels deep: 8 categories, 24 high-level controls, no L1/L2/R
levels and no embedded tests (those moved to the MASTG). So there is no `level` attribute —
the control `statement` is the normative line and its `description` is the rationale.

Two invariants make re-running safe and faithful:

* **UIDs are permanent.** The mapping from a MASVS id (its `source_ref`, e.g.
  ``MASVS-STORAGE-1``) to a throughline UID is derived from the items already on disk.
  Existing items are never rewritten; only ids with no item yet get a freshly allocated UID,
  in document order, continuing from the highest number already used.
* **Data-driven docs.** `docs/spec.md` is regenerated with blanked `tl:*` markers, so
  `tl docs` MUST run after this script (CI's `tl docs --check` enforces it).

Usage:  python tools/generate_from_masvs.py tools/OWASP_MASVS.yaml

Because existing items are never rewritten, a change to how a *title* is derived cannot
reach the graph through an ordinary run. Applying one is a separate, explicit operation:

    python tools/generate_from_masvs.py --retitle [--dry-run]

which rewrites only those titles still matching the superseded derivation, and leaves
every hand-curated title untouched.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CATS_DIR = REPO / "categories"           # user_requirement, prefix UR
CTRL_DIR = REPO / "controls"             # system_requirement, prefix SR
SPEC = REPO / "docs" / "spec.md"
INTENT = "INT-0001"
EDITION = "2.1.0"

_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_WS = re.compile(r"\s+")


def clean_text(desc: str) -> str:
    t = _MD_LINK.sub(r"\1", (desc or "").strip())   # [text](url) -> text
    return _WS.sub(" ", t).strip()


# The "The app" subject every MASVS control statement opens with. The optional comma
# matters: a statement reading "The app, on first launch, ..." puts one where the space
# would be, and a pattern anchored on `app\s` leaves the comma stranded at the front.
_PREFIX = re.compile(r"^The\s+app\s*[,:;]?\s+", re.IGNORECASE)
_ABBREV = re.compile(
    r"(?<![A-Za-z0-9])(?:e\.g|i\.e|etc|vs|cf|approx|resp|incl|Fig|No|Inc|Ltd)\.",
    re.IGNORECASE,
)


def _mask_non_terminators(t: str) -> str:
    """Blank out `.`/`!`/`?` that do not end a sentence, so the first real one is found.

    Control text carries full stops that terminate nothing: abbreviations (``e.g.``),
    dotted version numbers (``TLS 1.3``), and whole sentences quoted or parenthesised
    inside a larger one. Each is replaced by a NUL of the same width, so offsets into the
    masked string index the original unchanged.
    """
    chars = list(t)
    for m in _ABBREV.finditer(t):
        for i in range(m.start(), m.end()):
            if chars[i] == ".":
                chars[i] = "\x00"
    s = "".join(chars)
    s = re.sub(r"(?<=\d)\.(?=\d)", "\x00", s)                   # decimals: v1.5
    s = re.sub(r"(?<=\b[A-Za-z])\.(?=[A-Za-z]\.)", "\x00", s)   # initialisms: U.S.
    s = re.sub(r"(?<=\b[A-Za-z])\.(?=\s*[a-z])", "\x00", s)     # single letter + lower
    out, depth, in_quote = list(s), 0, False
    for i, ch in enumerate(s):
        if ch == '"':
            in_quote = not in_quote
        elif ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if (depth > 0 or in_quote) and out[i] in ".!?":
            out[i] = "\x00"
    return "".join(out)


def short_title(text: str) -> str:
    """A label for the control: its first complete sentence, minus the subject preamble.

    Deliberately uncapped. A title is cut at a sentence boundary or not at all, because
    every cheaper rule truncates mid-thought — see `_legacy_short_title`, which split on
    the first ``[,;.]`` and so would render a statement listing three storage locations
    as only the first of them. Most MASVS statements are a single sentence, so most
    titles are the whole statement; that is the intended outcome, not an accident.

    Satisfies throughline-source-quality REQ-0001 (a derived title is a complete
    statement) and REQ-0002 (the derivation is deterministic).
    """
    t = _PREFIX.sub("", text.strip())
    t = (t[:1].upper() + t[1:]) if t else t
    m = re.search(r"[.!?](?=\s|$)", _mask_non_terminators(t))
    return (t[:m.start()] if m else t).strip().rstrip(" ,;:")


def _legacy_short_title(text: str) -> str:
    """The title derivation used before the sentence-based one replaced it.

    Kept for exactly one job: `retitle` compares a stored title against this to tell a
    generated title from a hand-curated one, so curation survives the rewrite
    (throughline-source-quality REQ-0005). It is not a fallback — nothing else calls it,
    and it must not be 'fixed'. Delete it once no branch carries legacy titles.
    """
    t = re.sub(r"^The app\s+", "", text, flags=re.IGNORECASE)
    t = (t[:1].upper() + t[1:]) if t else t
    clause = re.split(r"[,;.]", t, maxsplit=1)[0].strip()
    if len(clause) > 100:
        clause = clause[:100].rsplit(" ", 1)[0]
    return clause


def _scan_existing(dir_: Path) -> dict[str, str]:
    """Map source_ref -> UID for the items already on disk."""
    ref2uid: dict[str, str] = {}
    for f in dir_.glob("*.yml"):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        ref = (data.get("attrs") or {}).get("source_ref")
        if ref:
            ref2uid[ref] = data["uid"]
    return ref2uid


def _max_num(ref2uid: dict[str, str], prefix: str) -> int:
    nums = [int(u.split("-")[1]) for u in ref2uid.values() if u.startswith(prefix + "-")]
    return max(nums, default=0)


def _dump(path: Path, item: dict) -> None:
    path.write_text(
        yaml.safe_dump(item, sort_keys=False, allow_unicode=True, width=80),
        encoding="utf-8",
    )


SPEC_HEADER = """\
# OWASP MASVS {edition} — throughline source

This document is **generated from the graph** by `tl docs`; `tl docs --check` gates
it in CI. The prose headings are hand-owned — everything between `tl:*` markers is
injected from the YAML items, so the published spec can never drift from the graph.

This source is a faithful, complete cut of **OWASP MASVS v{edition}**: every category is
a `user_requirement`, and every control is a `system_requirement` that `implements` its
category. The published MASVS id lives in `attrs.source_ref` (e.g. `MASVS-STORAGE-1`). The
throughline UIDs are this source's own and immutable — a consumer cites a control as
`masvs:SR-0001`, never by its MASVS id.

It carries
<!-- tl:count type == 'user_requirement' -->
<!-- tl:end --> categories and
<!-- tl:count type == 'system_requirement' -->
<!-- tl:end --> controls.

## Purpose

<!-- tl:item INT-0001 -->
<!-- tl:end -->
"""


def generate_spec(cat_ref2uid: dict[str, str], category_name: dict[str, str],
                  seen_cat: list[str]) -> None:
    """Write docs/spec.md: a hand-owned header plus, per category in document order, a
    tl:item block for its UR and a tl:table of its controls. `tl docs` injects the live
    content into the markers."""
    parts = [SPEC_HEADER.format(edition=EDITION)]
    for cid in seen_cat:
        parts.append(f"## {cid} {category_name[cid]}\n")
        parts.append(f"<!-- tl:item {cat_ref2uid[cid]} -->\n<!-- tl:end -->\n")
        flt = (
            "type == 'system_requirement' and "
            f"attrs.get('source_ref').startswith('{cid}-')"
        )
        parts.append(f"<!-- tl:table {flt} -->\n<!-- tl:end -->\n")
    SPEC.write_text("\n".join(parts) + "\n", encoding="utf-8")


def retitle(dry_run: bool = False) -> int:
    """Rewrite generated titles in place under the current `short_title`.

    An ordinary run never revisits an item that already exists (that is what keeps UIDs
    and curation safe), so a change to the title derivation cannot reach the graph by
    re-running the generator. This is the explicit operation that applies it, and it
    states what it overwrites rather than doing it silently — the shape
    throughline-source-quality REQ-0005 asks for.

    An item is rewritten only if its stored title is exactly what `_legacy_short_title`
    would have produced from its own text. Anything else is a human's work and is left
    alone; `text` is never touched at all.
    """
    changed: list[tuple[str, str, str]] = []
    curated = unchanged = 0
    for f in sorted(CTRL_DIR.glob("*.yml")):
        if f.name.startswith("."):
            continue  # .register.yml is the folder manifest, not an item
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        text, old = data.get("text"), data.get("title")
        if not text or not old:
            continue
        if old != _legacy_short_title(text):
            curated += 1  # hand-written, or already migrated — not ours to rewrite
            continue
        new = short_title(text)
        if new == old:
            unchanged += 1
            continue
        changed.append((data["uid"], old, new))
        if not dry_run:
            data["title"] = new
            _dump(f, data)

    for uid, old, new in changed:
        print(f"{uid}\n  - {old}\n  + {new}")
    verb = "would rewrite" if dry_run else "rewrote"
    print(f"\n{verb} {len(changed)} title(s); "
          f"{unchanged} already correct, {curated} left alone (curated or migrated)")
    return 0


def main(src: str) -> int:
    groups = yaml.safe_load(Path(src).read_text(encoding="utf-8"))["groups"]

    cat_ref2uid = _scan_existing(CATS_DIR)
    ctrl_ref2uid = _scan_existing(CTRL_DIR)
    next_ur = _max_num(cat_ref2uid, "UR") + 1
    next_sr = _max_num(ctrl_ref2uid, "SR") + 1

    # Categories, in document order.
    seen_cat: list[str] = []
    category_name: dict[str, str] = {}
    for g in groups:
        cid = g["id"]
        seen_cat.append(cid)
        category_name[cid] = g["title"]
        if cid in cat_ref2uid:
            continue  # keep the existing category item
        uid = f"UR-{next_ur:04d}"
        next_ur += 1
        cat_ref2uid[cid] = uid
        _dump(CATS_DIR / f"{uid}.yml", {
            "uid": uid,
            "type": "user_requirement",
            "status": "approved",
            "title": f"{cid} {g['title']}",
            "text": clean_text(g["description"]),
            "links": [{"target": INTENT, "type": "derives_from"}],
            "attrs": {"source_ref": cid},
        })

    # Controls, in document order.
    written = 0
    for g in groups:
        for c in g["controls"]:
            ref = c["id"]
            if ref in ctrl_ref2uid:
                continue  # keep the existing item and its curated title, untouched
            uid = f"SR-{next_sr:04d}"
            next_sr += 1
            ctrl_ref2uid[ref] = uid
            text = clean_text(c["statement"])
            _dump(CTRL_DIR / f"{uid}.yml", {
                "uid": uid,
                "type": "system_requirement",
                "status": "approved",
                "title": short_title(text),
                "text": text,
                "rationale": clean_text(c["description"]),
                "links": [{"target": cat_ref2uid[g["id"]], "type": "implements"}],
                "attrs": {"source_ref": ref},
            })
            written += 1

    generate_spec(cat_ref2uid, category_name, seen_cat)

    print(f"categories: {len(seen_cat)} total, {len(cat_ref2uid)} mapped")
    print(f"controls: {written} new items written, {len(ctrl_ref2uid)} total mapped")
    print(f"spec: {SPEC} regenerated for {len(seen_cat)} categories")
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--retitle" in argv:
        argv.remove("--retitle")
        raise SystemExit(retitle(dry_run="--dry-run" in argv))
    raise SystemExit(main(argv[0] if argv else str(REPO / "tools/OWASP_MASVS.yaml")))
