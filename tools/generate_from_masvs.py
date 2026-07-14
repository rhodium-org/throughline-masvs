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


def short_title(text: str) -> str:
    """A concise label distilled from the control statement."""
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
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else str(REPO / "tools/OWASP_MASVS.yaml")))
