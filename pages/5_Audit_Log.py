import pandas as pd
import streamlit as st

from style import inject_css, inject_sidebar_brand, inject_footer
from audit_core import get_supabase_client

st.set_page_config(page_title="Audit Log", page_icon="📝", layout="wide")
inject_css()
inject_sidebar_brand()

st.markdown(
    """
    <div class="page-head">
        <div class="page-head-icon">📝</div>
        <h2>Audit Log</h2>
        <p>Riwayat Save & Download di halaman DETAIL AUDIT</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Password protection ──
if "audit_log_ok" not in st.session_state:
    st.session_state.audit_log_ok = False

if not st.session_state.audit_log_ok:
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        try:
            correct = st.secrets["TRAFFIC_LOG_PASSWORD"]
        except Exception:
            correct = None
        if correct is None:
            st.error("TRAFFIC_LOG_PASSWORD belum diatur di secrets.")
        elif pw == correct:
            st.session_state.audit_log_ok = True
            st.rerun()
        else:
            st.error("Password salah.")
    st.stop()

st.success("Login berhasil.")
if st.button("Keluar"):
    st.session_state.audit_log_ok = False
    st.rerun()

st.markdown("---")

if st.button("🔄 Refresh"):
    st.cache_data.clear()


@st.cache_data(ttl=60)
def fetch_audit_log():
    supabase = get_supabase_client()
    if supabase is None:
        return []
    try:
        resp = (
            supabase.table("audit_traffic_log")
            .select("*")
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )
        data = resp.data or []
        formatted = []
        for r in data:
            ts = r.get("created_at", "")
            if ts:
                ts = ts[:19].replace("T", " ")
            formatted.append({
                "Auditor": r.get("auditor", ""),
                "Store": r.get("store_name", ""),
                "Date QC": r.get("audit_date", ""),
                "Score": r.get("score_info", ""),
                "Action": r.get("action", ""),
                "Timestamp": ts,
            })
        return formatted
    except Exception:
        return []


try:
    data = fetch_audit_log()
except Exception as e:
    st.error(f"Gagal mengambil data log: {e}")
    data = []

if not data:
    st.caption("Belum ada log tercatat.")
else:
    df = pd.DataFrame(data)
    st.caption(f"Total {len(df)} aktivitas tercatat.")

    with st.expander("🔍 Filter"):
        f1, f2, f3 = st.columns(3)
        auditor_filter = f1.text_input("Filter Auditor")
        store_filter = f2.text_input("Filter Store")
        action_filter = f3.selectbox("Filter Action", ["Semua", "Save", "Download"])

    if auditor_filter:
        df = df[df["Auditor"].astype(str).str.contains(auditor_filter, case=False, na=False)]
    if store_filter:
        df = df[df["Store"].astype(str).str.contains(store_filter, case=False, na=False)]
    if action_filter != "Semua":
        df = df[df["Action"] == action_filter]

    st.dataframe(df, hide_index=True, width="stretch")

inject_footer()
