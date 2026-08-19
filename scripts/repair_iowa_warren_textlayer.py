#!/usr/bin/env python3
"""Recover Warren County IA 2026 real-estate tax-sale items from official PDF text layers.

The county publication has multiple usable text-layer interpretations. Prefer a
single complete interpretation, but when each is incomplete, reconstruct the
official 1-426 real-estate set item-by-item across independent extractors. A
candidate is accepted only when at least two extraction strategies agree on the
parcel, amount, and public-bidder status. Owner/taxpayer names remain
intentionally excluded by the shared Warren parser.
"""
from __future__ import annotations

import io
import re
from collections import Counter
from datetime import date

import pdfplumber
from pypdf import PdfReader

import refresh_iowa_warren_tax_liens as warren


def _pypdf_lines(raw: bytes, layout: bool = False) -> list[str]:
    reader = PdfReader(io.BytesIO(raw))
    lines: list[str] = []
    for page in reader.pages:
        if layout:
            try:
                text = page.extract_text(extraction_mode="layout") or ""
            except TypeError:
                text = page.extract_text() or ""
        else:
            text = page.extract_text() or ""
        lines.extend(text.splitlines())
    return lines


def _pdfplumber_plain_lines(raw: bytes) -> list[str]:
    lines: list[str] = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            lines.extend((page.extract_text(layout=False) or "").splitlines())
    return lines


def _item_window(lines: list[str], item_number: int) -> list[str] | None:
    """Return one isolated official sale-item block, if visible in this text layer."""
    target = re.compile(rf"^\s*{item_number}\)\s*(.*)$")
    for index, line in enumerate(lines):
        if not target.match(line):
            continue

        start = index
        for cursor in range(index - 1, max(-1, index - 21), -1):
            if warren.ITEM_RE.match(lines[cursor]):
                start = cursor + 1
                break
            start = cursor

        end = min(len(lines), index + 21)
        for cursor in range(index + 1, min(len(lines), index + 21)):
            if warren.ITEM_RE.match(lines[cursor]):
                end = cursor
                break

        block = lines[start:end]
        relative = index - start
        block[relative] = target.sub(r"1) \1", block[relative], count=1)
        return block
    return None


def _parse_single_item(lines: list[str], item_number: int, verified: str) -> dict | None:
    """Parse one isolated item through the shared privacy/safety-aware parser."""
    block = _item_window(lines, item_number)
    if not block:
        return None

    original_count = warren.REAL_ESTATE_ITEM_COUNT
    try:
        # The shared parser is intentionally fail-closed. Isolating one official
        # item and temporarily setting its expected set to {1} lets us reuse all
        # parcel/amount/legal/privacy logic without weakening the final 1-426 gate.
        warren.REAL_ESTATE_ITEM_COUNT = 1
        rows = warren.parse_real_estate_rows(block, verified)
    except RuntimeError:
        return None
    finally:
        warren.REAL_ESTATE_ITEM_COUNT = original_count

    if len(rows) != 1:
        return None
    row = rows[0]
    row["sale_item_number"] = str(item_number)
    row["record_id"] = f"IA-Warren-2026-{item_number}"
    return row


def _candidate_signature(row: dict) -> tuple[str, float, bool]:
    return (
        str(row.get("parcel_id") or ""),
        float(row.get("delinquent_tax_amount") or 0.0),
        "Public bidder tax sale" in str(row.get("sale_status") or ""),
    )


