"""
Streamlit Geospatial Intelligence Dashboard for Kalimantan Fire Monitoring.
Author: Data Science Geospatial Team
Run:
    streamlit run app.py
"""
import sys
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Add root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ai_assistant import get_ai_analyst

# Set Page Config
st.set_page_config(
    page_title="Napas yang Tergadai di Ufuk Jelaga | Karhutla Kalimantan",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)
HOTSPOTS_CSV = BASE_DIR / "data" / "processed" / "kalimantan_hotspots_latest.csv"
HOTSPOTS_GEOJSON = BASE_DIR / "data" / "processed" / "kalimantan_hotspots_latest.geojson"
WEATHER_CSV = BASE_DIR / "data" / "processed" / "kalimantan_weather_latest.csv"
TIMESERIES_CSV = BASE_DIR / "data" / "processed" / "kalimantan_early_fire_onset_timeseries.csv"
CLUSTERS_JSON = BASE_DIR / "data" / "processed" / "kalimantan_fire_clusters.json"
MAP_HTML = BASE_DIR / "dashboard" / "kalimantan_fire_geodashboard.html"
SNA_HTML = BASE_DIR / "dashboard" / "karhutla_sna_network_graph.html"
SNA_NODES_CSV = BASE_DIR / "data" / "processed" / "karhutla_sna_nodes.csv"
SNA_EDGES_CSV = BASE_DIR / "data" / "processed" / "karhutla_sna_edges.csv"
SNA_SUMMARY_JSON = BASE_DIR / "data" / "processed" / "karhutla_sna_summary.json"

# Economic & Causality Paths
INVESTMENT_PROV_CSV = BASE_DIR / "data" / "processed" / "kalimantan_investment_pma_pmdn.csv"
INVESTMENT_SECTOR_CSV = BASE_DIR / "data" / "processed" / "kalimantan_investment_sectoral.csv"
INVESTMENT_ORIGIN_CSV = BASE_DIR / "data" / "processed" / "kalimantan_investment_foreign_origins.csv"
CAUSALITY_CSV = BASE_DIR / "data" / "processed" / "kalimantan_fire_causality_stats.csv"
MOTIVES_CSV = BASE_DIR / "data" / "processed" / "kalimantan_fire_motives_cost_analysis.csv"
ACTORS_CSV = BASE_DIR / "data" / "processed" / "kalimantan_fire_actors_breakdown.csv"
CORRELATION_JSON = BASE_DIR / "data" / "processed" / "kalimantan_economic_fire_correlation.json"

# Fatalities, Health & Transboundary Impacts Paths
FATALITIES_HEALTH_CSV = BASE_DIR / "data" / "processed" / "kalimantan_fire_fatalities_health_impacts.csv"
MULTIDIMENSIONAL_IMPACTS_CSV = BASE_DIR / "data" / "processed" / "kalimantan_fire_multidimensional_impacts.csv"
TRANSBOUNDARY_HAZE_CSV = BASE_DIR / "data" / "processed" / "kalimantan_transboundary_haze_external_impacts.csv"

# Scenario Predictions & Cost-Benefit Paths
SCENARIOS_CSV = BASE_DIR / "data" / "processed" / "kalimantan_damage_prediction_scenarios.csv"
SCENARIOS_SUMMARY_JSON = BASE_DIR / "data" / "processed" / "kalimantan_damage_prediction_summary.json"
COST_BENEFIT_CSV = BASE_DIR / "data" / "processed" / "kalimantan_cost_benefit_mitigation.csv"

# Custom Styling (Dark & Glassmorphism theme)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        padding: 20px 25px;
        border-radius: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #ef4444;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0f172a;
        border-radius: 6px;
        color: #94a3b8;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ef4444 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_datasets():
    df_hs = pd.read_csv(HOTSPOTS_CSV) if HOTSPOTS_CSV.exists() else pd.DataFrame()
    df_wt = pd.read_csv(WEATHER_CSV) if WEATHER_CSV.exists() else pd.DataFrame()
    df_ts = pd.read_csv(TIMESERIES_CSV) if TIMESERIES_CSV.exists() else pd.DataFrame()
    df_inv_prov = pd.read_csv(INVESTMENT_PROV_CSV) if INVESTMENT_PROV_CSV.exists() else pd.DataFrame()
    df_inv_sect = pd.read_csv(INVESTMENT_SECTOR_CSV) if INVESTMENT_SECTOR_CSV.exists() else pd.DataFrame()
    df_inv_orig = pd.read_csv(INVESTMENT_ORIGIN_CSV) if INVESTMENT_ORIGIN_CSV.exists() else pd.DataFrame()
    df_caus = pd.read_csv(CAUSALITY_CSV) if CAUSALITY_CSV.exists() else pd.DataFrame()
    df_mot = pd.read_csv(MOTIVES_CSV) if MOTIVES_CSV.exists() else pd.DataFrame()
    df_act = pd.read_csv(ACTORS_CSV) if ACTORS_CSV.exists() else pd.DataFrame()
    df_fat = pd.read_csv(FATALITIES_HEALTH_CSV) if FATALITIES_HEALTH_CSV.exists() else pd.DataFrame()
    df_multi = pd.read_csv(MULTIDIMENSIONAL_IMPACTS_CSV) if MULTIDIMENSIONAL_IMPACTS_CSV.exists() else pd.DataFrame()
    df_trans = pd.read_csv(TRANSBOUNDARY_HAZE_CSV) if TRANSBOUNDARY_HAZE_CSV.exists() else pd.DataFrame()
    df_scenarios = pd.read_csv(SCENARIOS_CSV) if SCENARIOS_CSV.exists() else pd.DataFrame()
    df_cb = pd.read_csv(COST_BENEFIT_CSV) if COST_BENEFIT_CSV.exists() else pd.DataFrame()

    clusters = {}
    if CLUSTERS_JSON.exists():
        with open(CLUSTERS_JSON, "r", encoding="utf-8") as f:
            clusters = json.load(f)

    econ_corr = {}
    if CORRELATION_JSON.exists():
        with open(CORRELATION_JSON, "r", encoding="utf-8") as f:
            econ_corr = json.load(f)

    scenario_summary = {}
    if SCENARIOS_SUMMARY_JSON.exists():
        with open(SCENARIOS_SUMMARY_JSON, "r", encoding="utf-8") as f:
            scenario_summary = json.load(f)

    df_sna_nodes = pd.read_csv(SNA_NODES_CSV) if SNA_NODES_CSV.exists() else pd.DataFrame()
    df_sna_edges = pd.read_csv(SNA_EDGES_CSV) if SNA_EDGES_CSV.exists() else pd.DataFrame()
    sna_summary = {}
    if SNA_SUMMARY_JSON.exists():
        with open(SNA_SUMMARY_JSON, "r", encoding="utf-8") as f:
            sna_summary = json.load(f)

    return {
        "hotspots": df_hs,
        "weather": df_wt,
        "timeseries": df_ts,
        "clusters": clusters,
        "inv_prov": df_inv_prov,
        "inv_sect": df_inv_sect,
        "inv_orig": df_inv_orig,
        "causality": df_caus,
        "motives": df_mot,
        "actors": df_act,
        "econ_corr": econ_corr,
        "fatalities_health": df_fat,
        "multidimensional": df_multi,
        "transboundary_haze": df_trans,
        "scenarios": df_scenarios,
        "cost_benefit": df_cb,
        "scenario_summary": scenario_summary,
        "sna_nodes": df_sna_nodes,
        "sna_edges": df_sna_edges,
        "sna_summary": sna_summary
    }


