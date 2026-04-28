#!/usr/bin/env python3
"""Extract brochure product images and attach image paths to products.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

from extract_products import group_lines, join_words, normalize_ref, product_candidates


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "source" / "ELITE_PRODUCT_BROCHURE_2025.pdf"
PRODUCTS_PATH = ROOT / "data" / "products.json"
IMAGE_DIR = ROOT / "public" / "products"


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return value or "needs_review"


def unique_path(base_name: str) -> Path:
    candidate = IMAGE_DIR / f"{base_name}.png"
    counter = 2
    while candidate.exists():
        candidate = IMAGE_DIR / f"{base_name}_{counter}.png"
        counter += 1
    return candidate


def first_ref_for_candidate(candidate: dict, words: list[dict], lines: list[dict], candidates: list[dict]) -> str:
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
    ref_x = x_start + 175

    for word in words:
        if (
            abs(word["top"] - candidate["top"]) < 8
            and x_start < word["x0"] < x_end
            and word["text"].upper() == "REF"
        ):
            ref_x = word["x0"]
            break

    for line in lines:
        if not (candidate["top"] + 8 <= line["top"] < block_bottom):
            continue
        ref_words = [
            word for word in line["words"] if ref_x - 5 <= word["x0"] < x_end
        ]
        text = normalize_ref(join_words(ref_words))
        match = re.search(r"EL-?\d[\d\-.A-Za-z]*", text, re.I)
        if match:
            return normalize_ref(match.group(0))

    return f"EL{candidate['code']}"


def candidate_zones(page) -> list[dict]:
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3,
        keep_blank_chars=False,
        use_text_flow=False,
    )
    words = [word for word in words if 45 < word["top"] < 750]
    lines = group_lines(words)
    candidates = product_candidates(words)
    zones: list[dict] = []

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

        for word in words:
            if (
                abs(word["top"] - candidate["top"]) < 8
                and x_start < word["x0"] < x_end
                and word["text"].upper() in {"SPEC", "TYPE"}
            ):
                spec_x = word["x0"]
                break

        zones.append(
            {
                "id": first_ref_for_candidate(candidate, words, lines, candidates),
                "x0": max(0, x_start - 16),
                "x1": min(page.width, spec_x - 5),
                "top": candidate["top"] + 16,
                "bottom": block_bottom,
            }
        )

    return zones


def image_overlap(image: dict, zone: dict) -> float:
    x_overlap = max(0, min(image["x1"], zone["x1"]) - max(image["x0"], zone["x0"]))
    y_overlap = max(
        0, min(image["bottom"], zone["bottom"]) - max(image["top"], zone["top"])
    )
    return x_overlap * y_overlap


def save_image(page, image: dict, output_path: Path) -> None:
    bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
    page.crop(bbox).to_image(resolution=170).save(output_path)


def valid_image_box(page, image: dict) -> bool:
    return (
        0 <= image.get("x0", -1) < image.get("x1", -1) <= page.width
        and 0 <= image.get("top", -1) < image.get("bottom", -1) <= page.height
        and image.get("width", 0) >= 18
        and image.get("height", 0) >= 18
    )


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    products = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))
    product_by_id = {product.get("id"): product for product in products}
    matched_product_images: dict[str, str] = {}
    saved_images: set[int] = set()
    saved_count = 0

    with pdfplumber.open(PDF_PATH) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            zones = candidate_zones(page)

            for image_index, image in enumerate(page.images, start=1):
                if not valid_image_box(page, image):
                    continue

                best_zone = None
                best_score = 0.0
                for zone in zones:
                    score = image_overlap(image, zone)
                    if score > best_score:
                        best_zone = zone
                        best_score = score

                if best_zone and best_score > 50:
                    product_id = best_zone["id"]
                    output_path = unique_path(slug(product_id))
                    if product_id not in matched_product_images:
                        matched_product_images[product_id] = (
                            f"/public/products/{output_path.name}"
                        )
                else:
                    output_path = unique_path(f"page_{page_number:02d}_image_{image_index:02d}")

                save_image(page, image, output_path)
                saved_images.add(id(image))
                saved_count += 1

    for product in products:
        product_id = product.get("id")
        product["image"] = matched_product_images.get(product_id, "needs_review")

    PRODUCTS_PATH.write_text(json.dumps(products, indent=2) + "\n", encoding="utf-8")

    print(f"Saved {saved_count} images")
    print(f"Matched {sum(1 for product in products if product.get('image') != 'needs_review')} products")
    print(f"Needs review {sum(1 for product in products if product.get('image') == 'needs_review')} products")
    print(f"Known product ids {len(product_by_id)}")


if __name__ == "__main__":
    main()