def _merge_item_candidates(strategy_lines: list[tuple[str, list[str]]], verified: str) -> list[dict]:
    merged: list[dict] = []
    conflicts: list[int] = []
    missing: list[int] = []

    for item_number in range(1, warren.REAL_ESTATE_ITEM_COUNT + 1):
        candidates: list[tuple[str, dict]] = []
        for label, lines in strategy_lines:
            row = _parse_single_item(lines, item_number, verified)
            if row:
                candidates.append((label, row))

        if not candidates:
            missing.append(item_number)
            continue

        # Multi-column extraction can attach a neighboring dollar amount to the
        # correct parcel in one text interpretation. Requiring *all* extractors
        # to agree made those known layout artifacts veto otherwise corroborated
        # official data. Accept only an exact signature that is supported by at
        # least two strategies and has strictly more support than any alternative.
        # This is still fail-closed: a lone interpretation or a tie remains a
        # conflict and cannot be published.
        signatures = [_candidate_signature(row) for _, row in candidates]
        counts = Counter(signatures)
        ranked = counts.most_common()
        winner, support = ranked[0]
        runner_up = ranked[1][1] if len(ranked) > 1 else 0
        if support < 2 or support <= runner_up:
            conflicts.append(item_number)
            details = "; ".join(f"{label}={_candidate_signature(row)}" for label, row in candidates)
            print(f"Warren County IA: unresolved official text-layer interpretations for item {item_number}: {details}")
            continue

        corroborated = [(label, row) for label, row in candidates if _candidate_signature(row) == winner]
        # When key facts agree, prefer the corroborated candidate with the most
        # complete public legal description. Owner/taxpayer text is never emitted.
        chosen = max(corroborated, key=lambda pair: len(str(pair[1].get("legal_description") or "")))[1]
        merged.append(chosen)

    if missing or conflicts:
        raise RuntimeError(
            "Warren County cross-text-layer reconstruction incomplete: "
            f"loaded {len(merged)}/{warren.REAL_ESTATE_ITEM_COUNT}; "
            f"missing {missing[:20]}; conflicts {conflicts[:20]}"
        )

    merged.sort(key=lambda row: int(row["sale_item_number"]))
    expected = list(range(1, warren.REAL_ESTATE_ITEM_COUNT + 1))
    actual = [int(row["sale_item_number"]) for row in merged]
    if actual != expected:
        raise RuntimeError("Warren County reconstructed rows are not the exact official item set 1-426")
    if len({row.get("parcel_id") for row in merged}) != warren.REAL_ESTATE_ITEM_COUNT:
        raise RuntimeError("Warren County reconstructed rows contain duplicate parcel IDs")
    if any(row.get("opening_bid") is not None or row.get("minimum_bid") is not None for row in merged):
        raise RuntimeError("Warren County reconstruction incorrectly populated opening/minimum bid")
    if any(any("owner" in str(key).lower() or "taxpayer" in str(key).lower() for key in row) for row in merged):
        raise RuntimeError("Warren County reconstruction contains a restricted owner/taxpayer-name field")
    return merged


def main() -> None:
    raw = warren.fetch_pdf()
    verified = date.today().isoformat()
    strategies = [
        ("pypdf sequential text", lambda: _pypdf_lines(raw, layout=False)),
        ("pypdf layout text", lambda: _pypdf_lines(raw, layout=True)),
        ("pdfplumber sequential text", lambda: _pdfplumber_plain_lines(raw)),
        ("pdfplumber geometry fallback", lambda: warren.extract_lines(raw)),
    ]

    extracted: list[tuple[str, list[str]]] = []
    for label, extractor in strategies:
        lines = extractor()
        extracted.append((label, lines))
        try:
            rows = warren.parse_real_estate_rows(lines, verified)
        except RuntimeError as exc:
            print(f"Warren County IA: {label} incomplete; retaining it for item-level reconciliation. Reason: {exc}")
            continue
        warren.update_details(rows)
        print(
            f"Warren County IA: loaded {len(rows)} official real-estate tax-lien rows via {label}; "
            "taxpayer names intentionally omitted"
        )
        return

    print("Warren County IA: no single official text layer was complete; reconciling items across text layers.")
    rows = _merge_item_candidates(extracted, verified)
    warren.update_details(rows)
    print(
        f"Warren County IA: loaded {len(rows)} official real-estate tax-lien rows via cross-text-layer reconciliation; "
        "taxpayer names intentionally omitted"
    )


if __name__ == "__main__":
    main()
