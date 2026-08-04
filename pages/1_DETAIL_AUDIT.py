import pandas as pd
import streamlit as st

from style import inject_css, inject_sidebar_brand, inject_footer
from scoring import compute_all
from audit_core import (
    load_structure,
    get_supabase_client,
    list_saved_drafts,
    fetch_draft,
    save_draft,
    build_filled_workbook,
    workbook_to_bytes,
)

st.set_page_config(page_title="DETAIL AUDIT", page_icon="📋", layout="wide")
inject_css()
inject_sidebar_brand()

# Panel tombol kecil melayang di kiri bawah (bukan full width lagi)
st.markdown(
    """
    <style>
    .cat-banner {
        background: linear-gradient(135deg, var(--accent), #c0242a);
        color: #fff;
        font-weight: 700;
        font-size: 0.95rem;
        padding: 7px 14px;
        border-radius: 8px;
        margin: 16px 0 6px 0;
        letter-spacing: .03em;
    }
    .subcat-label {
        font-weight: 700;
        text-decoration: underline;
        margin: 8px 0 4px 4px;
        color: var(--accent);
    }
    div.st-key-floating_actions {
        position: fixed;
        left: 14px;
        bottom: 14px;
        z-index: 9999;
        background: var(--surface);
        padding: 8px;
        border-radius: 10px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35);
        border: 1px solid var(--border);
        width: 150px;
    }
    div.st-key-floating_actions button,
    div.st-key-floating_actions a {
        font-size: 0.78rem !important;
        padding: 0.4rem 0.6rem !important;
        margin-bottom: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

structure = load_structure()
supabase = get_supabase_client()

defaults = {
    "store_name": "", "date1": "", "date2": "",
    "auditor": "", "pic_on_duty": "", "remarks": {}, "loaded_key": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def reset_form():
    for k, v in defaults.items():
        st.session_state[k] = v if not isinstance(v, dict) else {}
    st.query_params.clear()


def load_into_state(row: dict):
    st.session_state["store_name"] = row.get("store_name", "") or ""
    st.session_state["date1"] = row.get("audit_date", "") or ""
    st.session_state["date2"] = row.get("date2", "") or ""
    st.session_state["auditor"] = row.get("auditor", "") or ""
    st.session_state["pic_on_duty"] = row.get("pic_on_duty", "") or ""
    st.session_state["remarks"] = row.get("remarks", {}) or {}
    st.session_state["loaded_key"] = (row.get("store_name"), row.get("audit_date"))


qp = st.query_params
if supabase is not None and "store" in qp and "date" in qp and st.session_state["loaded_key"] is None:
    row = fetch_draft(qp["store"], qp["date"])
    if row:
        load_into_state(row)

st.markdown(
    """
    <div class="page-head">
        <div class="page-head-icon">📋</div>
        <h2>DETAIL AUDIT</h2>
        <p>Isi penilaian audit toko, simpan, lanjut ke QC Image Inserter untuk foto</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if supabase is None:
    st.error("Supabase belum terkoneksi. Isi SUPABASE_URL & SUPABASE_KEY di secrets.")

with st.expander("📂 Buka data toko yang tersimpan (lanjutkan audit)"):
    rows = list_saved_drafts()
    if rows:
        options = {
            f"{r['store_name']}  —  {r['audit_date']}  (update: {r['updated_at'][:16].replace('T',' ')})": r
            for r in rows
        }
        choice = st.selectbox("Pilih draft", ["-- pilih --"] + list(options.keys()))
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Muat Draft", disabled=(choice == "-- pilih --")):
                picked = options[choice]
                full = fetch_draft(picked["store_name"], picked["audit_date"])
                if full:
                    load_into_state(full)
                    st.query_params["store"] = picked["store_name"]
                    st.query_params["date"] = picked["audit_date"]
                    st.rerun()
        with col_b:
            if st.button("🆕 Mulai Audit Baru"):
                reset_form()
                st.rerun()
    else:
        st.caption("Belum ada draft tersimpan.")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.session_state["store_name"] = st.text_input("STORE NAME", value=st.session_state["store_name"])
    st.session_state["date1"] = st.text_input("DATE", value=st.session_state["date1"])
    st.session_state["date2"] = st.text_input("DATE (2)", value=st.session_state["date2"])
with c2:
    st.session_state["auditor"] = st.text_input("AUDITOR", value=st.session_state["auditor"])
    st.session_state["pic_on_duty"] = st.text_input("PIC ON DUTY", value=st.session_state["pic_on_duty"])

st.markdown("---")
st.subheader("DETAIL TO VERIFY")
st.caption("Isi kolom Remarks kalau ada temuan. Remarks terisi -> Actual Score poin itu otomatis 0.")

remarks_state = st.session_state["remarks"]
ROW_COLS = [0.5, 4.2, 0.9, 0.9, 3.5]


def _safe_remark(v) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return ""
    return str(v)


def render_header_row():
    h = st.columns(ROW_COLS)
    h[0].markdown("**No**")
    h[1].markdown("**Deskripsi**")
    h[2].markdown("**Basic**")
    h[3].markdown("**Actual**")
    h[4].markdown("**Remarks**")


def render_table(items: list[dict], key: str):
    render_header_row()
    for it in items:
        number = str(it["number"])
        widget_key = f"{key}_remark_{number}"

        if widget_key in st.session_state:
            current = _safe_remark(st.session_state[widget_key])
        else:
            current = _safe_remark(remarks_state.get(number, ""))

        actual = 0 if current.strip() else it["basic"]

        cols = st.columns(ROW_COLS)
        cols[0].markdown(str(it["number"]))
        cols[1].markdown(it["desc"])
        cols[2].markdown(str(it["basic"]))
        if actual == 0:
            cols[3].markdown(f":red[**{actual}**]")
        else:
            cols[3].markdown(str(actual))

        new_val = cols[4].text_area(
            "Remarks", value=current, key=widget_key,
            label_visibility="collapsed", height=68,
        )
        remarks_state[number] = _safe_remark(new_val)
        st.markdown("<hr style='margin:4px 0;opacity:0.15'>", unsafe_allow_html=True)


def category_banner(name: str):
    st.markdown(f"<div class='cat-banner'>{name}</div>", unsafe_allow_html=True)


for cat in structure:
    if cat["name"] == "ETC":
        note = cat["note"]
        category_banner("ETC")
        st.info(f"{note['note_number']}. {note['note_text']}")
        continue
    category_banner(cat["name"])
    if "subcategories" in cat:
        for sub in cat["subcategories"]:
            st.markdown(f"<div class='subcat-label'>{sub['name']}</div>", unsafe_allow_html=True)
            render_table(sub["items"], key=f"editor_{sub['row']}")
    else:
        render_table(cat["items"], key=f"editor_{cat['row']}")

st.session_state["remarks"] = remarks_state

result = compute_all(structure, remarks_state)

st.markdown("---")
st.subheader("📊 Rincian Nilai per Kategori")
summary_df = pd.DataFrame([
    {"Kategori": c["name"], "Basic Score": c["basic"], "Actual Score": c["actual"], "%": round(c["percent"], 2)}
    for c in result["categories"]
])
st.dataframe(summary_df, hide_index=True, width="stretch")

m1, m2, m3 = st.columns(3)
m1.metric("TOTAL SCORE (E175)", round(result["grand_percent_sum"], 2))
m2.metric("FINAL SCORE", round(result["final_score"], 2))
m3.metric("GRADING", result["grade"])

st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)

