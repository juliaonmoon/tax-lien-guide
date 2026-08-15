#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "property-screener.html"


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"Expected property-screener marker not found: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "['neighborhood','Neighborhood value',true,205],['research_priority'",
        "['neighborhood','Neighborhood value',true,205],['public_safety','Public safety',false,245],['research_priority'",
    )

    marker = "function hasAddress(x){return !!String(x.address||'').trim()}"
    public_safety_fn = """function publicSafety(x){if(x.public_safety_12mo_offenses==null||x.public_safety_12mo_offenses==='')return '—';const count=Number(x.public_safety_12mo_offenses).toLocaleString();const area=x.public_safety_area||'Published service area';const dates=[x.public_safety_period_start,x.public_safety_period_end].filter(Boolean).join(' → ');const detail=[`${count} reported offenses`,area,dates].filter(Boolean).join(' • ');const scope=x.public_safety_scope||'Official public-safety count; scope varies by source';const source=x.public_safety_source?`<a target=\"_blank\" rel=\"noopener\" href=\"${esc(x.public_safety_source)}\">source ↗</a>`:'';return `${esc(detail)}<div class=\"reason\">${esc(scope)}${source?` • ${source}`:''}</div>`}function hasAddress(x){return !!String(x.address||'').trim()}"""
    text = replace_once(text, marker, public_safety_fn)

    text = replace_once(
        text,
        "legal:legal(x),neighborhood:neighborhood(x),research_priority:",
        "legal:legal(x),neighborhood:neighborhood(x),public_safety:publicSafety(x),research_priority:",
    )

    text = replace_once(
        text,
        "Neighborhood Value is a ZIP/ZCTA research proxy, not a prediction of actual rentability.",
        "Neighborhood Value is a ZIP/ZCTA research proxy, not a prediction of actual rentability. Public-safety counts retain each official source's stated geographic/time scope and should not be compared as standardized crime rates.",
    )

    PAGE.write_text(text, encoding="utf-8")
    print("Property screener now exposes scoped official public-safety metrics")


if __name__ == "__main__":
    main()
