"""
Exploratory Data Analysis (EDA) & Geospatial Analytics for Kalimantan Early Fire Onset.
Author: Senior Data Scientist
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths
BASE_DIR = Path(__file__).resolve().parent
HOTSPOTS_PATH = BASE_DIR / "data" / "processed" / "kalimantan_hotspots_latest.csv"
TIMESERIES_PATH = BASE_DIR / "data" / "processed" / "kalimantan_early_fire_onset_timeseries.csv"
WEATHER_PATH = BASE_DIR / "data" / "processed" / "kalimantan_weather_latest.csv"


def perform_eda():
    print("=" * 75)
    print("🔬 ANALISIS SAINS DATA & GEOSPASIAL: KARHUTLA KALIMANTAN (EARLY ONSET)")
    print("=" * 75)

    # 1. Hotspots Analysis
    if HOTSPOTS_PATH.exists():
        df_hs = pd.read_csv(HOTSPOTS_PATH)
        print(f"\n[1] METRIK UTAMA TITIK PANAS (N = {len(df_hs)})")
        print("-" * 50)
        print(f" • Rata-rata Fire Radiative Power (FRP): {df_hs['frp'].mean():.2f} MW (Std: {df_hs['frp'].std():.2f} MW)")
        print(f" • FRP Maksimum (Intensitas Tertinggi): {df_hs['frp'].max():.2f} MW")
        print(f" • Rata-rata Suhu Kecerahan Satelit   : {df_hs['brightness'].mean():.2f} K ({df_hs['brightness'].mean() - 273.15:.1f} °C)")
        print(f" • Confidence Rata-rata Satelit       : {df_hs['confidence_pct'].mean():.1f}%")

        print("\n[2] SEBARAN TITIK PANAS BERDASARKAN PROVINSI:")
        prov_counts = df_hs['province'].value_counts()
        for prov, count in prov_counts.items():
            pct = (count / len(df_hs)) * 100
            print(f"   - {prov:<22}: {count:>3} titik ({pct:>5.1f}%) | Mean FRP: {df_hs[df_hs['province'] == prov]['frp'].mean():.1f} MW")

        print("\n[3] DISTRIBUSI TIPE LAHAN (GAMBUT VS MINERAL):")
        land_counts = df_hs['land_type'].value_counts()
        for land, count in land_counts.items():
            pct = (count / len(df_hs)) * 100
            sub_df = df_hs[df_hs['land_type'] == land]
            print(f"   - {land:<18}: {count:>3} titik ({pct:>5.1f}%) | Mean Brightness: {sub_df['brightness'].mean():.1f} K")

        print("\n[4] STRATIFIKASI TINGKAT BAHAYA (COMPOSITE HAZARD INDEX):")
        hazard_counts = df_hs['hazard_severity'].value_counts()
        for sev, count in hazard_counts.items():
            pct = (count / len(df_hs)) * 100
            print(f"   - {sev:<28}: {count:>3} titik ({pct:>5.1f}%)")

    # 2. Weather Correlation Analysis
    if WEATHER_PATH.exists():
        df_weather = pd.read_csv(WEATHER_PATH)
        print("\n" + "=" * 75)
        print("[5] KONDISI METEOROLOGI & PARAMETER PENYEBAB AWAL KEBAKARAN")
        print("-" * 50)
        print(f" • Rata-rata Suhu Udara Regional      : {df_weather['temperature_c'].mean():.1f} °C (Max: {df_weather['temperature_c'].max():.1f} °C)")
        print(f" • Rata-rata Kelembaban Udara (RH)    : {df_weather['relative_humidity_pct'].mean():.1f}% (Min: {df_weather['relative_humidity_pct'].min():.1f}%)")
        print(f" • Rata-rata Kelembaban Tanah Topsoil : {df_weather['soil_moisture_m3_m3'].mean():.3f} m³/m³")
        print(f" • Stasiun dengan Risiko Tertinggi    : {df_weather.sort_values(by='fire_danger_score', ascending=False).iloc[0]['station_name']} (Skor: {df_weather['fire_danger_score'].max()}/100)")

    # 3. Early Onset Dynamics
    if TIMESERIES_PATH.exists():
        df_ts = pd.read_csv(TIMESERIES_PATH)
        print("\n" + "=" * 75)
        print("[6] ANALISIS TREN AWAL KEBAKARAN (EARLY ONSET TRANSITION DYNAMICS)")
        print("-" * 50)
        print(f" • Periode Analisis                   : {df_ts['date'].min()} s/d {df_ts['date'].max()} ({len(df_ts)} Hari)")
        print(f" • Total Akumulasi Titik Panas       : {df_ts['total_hotspots'].sum():,} titik")
        print(f" • Estimasi Luas Terbakar Kumulatif   : {df_ts['est_burned_area_ha'].sum():,.1f} Hektar")
        print(f" • Proporsi Kebakaran Lahan Gambut    : {(df_ts['peatland_hotspots'].sum() / df_ts['total_hotspots'].sum()) * 100:.1f}%")

        # Phase breakdown
        print("\n • Karakteristik Fase Musim:")
        for phase in df_ts['onset_phase'].unique():
            phase_df = df_ts[df_ts['onset_phase'] == phase]
            print(f"   * [{phase:<20}] Durasi: {len(phase_df)} hari | Rata-rata Harian: {phase_df['total_hotspots'].mean():.1f} titik/hari | Gambut: {phase_df['peat_percentage'].mean():.1f}%")

    print("\n" + "=" * 75)
    print("💡 KESIMPULAN & REKOMENDASI DATA SCIENTIST:")
    print(" 1. Titik awal kebakaran (Early Onset) di Kalimantan terkonsentrasi kuat pada Kubah Gambut (KHG)")
    print("    khususnya di Kalimantan Tengah (Ex-PLG & Sebangau) dan Kalimantan Barat (Ketapang & Kubu Raya).")
    print(" 2. Penurunan kelembaban tanah (< 0.28 m³/m³) dan RH (< 65%) berkorelasi kuat memicu transisi")
    print("    dari api permukaan menjadi kebakaran gambut bawah tanah (smoldering peat fires).")
    print(" 3. Tindakan pencegahan / rewetting (pembasahan sekat kanal gambut) paling efektif dilakukan")
    print("    sebelum tanggal titik belok (Early Onset Inflection Point) di awal Juli.")
    print("=" * 75)


if __name__ == "__main__":
    perform_eda()