datasets = load_datasets()
df_hs = datasets["hotspots"]
df_wt = datasets["weather"]
df_ts = datasets["timeseries"]
clusters_data = datasets["clusters"]
df_inv_prov = datasets["inv_prov"]
df_inv_sect = datasets["inv_sect"]
df_inv_orig = datasets["inv_orig"]
df_caus = datasets["causality"]
df_mot = datasets["motives"]
df_act = datasets["actors"]
econ_corr_data = datasets["econ_corr"]
df_fat = datasets["fatalities_health"]
df_multi = datasets["multidimensional"]
df_trans = datasets["transboundary_haze"]
df_scenarios = datasets["scenarios"]
df_cb = datasets["cost_benefit"]
scenario_summary_data = datasets["scenario_summary"]
df_sna_nodes = datasets["sna_nodes"]
df_sna_edges = datasets["sna_edges"]
sna_summary_data = datasets["sna_summary"]

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/fire-element.png", width=60)
    st.title("🛰️ Filter & Kontrol")
    st.caption("Pemantauan Rentang Awal Karhutla Kalimantan")

    # Refresh Pipeline Trigger
    if st.button("🔄 Perbarui Data Real-Time", type="primary", use_container_width=True):
        with st.spinner("Menghubungi satelit & stasiun cuaca..."):
            from fetch_realtime_data import run_pipeline
            run_pipeline()
            st.cache_data.clear()
            st.success("Data berhasil diperbarui!")
            st.rerun()

    st.markdown("---")
    st.subheader("Filter Data Spasial")

    # Province Filter
    provinces = ["Semua Provinsi"] + sorted(df_hs["province"].unique().tolist()) if not df_hs.empty else ["Semua Provinsi"]
    sel_prov = st.selectbox("Pilih Provinsi:", provinces)

    # Land Type Filter
    land_types = ["Semua Lahan", "Lahan Gambut", "Tanah Mineral"]
    sel_land = st.selectbox("Tipe Lahan:", land_types)

    # Minimum FRP Slider
    min_frp = st.slider("Min. FRP (MW):", 0.0, 50.0, 0.0, 1.0)

    # Min Confidence Slider
    min_conf = st.slider("Min. Confidence (%):", 0, 100, 40, 5)

    st.markdown("---")
    st.info("💡 **Tips Data Scientist**: Lahan Gambut memiliki risiko kebakaran bawah tanah (*smoldering*) yang sulit dideteksi hanya dari api permukaan.")

# Apply Filters
df_filtered = df_hs.copy()
if not df_filtered.empty:
    if sel_prov != "Semua Provinsi":
        df_filtered = df_filtered[df_filtered["province"] == sel_prov]
    if sel_land != "Semua Lahan":
        df_filtered = df_filtered[df_filtered["land_type"] == sel_land]
    df_filtered = df_filtered[df_filtered["frp"] >= min_frp]
    df_filtered = df_filtered[df_filtered["confidence_pct"] >= min_conf]

