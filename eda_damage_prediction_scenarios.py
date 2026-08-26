"""
Exploratory Data Science Analysis: Disaster Damage Prediction and Scenario Modeling
Comparing Unmitigated (Tidak Ditangani) vs Mitigated (Ditangani Terpadu).
Author: Senior Data Scientist & Environmental Econometrician
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

from src.scenario_predictor import ScenarioPredictor


def run_damage_prediction_eda():
    print("=" * 85)
    print("📈🔮 ANALISIS PREDIKSI DAMPAK KERUGIAN KARHUTLA KALIMANTAN (DATA SCIENCE SCENARIOS)")
    print("=" * 85)

    predictor = ScenarioPredictor()
    summary = predictor.simulate_scenarios()

    df_scenarios = pd.read_csv(BASE_DIR / "data" / "processed" / "kalimantan_damage_prediction_scenarios.csv")
    df_cb = pd.read_csv(BASE_DIR / "data" / "processed" / "kalimantan_cost_benefit_mitigation.csv")

    total_unmit = summary["unmitigated_damage_trillion_idr"]
    total_mit_res = summary["mitigated_residual_damage_trillion_idr"]
    total_mit_cost = summary["mitigation_intervention_cost_trillion_idr"]
    net_avoided = summary["net_avoided_losses_trillion_idr"]
    bcr = summary["benefit_cost_ratio_multiplier"]

    print(f"\n[1] MATRIKS EKSEKUTIF PREDIKSI KERUGIAN BENCANA (RUN-TIME MODEL)")
    print("-" * 85)
    print(f" 🔴 PROYEKSI KERUGIAN JIKA TIDAK DITANGANI (Unmitigated) : Rp {total_unmit:,.2f} Triliun (US$ {total_unmit*1000/16000:.1f} Miliar)")
    print(f" 🟡 KERUGIAN RESIDUAL MESKIPUN DITANGANI (Residual Loss)  : Rp {total_mit_res:,.2f} Triliun (US$ {total_mit_res*1000/16000:.1f} Miliar)")
    print(f" 🟢 BIAYA INVESTASI MITIGASI TERPADU (Intervention Cost) : Rp {total_mit_cost:,.2f} Triliun")
    print(f" 💎 KERUGIAN BERSIH YANG DISELAMATKAN (Avoided Losses)    : Rp {net_avoided:,.2f} Triliun")
    print(f" 🚀 BENEFIT-COST RATIO (RETURN ON INVESTMENT / ROI)      : {bcr:.2f}x Lipat (Sangat Layak Ekonomi)")

    print("\n" + "=" * 85)
    print("[2] RINCIAN KOMPARASI KERUGIAN PER SEKTOR (TIDAK DITANGANI VS DITANGANI)")
    print("=" * 85)
    print(f"{'Sektor Kerugian':<42} | {'Tdk Ditangani':<14} | {'Ditangani':<12} | {'Diselamatkan':<13} | {'Reduksi'}")
    print("-" * 85)
    for _, row in df_scenarios.iterrows():
        print(f"{row['sector']:<42} | Rp {row['unmitigated_loss_trillion_idr']:>7.2f} T   | Rp {row['mitigated_residual_loss_trillion_idr']:>6.2f} T  | Rp {row['avoided_loss_trillion_idr']:>7.2f} T   | {row['reduction_pct']:>5.1f}%")
        print(f"   • Tdk Ditangani : {row['unmitigated_physical_impact']}")
        print(f"   • Ditangani     : {row['mitigated_physical_impact']}\n")

    print("=" * 85)
    print("[3] STRUKTUR ALOKASI BIAYA MITIGASI TERPADU (CAPEX & OPEX)")
    print("=" * 85)
    costs = summary["mitigation_costs_breakdown"]
    for k, v in costs.items():
        name = k.replace("_trillion_idr", "").replace("_", " ").title()
        pct = (v / total_mit_cost) * 100
        print(f" • {name:<45}: Rp {v:>4.2f} Triliun ({pct:>5.1f}%)")

    print("\n" + "=" * 85)
    print("💡 KESIMPULAN SAINS DATA & REKOMENDASI KEBIJAKAN EKONOMI:")
    for takeaway in summary["key_takeaways"]:
        print(f" {takeaway}")
    print("=" * 85)


if __name__ == "__main__":
    run_damage_prediction_eda()
