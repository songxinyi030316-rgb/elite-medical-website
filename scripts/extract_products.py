#!/usr/bin/env python3
"""Extract product families and variants from the Elite Medical brochure.

The brochure is laid out in visual columns, so this parser uses word
coordinates rather than plain text order. Rows that cannot be extracted with
high confidence are written to data/review_needed.csv.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover - dependency hint for local use
    raise SystemExit(
        "pdfplumber is required. Install it with: python3 -m pip install pdfplumber"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "source" / "ELITE_PRODUCT_BROCHURE_2025.pdf"
FALLBACK_PDF = ROOT / "ELITE PRODUCT BROCHURE 2025.pdf"
PRODUCTS_PATH = ROOT / "data" / "products.json"
CATEGORIES_PATH = ROOT / "data" / "categories.json"
REVIEW_PATH = ROOT / "data" / "review_needed.csv"


def ensure_pdf_path() -> None:
    if PDF_PATH.exists():
        return

    if FALLBACK_PDF.exists():
        PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FALLBACK_PDF, PDF_PATH)
        return

    raise FileNotFoundError(f"Brochure not found at {PDF_PATH}")


def join_words(words: list[dict]) -> str:
    return " ".join(word["text"] for word in sorted(words, key=lambda word: word["x0"]))


def group_lines(words: list[dict], tolerance: float = 3) -> list[dict]:
    lines: list[dict] = []

    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not lines or abs(lines[-1]["top"] - word["top"]) > tolerance:
            lines.append({"top": word["top"], "words": [word]})
        else:
            lines[-1]["words"].append(word)
            lines[-1]["top"] = sum(item["top"] for item in lines[-1]["words"]) / len(
                lines[-1]["words"]
            )

    for line in lines:
        line["text"] = join_words(line["words"])
        line["x0"] = min(word["x0"] for word in line["words"])
        line["x1"] = max(word["x1"] for word in line["words"])
        line["height"] = max(word["bottom"] - word["top"] for word in line["words"])

    return lines


def normalize_category(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("MEDICALTAPES", "MEDICAL TAPES")
    return text


def normalize_ref(text: str) -> str:
    text = text.replace(" ", "").replace("\u00a0", "")
    text = text.replace("El", "EL").replace("eL", "EL")
    return text


def product_candidates(words: list[dict]) -> list[dict]:
    candidates: list[dict] = []

    for index, word in enumerate(words[:-1]):
        current = word["text"].upper().replace("-", "")
        next_word = words[index + 1]
        same_line = abs(word["top"] - next_word["top"]) < 2.5
        is_product_header = word["bottom"] - word["top"] > 10

        if (
            current == "EL"
            and same_line
            and is_product_header
            and re.fullmatch(r"\d{4}", next_word["text"])
        ):
            candidates.append(
                {
                    "code": next_word["text"],
                    "x": word["x0"],
                    "top": word["top"],
                }
            )

    deduped: list[dict] = []
    seen: set[tuple[int, int, str]] = set()

    for candidate in candidates:
        key = (
            round(candidate["x"]),
            round(candidate["top"]),
            candidate["code"],
        )
        if key not in seen:
            deduped.append(candidate)
            seen.add(key)

    filtered: list[dict] = []
    for candidate in deduped:
        row_words = [
            word
            for word in words
            if abs(word["top"] - candidate["top"]) < 8
            and candidate["x"] < word["x0"] < candidate["x"] + 260
        ]
        row_text = " ".join(word["text"].upper() for word in row_words)
        if "SPEC" in row_text or "TYPE" in row_text or "REF" in row_text:
            filtered.append(candidate)

    return sorted(filtered, key=lambda item: (item["x"] >= 300, item["top"], item["x"]))


def extract_category_map(pdf) -> dict[str, str]:
    category_map: dict[str, str] = {}

    for page in pdf.pages:
        words = page.extract_words(
            x_tolerance=2,
            y_tolerance=3,
            keep_blank_chars=False,
            use_text_flow=False,
        )
        lines = group_lines(words)

        for line in lines:
            if line["height"] <= 10 or re.search(r"\d{4}", line["text"]):
                continue

            matches = re.finditer(
                r"EL\s+([0-9]{2})(?:-([0-9]{2}))?\s+(.+?)(?=\s+EL\s+[0-9]{2}(?:-[0-9]{2})?\s+|$)",
                line["text"],
            )
            for match in matches:
                start = int(match.group(1))
                end = int(match.group(2) or match.group(1))
                category = normalize_category(match.group(3))

                for number in range(start, end + 1):
                    category_map[f"{number:02d}"] = category

    return category_map


def extract_page(page, page_number: int, category_map: dict[str, str]) -> tuple[list[dict], list[dict]]:
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=False,
    )
    words = [
        word
        for word in words
        if 45 < word["top"] < 750
        and word["text"][::-1].upper() not in {"BROCHURE", "PRODUCT", "2025"}
    ]
    lines = group_lines(words)
    candidates = product_candidates(words)
    products: list[dict] = []
    review_rows: list[dict] = []

    for candidate in candidates:
        is_left_column = candidate["x"] < 300
        same_side_next_tops = [
            item["top"]
            for item in candidates
            if item["top"] > candidate["top"] + 5
            and (item["x"] < 300) == is_left_column
        ]
        block_bottom = min(same_side_next_tops) if same_side_next_tops else 740

        x_start = candidate["x"]
        x_end = 300 if is_left_column else 560
        spec_x = x_start + 115
        ref_x = x_start + 175

        header_words = [
            word
            for word in words
            if abs(word["top"] - candidate["top"]) < 8
            and x_start < word["x0"] < x_end
        ]
        for word in header_words:
            upper = word["text"].upper()
            if upper in {"SPEC", "TYPE"}:
                spec_x = word["x0"]
            elif upper == "REF":
                ref_x = word["x0"]

        name_lines: list[str] = []
        for line in lines:
            if not (candidate["top"] + 8 <= line["top"] < min(block_bottom, candidate["top"] + 75)):
                continue
            name_words = [
                word
                for word in line["words"]
                if x_start - 2 <= word["x0"] < spec_x - 8
                and word["bottom"] - word["top"] > 8
            ]
            text = join_words(name_words).strip()
            if text and not re.fullmatch(r"(EL|\d{4}|SPEC|REF).*", text, re.I):
                name_lines.append(text)

        name = " ".join(name_lines).strip()

        ref_lines: list[tuple[float, str]] = []
        for line in lines:
            if not (candidate["top"] + 8 <= line["top"] < block_bottom):
                continue
            ref_words = [
                word for word in line["words"] if ref_x - 5 <= word["x0"] < x_end
            ]
            text = normalize_ref(join_words(ref_words))
            ref_match = re.search(r"EL-?\d[\d\-.A-Za-z]*", text, re.I)
            if ref_match:
                ref_lines.append((line["top"], normalize_ref(ref_match.group(0))))

        ref_lines = sorted(ref_lines, key=lambda item: item[0])
        variants: list[dict] = []

        for index, (top, ref) in enumerate(ref_lines):
            previous_top = ref_lines[index - 1][0] if index else candidate["top"] + 8
            next_top = ref_lines[index + 1][0] if index + 1 < len(ref_lines) else block_bottom
            low = candidate["top"] + 8 if index == 0 else (previous_top + top) / 2
            high = block_bottom if index == len(ref_lines) - 1 else (top + next_top) / 2

            spec_words = [
                word
                for word in words
                if low - 1 <= word["top"] < high + 1
                and spec_x - 3 <= word["x0"] < ref_x - 6
                and word["text"].upper() not in {"SPEC", "TYPE", "REF"}
            ]
            spec = " ".join(
                join_words(line["words"]) for line in group_lines(spec_words)
            ).strip()
            variants.append({"spec": spec or "needs_review", "ref": ref})

        issues: list[str] = []
        category = category_map.get(candidate["code"][:2], "needs_review")
        if not name:
            issues.append("missing_name")
        if not variants:
            issues.append("missing_variants")
        if any(variant["spec"] == "needs_review" for variant in variants):
            issues.append("missing_spec")
        if category == "needs_review":
            issues.append("missing_category")

        product_id = variants[0]["ref"] if variants else f"EL{candidate['code']}"
        product = {
            "id": product_id,
            "category": category,
            "name": name or "needs_review",
            "variants": variants,
        }
        products.append(product)

        if issues:
            review_rows.append(
                {
                    "page": page_number,
                    "product_code": f"EL{candidate['code']}",
                    "id": product_id,
                    "category": product["category"],
                    "name": product["name"],
                    "reason": ";".join(sorted(set(issues))),
                }
            )

    return products, review_rows


def main() -> None:
    ensure_pdf_path()
    all_products: list[dict] = []
    review_rows: list[dict] = []

    with pdfplumber.open(PDF_PATH) as pdf:
        category_map = extract_category_map(pdf)
        for page_number, page in enumerate(pdf.pages, start=1):
            products, page_review_rows = extract_page(page, page_number, category_map)
            all_products.extend(products)
            review_rows.extend(page_review_rows)

    seen_ids: set[str] = set()
    for product in all_products:
        if product["id"] in seen_ids:
            review_rows.append(
                {
                    "page": "needs_review",
                    "product_code": "needs_review",
                    "id": product["id"],
                    "category": product["category"],
                    "name": product["name"],
                    "reason": "duplicate_id",
                }
            )
        seen_ids.add(product["id"])

    categories = sorted({product["category"] for product in all_products})

    PRODUCTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRODUCTS_PATH.write_text(json.dumps(all_products, indent=2) + "\n", encoding="utf-8")
    CATEGORIES_PATH.write_text(json.dumps(categories, indent=2) + "\n", encoding="utf-8")

    fieldnames = ["page", "product_code", "id", "category", "name", "reason"]
    with REVIEW_PATH.open("w", newline="", encoding="utf-8") as review_file:
        writer = csv.DictWriter(review_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"Extracted {len(all_products)} products")
    print(f"Wrote {len(review_rows)} review rows")


if __name__ == "__main__":
    main()
