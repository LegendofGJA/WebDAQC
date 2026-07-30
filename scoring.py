"""
Logika perhitungan skor, direplikasi persis dari rumus di file Excel
Template_0726.xlsx (sheet DETAIL AUDIT), supaya hasil di web SAMA
dengan hasil kalau dihitung manual di Excel.

Rumus asli (referensi baris di Excel):
  - Tiap kategori/subkategori: ACTUAL = SUM(item-item di bawahnya)
  - Baris rekap per kategori (167-174): E = D/C*100
    kecuali kategori "OTHER" (baris 174): E = D/C*100*3   <-- ini memang
    bobot x3 di template asli, tetap dipertahankan apa adanya.
  - Total Score (E175) = SUM(E167:E174)
  - Final Score (E9)   = E175/10
  - Grade (E2): >=96 A | >=91 B+ | >=86 B | >=81 B- | else C
"""

from __future__ import annotations

CATEGORY_WEIGHTS = {
    "OTHER": 3,  # sesuai rumus asli =D174/C174*100*3
}


def item_actual_score(basic: float, remark: str | None) -> float:
    """Actual score = 0 jika remarks diisi (ada kata), selain itu = basic score."""
    if remark and str(remark).strip():
        return 0
    return basic


def compute_all(structure: list[dict], remarks: dict[str, str]) -> dict:
    """
    structure: hasil parse structure.json
    remarks: dict {str(item_number): remark_text}
    Mengembalikan dict berisi rincian per kategori + total & grade,
    persis seperti rekap baris 165-175 & E2/E9 di Excel.
    """
    category_results = []
    total_basic_check = 0
    total_actual_check = 0
    grand_percent_sum = 0.0

    for cat in structure:
        name = cat["name"]
        if name == "ETC":
            continue  # tidak ikut skor, sama seperti di Excel

        cat_basic = 0
        cat_actual = 0
        item_rows = []

        if "subcategories" in cat:
            for sub in cat["subcategories"]:
                sub_basic = 0
                sub_actual = 0
                for it in sub["items"]:
                    r = remarks.get(str(it["number"]), "")
                    a = item_actual_score(it["basic"], r)
                    sub_basic += it["basic"]
                    sub_actual += a
                    item_rows.append({**it, "remark": r, "actual": a})
                cat_basic += sub_basic
                cat_actual += sub_actual
        else:
            for it in cat.get("items", []):
                r = remarks.get(str(it["number"]), "")
                a = item_actual_score(it["basic"], r)
                cat_basic += it["basic"]
                cat_actual += a
                item_rows.append({**it, "remark": r, "actual": a})

        weight = CATEGORY_WEIGHTS.get(name, 1)
        percent = (cat_actual / cat_basic * 100 * weight) if cat_basic else 0

        category_results.append({
            "name": name,
            "basic": cat_basic,
            "actual": cat_actual,
            "percent": percent,
            "items": item_rows,
        })

        total_basic_check += cat_basic
        total_actual_check += cat_actual
        grand_percent_sum += percent

    final_score = grand_percent_sum / 10  # = E175/10 (E9)

    if final_score >= 96:
        grade = "A"
    elif final_score >= 91:
        grade = "B+"
    elif final_score >= 86:
        grade = "B"
    elif final_score >= 81:
        grade = "B-"
    else:
        grade = "C"

    return {
        "categories": category_results,
        "total_basic": total_basic_check,
        "total_actual": total_actual_check,
        "grand_percent_sum": grand_percent_sum,  # = E175
        "final_score": final_score,               # = E9
        "grade": grade,                            # = E2
    }
