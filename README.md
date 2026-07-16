# throughline-masvs

The **OWASP Mobile Application Security Verification Standard (MASVS)** expressed as a
[throughline](https://pypi.org/project/throughline/) **source** — a standalone,
grounded requirements graph that a consuming project composes with
[throughline-compose](https://github.com/timebacksolutions/throughline-compose).

This repository holds no code. It is a directory of small YAML items with permanent
UIDs, validated by `tl check`. Consumers import it under a namespace and reference
its controls as `masvs:SR-0001`.

## Status

This is the **complete MASVS v2.1.0 edition** —
<!-- tl:count type == 'user_requirement' -->
8
<!-- tl:end --> categories and
<!-- tl:count type == 'system_requirement' -->
24
<!-- tl:end --> high-level controls, generated from OWASP's official
machine-readable export and published to [`docs/spec.md`](docs/spec.md):

- `INT-0001` — the root intent (why MASVS exists), `normative: false`.
- Categories `MASVS-STORAGE`…`MASVS-PRIVACY` as `user_requirement`s that `derives_from`
  the intent.
- Every control as a `system_requirement` that `implements` its category, carrying its
  MASVS id in `attrs.source_ref` and the control's rationale in `rationale`.

The counts above are rendered from the live graph by the `tl:count` directive, so
they cannot drift. Re-run [`tools/generate_from_masvs.py`](tools/generate_from_masvs.py)
against a newer OWASP export to extend the graph; it preserves every existing
UID↔id mapping and only allocates UIDs for ids that have none yet.

## Why there are no levels

MASVS **v2** deliberately removed the old L1/L2/R verification levels and moved the
detailed, testable procedures out to the **MASTG** (Mobile Application Security Testing
Guide). MASVS is now the control layer only — 8 categories, 24 high-level controls — so,
unlike `throughline-asvs`, there is **no `attrs.level`**. A consumer that needs concrete
tests composes the MASTG separately.

## Editions

MASVS v1 is retired; this source carries **v2 only** on `main`. A minor revision
(v2.0.0 → v2.1.0) is additive and stays on one graph. Were OWASP to publish a full
restructure, it would become a release branch + tag, the way
[`throughline-asvs`](https://github.com/timebacksolutions/throughline-asvs) handles v4 → v5.

## Modelling conventions

- **throughline UIDs are this source's own** (`SR-0001`…), immutable and never the
  MASVS id. The published id lives in `attrs.source_ref` (`"MASVS-STORAGE-1"`).
- **One root intent.** Every category serves the same purpose — a mobile app's security
  can be verified against a consistent baseline — so MASVS is modelled single-root, like
  ASVS (contrast WCAG/AISVS, which carry several genuinely-distinct "why"s and so get
  several roots).

## Composing it

In a consuming throughline project's `throughline.toml`:

```toml
[[sources]]
namespace = "masvs"
url = "https://github.com/timebacksolutions/throughline-masvs"
ref = "v2.1.0"
```

(For local side-by-side development you can use `path = "vendor/throughline-masvs"`
instead of `url`/`ref`.)

Then reference a control from your own items:

```yaml
links:
- target: masvs:SR-0001          # MASVS-STORAGE-1, the app securely stores sensitive data
  type: satisfies
```

`tl-compose check` resolves the reference; bare `tl check` fails fast and points you
at `tl-compose`.

## Local checks

```sh
pip install throughline
tl check --strict     # the graph must stay sound
tl docs --check       # docs/spec.md must match the graph
```

## Provenance

MASVS is © the OWASP Foundation, licensed CC BY-SA 4.0. See [NOTICE](NOTICE) and
https://github.com/OWASP/masvs. This repository is Apache-2.0 for its structure and
tooling; the reproduced requirement text remains OWASP's, redistributed under the same
CC BY-SA 4.0 terms.
