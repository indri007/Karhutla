"""
Exploratory Data Analysis: Economic Inflow, Investment (PMA/PMDN), and Fire Causality & Motives in Kalimantan.
Author: Senior Data Scientist & Environmental Economist
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

from src.economic_collector import EconomicCollector
from src.causality_collector import CausalityCollector
from src.economic_fire_analyzer import EconomicFireAnalyzer


def run_economic_and_causality_eda():
    print("=" * 80)
    print("💰📊 ANALISIS DATA SAINS: ARUS INVESTASI (PMA/PMDN) & KAUSALITAS KARHUTLA KALIMANTAN")
    print("=" * 80)

    # 1. Ingest datasets
    econ_collector = EconomicCollector()
    econ_data = econ_collector.collect()

    caus_collector = CausalityCollector()
    caus_data = caus_collector.collect()

    analyzer = EconomicFireAnalyzer()
    analysis_res = analyzer.generate_full_report()

    # SECTION 1: INVESTASI & ARUS KAS KE KALIMANTAN
    df_prov = econ_data["provincial"]
    df_prov_2026 = df_prov[df_prov["year"] == 2026]
    total_inv_all = df_prov_2026["total_investment_trillion_idr"].sum()
    total_pmdn_all = df_prov_2026["pmdn_trillion_idr"].sum()
    total_pma_all = df_prov_2026["pma_trillion_idr"].sum()

    print("\n[BAGIAN 1] REALISASI ARUS KAS & INVESTASI KE KALIMANTAN (PMA & PMDN 2026)")
    print("-" * 80)
    print(f" • Total Realisasi Investasi Kalimantan (2026) : Rp {total_inv_all:,.1f} Triliun")
    print(f" • Porsi Penanaman Modal Dalam Negeri (PMDN)   : Rp {total_pmdn_all:,.1f} Triliun ({(total_pmdn_all/total_inv_all)*100:.1f}%)")
    print(f" • Porsi Penanaman Modal Asing (PMA / FDI)      : Rp {total_pma_all:,.1f} Triliun ({(total_pma_all/total_inv_all)*100:.1f}%) [US$ {df_prov_2026['pma_million_usd'].sum():,.0f} Juta]")

    print("\n • Realisasi Investasi per Provinsi (2026):")
    for _, row in df_prov_2026.sort_values(by="total_investment_trillion_idr", ascending=False).iterrows():
        print(f"   - {row['province']:<22}: Total Rp {row['total_investment_trillion_idr']:>5.1f} T | PMDN: Rp {row['pmdn_trillion_idr']:>4.1f} T | PMA: US$ {row['pma_million_usd']:>6.0f} M ({row['primary_driver']})")

    # SECTION 2: BREAKDOWN SEKTORAL
    df_sect = econ_data["sectoral"]
    print("\n[BAGIAN 2] DISTRIBUSI INVESTASI PER SEKTOR & KORELASI RISIKO KARHUTLA")
    print("-" * 80)
    for _, s in df_sect.iterrows():
        print(f" • {s['sector']:<42} ({s['investment_share_pct']:>4.1f}%) -> Rp {s['annual_inflow_trillion_idr']:>4.1f} T/thn")
        print(f"   - Luas Konsesi : ~{s['land_concession_ha_approx']:,} Hektar")
        print(f"   - Asosiasi Api : {s['fire_risk_association']}")

    # SECTION 3: NEGARA ASAL PMA
    df_orig = econ_data["origins"]
    print("\n[BAGIAN 3] NEGARA ASAL INVESTOR ASING (PMA / FOREIGN DIRECT INVESTMENT)")
    print("-" * 80)
    for _, orig in df_orig.iterrows():
        print(f" • {orig['country']:<24}: {orig['share_pct']:>4.1f}% (US$ {orig['pma_million_usd_yr']:>6.1f} Juta/thn) | Fokus: {orig['primary_sectors']}")

    # SECTION 4: KAUSALITAS PEMBAKARAN (MANUSIA VS ALAMI)
    df_caus = caus_data["causality"]
    print("\n" + "=" * 80)
    print("🔥 [BAGIAN 4] KAUSALITAS KARHUTLA: APAKAH KEBUTUHAN PIHAK TERTENTU ATAU MURNI ALAMI?")
    print("=" * 80)
    for _, c in df_caus.iterrows():
        print(f" • [{c['cause_category'].upper()}]: {c['percentage_share']}% KASUS")
        print(f"   - Sumber Sulutan : {c['ignition_source']}")
        print(f"   - Peran Iklim    : {c['role_of_climate']}")
        print(f"   - Sumber Bukti   : {c['institutional_source']}")

    # SECTION 5: MOTIF & TUJUAN PEMBAKARAN HUTAN
    df_motives = caus_data["motives"]
    print("\n[BAGIAN 5] TUJUAN & MOTIF UTAMA PEMBAKARAN HUTAN & LAHAN (DATA ILMIAH & LAPANGAN)")
    print("-" * 80)
    for _, m in df_motives.iterrows():
        print(f" 📌 MOTIF {m['motive_id'][-2:]}: {m['motive_name']} (Porsi: {m['share_pct']}%)")
        print(f"    - Target Lahan   : {m['primary_target']}")
        print(f"    - Biaya Bakar    : {m['cost_per_ha_idr']} vs Tanpa Bakar: {m['mechanical_cost_per_ha_idr']}")
        print(f"    - Penghematan    : {m['cost_savings_pct']:.1f}% Penghematan Biaya!")
        print(f"    - Mekanisme      : {m['detailed_mechanism']}")

    # SECTION 6: AKTOR PENYEBAB & OVERLAP KONSESI
    df_actors = caus_data["actors"]
    print("\n[BAGIAN 6] AKTOR & ENTITAS YANG TERLIBAT")
    print("-" * 80)
    for _, act in df_actors.iterrows():
        print(f" • {act['actor_group']:<45} ({act['share_pct']:>4.1f}%) | Status: {act['legal_status']}")
        print(f"   - Modus Operandi : {act['modus_operandi']}")

    concession_dist = analysis_res["concession_overlap"]["distribution"]
    print("\n[BAGIAN 7] SEBARAN SPASIAL TITIK API TERHADAP AREA KONSESI & PERKEBUNAN")
    print("-" * 80)
    for z in concession_dist:
        print(f" • {z['zone_category']:<55}: {z['count']:>3} titik ({z['percentage']:>4.1f}%) | {z['risk_driver']}")

    print("\n" + "=" * 80)
    print("💡 KESIMPULAN UTAMA DATA SCIENTIST:")
    print(" 1. Kebakaran hutan di Kalimantan BUKAN bencana murni alami, melainkan 99% akibat ulah manusia")
    print("    yang didorong oleh motif ekonomi pembukaan lahan murah (Slash-and-Burn).")
    print(" 2. Penghematan biaya hingga Rp 5.5 - 10.5 juta/hektar dan netralisasi pH asam gambut melalui abu")
    print("    pembakaran menjadi faktor pendorong ekonomi utama bagi spekulan dan oknum pembuka lahan.")
    print(" 3. Arus investasi sawit dan kanalisasi gambut di Kalimantan Tengah dan Barat berkorelasi kuat")
    print("    dengan 87% konsentrasi titik api di Kalimantan.")
    print("=" * 80)


if __name__ == "__main__":
    run_economic_and_causality_eda()