with st.container(key="floating_actions"):
    if st.button("💾 Save", width="stretch"):
        if not st.session_state["store_name"] or not st.session_state["date1"]:
            st.error("STORE NAME & DATE wajib diisi.")
        else:
            try:
                save_draft({
                    "store_name": st.session_state["store_name"],
                    "audit_date": st.session_state["date1"],
                    "date2": st.session_state["date2"],
                    "auditor": st.session_state["auditor"],
                    "pic_on_duty": st.session_state["pic_on_duty"],
                    "remarks": remarks_state,
                })
                st.query_params["store"] = st.session_state["store_name"]
                st.query_params["date"] = st.session_state["date1"]
                st.session_state["loaded_key"] = (st.session_state["store_name"], st.session_state["date1"])
                st.success("Tersimpan!")
            except Exception as e:
                st.error(f"Gagal: {e}")

    wb = build_filled_workbook(
        st.session_state["store_name"], st.session_state["date1"], st.session_state["date2"],
        st.session_state["auditor"], st.session_state["pic_on_duty"], remarks_state,
    )
    fname = f"Audit_{st.session_state['store_name'] or 'Store'}_{st.session_state['date1'] or 'Date'}.xlsx".replace(" ", "_")
    st.download_button(
        "⬇️ Download",
        data=workbook_to_bytes(wb),
        file_name=fname,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

inject_footer()
