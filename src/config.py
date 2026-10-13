"""
Configuration and constants for Kalimantan Fire Geospatial Intelligence System.
Author: Data Science Geospatial Team
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GEOJSON_DIR = DATA_DIR / "geojson"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Ensure all directories exist
for directory in [DATA_DIR, GEOJSON_DIR, RAW_DIR, PROCESSED_DIR, DASHBOARD_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Kalimantan Geographic Bounding Box (Lat min, Lon min, Lat max, Lon max)
KALIMANTAN_BBOX = {
    "lat_min": -4.5,
    "lat_max": 4.5,
    "lon_min": 108.5,
    "lon_max": 119.5
}

# Key Regional Monitoring Stations across Kalimantan for Realtime Meteorology
MONITORING_STATIONS = [
    {
        "id": "STN_KT_PLK",
        "name": "Palangka Raya",
        "province": "Kalimantan Tengah",
        "lat": -2.2136,
        "lon": 113.9108,
        "elevation_m": 25,
        "type": "Peatland Center / High Risk"
    },
    {
        "id": "STN_KT_SMP",
        "name": "Sampit (Kotawaringin Timur)",
        "province": "Kalimantan Tengah",
        "lat": -2.5333,
        "lon": 112.9500,
        "elevation_m": 15,
        "type": "Peatland & Plantation Corridor"
    },
    {
        "id": "STN_KB_KTP",
        "name": "Ketapang (Kendawangan)",
        "province": "Kalimantan Barat",
        "lat": -1.8344,
        "lon": 109.9714,
        "elevation_m": 12,
        "type": "Coastal Peat Dome"
    },
    {
        "id": "STN_KB_PTK",
        "name": "Pontianak / Kubu Raya",
        "province": "Kalimantan Barat",
        "lat": -0.0263,
        "lon": 109.3425,
        "elevation_m": 8,
        "type": "Urban & Peatland Interface"
    },
    {
        "id": "STN_KS_BJB",
        "name": "Banjarbaru / Liang Anggang",
        "province": "Kalimantan Selatan",
        "lat": -3.4439,
        "lon": 114.8319,
        "elevation_m": 35,
        "type": "Airport & Peatland Zone"
    },
    {
        "id": "STN_KS_BRT",
        "name": "Barito Kuala (Marabahan)",
        "province": "Kalimantan Selatan",
        "lat": -2.9833,
        "lon": 114.7667,
        "elevation_m": 10,
        "type": "Agricultural Wetland / Peat"
    },
    {
        "id": "STN_KI_SMD",
        "name": "Samarinda / Kutai Kartanegara",
        "province": "Kalimantan Timur",
        "lat": -0.5022,
        "lon": 117.1536,
        "elevation_m": 20,
        "type": "Mahakam Basin / Mineral & Peat"
    },
    {
        "id": "STN_KU_TJS",
        "name": "Tanjung Selor / Bulungan",
        "province": "Kalimantan Utara",
        "lat": 2.8375,
        "lon": 117.3653,
        "elevation_m": 18,
        "type": "Northern Forest Corridor"
    }
]

# NASA FIRMS API Configuration
NASA_FIRMS_API_KEY = os.getenv("NASA_FIRMS_MAP_KEY", "")
NASA_FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/country/csv"

# Open-Meteo Weather API Configuration (Realtime, No API Key Required)
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Geospatial File Paths
PROVINCES_GEOJSON_PATH = GEOJSON_DIR / "kalimantan_provinces.geojson"
PEATLANDS_GEOJSON_PATH = GEOJSON_DIR / "kalimantan_peatlands.geojson"

# Processed output paths
HOTSPOTS_GEOJSON_PATH = PROCESSED_DIR / "kalimantan_hotspots_latest.geojson"
HOTSPOTS_CSV_PATH = PROCESSED_DIR / "kalimantan_hotspots_latest.csv"
HOTSPOTS_HISTORICAL_CSV = PROCESSED_DIR / "kalimantan_early_fire_onset_timeseries.csv"
WEATHER_LATEST_JSON = PROCESSED_DIR / "kalimantan_weather_latest.json"
WEATHER_LATEST_CSV = PROCESSED_DIR / "kalimantan_weather_latest.csv"
CLUSTER_METRICS_JSON = PROCESSED_DIR / "kalimantan_fire_clusters.json"

# Fire Risk Thresholds
FIRE_RISK_WEIGHTS = {
    "high_temp": 0.25,        # Temp > 32C
    "low_humidity": 0.25,    # RH < 65%
    "low_soil_moisture": 0.20,# Moisture < 0.25 m3/m3
    "high_wind": 0.15,       # Wind > 15 km/h
    "peatland_factor": 0.15  # Located in peatland
}
