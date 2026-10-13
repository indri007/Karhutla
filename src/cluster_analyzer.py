"""
Cluster Analyzer & Early Onset Detection for Kalimantan Forest Fires.
Implements DBSCAN Haversine Spatial Clustering and Time-Series Change-Point Analysis.
"""
import json
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from typing import Dict, Any, List, Tuple

try:
    from src.config import (
        CLUSTER_METRICS_JSON,
        HOTSPOTS_HISTORICAL_CSV
    )
except ImportError:
    from config import (
        CLUSTER_METRICS_JSON,
        HOTSPOTS_HISTORICAL_CSV
    )


class ClusterAnalyzer:
    """Performs spatial cluster extraction and early onset surge detection."""

    def __init__(self, eps_km: float = 35.0, min_samples: int = 3):
        # Earth radius in km ~ 6371.0088
        self.kms_per_radian = 6371.0088
        self.epsilon_rad = eps_km / self.kms_per_radian
        self.min_samples = min_samples

    def perform_dbscan_clustering(self, df_hotspots: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Executes DBSCAN using Haversine metric on (latitude, longitude).
        Returns enriched dataframe with cluster labels and cluster metadata summaries.
        """
        if df_hotspots.empty:
            return df_hotspots, []

        coords_rad = np.radians(df_hotspots[["latitude", "longitude"]].values)
        db = DBSCAN(eps=self.epsilon_rad, min_samples=self.min_samples, metric="haversine")
        cluster_labels = db.fit_predict(coords_rad)

        df_result = df_hotspots.copy()
        df_result["cluster_id"] = cluster_labels

        unique_labels = set(cluster_labels)
        clusters_summary = []

        for label in unique_labels:
            if label == -1:
                # Noise / isolated points
                continue

            cluster_df = df_result[df_result["cluster_id"] == label]
            centroid_lat = float(cluster_df["latitude"].mean())
            centroid_lon = float(cluster_df["longitude"].mean())
            total_frp = float(cluster_df["frp"].sum())
            max_brightness = float(cluster_df["brightness"].max())
            hotspot_count = len(cluster_df)

            dominant_province = cluster_df["province"].mode()[0] if "province" in cluster_df else "Kalimantan"
            peat_count = (cluster_df["land_type"] == "Lahan Gambut").sum() if "land_type" in cluster_df else 0
            peat_pct = round((peat_count / hotspot_count) * 100, 1)

            # Determine cluster classification
            if peat_pct >= 60 and total_frp >= 60:
                cluster_type = "Episentrum Gambut Kritis (Critical Peat Smoldering)"
                risk_color = "#dc2626"
            elif total_frp >= 50:
                cluster_type = "Klaster Intensitas Tinggi (High-Intensity Spread)"
                risk_color = "#f97316"
            else:
                cluster_type = "Klaster Titik Api Awal (Emerging Early Onset Cluster)"
                risk_color = "#f59e0b"

            clusters_summary.append({
                "cluster_id": int(label),
                "name": f"Klaster Karhutla #{label+1} - {dominant_province}",
                "centroid_lat": round(centroid_lat, 5),
                "centroid_lon": round(centroid_lon, 5),
                "hotspot_count": hotspot_count,
                "total_frp_mw": round(total_frp, 1),
                "mean_frp_mw": round(float(cluster_df["frp"].mean()), 1),
                "max_brightness_k": round(max_brightness, 1),
                "dominant_province": dominant_province,
                "peat_percentage": peat_pct,
                "cluster_type": cluster_type,
                "risk_color": risk_color,
                "hotspots_ids": cluster_df["hotspot_id"].tolist() if "hotspot_id" in cluster_df else []
            })

        # Sort clusters by total FRP descending
        clusters_summary.sort(key=lambda x: x["total_frp_mw"], reverse=True)

        # Save cluster metadata to JSON
        with open(CLUSTER_METRICS_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "total_clusters_detected": len(clusters_summary),
                "isolated_hotspots_count": int((cluster_labels == -1).sum()),
                "clusters": clusters_summary
            }, f, indent=2)

        return df_result, clusters_summary

    def analyze_early_onset_dynamics(self, df_ts: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Analyzes early-onset time series to detect inflection points where fire counts
        accelerate from dry season baseline into an epidemic surge.
        """
        if df_ts is None:
            try:
                df_ts = pd.read_csv(HOTSPOTS_HISTORICAL_CSV)
            except Exception:
                return {}

        # 7-day Rolling Moving Average
        df_ts["rolling_7d"] = df_ts["total_hotspots"].rolling(window=7, min_periods=1).mean()
        df_ts["diff_rate"] = df_ts["rolling_7d"].diff().fillna(0)

        # Find inflection point (acceleration > threshold)
        surge_rows = df_ts[df_ts["rolling_7d"] > df_ts["rolling_7d"].mean() * 1.5]
        if not surge_rows.empty:
            inflection_date = str(surge_rows.iloc[0]["date"])
            inflection_day = int(surge_rows.iloc[0]["day_of_season"])
        else:
            inflection_date = str(df_ts.iloc[len(df_ts)//2]["date"])
            inflection_day = len(df_ts)//2

        return {
            "total_days_analyzed": len(df_ts),
            "peak_daily_hotspots": int(df_ts["total_hotspots"].max()),
            "total_season_hotspots": int(df_ts["total_hotspots"].sum()),
            "estimated_burned_area_ha": round(float(df_ts["est_burned_area_ha"].sum()), 1),
            "early_onset_inflection_date": inflection_date,
            "early_onset_day_of_season": inflection_day,
            "peat_vs_mineral_ratio": round(float(df_ts["peatland_hotspots"].sum() / max(1, df_ts["mineral_hotspots"].sum())), 2),
            "top_provinces_historical": {
                "Kalimantan Tengah": int(df_ts["kalteng_hotspots"].sum()),
                "Kalimantan Barat": int(df_ts["kalbar_hotspots"].sum()),
                "Kalimantan Selatan": int(df_ts["kalsel_hotspots"].sum()),
                "Kalimantan Timur": int(df_ts["kaltim_hotspots"].sum()),
                "Kalimantan Utara": int(df_ts["kaltara_hotspots"].sum())
            }
        }


if __name__ == "__main__":
    from geospatial_processor import GeospatialProcessor
    from nasa_firms_collector import NasaFirmsCollector

    collector = NasaFirmsCollector()
    df_raw = collector.collect()
    processor = GeospatialProcessor()
    df_proc, _ = processor.process(df_raw)

    analyzer = ClusterAnalyzer()
    df_clustered, clusters = analyzer.perform_dbscan_clustering(df_proc)
    print(f"DBSCAN Clustering Finished. Found {len(clusters)} Fire Clusters.")
    for c in clusters[:3]:
        print(f"- [{c['name']}] Hotspots: {c['hotspot_count']}, Total FRP: {c['total_frp_mw']} MW, Type: {c['cluster_type']}")

    onset_analytics = analyzer.analyze_early_onset_dynamics()
    print("\nEarly Onset Analytics:")
    print(json.dumps(onset_analytics, indent=2))
