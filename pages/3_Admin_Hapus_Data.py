import streamlit as st

from style import inject_css, inject_sidebar_brand, inject_footer
from audit_core import list_saved_drafts, delete_draft, update_draft_by_id

st.set_page_config(page_title="Admin - Hapus Data", page_icon="🔐", layout="wide")
inject_css()
inject_sidebar_brand()

st.markdown(
    """
    <style>
    .admin-row {
        padding: 3px 0;
        font-size: 0.8rem;
    }
    .admin-row [data-testid="stButton"] button {
        font-size: 0.72rem !important;
        padding: 0.25rem 0.5rem !important;
        min-height: 0 !important;
    }
    .admin-row [data-testid="stTextInput"] input {
        font-size: 0.78rem !important;
        padding: 0.3rem 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-head">
        <div class="page-head-icon">🔐</div>
        <h2>Admin — Kelola Data Draft</h2>
        <p>Khusus master/admin. Edit atau hapus draft DETAIL AUDIT dari Supabase.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

if not st.session_state.admin_ok:
    pw = st.text_input("Password Admin", type="password")
    if st.button("Masuk"):
        try:
            correct = st.secrets["ADMIN_PASSWORD"]
        except Exception:
            correct = None
        if correct is None:
            st.error("ADMIN_PASSWORD belum diatur di secrets.")
        elif pw == correct:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Password salah.")
    st.stop()

st.success("Login admin berhasil.")
if st.button("Keluar"):
    st.session_state.admin_ok = False
    st.rerun()

st.markdown("---")

rows = list_saved_drafts(limit=1000)
if not rows:
    st.caption("Belum ada draft tersimpan.")
else:
    st.caption(f"Total {len(rows)} draft tersimpan.")
    for r in rows:
        draft_id = r["id"]
        edit_key = f"edit_{draft_id}"
        confirm_key = f"confirm_{draft_id}"

        with st.container():
            st.markdown('<div class="admin-row">', unsafe_allow_html=True)

            if st.session_state.get(edit_key):
                # --- MODE EDIT: ubah Store Name & Date ---
                ce1, ce2, ce3, ce4 = st.columns([2.5, 2, 0.8, 0.8])
                new_name = ce1.text_input("Store Name", value=r["store_name"], key=f"name_{draft_id}", label_visibility="collapsed")
                new_date = ce2.text_input("Date", value=r["audit_date"], key=f"date_{draft_id}", label_visibility="collapsed")
                if ce3.button("💾", key=f"savebtn_{draft_id}", help="Simpan perubahan"):
                    try:
                        update_draft_by_id(draft_id, {
                            "store_name": new_name.strip(),
                            "audit_date": new_date.strip(),
                        })
                        st.success("Diperbarui.")
                        st.session_state[edit_key] = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal: {e}")
                if ce4.button("✖️", key=f"cancelbtn_{draft_id}", help="Batal"):
                    st.session_state[edit_key] = False
                    st.rerun()
            else:
                c1, c2, c3, c4 = st.columns([2.5, 2, 0.8, 0.8])
                c1.markdown(f"**{r['store_name']}**")
                c2.markdown(
                    f"{r['audit_date']}  \n<span style='font-size:0.68rem;color:#8888a5;'>update: {r['updated_at'][:16].replace('T',' ')}</span>",
                    unsafe_allow_html=True,
                )
                if c3.button("✏️", key=f"editbtn_{draft_id}", help="Edit nama/tanggal"):
                    st.session_state[edit_key] = True
                    st.rerun()

                if st.session_state.get(confirm_key):
                    if c4.button("⚠️", key=f"yesdel_{draft_id}", help="Yakin hapus?"):
                        try:
                            delete_draft(r["store_name"], r["audit_date"])
                            st.success(f"Draft '{r['store_name']} — {r['audit_date']}' dihapus.")
                            st.session_state[confirm_key] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal hapus: {e}")
                else:
                    if c4.button("🗑️", key=f"delbtn_{draft_id}", help="Hapus draft"):
                        st.session_state[confirm_key] = True
                        st.rerun()

            st.markdown("</div><hr style='margin:2px 0;opacity:0.12'>", unsafe_allow_html=True)

inject_footer()
