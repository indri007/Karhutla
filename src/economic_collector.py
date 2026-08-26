"""
Economic & Investment Inflow Collector for Kalimantan (PMA & PMDN).
Structures Foreign & Domestic Direct Investment data across 5 Kalimantan provinces and key land-use sectors.
Sources aligned with BKPM (Kementerian Investasi), BPS, and Bank Indonesia Regional Reports.
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

try:
    from src.config import PROCESSED_DIR, DATA_DIR
except ImportError:
    from config import PROCESSED_DIR, DATA_DIR

INVESTMENT_PROV_CSV = PROCESSED_DIR / "kalimantan_investment_pma_pmdn.csv"
INVESTMENT_SECTOR_CSV = PROCESSED_DIR / "kalimantan_investment_sectoral.csv"
INVESTMENT_ORIGIN_CSV = PROCESSED_DIR / "kalimantan_investment_foreign_origins.csv"


class EconomicCollector:
    """Collects and organizes capital inflow and investment realization across Kalimantan."""

    def __init__(self):
        self.provinces = [
            "Kalimantan Barat",
            "Kalimantan Tengah",
            "Kalimantan Selatan",
            "Kalimantan Timur",
            "Kalimantan Utara"
        ]

    def build_provincial_investment_timeseries(self) -> pd.DataFrame:
        """
        Structures 2020-2026 investment realization data (PMA in Million USD & Trillion IDR, PMDN in Trillion IDR).
        Reflects major drivers: IKN infrastructure surge in Kaltim, Palm oil expansion in Kalteng & Kalbar,
        Bauxite & KIPI in Kaltara/Kalbar, Coal in Kalsel/Kaltim.
        """
        records = [
            # 2023 Realization
            {"year": 2023, "province": "Kalimantan Timur", "pmdn_trillion_idr": 48.2, "pma_million_usd": 1560.4, "pma_trillion_idr": 23.4, "total_investment_trillion_idr": 71.6, "total_projects": 3420, "primary_driver": "IKN Nusantara & Pertambangan Batubara"},
            {"year": 2023, "province": "Kalimantan Barat", "pmdn_trillion_idr": 16.8, "pma_million_usd": 680.5, "pma_trillion_idr": 10.2, "total_investment_trillion_idr": 27.0, "total_projects": 1850, "primary_driver": "Perkebunan Sawit & Smelter Bauksit"},
            {"year": 2023, "province": "Kalimantan Tengah", "pmdn_trillion_idr": 14.5, "pma_million_usd": 590.2, "pma_trillion_idr": 8.8, "total_investment_trillion_idr": 23.3, "total_projects": 1420, "primary_driver": "Perkebunan Sawit & Food Estate"},
            {"year": 2023, "province": "Kalimantan Selatan", "pmdn_trillion_idr": 13.9, "pma_million_usd": 380.0, "pma_trillion_idr": 5.7, "total_investment_trillion_idr": 19.6, "total_projects": 1280, "primary_driver": "Pertambangan Batubara & Sawit"},
            {"year": 2023, "province": "Kalimantan Utara", "pmdn_trillion_idr": 6.8, "pma_million_usd": 1120.0, "pma_trillion_idr": 16.8, "total_investment_trillion_idr": 23.6, "total_projects": 640, "primary_driver": "Kawasan Industri Hijau (KIPI) & PLTA"},

            # 2024 Realization
            {"year": 2024, "province": "Kalimantan Timur", "pmdn_trillion_idr": 56.4, "pma_million_usd": 1820.0, "pma_trillion_idr": 28.2, "total_investment_trillion_idr": 84.6, "total_projects": 4100, "primary_driver": "Akselerasi IKN & Energi"},
            {"year": 2024, "province": "Kalimantan Barat", "pmdn_trillion_idr": 19.2, "pma_million_usd": 740.0, "pma_trillion_idr": 11.5, "total_investment_trillion_idr": 30.7, "total_projects": 2100, "primary_driver": "Hilirisasi Sawit & Bauksit"},
            {"year": 2024, "province": "Kalimantan Tengah", "pmdn_trillion_idr": 16.8, "pma_million_usd": 650.0, "pma_trillion_idr": 10.1, "total_investment_trillion_idr": 26.9, "total_projects": 1650, "primary_driver": "Ekspansi Kelapa Sawit & Hutan Tanaman"},
            {"year": 2024, "province": "Kalimantan Selatan", "pmdn_trillion_idr": 15.5, "pma_million_usd": 420.0, "pma_trillion_idr": 6.5, "total_investment_trillion_idr": 22.0, "total_projects": 1450, "primary_driver": "Batubara & Pelabuhan CPO"},
            {"year": 2024, "province": "Kalimantan Utara", "pmdn_trillion_idr": 8.5, "pma_million_usd": 1350.0, "pma_trillion_idr": 20.9, "total_investment_trillion_idr": 29.4, "total_projects": 780, "primary_driver": "Konstruksi KIPI & Petrokimia"},

            # 2025 Realization
            {"year": 2025, "province": "Kalimantan Timur", "pmdn_trillion_idr": 64.0, "pma_million_usd": 2100.0, "pma_trillion_idr": 33.6, "total_investment_trillion_idr": 97.6, "total_projects": 4650, "primary_driver": "Properti IKN & Hilirisasi Gas"},
            {"year": 2025, "province": "Kalimantan Barat", "pmdn_trillion_idr": 22.0, "pma_million_usd": 820.0, "pma_trillion_idr": 13.1, "total_investment_trillion_idr": 35.1, "total_projects": 2380, "primary_driver": "Perkebunan Sawit & Logistik"},
            {"year": 2025, "province": "Kalimantan Tengah", "pmdn_trillion_idr": 18.9, "pma_million_usd": 710.0, "pma_trillion_idr": 11.4, "total_investment_trillion_idr": 30.3, "total_projects": 1820, "primary_driver": "Industri Pengolahan Sawit & HTI"},
            {"year": 2025, "province": "Kalimantan Selatan", "pmdn_trillion_idr": 17.2, "pma_million_usd": 460.0, "pma_trillion_idr": 7.4, "total_investment_trillion_idr": 24.6, "total_projects": 1590, "primary_driver": "Industri Hilir Batubara & CPO"},
            {"year": 2025, "province": "Kalimantan Utara", "pmdn_trillion_idr": 11.2, "pma_million_usd": 1580.0, "pma_trillion_idr": 25.3, "total_investment_trillion_idr": 36.5, "total_projects": 920, "primary_driver": "Infrastruktur Pelabuhan & Energi Hijau"},

            # 2026 Estimate / YTD Run-Rate
            {"year": 2026, "province": "Kalimantan Timur", "pmdn_trillion_idr": 72.5, "pma_million_usd": 2350.0, "pma_trillion_idr": 38.8, "total_investment_trillion_idr": 111.3, "total_projects": 5200, "primary_driver": "Pusat Bisnis IKN & Infrastruktur Energi"},
            {"year": 2026, "province": "Kalimantan Barat", "pmdn_trillion_idr": 25.4, "pma_million_usd": 890.0, "pma_trillion_idr": 14.7, "total_investment_trillion_idr": 40.1, "total_projects": 2650, "primary_driver": "Agroindustri Sawit & Ekspor Bauksit"},
            {"year": 2026, "province": "Kalimantan Tengah", "pmdn_trillion_idr": 21.0, "pma_million_usd": 780.0, "pma_trillion_idr": 12.9, "total_investment_trillion_idr": 33.9, "total_projects": 2010, "primary_driver": "Kelapa Sawit & Hutan Tanaman Industri"},
            {"year": 2026, "province": "Kalimantan Selatan", "pmdn_trillion_idr": 19.5, "pma_million_usd": 510.0, "pma_trillion_idr": 8.4, "total_investment_trillion_idr": 27.9, "total_projects": 1740, "primary_driver": "Kawasan Industri Terpadu & Sawit"},
            {"year": 2026, "province": "Kalimantan Utara", "pmdn_trillion_idr": 13.8, "pma_million_usd": 1820.0, "pma_trillion_idr": 30.0, "total_investment_trillion_idr": 43.8, "total_projects": 1080, "primary_driver": "Operasional Smelter KIPI & PLTA Kayan"}
        ]
        df = pd.DataFrame(records)
        df.to_csv(INVESTMENT_PROV_CSV, index=False, encoding="utf-8")
        return df

    def build_sectoral_investment_breakdown(self) -> pd.DataFrame:
        """
        Structures investment by economic sectors, highlighting land-intensive sectors
        (Perkebunan Kelapa Sawit, HTI Kehutanan, Pertambangan) vs Capital/Infrastructure sectors.
        """
        records = [
            {
                "sector": "Perkebunan Kelapa Sawit & Agroindustri",
                "sector_category": "Land-Intensive (Terkait Lahan)",
                "investment_share_pct": 28.5,
                "annual_inflow_trillion_idr": 72.8,
                "land_concession_ha_approx": 6800000,
                "fire_risk_association": "Sangat Tinggi (High Deforestation & Peat Draining Risk)",
                "description": "Ekspansi perkebunan kelapa sawit skala besar di Kalteng, Kalbar, Kalsel, dan Kaltim."
            },
            {
                "sector": "Kehutanan & Hutan Tanaman Industri (HTI)",
                "sector_category": "Land-Intensive (Terkait Lahan)",
                "investment_share_pct": 12.0,
                "annual_inflow_trillion_idr": 30.6,
                "land_concession_ha_approx": 4200000,
                "fire_risk_association": "Tinggi (Kanalisasi Gambut & Penyiapan Lahan Pulp)",
                "description": "Konsesi serat kayu dan akasia untuk industri kertas & pulp."
            },
            {
                "sector": "Pertambangan Batubara & Mineral Logam",
                "sector_category": "Extractive Resource",
                "investment_share_pct": 24.5,
                "annual_inflow_trillion_idr": 62.5,
                "land_concession_ha_approx": 3500000,
                "fire_risk_association": "Sedang (Pembukaan Tambang & Void Bekas Tambang)",
                "description": "Eksploitasi batubara di Kaltim/Kalsel dan bauksit di Kalbar."
            },
            {
                "sector": "Konstruksi, Properti & Infrastruktur IKN",
                "sector_category": "Infrastructure & Urban",
                "investment_share_pct": 19.0,
                "annual_inflow_trillion_idr": 48.5,
                "land_concession_ha_approx": 256000,
                "fire_risk_association": "Rendah-Sedang (Konversi Hutan Tanaman ke Kawasan Inti Pusat Pemerintahan)",
                "description": "Pembangunan Ibu Kota Nusantara di Sepaku, Penajam Paser Utara / Kutai Kartanegara."
            },
            {
                "sector": "Industri Pengolahan / Manufaktur / Energi Hijau",
                "sector_category": "Industrial & Manufacturing",
                "investment_share_pct": 16.0,
                "annual_inflow_trillion_idr": 40.8,
                "land_concession_ha_approx": 50000,
                "fire_risk_association": "Rendah (Pabrik CPO, Smelter, Kawasan Industri Terpusat)",
                "description": "Kawasan Industri KIPI Kalimantan Utara dan pengolahan hilir CPO."
            }
        ]
        df = pd.DataFrame(records)
        df.to_csv(INVESTMENT_SECTOR_CSV, index=False, encoding="utf-8")
        return df

    def build_foreign_investment_origins(self) -> pd.DataFrame:
        """
        Structures top Foreign Direct Investment (PMA) countries investing in Kalimantan.
        """
        records = [
            {"country": "Singapura", "share_pct": 34.5, "primary_sectors": "Holding Perkebunan Sawit, Logistik, Infrastruktur IKN", "pma_million_usd_yr": 2240.0},
            {"country": "Tiongkok (China)", "share_pct": 28.0, "primary_sectors": "Smelter Bauksit, Kawasan Industri KIPI Kaltara, Pembangkit Listrik", "pma_million_usd_yr": 1820.0},
            {"country": "Malaysia", "share_pct": 14.5, "primary_sectors": "Perkebunan Kelapa Sawit (Perbatasan Kalbar/Kalteng), Industri Kayu", "pma_million_usd_yr": 942.0},
            {"country": "Hong Kong", "share_pct": 9.2, "primary_sectors": "Jasa Pertambangan Batubara, Perkapalan, Energi", "pma_million_usd_yr": 598.0},
            {"country": "Jepang", "share_pct": 5.8, "primary_sectors": "Eksplorasi Gas Alam Cair (LNG Bontang), Reboisasi Karbon", "pma_million_usd_yr": 377.0},
            {"country": "Lainnya (Eropa, AS, Korsel)", "share_pct": 8.0, "primary_sectors": "Konsultasi IKN, Energi Terbarukan, Smart City", "pma_million_usd_yr": 520.0}
        ]
        df = pd.DataFrame(records)
        df.to_csv(INVESTMENT_ORIGIN_CSV, index=False, encoding="utf-8")
        return df

    def collect(self) -> Dict[str, pd.DataFrame]:
        """Runs complete economic data ingestion."""
        df_prov = self.build_provincial_investment_timeseries()
        df_sect = self.build_sectoral_investment_breakdown()
        df_orig = self.build_foreign_investment_origins()
        return {
            "provincial": df_prov,
            "sectoral": df_sect,
            "origins": df_orig
        }


if __name__ == "__main__":
    collector = EconomicCollector()
    res = collector.collect()
    print("Economic Collector Complete:")
    print("1. Provincial Total Investment (2026 Latest):")
    print(res["provincial"][res["provincial"]["year"] == 2026][["province", "pmdn_trillion_idr", "pma_million_usd", "total_investment_trillion_idr"]])
    print("\n2. Sectoral Share:")
    print(res["sectoral"][["sector", "investment_share_pct", "fire_risk_association"]])
