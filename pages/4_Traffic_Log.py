import pandas as pd
import requests
import streamlit as st

from style import inject_css, inject_sidebar_brand, inject_footer

JSONBLOB_ID = "019e8740-72c4-7731-8328-0e2c67465233"
API_URL = f"https://jsonblob.com/api/jsonBlob/{JSONBLOB_ID}"

st.set_page_config(page_title="Traffic Log", page_icon="📈", layout="wide")
inject_css()
inject_sidebar_brand()

st.markdown(
    """
    <div class="page-head">
        <div class="page-head-icon">📈</div>
        <h2>Traffic Log</h2>
        <p>Riwayat pemakaian QC Image Inserter (siapa, toko mana, kapan)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "traffic_ok" not in st.session_state:
    st.session_state.traffic_ok = False

if not st.session_state.traffic_ok:
    pw = st.text_input("Password Traffic Log", type="password")
    if st.button("Masuk"):
        try:
            correct = st.secrets["TRAFFIC_LOG_PASSWORD"]
        except Exception:
            correct = None
        if correct is None:
            st.error("TRAFFIC_LOG_PASSWORD belum diatur di secrets.")
        elif pw == correct:
            st.session_state.traffic_ok = True
            st.rerun()
        else:
            st.error("Password salah.")
    st.stop()

st.success("Login berhasil.")
if st.button("Keluar"):
    st.session_state.traffic_ok = False
    st.rerun()

st.markdown("---")

if st.button("🔄 Refresh"):
    st.cache_data.clear()


@st.cache_data(ttl=60)
def fetch_log():
    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        data = []
    return data


try:
    data = fetch_log()
except Exception as e:
    st.error(f"Gagal mengambil data log: {e}")
    data = []

if not data:
    st.caption("Belum ada log tercatat.")
else:
    # entri terbaru ditambahkan paling akhir oleh log_traffic() -> balik urutannya
    data_sorted = list(reversed(data))
    df = pd.DataFrame(data_sorted)

    st.caption(f"Total {len(df)} aktivitas tercatat.")

    with st.expander("🔍 Filter"):
        f1, f2 = st.columns(2)
        nama_filter = f1.text_input("Filter Nama Pengguna")
        toko_filter = f2.text_input("Filter Nama Toko")

    if nama_filter:
        df = df[df.get("Nama Pengguna", "").astype(str).str.contains(nama_filter, case=False, na=False)]
    if toko_filter:
        df = df[df.get("Nama Toko", "").astype(str).str.contains(toko_filter, case=False, na=False)]

    st.dataframe(df, hide_index=True, width="stretch")

st.caption(
    "Catatan: log ini disimpan di layanan pihak ketiga (JSONBlob), bukan Supabase. "
    "Halaman ini hanya menampilkan (read-only)."
)

inject_footer()
