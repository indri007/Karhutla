"""
Real-time Weather and Soil Moisture Ingestion for Kalimantan Monitoring Stations.
Uses Open-Meteo API (Open access, high-resolution meteorological model).
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
import pandas as pd
from typing import List, Dict, Any

try:
    from src.config import (
        MONITORING_STATIONS,
        OPEN_METEO_BASE_URL,
        WEATHER_LATEST_JSON,
        WEATHER_LATEST_CSV
    )
except ImportError:
    from config import (
        MONITORING_STATIONS,
        OPEN_METEO_BASE_URL,
        WEATHER_LATEST_JSON,
        WEATHER_LATEST_CSV
    )


class WeatherCollector:
    """Collects real-time meteorological indicators for fire risk analysis across Kalimantan."""

    def __init__(self, stations: List[Dict[str, Any]] = None):
        self.stations = stations or MONITORING_STATIONS

    def calculate_fire_danger_index(self, temp: float, rh: float, wind: float, precip: float, soil_moist: float) -> Dict[str, Any]:
        """
        Computes a calibrated Fire Weather / Danger Index (0 - 100) based on
        temperature, relative humidity, wind speed, precipitation, and topsoil moisture.
        """
        # 1. Temperature score (higher = higher fire risk)
        temp_score = min(max((temp - 24) / (38 - 24), 0), 1) * 30

        # 2. Relative Humidity score (lower = higher fire risk)
        rh_score = min(max((85 - rh) / (85 - 45), 0), 1) * 30

        # 3. Soil moisture score (lower = higher peat/soil ignition risk)
        # Typical tropical peat moisture dry threshold: < 0.35 m3/m3
        soil_score = min(max((0.45 - (soil_moist or 0.35)) / (0.45 - 0.15), 0), 1) * 20

        # 4. Wind speed score (higher = faster fire propagation)
        wind_score = min(max((wind - 5) / (30 - 5), 0), 1) * 15

        # 5. Precipitation penalty (recent rain dampens fire risk)
        precip_penalty = min(precip * 5, 25)

        raw_index = temp_score + rh_score + soil_score + wind_score - precip_penalty
        fdr_score = round(max(5, min(raw_index, 100)), 1)

        # Classification
        if fdr_score < 30:
            category = "LOW (Rendah - Aman)"
            color = "#10b981"  # Emerald green
            level = 1
        elif fdr_score < 55:
            category = "MODERATE (Sedang - Waspada)"
            color = "#f59e0b"  # Amber
            level = 2
        elif fdr_score < 75:
            category = "HIGH (Tinggi - Siaga)"
            color = "#f97316"  # Orange
            level = 3
        else:
            category = "EXTREME (Ekstrem - Sangat Kritis)"
            color = "#ef4444"  # Red
            level = 4

        return {
            "score": fdr_score,
            "category": category,
            "color": color,
            "level": level
        }

    def fetch_station_weather(self, station: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch current and hourly weather for a single station."""
        params = (
            f"?latitude={station['lat']}&longitude={station['lon']}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,wind_direction_10m,soil_moisture_0_to_7cm"
            f"&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,soil_moisture_0_to_7cm"
            f"&forecast_days=3&timezone=Asia%2FJakarta"
        )
        url = OPEN_METEO_BASE_URL + params
        req = urllib.request.Request(url, headers={"User-Agent": "Kalimantan-Fire-DataScience/1.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                current = payload.get("current", {})

                temp = current.get("temperature_2m", 30.0)
                rh = current.get("relative_humidity_2m", 70.0)
                wind = current.get("wind_speed_10m", 10.0)
                wind_dir = current.get("wind_direction_10m", 0)
                precip = current.get("precipitation", 0.0)
                soil_moist = current.get("soil_moisture_0_to_7cm", 0.35)

                fdr = self.calculate_fire_danger_index(temp, rh, wind, precip, soil_moist)

                return {
                    "station_id": station["id"],
                    "station_name": station["name"],
                    "province": station["province"],
                    "lat": station["lat"],
                    "lon": station["lon"],
                    "elevation_m": station["elevation_m"],
                    "station_type": station["type"],
                    "timestamp": current.get("time", datetime.now(timezone.utc).isoformat()),
                    "temperature_c": temp,
                    "relative_humidity_pct": rh,
                    "wind_speed_kmh": wind,
                    "wind_direction_deg": wind_dir,
                    "precipitation_mm": precip,
                    "soil_moisture_m3_m3": soil_moist,
                    "fire_danger_score": fdr["score"],
                    "fire_danger_category": fdr["category"],
                    "fire_danger_color": fdr["color"],
                    "fire_danger_level": fdr["level"],
                    "status": "SUCCESS"
                }
        except Exception as err:
            # Fallback estimation if network times out
            fdr = self.calculate_fire_danger_index(31.5, 68.0, 12.0, 0.0, 0.30)
            return {
                "station_id": station["id"],
                "station_name": station["name"],
                "province": station["province"],
                "lat": station["lat"],
                "lon": station["lon"],
                "elevation_m": station["elevation_m"],
                "station_type": station["type"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "temperature_c": 31.5,
                "relative_humidity_pct": 68.0,
                "wind_speed_kmh": 12.0,
                "wind_direction_deg": 180,
                "precipitation_mm": 0.0,
                "soil_moisture_m3_m3": 0.30,
                "fire_danger_score": fdr["score"],
                "fire_danger_category": fdr["category"],
                "fire_danger_color": fdr["color"],
                "fire_danger_level": fdr["level"],
                "status": f"FALLBACK_ESTIMATE: {str(err)}"
            }

    def collect_all_stations(self) -> pd.DataFrame:
        """Collects weather for all Kalimantan stations and saves to disk."""
        records = []
        for stn in self.stations:
            rec = self.fetch_station_weather(stn)
            records.append(rec)

        df = pd.DataFrame(records)
        df.to_csv(WEATHER_LATEST_CSV, index=False, encoding="utf-8")

        with open(WEATHER_LATEST_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "stations_count": len(records),
                "data": records
            }, f, indent=2)

        return df


if __name__ == "__main__":
    collector = WeatherCollector()
    df_weather = collector.collect_all_stations()
    print("Collected Weather Stations for Kalimantan:")
    print(df_weather[["station_name", "province", "temperature_c", "relative_humidity_pct", "soil_moisture_m3_m3", "fire_danger_category"]])
