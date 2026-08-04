import streamlit as st

from style import inject_css, inject_sidebar_brand, inject_footer
from audit_core import list_saved_drafts, delete_draft

st.set_page_config(page_title="Admin - Hapus Data", page_icon="🔐", layout="wide")
inject_css()
inject_sidebar_brand()

st.markdown(
    """
    <div class="page-head">
        <div class="page-head-icon">🔐</div>
        <h2>Admin — Hapus Data Draft</h2>
        <p>Khusus master/admin. Menghapus draft DETAIL AUDIT dari Supabase secara permanen.</p>
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
            st.error("ADMIN_PASSWORD belum diatur di secrets. Tambahkan dulu, lihat README.")
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
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f"**{r['store_name']}**")
        c2.markdown(f"{r['audit_date']}  \n<span style='font-size:0.75rem;color:#8888a5;'>update: {r['updated_at'][:16].replace('T',' ')}</span>", unsafe_allow_html=True)
        confirm_key = f"confirm_{r['store_name']}_{r['audit_date']}"
        if st.session_state.get(confirm_key):
            if c3.button("⚠️ Yakin?", key=f"yes_{confirm_key}"):
                try:
                    delete_draft(r["store_name"], r["audit_date"])
                    st.success(f"Draft '{r['store_name']} — {r['audit_date']}' dihapus.")
                    st.session_state[confirm_key] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal hapus: {e}")
        else:
            if c3.button("🗑️ Hapus", key=f"del_{confirm_key}"):
                st.session_state[confirm_key] = True
                st.rerun()
        st.markdown("<hr style='margin:4px 0;opacity:0.15'>", unsafe_allow_html=True)

inject_footer()