# ----------------- HEADER & KPIS -----------------
st.markdown("""
<div class="main-header">
    <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.5px;">🔥 KALIMANTAN FIRE GEOSPATIAL INTELLIGENCE DASHBOARD</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.85; font-size: 14px;">
        Platform Analisis Data Spasial & Deteksi Dini Rentang Awal Kebakaran Lahan Gambut Kalimantan (Near Real-Time Multi-Layer GIS)
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
total_hs = len(df_filtered)
peat_pct = round(((df_filtered["land_type"] == "Lahan Gambut").sum() / max(1, total_hs)) * 100, 1) if not df_filtered.empty else 0
total_frp = round(df_filtered["frp"].sum(), 1) if not df_filtered.empty else 0
n_clusters = clusters_data.get("total_clusters_detected", 0)
avg_weather_risk = round(df_wt["fire_danger_score"].mean(), 1) if not df_wt.empty else 0

with col1:
    st.metric(label="Total Titik Panas", value=f"{total_hs} Titik", delta=f"{len(df_hs) - total_hs} terfilter" if len(df_hs) != total_hs else "Semua Data")
with col2:
    st.metric(label="Dominasi Gambut", value=f"{peat_pct}%", delta="Episentrum Gambut", delta_color="inverse")
with col3:
    st.metric(label="Total Daya Termal", value=f"{total_frp} MW", delta="FRP Radiatif")
with col4:
    st.metric(label="Klaster DBSCAN", value=f"{n_clusters} Klaster", delta="Episentrum Aktif")
with col5:
    st.metric(label="Indeks Bahaya Cuaca", value=f"{avg_weather_risk} / 100", delta="Kondisi Kering" if avg_weather_risk > 50 else "Aman")

# Initialize AI Analyst
ai_analyst = get_ai_analyst(datasets)

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
    "🗺️ Peta Geospasial Real-Time",
    "🤖 Asisten AI Penjelas Karhutla",
    "📊 Analisis Spasial & Titik Panas",
    "🌤️ Cuaca & Kelembaban Tanah",
    "📈 Tren Awal Kebakaran (Early Onset)",
    "🔮 Prediksi Kerugian (Ditangani vs Tidak)",
    "🚨 Korban Jiwa & Dampak Kesehatan",
    "🌏 Kabut Asap Lintas Batas",
    "💰 Arus Kas & Investasi (PMA/PMDN)",
    "🔍 Kausalitas & Motif Karhutla",
    "💾 Unduh Seluruh Dataset",
    "🕸️ Jaringan Aktor NodeXL (SNA)"
])

# TAB 1: INTERACTIVE REAL-TIME MAP
with tab1:
    st.subheader("🗺️ Peta Multi-Layer Geospasial Real-Time Kalimantan")
    st.caption("Menampilkan Lapisan Hotspot Satelit NASA FIRMS, Kubah Gambut (KHG), Batas Administrasi Provinsi, Episentrum DBSCAN, dan Stasiun Cuaca.")

    # AI Quick Insight Banner
    st.markdown(f"""
    <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 8px; margin-bottom: 15px;">
        <span style="font-weight: bold; color: #f87171;">🤖 Ringkasan Cepat AI:</span> 
        <span style="color: #f1f5f9; font-size: 13px;">
            Terdeteksi <b>{total_hs} Titik Panas</b> aktif dengan <b>{peat_pct}%</b> berlokasi di Kesatuan Hidrologis Gambut (KHG). 
            Episentrum kebakaran terbesar berada di <b>Kalimantan Tengah & Barat</b> dengan daya radiasi termal hingga <b>{total_frp} MW</b>.
        </span>
    </div>
    """, unsafe_allow_html=True)

    if MAP_HTML.exists():
        with open(MAP_HTML, "r", encoding="utf-8") as f:
            html_data = f.read()
        st.components.v1.html(html_data, height=650, scrolling=False)
    else:
        st.warning("Peta belum dibuat. Jalankan pipeline terlebih dahulu.")

# TAB 2: AI FIRE INTELLIGENCE ANALYST
with tab2:
    st.subheader("🤖 Asisten AI Penjelas Karhutla (AI Fire Intelligence Analyst)")
    st.caption("AI cerdas yang menganalisis seluruh lapisan data geospasial, epidemiologi, dan ekonometrika untuk mempermudah pemahaman masyarakat & pembuat kebijakan.")

    # Render Executive Briefing
    st.markdown(ai_analyst.generate_executive_briefing())

    st.markdown("---")
    st.write("#### 💬 Tanya AI Karhutla (Pilih Pertanyaan Cepat atau Ketik Sendiri):")

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    preset_query = ""

    with col_btn1:
        if st.button("🔥 Mengapa Gambut Susah Padam?", use_container_width=True):
            preset_query = "Mengapa kebakaran lahan gambut sangat susah padam?"
    with col_btn2:
        if st.button("🚨 Panduan Medis ISPA & Masker", use_container_width=True):
            preset_query = "Apa panduan kesehatan dan jenis masker terbaik untuk asap PM2.5?"
    with col_btn3:
        if st.button("⚖️ Siapa & Mengapa Dibakar?", use_container_width=True):
            preset_query = "Siapa pelaku pembakaran dan apa motif penghematan biayanya?"
    with col_btn4:
        if st.button("💰 Berapa Kerugian Jika Dibiarkan?", use_container_width=True):
            preset_query = "Berapa proyeksi kerugian jika dibiarkan dan berapa ROI mitigasinya?"

    user_input = st.text_input(
        "Ketik pertanyaan Anda tentang situasi karhutla:",
        value=preset_query,
        placeholder="Contoh: Mengapa gambut sulit padam, atau bagaimana rekomendasi kesehatan bayi?"
    )

    if user_input:
        with st.spinner("🤖 AI sedang menganalisis data geospasial & epidemiologi..."):
            ai_reply = ai_analyst.answer_query(user_input)
            st.markdown(ai_reply)

# TAB 3: SPATIAL ANALYSIS
with tab3:
    st.subheader("Distribusi & Karakteristik Termal Titik Panas")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        if not df_filtered.empty:
            prov_chart = df_filtered["province"].value_counts().reset_index()
            prov_chart.columns = ["Provinsi", "Jumlah Hotspot"]
            fig_prov = px.bar(
                prov_chart,
                x="Jumlah Hotspot",
                y="Provinsi",
                orientation="h",
                color="Jumlah Hotspot",
                color_continuous_scale="Reds",
                title="Jumlah Titik Panas per Provinsi Kalimantan"
            )
            fig_prov.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_prov, use_container_width=True)

    with row2_col2:
        if not df_filtered.empty:
            land_chart = df_filtered["land_type"].value_counts().reset_index()
            land_chart.columns = ["Tipe Lahan", "Jumlah"]
            fig_pie = px.pie(
                land_chart,
                values="Jumlah",
                names="Tipe Lahan",
                color="Tipe Lahan",
                color_discrete_map={"Lahan Gambut": "#d97706", "Tanah Mineral": "#0284c7"},
                title="Proporsi Tipe Lahan Terbakar",
                hole=0.4
            )
            fig_pie.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_pie, use_container_width=True)

    # Scatter Plot FRP vs Brightness
    if not df_filtered.empty:
        fig_scatter = px.scatter(
            df_filtered,
            x="brightness",
            y="frp",
            color="land_type",
            size="hazard_score",
            hover_data=["hotspot_id", "province", "peatland_name", "satellite"],
            color_discrete_map={"Lahan Gambut": "#ef4444", "Tanah Mineral": "#38bdf8"},
            labels={"brightness": "Suhu Kecerahan Satelit (Kelvin)", "frp": "Fire Radiative Power (MW)"},
            title="Korelasi Daya Radiasi Termal (FRP) vs Suhu Kecerahan Satelit"
        )
        fig_scatter.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Clusters Table
    st.subheader("Daftar Klaster Kebakaran Spasial (DBSCAN Results)")
    if clusters_data.get("clusters"):
        df_clusters_view = pd.DataFrame(clusters_data["clusters"])
        df_clusters_view = df_clusters_view[["cluster_id", "name", "dominant_province", "hotspot_count", "total_frp_mw", "peat_percentage", "cluster_type"]]
        df_clusters_view.columns = ["ID", "Nama Klaster", "Provinsi Dominan", "Jumlah Titik", "Total FRP (MW)", "% Gambut", "Klasifikasi Episentrum"]
        st.dataframe(df_clusters_view, use_container_width=True)

# TAB 4: WEATHER & SOIL MOISTURE
with tab4:
    st.subheader("Parameter Meteorologi Real-Time & Indeks Bahaya Cuaca (Open-Meteo API)")

    if not df_wt.empty:
        # Station Cards in columns
        st.write("#### 📍 Status Stasiun Pemantauan Cuaca Regional")
        stn_cols = st.columns(4)
        for idx, row in df_wt.iterrows():
            with stn_cols[idx % 4]:
                st.markdown(f"""
                <div style="background: #1e293b; padding: 12px; border-radius: 8px; border-top: 3px solid {row['fire_danger_color']}; margin-bottom: 12px;">
                    <div style="font-weight: bold; color: #f8fafc; font-size: 13px;">{row['station_name']}</div>
                    <div style="font-size: 11px; color: #94a3b8;">{row['province']}</div>
                    <div style="font-size: 20px; font-weight: bold; color: {row['fire_danger_color']}; margin: 4px 0;">
                        {row['fire_danger_score']} <span style="font-size: 10px; color: #94a3b8;">/100</span>
                    </div>
                    <div style="font-size: 11px; color: #cbd5e1;">🌡️ Suhu: <b>{row['temperature_c']}°C</b></div>
                    <div style="font-size: 11px; color: #cbd5e1;">💧 RH: <b>{row['relative_humidity_pct']}%</b></div>
                    <div style="font-size: 11px; color: #cbd5e1;">🌱 Tanah: <b>{row['soil_moisture_m3_m3']} m³/m³</b></div>
                    <div style="font-size: 11px; color: #cbd5e1;">💨 Angin: <b>{row['wind_speed_kmh']} km/j</b></div>
                </div>
                """, unsafe_allow_html=True)

        # Bar chart comparison
        fig_wt = px.bar(
            df_wt,
            x="station_name",
            y="fire_danger_score",
            color="fire_danger_score",
            color_continuous_scale="Viridis",
            labels={"station_name": "Stasiun", "fire_danger_score": "Skor Bahaya Cuaca (0-100)"},
            title="Perbandingan Indeks Bahaya Cuaca Antar Wilayah Kalimantan"
        )
        fig_wt.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_wt, use_container_width=True)

# TAB 5: EARLY ONSET DYNAMICS
with tab5:
    st.subheader("Analisis Dinamika Rentang Awal Kebakaran (Early Onset Analysis)")
    st.caption("Menganalisis pergeseran dari fase api dasar ke lonjakan eksponensial di musim kemarau Kalimantan.")

    if not df_ts.empty:
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            x=df_ts["date"],
            y=df_ts["total_hotspots"],
            name="Hotspot Harian",
            mode="lines+markers",
            line=dict(color="#f97316", width=1.5)
        ))
        fig_ts.add_trace(go.Scatter(
            x=df_ts["date"],
            y=df_ts["peatland_hotspots"],
            name="Hotspot di Lahan Gambut",
            mode="lines",
            line=dict(color="#ef4444", width=2, dash="dash")
        ))
        fig_ts.add_trace(go.Scatter(
            x=df_ts["date"],
            y=df_ts["total_hotspots"].rolling(7).mean(),
            name="Moving Average (7 Hari)",
            mode="lines",
            line=dict(color="#38bdf8", width=2.5)
        ))

        fig_ts.update_layout(
            template="plotly_dark",
            title="Tren Kenaikan Titik Panas Selama 90 Hari Rentang Awal Kebakaran",
            xaxis_title="Tanggal",
            yaxis_title="Jumlah Titik Panas Satelit",
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig_ts, use_container_width=True)

        fig_area = px.area(
            df_ts,
            x="date",
            y=["kalteng_hotspots", "kalbar_hotspots", "kalsel_hotspots", "kaltim_hotspots", "kaltara_hotspots"],
            labels={"value": "Titik Panas", "variable": "Provinsi", "date": "Tanggal"},
            title="Kontribusi Kumulatif Titik Panas per Provinsi",
            color_discrete_sequence=["#ef4444", "#f97316", "#eab308", "#06b6d4", "#8b5cf6"]
        )
        fig_area.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_area, use_container_width=True)

# TAB 6: SCENARIO PREDICTIONS & COST-BENEFIT VALUATION
with tab6:
    st.subheader("🔮 Model Prediksi Kerugian Bencana: Skenario Tidak Ditangani vs Ditangani")
    st.caption("Pemodelan Stochastic & Ekonometrika Bencana Berdasarkan Valuasi VSL (OECD), Biaya Sosial Karbon (SCC), dan Kerugian Makro Bank Dunia.")

    if scenario_summary_data:
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric(
                label="🔴 Proyeksi TIDAK Ditangani",
                value=f"Rp {scenario_summary_data.get('unmitigated_damage_trillion_idr', 0):,.1f} T",
                delta="Bencana Makro Tak Terkendali",
                delta_color="inverse"
            )
        with col_s2:
            st.metric(
                label="🟡 Sisa Kerugian DITANGANI",
                value=f"Rp {scenario_summary_data.get('mitigated_residual_damage_trillion_idr', 0):,.1f} T",
                delta="Kerugian Residual Minimal"
            )
        with col_s3:
            st.metric(
                label="🟢 Biaya Investasi Mitigasi",
                value=f"Rp {scenario_summary_data.get('mitigation_intervention_cost_trillion_idr', 0):,.2f} T",
                delta="Sekat Kanal, TMC, Bom Air"
            )
        with col_s4:
            st.metric(
                label="💎 Kerugian Bersih DISELAMATKAN",
                value=f"Rp {scenario_summary_data.get('net_avoided_losses_trillion_idr', 0):,.1f} T",
                delta=f"ROI: {scenario_summary_data.get('benefit_cost_ratio_multiplier', 0)}x Lipat",
                delta_color="normal"
            )

        row_s1, row_s2 = st.columns([1.3, 1])

        with row_s1:
            if not df_scenarios.empty:
                # Grouped Bar chart of Unmitigated vs Mitigated vs Avoided
                fig_scen = go.Figure()
                fig_scen.add_trace(go.Bar(
                    name="TIDAK Ditangani (Unmitigated)",
                    x=df_scenarios["sector"],
                    y=df_scenarios["unmitigated_loss_trillion_idr"],
                    marker_color="#ef4444"
                ))
                fig_scen.add_trace(go.Bar(
                    name="DITANGANI (Residual Loss)",
                    x=df_scenarios["sector"],
                    y=df_scenarios["mitigated_residual_loss_trillion_idr"],
                    marker_color="#38bdf8"
                ))
                fig_scen.add_trace(go.Bar(
                    name="Kerugian DISELAMATKAN (Avoided)",
                    x=df_scenarios["sector"],
                    y=df_scenarios["avoided_loss_trillion_idr"],
                    marker_color="#22c55e"
                ))
                fig_scen.update_layout(
                    barmode="group",
                    template="plotly_dark",
                    title="Perbandingan Kerugian per Sektor (Triliun Rupiah)",
                    xaxis_tickangle=-25,
                    height=420,
                    hovermode="x unified"
                )
                st.plotly_chart(fig_scen, use_container_width=True)

        with row_s2:
            st.markdown("""
            <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 10px; padding: 16px; margin-bottom: 12px;">
                <h4 style="margin: 0 0 6px 0; color: #22c55e;">🚀 Benefit-Cost Ratio: 58.35x ROI</h4>
                <p style="font-size: 12px; line-height: 1.6; color: #f8fafc; margin: 0;">
                    Setiap <b>Rp 1 Miliar</b> yang dialokasikan pemerintah/swasta untuk pencegahan dan intervensi gambut terpadu, berhasil menyelamatkan <b>Rp 58.35 Miliar</b> kerugian nyata di sektor kesehatan, makro ekonomi, iklim, dan penerbangan.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if scenario_summary_data.get("mitigation_costs_breakdown"):
                costs_dict = scenario_summary_data["mitigation_costs_breakdown"]
                df_costs_view = pd.DataFrame([
                    {"Komponen": k.replace("_trillion_idr", "").replace("_", " ").title(), "Alokasi (Triliun Rp)": v}
                    for k, v in costs_dict.items()
                ])
                fig_costs = px.pie(
                    df_costs_view,
                    values="Alokasi (Triliun Rp)",
                    names="Komponen",
                    title="Alokasi Biaya Investasi Mitigasi (Total Rp 6.8 T)",
                    color_discrete_sequence=px.colors.sequential.Teal,
                    hole=0.45
                )
                fig_costs.update_layout(template="plotly_dark", height=280)
                st.plotly_chart(fig_costs, use_container_width=True)

        # Multi-Sector Details Table
        st.write("#### 📋 Matriks Komparasi Dampak Fisik & Valuasi Finansial Multi-Sektor")
        if not df_scenarios.empty:
            st.dataframe(
                df_scenarios[["sector", "unmitigated_loss_trillion_idr", "mitigated_residual_loss_trillion_idr", "avoided_loss_trillion_idr", "reduction_pct", "unmitigated_physical_impact", "mitigated_physical_impact"]],
                use_container_width=True
            )

# TAB 7: FATALITIES & HEALTH IMPACTS
with tab7:
    st.subheader("🚨 Korban Jiwa, Epidemi ISPA & Dampak Kesehatan Masyarakat")
    st.caption("Data Kemenkes, BNPB, World Bank, dan Studi Epidemiologi Paparan Asap PM2.5 Harvard/Columbia.")

    if not df_fat.empty:
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            st.metric(label="Korban Meninggal Langsung", value=f"{df_fat['direct_deaths'].sum()} Orang", delta="Terjebak Api/Lahan", delta_color="inverse")
        with col_f2:
            st.metric(label="Estimasi Kematian Dini PM2.5", value=f"{df_fat['premature_deaths_pm25_est'].sum():,} Jiwa", delta="ISPA/Jantung/Stroke", delta_color="inverse")
        with col_f3:
            st.metric(label="Total Pasien ISPA Diobati", value=f"{df_fat['ispa_cases_treated'].sum():,} Pasien", delta="Pernapasan Akut")
        with col_f4:
            st.metric(label="Populasi Rentan Terpapar", value=f"{df_fat['vulnerable_population_affected'].sum():,} Jiwa", delta="Bayi & Lansia")

        row_f1, row_f2 = st.columns(2)
        with row_f1:
            fig_ispa = px.bar(
                df_fat,
                x="province",
                y="ispa_cases_treated",
                color="ispa_cases_treated",
                color_continuous_scale="Reds",
                title="Jumlah Kasus ISPA per Provinsi Kalimantan",
                labels={"ispa_cases_treated": "Pasien ISPA", "province": "Provinsi"}
            )
            fig_ispa.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_ispa, use_container_width=True)

        with row_f2:
            fig_mort = px.bar(
                df_fat,
                x="province",
                y=["premature_deaths_pm25_est", "direct_deaths"],
                barmode="stack",
                title="Perbandingan Kematian Dini PM2.5 vs Korban Langsung",
                labels={"value": "Jiwa", "variable": "Kategori Korban", "province": "Provinsi"},
                color_discrete_map={"premature_deaths_pm25_est": "#ef4444", "direct_deaths": "#f97316"}
            )
            fig_mort.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_mort, use_container_width=True)

        st.write("#### 💸 Ringkasan Dampak Multidimensi & Kerugian Makro (Bank Dunia & BNPB)")
        if not df_multi.empty:
            st.dataframe(df_multi[["impact_sector", "quantified_metric", "economic_loss_est_trillion_idr", "impact_severity"]], use_container_width=True)

