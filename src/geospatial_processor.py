"""
Geospatial Processor for Kalimantan Active Fires.
Performs Point-in-Polygon spatial joins with official Provincial boundaries,
Peatland Hydrological Units (KHG), and calculates Multi-Criteria Fire Hazard Indexes.
"""
import json
import numpy as np
import pandas as pd
from shapely.geometry import shape, Point
from typing import Dict, Any, List, Tuple

try:
    from src.config import (
        PROVINCES_GEOJSON_PATH,
        PEATLANDS_GEOJSON_PATH,
        HOTSPOTS_GEOJSON_PATH,
        HOTSPOTS_CSV_PATH
    )
except ImportError:
    from config import (
        PROVINCES_GEOJSON_PATH,
        PEATLANDS_GEOJSON_PATH,
        HOTSPOTS_GEOJSON_PATH,
        HOTSPOTS_CSV_PATH
    )


class GeospatialProcessor:
    """Handles spatial point-in-polygon assignment and risk stratification."""

    def __init__(self):
        self.provinces = self._load_provinces()
        self.peatlands = self._load_peatlands()

    def _load_provinces(self) -> List[Dict[str, Any]]:
        """Loads and parses provincial geometry boundaries."""
        with open(PROVINCES_GEOJSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        provinces = []
        for feature in data.get("features", []):
            geom = shape(feature["geometry"])
            props = feature.get("properties", {})
            name = props.get("state") or props.get("Propinsi") or props.get("NAME_1")
            provinces.append({
                "name": name,
                "code": props.get("prov_code", ""),
                "capital": props.get("capital", ""),
                "geometry": geom,
                "properties": props
            })
        return provinces

    def _load_peatlands(self) -> List[Dict[str, Any]]:
        """Loads and parses peatland hydrological units (KHG)."""
        with open(PEATLANDS_GEOJSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        peatlands = []
        for feature in data.get("features", []):
            geom = shape(feature["geometry"])
            props = feature.get("properties", {})
            peatlands.append({
                "khg_id": props.get("khg_id", ""),
                "name": props.get("name", ""),
                "province": props.get("province", ""),
                "peat_depth": props.get("peat_depth", "Unknown"),
                "vulnerability": props.get("vulnerability", "High"),
                "geometry": geom,
                "properties": props
            })
        return peatlands

    def find_province(self, point: Point, default_hint: str = "Kalimantan") -> Tuple[str, str]:
        """Find which province contains the point."""
        for prov in self.provinces:
            if prov["geometry"].contains(point):
                return prov["name"], prov["code"]

        # Fallback to nearest province or hint
        for prov in self.provinces:
            if prov["name"] in default_hint:
                return prov["name"], prov["code"]

        return default_hint, "KLM"

    def find_peatland(self, point: Point) -> Dict[str, Any]:
        """Check if point falls inside any peatland hydrological unit."""
        for peat in self.peatlands:
            if peat["geometry"].contains(point):
                return {
                    "is_peatland": True,
                    "peatland_name": peat["name"],
                    "khg_id": peat["khg_id"],
                    "peat_vulnerability": peat["vulnerability"],
                    "peat_depth": peat["peat_depth"]
                }
            # Also check small buffer (0.05 deg ~= 5.5 km proximity)
            elif peat["geometry"].buffer(0.05).contains(point):
                return {
                    "is_peatland": True,
                    "peatland_name": f"{peat['name']} (Buffer Zone)",
                    "khg_id": peat["khg_id"],
                    "peat_vulnerability": peat["vulnerability"],
                    "peat_depth": peat["peat_depth"]
                }

        return {
            "is_peatland": False,
            "peatland_name": "Lahan Non-Gambut / Tanah Mineral",
            "khg_id": "N/A",
            "peat_vulnerability": "Low-Moderate",
            "peat_depth": "0m (Mineral)"
        }

    def compute_composite_hazard_score(self, frp: float, brightness: float, confidence_pct: float, is_peat: bool) -> Dict[str, Any]:
        """
        Calculates composite fire hazard score (0 to 100) based on FRP intensity,
        brightness temperature, satellite confidence, and peatland presence.
        """
        # Normalization
        frp_norm = min(frp / 60.0, 1.0) * 35  # Up to 35 pts
        bright_norm = min(max((brightness - 310) / (365 - 310), 0.0), 1.0) * 25  # Up to 25 pts
        conf_norm = (confidence_pct / 100.0) * 20  # Up to 20 pts
        peat_bonus = 20 if is_peat else 5  # Peat fire smolder risk (20 pts)

        total_score = round(frp_norm + bright_norm + conf_norm + peat_bonus, 1)
        total_score = min(max(total_score, 10), 100)

        if total_score < 40:
            severity = "Low"
            color = "#3b82f6"  # Blue
            badge = "Siaga Rendah"
        elif total_score < 65:
            severity = "Moderate"
            color = "#f59e0b"  # Amber
            badge = "Waspada Sedang"
        elif total_score < 82:
            severity = "High"
            color = "#f97316"  # Orange
            badge = "Bahaya Tinggi"
        else:
            severity = "Critical / Peat Smoldering"
            color = "#dc2626"  # Crimson Red
            badge = "Kritis (Gambut / Api Besar)"

        return {
            "hazard_score": total_score,
            "severity": severity,
            "color": color,
            "badge": badge
        }

    def process(self, df_hotspots: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Processes and enriches hotspot dataset with spatial polygons."""
        enriched_records = []
        geojson_features = []

        for _, row in df_hotspots.iterrows():
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            point = Point(lon, lat)

            hint = str(row.get("province_hint", "Kalimantan"))
            prov_name, prov_code = self.find_province(point, default_hint=hint)
            peat_info = self.find_peatland(point)

            frp = float(row.get("frp", 15.0))
            brightness = float(row.get("brightness", 330.0))
            conf_pct = float(row.get("confidence_pct", 75.0))

            hazard = self.compute_composite_hazard_score(frp, brightness, conf_pct, peat_info["is_peatland"])

            rec = dict(row)
            rec["province"] = prov_name
            rec["prov_code"] = prov_code
            rec["land_type"] = "Lahan Gambut" if peat_info["is_peatland"] else "Tanah Mineral"
            rec["peatland_name"] = peat_info["peatland_name"]
            rec["khg_id"] = peat_info["khg_id"]
            rec["peat_vulnerability"] = peat_info["peat_vulnerability"]
            rec["hazard_score"] = hazard["hazard_score"]
            rec["hazard_severity"] = hazard["severity"]
            rec["hazard_color"] = hazard["color"]
            rec["hazard_badge"] = hazard["badge"]

            enriched_records.append(rec)

            # Build GeoJSON feature
            geojson_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "hotspot_id": rec.get("hotspot_id", ""),
                    "province": prov_name,
                    "land_type": rec["land_type"],
                    "peatland_name": rec["peatland_name"],
                    "frp_mw": frp,
                    "brightness_k": brightness,
                    "confidence_pct": conf_pct,
                    "acq_datetime": rec.get("acq_datetime", ""),
                    "satellite": rec.get("satellite", ""),
                    "instrument": rec.get("instrument", ""),
                    "daynight": rec.get("daynight", "D"),
                    "hazard_score": hazard["hazard_score"],
                    "hazard_severity": hazard["severity"],
                    "hazard_color": hazard["color"]
                }
            })

        df_enriched = pd.DataFrame(enriched_records)

        # Save to CSV
        df_enriched.to_csv(HOTSPOTS_CSV_PATH, index=False, encoding="utf-8")

        # Save to GeoJSON
        geojson_collection = {
            "type": "FeatureCollection",
            "name": "Kalimantan_Active_Fire_Hotspots",
            "features": geojson_features
        }
        with open(HOTSPOTS_GEOJSON_PATH, "w", encoding="utf-8") as f:
            json.dump(geojson_collection, f, indent=2)

        # Summary Metrics
        summary = {
            "total_hotspots": len(df_enriched),
            "by_province": df_enriched["province"].value_counts().to_dict(),
            "by_land_type": df_enriched["land_type"].value_counts().to_dict(),
            "peat_percentage": round((df_enriched["land_type"].value_counts().get("Lahan Gambut", 0) / len(df_enriched)) * 100, 1),
            "mean_frp": round(float(df_enriched["frp"].mean()), 2),
            "max_frp": round(float(df_enriched["frp"].max()), 2),
            "mean_brightness_k": round(float(df_enriched["brightness"].mean()), 2),
            "high_hazard_count": int((df_enriched["hazard_score"] >= 65).sum())
        }

        return df_enriched, summary


if __name__ == "__main__":
    from nasa_firms_collector import NasaFirmsCollector
    collector = NasaFirmsCollector()
    df_raw = collector.collect()

    processor = GeospatialProcessor()
    df_proc, summary = processor.process(df_raw)
    print("Geospatial Processing Complete:")
    print(json.dumps(summary, indent=2))
