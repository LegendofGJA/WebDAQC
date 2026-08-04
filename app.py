import streamlit as st
from style import inject_css, inject_sidebar_brand, inject_footer

st.set_page_config(page_title="Audit & QC Toolkit", page_icon="📸", layout="wide")
inject_css()
inject_sidebar_brand()

# HERO
st.markdown(
    """
    <section class="ilp-hero">
        <div class="ilp-hero-icon">📋</div>
        <h1>Audit &amp; QC Toolkit</h1>
        <p>Isi penilaian audit toko, lalu susun foto QC ke template Excel secara otomatis.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

# TOOL CARDS
st.markdown(
    """
    <div style="display:flex; justify-content:center; gap:24px; margin: 36px 0; flex-wrap:wrap;">
        <a href="/DETAIL_AUDIT" class="tool-card-link" target="_self" style="max-width:380px; width:100%;">
            <div class="tool-card">
                <div class="tool-card-icon">📋</div>
                <h3>DETAIL AUDIT</h3>
                <p>Isi penilaian audit toko, simpan sebagai draft</p>
                <span class="tool-card-tag">MULAI</span>
            </div>
        </a>
        <a href="/QC_Image_Inserter" class="tool-card-link" target="_self" style="max-width:380px; width:100%;">
            <div class="tool-card">
                <div class="tool-card-icon">📸</div>
                <h3>QC Image Inserter</h3>
                <p>Ambil draft audit tersimpan, tempel foto, download Excel</p>
                <span class="tool-card-tag">MULAI</span>
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# STEPS
st.markdown(
    """
    <div class="ilp-steps">
        <div class="ilp-step active"><div class="ilp-step-num">1</div><div class="ilp-step-label">Isi DETAIL AUDIT</div></div>
        <div class="ilp-step-line active"></div>
        <div class="ilp-step active"><div class="ilp-step-num">2</div><div class="ilp-step-label">Simpan Draft</div></div>
        <div class="ilp-step-line active"></div>
        <div class="ilp-step active"><div class="ilp-step-num">3</div><div class="ilp-step-label">Ambil di QC Image Inserter</div></div>
        <div class="ilp-step-line active"></div>
        <div class="ilp-step active"><div class="ilp-step-num">4</div><div class="ilp-step-label">Tempel Foto &amp; Download</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#50506a; font-size:0.85rem;">'
    "Klik kartu tool di atas atau gunakan sidebar di kiri untuk mulai</p>",
    unsafe_allow_html=True,
)

inject_footer()
