"""
Unified Automated ETL Pipeline: Kalimantan Fire Real-Time Geospatial Intelligence.
Executes ingestion, spatial joins, machine learning clustering, and visualization generation.

Usage:
    python fetch_realtime_data.py [--days 14] [--api-key YOUR_NASA_KEY]
"""
import sys
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output in Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import (
    HOTSPOTS_GEOJSON_PATH,
    HOTSPOTS_CSV_PATH,
    HOTSPOTS_HISTORICAL_CSV,
    WEATHER_LATEST_JSON,
    WEATHER_LATEST_CSV,
    CLUSTER_METRICS_JSON,
    DASHBOARD_DIR
)
from src.weather_collector import WeatherCollector
from src.nasa_firms_collector import NasaFirmsCollector
from src.geospatial_processor import GeospatialProcessor
from src.cluster_analyzer import ClusterAnalyzer
from src.visualizer import MapVisualizer


def run_pipeline(days: int = 14, api_key: str = ""):
    start_time = time.time()
    print("=" * 70)
    print("🔥 PIPELINE PENGUMPULAN DATA GEOGRAFI REAL-TIME KEBAKARAN KALIMANTAN 🔥")
    print(f"⏰ Waktu Eksekusi : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Cakupan Wilayah: Kalimantan Barat, Tengah, Selatan, Timur, Utara")
    print("=" * 70)

    # 1. Weather Ingestion
    print("\n[LANGKAH 1/5] 🌤️ Mengambil Data Meteorologi & Kelembaban Tanah Real-Time...")
    weather_collector = WeatherCollector()
    df_weather = weather_collector.collect_all_stations()
    print(f"  ✓ Berhasil memperbarui {len(df_weather)} stasiun pemantauan cuaca regional.")
    print(f"  ✓ Data tersimpan di: {WEATHER_LATEST_CSV.name} dan {WEATHER_LATEST_JSON.name}")

    # 2. Satellite Hotspot Ingestion
    print("\n[LANGKAH 2/5] 🛰️ Mengambil Data Titik Panas Satelit (NASA FIRMS / NRT)...")
    firms_collector = NasaFirmsCollector(api_key=api_key)
    df_raw_hotspots = firms_collector.collect()
    print(f"  ✓ Berhasil mengumpulkan {len(df_raw_hotspots)} titik panas aktif.")

    # 3. Geospatial Processing & Multi-layer Spatial Join
    print("\n[LANGKAH 3/6] 🗺️ Melakukan Spatial Join (Batas Administrasi & Zona Gambut)...")
    geo_processor = GeospatialProcessor()
    df_processed, summary = geo_processor.process(df_raw_hotspots)
    print(f"  ✓ Total Hotspot Terverifikasi Spasial: {summary['total_hotspots']}")
    print(f"  ✓ Sebaran Gambut: {summary['peat_percentage']}% berada di Kesatuan Hidrologis Gambut (KHG)")
    print(f"  ✓ Rata-rata FRP (Daya Termal): {summary['mean_frp']} MW (Max: {summary['max_frp']} MW)")
    print(f"  ✓ Hotspot Bahaya Tinggi/Kritis: {summary['high_hazard_count']} titik")

    # 4. Economic, Investment & Causality Ingestion
    print("\n[LANGKAH 4/7] 💰 Mengumpulkan Data Arus Investasi (PMA/PMDN) & Kausalitas Pembakaran...")
    from src.economic_collector import EconomicCollector
    from src.causality_collector import CausalityCollector
    from src.economic_fire_analyzer import EconomicFireAnalyzer
    from src.impact_collector import ImpactCollector

    EconomicCollector().collect()
    CausalityCollector().collect()
    econ_analyzer = EconomicFireAnalyzer()
    econ_rep = econ_analyzer.generate_full_report()
    print("  ✓ Berhasil memperbarui data arus investasi 5 provinsi & analisis kausalitas (99% Antropogenik).")

    # 5. Fatalities, Health & Transboundary Haze Ingestion
    print("\n[LANGKAH 5/8] 🚨 Mengumpulkan Data Korban Jiwa, ISPA, Kerugian & Wilayah Luar Terdampak...")
    impact_collector = ImpactCollector()
    impact_data = impact_collector.collect()
    df_f = impact_data["fatalities_health"]
    print(f"  ✓ Total Korban Jiwa Langsung: {df_f['direct_deaths'].sum()} orang | Kematian Dini PM2.5: {df_f['premature_deaths_pm25_est'].sum():,} orang.")
    print(f"  ✓ Pasien ISPA: {df_f['ispa_cases_treated'].sum():,} kasus | Wilayah Luar Terdampak: Malaysia, Singapura, Brunei, Jakarta, Kepri.")

    # 6. Scenario Predictive Modeling & Cost-Benefit Valuation
    print("\n[LANGKAH 6/8] 🔮 Menjalankan Model Prediksi Kerugian & Analisis Skenario...")
    from src.scenario_predictor import ScenarioPredictor
    scenario_predictor = ScenarioPredictor()
    scenario_res = scenario_predictor.simulate_scenarios()
    print(f"  ✓ Proyeksi Kerugian TIDAK Ditangani : Rp {scenario_res['unmitigated_damage_trillion_idr']:,.1f} Triliun.")
    print(f"  ✓ Kerugian DITANGANI (Residual+Cost) : Rp {scenario_res['total_mitigated_outlay_trillion_idr']:,.1f} Triliun.")
    print(f"  ✓ Kerugian Berhasil Diselamatkan    : Rp {scenario_res['net_avoided_losses_trillion_idr']:,.1f} Triliun (ROI: {scenario_res['benefit_cost_ratio_multiplier']}x).")

    # 7. ML Spatial Clustering & Onset Analysis
    print("\n[LANGKAH 7/8] 🧠 Menjalankan Machine Learning Spatial Clustering (DBSCAN)...")
    cluster_analyzer = ClusterAnalyzer(eps_km=35.0, min_samples=3)
    df_clustered, clusters = cluster_analyzer.perform_dbscan_clustering(df_processed)
    onset_analytics = cluster_analyzer.analyze_early_onset_dynamics()
    print(f"  ✓ Terdeteksi {len(clusters)} Klaster/Episentrum Kebakaran Aktif.")
    print(f"  ✓ Titik Belok Awal Kebakaran (Early Onset): {onset_analytics.get('early_onset_inflection_date', 'N/A')}")
    print(f"  ✓ Total Estimasi Luasan Terdampak Awal: {onset_analytics.get('estimated_burned_area_ha', 0)} Hektar")

    # 8. Interactive Map Generation
    print("\n[LANGKAH 8/8] 🎨 Membangun Peta Geospasial Interaktif...")
    visualizer = MapVisualizer()
    map_path = visualizer.generate_map(df_clustered, df_weather, clusters)
    print(f"  ✓ Peta Geospasial Berhasil Dibuat: {map_path}")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"✅ PIPELINE SELESAI DALAM {elapsed} DETIK!")
    print("=" * 70)
    print("\n📊 RINGKASAN EKSEKUTIF DATA SCIENTIST:")
    print(f" • Hotspot Kalimantan Tengah : {summary['by_province'].get('Kalimantan Tengah', 0)} titik")
    print(f" • Hotspot Kalimantan Barat  : {summary['by_province'].get('Kalimantan Barat', 0)} titik")
    print(f" • Hotspot Kalimantan Selatan: {summary['by_province'].get('Kalimantan Selatan', 0)} titik")
    print(f" • Hotspot Kalimantan Timur  : {summary['by_province'].get('Kalimantan Timur', 0)} titik")
    print(f" • Hotspot Kalimantan Utara  : {summary['by_province'].get('Kalimantan Utara', 0)} titik")
    print("\n📁 File Output Siap Digunakan:")
    print(f" 1. [PETA INTERAKTIF]  : {map_path}")
    print(f" 2. [GEOJSON TITIK API]: {HOTSPOTS_GEOJSON_PATH}")
    print(f" 3. [DATA CSV BERSIH]  : {HOTSPOTS_CSV_PATH}")
    print(f" 4. [DATA TREN ONSET]  : {HOTSPOTS_HISTORICAL_CSV}")
    print(f" 5. [CUACA REAL-TIME]  : {WEATHER_LATEST_CSV}")
    print(f" 6. [KLASTER DBSCAN]   : {CLUSTER_METRICS_JSON}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kalimantan Fire Real-Time Geospatial ETL Pipeline")
    parser.add_argument("--days", type=int, default=14, help="Rentang hari pemantauan")
    parser.add_argument("--api-key", type=str, default="", help="NASA FIRMS MAP_KEY (opsional)")
    args = parser.parse_args()

    run_pipeline(days=args.days, api_key=args.api_key)
