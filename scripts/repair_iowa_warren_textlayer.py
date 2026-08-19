#!/usr/bin/env python3
"""Recover Warren County IA 2026 real-estate tax-sale items from the PDF text layer.

The county's official publication has a usable sequential text layer. Prefer that
before any geometric column reconstruction, which can discard item blocks when
x positions drift between pages. This helper is fail-closed: it delegates to the
existing Warren parser, which must recover exactly official items 1-426 before
anything is written. Owner/taxpayer names remain intentionally excluded.
"""
from __future__ import annotations

import io
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


def main() -> None:
    raw = warren.fetch_pdf()
    verified = date.today().isoformat()
    strategies = [
        ("pypdf sequential text", lambda: _pypdf_lines(raw, layout=False)),
        ("pypdf layout text", lambda: _pypdf_lines(raw, layout=True)),
        ("pdfplumber sequential text", lambda: _pdfplumber_plain_lines(raw)),
        ("pdfplumber geometry fallback", lambda: warren.extract_lines(raw)),
    ]
    failures: list[str] = []
    for label, extractor in strategies:
        try:
            rows = warren.parse_real_estate_rows(extractor(), verified)
        except RuntimeError as exc:
            failures.append(f"{label}: {exc}")
            print(f"Warren County IA: {label} incomplete; trying next safe extraction path. Reason: {exc}")
            continue
        warren.update_details(rows)
        print(
            f"Warren County IA: loaded {len(rows)} official real-estate tax-lien rows via {label}; "
            "taxpayer names intentionally omitted"
        )
        return
    raise RuntimeError("Warren County all safe text-layer extraction strategies failed: " + " | ".join(failures))


if __name__ == "__main__":
    main()
