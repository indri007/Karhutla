"""
Exploratory Data Analysis: Fatalities, Health Morbidity, Multidimensional Impacts,
and Transboundary Haze Dispersion Outside Kalimantan.
Author: Senior Data Scientist & Epidemiological Analyst
"""
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure UTF-8 console output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.impact_collector import ImpactCollector


def run_fatalities_and_impacts_eda():
    print("=" * 85)
    print("🚨📊 ANALISIS DATA SAINS: KORBAN JIWA, DAMPAK MULTIDIMENSI & WILAYAH TERDAMPAK LUAR KALIMANTAN")
    print("=" * 85)

    collector = ImpactCollector()
    data = collector.collect()

    df_fat = data["fatalities_health"]
    df_multi = data["multidimensional"]
    df_trans = data["transboundary_haze"]

    # SECTION 1: FATALITIES & MORTALITY
    total_direct_deaths = df_fat["direct_deaths"].sum()
    total_premature_deaths = df_fat["premature_deaths_pm25_est"].sum()
    total_ispa = df_fat["ispa_cases_treated"].sum()
    total_hosp = df_fat["emergency_hospitalizations"].sum()
    total_vulnerable = df_fat["vulnerable_population_affected"].sum()

    print("\n[BAGIAN 1] DATA KORBAN JIWA & KESEHATAN MASYARAKAT DI KALIMANTAN")
    print("-" * 85)
    print(f" ⚠️  Total Korban Jiwa Langsung (Direct Fatalities)       : {total_direct_deaths} Orang Meninggal")
    print(f" ⚠️  Estimasi Kematian Dini Akibat Asap PM2.5 (Premature) : {total_premature_deaths:,} Jiwa")
    print(f" 🏥  Total Pasien ISPA (Infeksi Saluran Pernapasan Akut) : {total_ispa:,} Pasien")
    print(f" 🚑  Pasien Rawat Inap Darurat Paru & Jantung            : {total_hosp:,} Pasien")
    print(f" 👶🧓 Populasi Rentan Terpapar (Bayi, Balita & Lansia)    : {total_vulnerable:,} Jiwa")

    print("\n • Rincian Dampak Kesehatan & Kematian per Provinsi:")
    for _, row in df_fat.sort_values(by="premature_deaths_pm25_est", ascending=False).iterrows():
        print(f"   - {row['province']:<22}: Korban Langsung: {row['direct_deaths']:>2} org | Kematian Dini PM2.5: {row['premature_deaths_pm25_est']:>5,} | ISPA: {row['ispa_cases_treated']:>7,} | Peak PM2.5: {row['peak_pm25_ug_m3']:>6.1f} µg/m³ ({row['air_quality_status']})")

    # SECTION 2: MULTIDIMENSIONAL IMPACTS
    total_economic_loss = df_multi["economic_loss_est_trillion_idr"].sum()
    print("\n" + "=" * 85)
    print(f"[BAGIAN 2] DAMPAK MULTIDIMENSI KARHUTLA (TOTAL KERUGIAN: RP {total_economic_loss:,.1f} TRILIUN)")
    print("=" * 85)
    for _, m in df_multi.iterrows():
        print(f" 📌 {m['impact_sector'].upper()} (Estimasi Kerugian: Rp {m['economic_loss_est_trillion_idr']:>5.1f} T)")
        print(f"    - Metrik Terukur : {m['quantified_metric']}")
        print(f"    - Tingkat Bahaya : {m['impact_severity']}")
        print(f"    - Dampak Rinci   : {m['detailed_description']}\n")

    # SECTION 3: EXTERNAL IMPACTS OUTSIDE KALIMANTAN
    print("=" * 85)
    print("🌏 [BAGIAN 3] DAERAH-DAERAH YANG TERDAMPAK DI LUAR KALIMANTAN (TRANSBOUNDARY HAZE)")
    print("=" * 85)

    print("\n A. NEGARA INTERNASIONAL LINTAS BATAS:")
    df_intl = df_trans[df_trans["region_category"].str.contains("Internasional")]
    for _, intl in df_intl.iterrows():
        print(f" 🌐 [{intl['region_name']}] (Jarak: {intl['distance_from_fire_km']})")
        print(f"    - Kualitas Udara : {intl['peak_aqi_pm25']}")
        print(f"    - Jalur Asap     : {intl['wind_transport_trajectory']}")
        print(f"    - Dampak Nyata   : {intl['impact_details']}")
        print(f"    - Isu Diplomatik : {intl['diplomatic_tension']}\n")

    print(" B. WILAYAH DOMESTIK INDONESIA DI LUAR KALIMANTAN:")
    df_dom = df_trans[df_trans["region_category"].str.contains("Domestik")]
    for _, dom in df_dom.iterrows():
        print(f" 🇮🇩 [{dom['region_name']}] (Jarak: {dom['distance_from_fire_km']})")
        print(f"    - Kualitas Udara : {dom['peak_aqi_pm25']}")
        print(f"    - Jalur Asap     : {dom['wind_transport_trajectory']}")
        print(f"    - Dampak Nyata   : {dom['impact_details']}\n")

    print("=" * 85)
    print("💡 KESIMPULAN UTAMA EPIDEMIOLOGI & GEOSPASIAL:")
    print(" 1. Korban Karhutla bukan hanya mereka yang terbakar langsung di lahan (34 orang),")
    print("    melainkan ribuan kematian dini (~6,460 jiwa) akibat infark miokard, stroke, dan PPOK")
    print("    dari paparan aerosol beracun PM2.5 pekat yang menembus pembuluh darah.")
    print(" 2. Partikel PM2.5 di Palangka Raya & Pontianak menembus >1,400 - 1,980 µg/m³, hampir 130 KALI")
    print("    di atas batas aman WHO (15 µg/m³ per 24 jam).")
    print(" 3. Kabut asap lintas batas (Transboundary Haze) tidak mengenal batas negara, mencakup")
    print("    Sarawak, Semenanjung Malaysia, Singapura, Brunei, hingga Jakarta dan Sulawesi.")
    print("=" * 85)


if __name__ == "__main__":
    run_fatalities_and_impacts_eda()