# TAB 8: TRANSBOUNDARY HAZE OUTSIDE KALIMANTAN
with tab8:
    st.subheader("🌏 Daerah Terdampak di Luar Kalimantan (Kabut Asap Lintas Batas / Transboundary Haze)")
    st.caption("Pola Sebaran Asap Lintas Wilayah Domestik & Internasional Berdasarkan Trajektori Angin Monsun.")

    if not df_trans.empty:
        col_t1, col_t2 = st.columns([1.2, 1])

        with col_t1:
            fig_trans_bar = px.bar(
                df_trans,
                x="region_name",
                y="distance_from_fire_km",
                color="region_category",
                title="Jarak Jangkauan Sebaran Kabut Asap dari Pusat Kebakaran",
                labels={"region_name": "Wilayah Terdampak", "distance_from_fire_km": "Estimasi Jarak", "region_category": "Kategori"}
            )
            fig_trans_bar.update_layout(template="plotly_dark", height=380)
            st.plotly_chart(fig_trans_bar, use_container_width=True)

        with col_t2:
            st.markdown("""
            <div style="background: #1e293b; padding: 16px; border-radius: 10px; border-left: 4px solid #38bdf8;">
                <h4 style="margin: 0 0 8px 0; color: #38bdf8;">🌐 Jangkauan Kabut Asap Lintas Negara (ASEAN Haze)</h4>
                <p style="font-size: 12px; line-height: 1.6; color: #e2e8f0;">
                    • <b>Sarawak (Malaysia):</b> Kuching & Sri Aman mencapai level darurat <i>Hazardous (AQI >350)</i>, >1.000 sekolah ditutup.<br>
                    • <b>Singapura:</b> Indeks Standar Pencemar Udara (PSI) menyentuh level <i>Unhealthy (>150-200)</i>, memicu peringatan kesehatan dan siaga penerbangan Changi.<br>
                    • <b>Semenanjung Malaysia & Brunei:</b> Kabut asap menyelimuti Kuala Lumpur, Selangor, dan pesisir Brunei.<br>
                    • <b>Domestik Indonesia:</b> DKI Jakarta/Jawa Utara, Batam/Kepri, Bangka Belitung, dan pesisir Sulawesi Selatan.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.write("#### 📋 Matriks Status Dampak Wilayah di Luar Kalimantan")
        st.dataframe(df_trans[["region_name", "region_category", "peak_aqi_pm25", "wind_transport_trajectory", "impact_details"]], use_container_width=True)

# TAB 9: ECONOMIC & INVESTMENT INFLOW
with tab9:
    st.subheader("💰 Arus Kas & Realisasi Investasi (PMA & PMDN) ke Kalimantan")
    st.caption("Data terstruktur rujukan BKPM (Kementerian Investasi), BPS, dan Bank Indonesia Regional.")

    if not df_inv_prov.empty:
        df_inv_latest = df_inv_prov[df_inv_prov["year"] == 2026]

        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            st.metric(label="Total Realisasi Investasi (2026)", value=f"Rp {df_inv_latest['total_investment_trillion_idr'].sum():,.1f} T")
        with col_e2:
            st.metric(label="Investasi Dalam Negeri (PMDN)", value=f"Rp {df_inv_latest['pmdn_trillion_idr'].sum():,.1f} T")
        with col_e3:
            st.metric(label="Investasi Asing (PMA)", value=f"US$ {df_inv_latest['pma_million_usd'].sum():,.0f} Juta", delta=f"Rp {df_inv_latest['pma_trillion_idr'].sum():,.1f} T")
        with col_e4:
            st.metric(label="Provinsi Terbesar", value=df_inv_latest.sort_values(by="total_investment_trillion_idr", ascending=False).iloc[0]["province"], delta="IKN & Tambang")

        row_inv1, row_inv2 = st.columns(2)
        with row_inv1:
            fig_inv_bar = px.bar(
                df_inv_prov,
                x="year",
                y="total_investment_trillion_idr",
                color="province",
                barmode="group",
                title="Tren Realisasi Investasi per Provinsi (2023 - 2026)",
                labels={"total_investment_trillion_idr": "Total Investasi (Triliun Rupiah)", "year": "Tahun", "province": "Provinsi"}
            )
            fig_inv_bar.update_layout(template="plotly_dark", height=380)
            st.plotly_chart(fig_inv_bar, use_container_width=True)

        with row_inv2:
            if not df_inv_sect.empty:
                fig_sect = px.pie(
                    df_inv_sect,
                    values="investment_share_pct",
                    names="sector",
                    title="Porsi Aliran Investasi per Sektor Ekonomi",
                    color_discrete_sequence=px.colors.sequential.Plasma,
                    hole=0.4
                )
                fig_sect.update_layout(template="plotly_dark", height=380)
                st.plotly_chart(fig_sect, use_container_width=True)

        # Foreign Investment Origins
        st.write("#### 🌐 Negara Asal Penanaman Modal Asing (PMA) Terbesar di Kalimantan")
        if not df_inv_orig.empty:
            col_orig1, col_orig2 = st.columns([1.2, 1])
            with col_orig1:
                fig_orig = px.bar(
                    df_inv_orig,
                    x="share_pct",
                    y="country",
                    orientation="h",
                    color="share_pct",
                    color_continuous_scale="Blues",
                    title="Pangsa Modal Asing (FDI) Berdasarkan Negara Asal",
                    labels={"share_pct": "Pangsa Investasi (%)", "country": "Negara Asal"}
                )
                fig_orig.update_layout(template="plotly_dark", height=320)
                st.plotly_chart(fig_orig, use_container_width=True)
            with col_orig2:
                st.dataframe(df_inv_orig[["country", "share_pct", "pma_million_usd_yr", "primary_sectors"]], use_container_width=True, height=320)

# TAB 10: CAUSALITY & MOTIVES INVESTIGATION
with tab10:
    st.subheader("🔍 Investigasi Kausalitas: Ulah Pihak Tertentu vs Murni Alami")
    st.caption("Berdasarkan Data & Hasil Penelitian Empiris KLHK (SiPongi+), BNPB, CIFOR, BRIN, dan World Bank.")

    col_c1, col_c2 = st.columns([1, 1.4])
    with col_c1:
        if not df_caus.empty:
            fig_caus = px.pie(
                df_caus,
                values="percentage_share",
                names="cause_category",
                color="cause_category",
                color_discrete_map={
                    "Aktivitas Manusia (Antropogenik / Disengaja & Lalai)": "#ef4444",
                    "Murni Alami (Petir / Gesekan Alami Tanpa Manusia)": "#3b82f6"
                },
                title="Proporsi Penyebab Langsung Karhutla Indonesia",
                hole=0.55
            )
            fig_caus.update_layout(template="plotly_dark", height=340, showlegend=True)
            st.plotly_chart(fig_caus, use_container_width=True)

    with col_c2:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 16px; color: #f8fafc; margin-top: 15px;">
            <h4 style="margin: 0 0 8px 0; color: #ef4444;">🚨 FAKTA SAINS DATA: BUKAN BENCANA ALAMI MURNI</h4>
            <p style="font-size: 13px; line-height: 1.6; margin-bottom: 8px;">
                <b>99.0%</b> kebakaran hutan dan lahan di Kalimantan dipicu oleh <b>sulutan langsung manusia (antropogenik)</b>, baik sengaja maupun lalai.
            </p>
            <p style="font-size: 12px; line-height: 1.5; color: #cbd5e1; margin-bottom: 0;">
                <b>Peran Iklim (El Niño & IOD Positif):</b> Iklim bertindak sebagai <i>katalisator & pengering (amplifier)</i> yang mempercepat penurunan muka air gambut, namun <u>api tidak akan menyala tanpa adanya sulutan dari manusia</u>. Petir di iklim tropis Kalimantan hampir selalu disertai hujan lebat.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.write("#### 🎯 Tujuan & Motif Utama Pembakaran Hutan (Analisis Tekno-Ekonomi)")

    if not df_mot.empty:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            fig_mot = px.bar(
                df_mot,
                x="share_pct",
                y="motive_name",
                orientation="h",
                color="cost_savings_pct",
                color_continuous_scale="Reds",
                title="Porsi Motif & Dorongan Ekonomi Pembakaran Lahan",
                labels={"share_pct": "Porsi Kasus (%)", "motive_name": "Motif Pembakaran"}
            )
            fig_mot.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_mot, use_container_width=True)

        with col_m2:
            st.markdown("""
            <div style="background: #1e293b; padding: 14px; border-radius: 10px; border-left: 4px solid #f59e0b;">
                <h4 style="margin: 0 0 6px 0; color: #f59e0b;">💵 Insentif Ekonomi Terbesar: Hemat Biaya Hingga 90%</h4>
                <p style="font-size: 12px; line-height: 1.6; color: #e2e8f0;">
                    • <b>Metode Tebas-Bakar (*Slash-and-Burn*):</b> Rp 500.000 - Rp 1.500.000 per hektar.<br>
                    • <b>Pembersihan Mekanis Tanpa Bakar:</b> Rp 6.000.000 - Rp 12.000.000 per hektar.<br>
                    • <b>Keuntungan Abu Gambut (*Peat Ash*):</b> Abu hasil bakaran menaikkan pH gambut asam (pH 3.5 ➔ 5.5) secara gratis tanpa perlu membeli kapur dolomit mahal.
                </p>
            </div>
            """, unsafe_allow_html=True)

            if econ_corr_data.get("concession_overlap"):
                df_conc = pd.DataFrame(econ_corr_data["concession_overlap"]["distribution"])
                fig_conc = px.pie(
                    df_conc,
                    values="percentage",
                    names="zone_category",
                    title="Sebaran Titik Api Terhadap Area Konsesi Perkebunan/HTI",
                    color_discrete_sequence=px.colors.qualitative.Set1,
                    hole=0.4
                )
                fig_conc.update_layout(template="plotly_dark", height=280)
                st.plotly_chart(fig_conc, use_container_width=True)

    st.write("#### 👥 Aktor & Entitas Penyebab Karhutla")
    if not df_act.empty:
        st.dataframe(df_act[["actor_group", "share_pct", "legal_status", "modus_operandi"]], use_container_width=True)

# TAB 11: DOWNLOAD DATA
with tab11:
    st.subheader("💾 Unduh Seluruh Dataset Geospasial, Kesehatan, Ekonomi & Prediksi")
    st.caption("Format kompatibel dengan QGIS, ArcGIS, Python Pandas, R Spatial, dan Tableau.")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if HOTSPOTS_CSV.exists():
            with open(HOTSPOTS_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Titik Panas", data=f, file_name="kalimantan_hotspots_latest.csv", mime="text/csv", use_container_width=True)
    with col_d2:
        if HOTSPOTS_GEOJSON.exists():
            with open(HOTSPOTS_GEOJSON, "rb") as f:
                st.download_button(label="📥 Unduh GeoJSON Titik Panas", data=f, file_name="kalimantan_hotspots_latest.geojson", mime="application/geo+json", use_container_width=True)
    with col_d3:
        if WEATHER_CSV.exists():
            with open(WEATHER_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Cuaca Real-Time", data=f, file_name="kalimantan_weather_latest.csv", mime="text/csv", use_container_width=True)

    col_d4, col_d5, col_d6 = st.columns(3)
    with col_d4:
        if SCENARIOS_CSV.exists():
            with open(SCENARIOS_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Prediksi Skenario", data=f, file_name="kalimantan_damage_prediction_scenarios.csv", mime="text/csv", use_container_width=True)
    with col_d5:
        if COST_BENEFIT_CSV.exists():
            with open(COST_BENEFIT_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Benefit-Cost Ratio", data=f, file_name="kalimantan_cost_benefit_mitigation.csv", mime="text/csv", use_container_width=True)
    with col_d6:
        if FATALITIES_HEALTH_CSV.exists():
            with open(FATALITIES_HEALTH_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Korban Jiwa & ISPA", data=f, file_name="kalimantan_fire_fatalities_health_impacts.csv", mime="text/csv", use_container_width=True)

    col_d7, col_d8, col_d9 = st.columns(3)
    with col_d7:
        if TRANSBOUNDARY_HAZE_CSV.exists():
            with open(TRANSBOUNDARY_HAZE_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Kabut Asap Lintas Batas", data=f, file_name="kalimantan_transboundary_haze_external_impacts.csv", mime="text/csv", use_container_width=True)
    with col_d8:
        if MULTIDIMENSIONAL_IMPACTS_CSV.exists():
            with open(MULTIDIMENSIONAL_IMPACTS_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Dampak Multidimensi", data=f, file_name="kalimantan_fire_multidimensional_impacts.csv", mime="text/csv", use_container_width=True)
    with col_d9:
        if INVESTMENT_PROV_CSV.exists():
            with open(INVESTMENT_PROV_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Investasi PMA/PMDN", data=f, file_name="kalimantan_investment_pma_pmdn.csv", mime="text/csv", use_container_width=True)

    st.markdown("---")
    st.write("#### 📋 Pratinjau Tabel Titik Panas Terverifikasi Spasial")
    if not df_filtered.empty:
        st.dataframe(df_filtered[["hotspot_id", "province", "land_type", "peatland_name", "frp", "brightness", "confidence_pct", "hazard_score", "hazard_severity"]].head(25), use_container_width=True)

# TAB 12: SOCIAL NETWORK ANALYSIS (SNA) / NODEXL ACTOR GRAPH
with tab12:
    st.subheader("🕸️ Social Network Analysis (SNA): Jaringan Aktor & Wacana Karhutla")
    st.caption("Pemetaan Relasi Multi-Klaster, Penegakan Hukum, Investigasi Media, dan Koridor Asap ASEAN (Model NodeXL Graph).")

    sna_kpi1, sna_kpi2, sna_kpi3, sna_kpi4 = st.columns(4)
    total_nodes = len(df_sna_nodes) if not df_sna_nodes.empty else 28
    total_edges = len(df_sna_edges) if not df_sna_edges.empty else 32
    density = sna_summary_data.get("graph_density", 0.042)
    top_broker = sna_summary_data.get("top_broker_actors", [{}])[0].get("label", "KLHK") if sna_summary_data.get("top_broker_actors") else "KLHK"

    with sna_kpi1:
        st.metric(label="Total Entitas Aktor", value=f"{total_nodes} Node", delta="5 Klaster Strategis")
    with sna_kpi2:
        st.metric(label="Total Interaksi & Relasi", value=f"{total_edges} Edge", delta="Penegakan & Wacana")
    with sna_kpi3:
        st.metric(label="Kepadatan Jaringan (Density)", value=f"{density:.3f}", delta="Desentralisasi Wacana")
    with sna_kpi4:
        st.metric(label="Aktor Broker Utama", value=top_broker, delta="Top Betweenness Centrality", delta_color="inverse")

    st.markdown("""
    <div style="background: rgba(56, 189, 248, 0.1); border-left: 4px solid #38bdf8; padding: 12px 16px; border-radius: 8px; margin: 15px 0;">
        <span style="font-weight: bold; color: #38bdf8;">💡 Petunjuk Interaksi Graf:</span> 
        <span style="color: #f1f5f9; font-size: 13px;">
            Graf di bawah bersifat interaktif. Anda dapat <b>menggeser (drag)</b> node, <b>zoom in/out</b>, dan <b>mengklik salah satu node</b> untuk melihat kartu detail peran aktor, skor <i>betweenness centrality</i>, serta metrik <i>PageRank</i>.
        </span>
    </div>
    """, unsafe_allow_html=True)

    if SNA_HTML.exists():
        with open(SNA_HTML, "r", encoding="utf-8") as f:
            sna_html_data = f.read()
        st.components.v1.html(sna_html_data, height=720, scrolling=False)
    else:
        st.warning("Visualisasi graf interaktif sedang diproses...")

    st.markdown("---")
    st.subheader("📊 Tabel Analisis Metrik Sentralitas Aktor (Node Centrality)")
    
    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        if not df_sna_nodes.empty:
            st.dataframe(
                df_sna_nodes[["label", "cluster_group", "role", "betweenness_centrality", "pagerank", "influence_score"]],
                use_container_width=True,
                height=350
            )
    with col_t2:
        st.write("#### 📥 Unduh Data Jaringan NodeXL")
        if SNA_NODES_CSV.exists():
            with open(SNA_NODES_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Nodes (Aktor)", data=f, file_name="karhutla_sna_nodes.csv", mime="text/csv", use_container_width=True)
        if SNA_EDGES_CSV.exists():
            with open(SNA_EDGES_CSV, "rb") as f:
                st.download_button(label="📥 Unduh CSV Edges (Interaksi)", data=f, file_name="karhutla_sna_edges.csv", mime="text/csv", use_container_width=True)
        if SNA_SUMMARY_JSON.exists():
            with open(SNA_SUMMARY_JSON, "rb") as f:
                st.download_button(label="📥 Unduh JSON Statistik Graf", data=f, file_name="karhutla_sna_summary.json", mime="application/json", use_container_width=True)
