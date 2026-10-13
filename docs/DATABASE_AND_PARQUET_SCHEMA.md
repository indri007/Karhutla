# 📐 TECHNICAL DATA SCHEMA SPECIFICATION
### *Sistem Prediksi Karhutla Indonesia (PostgreSQL/PostGIS, Apache Parquet, & Pydantic)*

---

## 🏛️ 1. Skema Basis Data Relasional / Spasial (PostgreSQL 15+ & PostGIS 3+)

Skema DDL lengkap untuk implementasi basis data operasional geospasial:

```sql
-- ============================================================================
-- 0. EKSTENSI GEOSPASIAL
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. TABEL ENTITAS SPASIAL STATIS
-- ============================================================================

-- A. Batas Administrasi Provinsi
CREATE TABLE administrative_regions (
    province_id VARCHAR(10) PRIMARY KEY,
    province_name VARCHAR(100) NOT NULL,
    island_name VARCHAR(50) NOT NULL CHECK (island_name IN ('Sumatera', 'Kalimantan', 'Jawa', 'Sulawesi', 'Papua', 'Lainnya')),
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_regions_geom ON administrative_regions USING GIST(geom);

-- B. Kesatuan Hidrologis Gambut (KHG / Peatland Domes)
CREATE TABLE peatland_hydrological_units (
    khg_id VARCHAR(30) PRIMARY KEY,
    khg_name VARCHAR(150) NOT NULL,
    depth_category VARCHAR(30) NOT NULL CHECK (depth_category IN ('Dangkal (<1m)', 'Sedang (1-2m)', 'Dalam (2-3m)', 'Sangat Dalam (>3m)')),
    vulnerability_index NUMERIC(4, 3) NOT NULL CHECK (vulnerability_index BETWEEN 0.0 AND 1.0),
    geom GEOMETRY(MultiPolygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_khg_geom ON peatland_hydrological_units USING GIST(geom);

-- C. Sel Grid Spasial 0.25 Derajat (~28km x 28km)
CREATE TABLE grid_cells (
    cell_id INT PRIMARY KEY,
    province_id VARCHAR(10) REFERENCES administrative_regions(province_id) ON DELETE SET NULL,
    khg_id VARCHAR(30) REFERENCES peatland_hydrological_units(khg_id) ON DELETE SET NULL,
    lon_centre NUMERIC(7, 4) NOT NULL,
    lat_centre NUMERIC(7, 4) NOT NULL,
    cell_area_km2 NUMERIC(8, 2) NOT NULL,
    peat_fraction NUMERIC(4, 3) DEFAULT 0.0 CHECK (peat_fraction BETWEEN 0.0 AND 1.0),
    oil_palm_fraction NUMERIC(4, 3) DEFAULT 0.0 CHECK (oil_palm_fraction BETWEEN 0.0 AND 1.0),
    wood_fibre_fraction NUMERIC(4, 3) DEFAULT 0.0 CHECK (wood_fibre_fraction BETWEEN 0.0 AND 1.0),
    road_length_km NUMERIC(8, 2) DEFAULT 0.0,
    road_density_km_per_km2 NUMERIC(6, 3) DEFAULT 0.0,
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grid_cells_geom ON grid_cells USING GIST(geom);
CREATE INDEX idx_grid_cells_coords ON grid_cells(lat_centre, lon_centre);
CREATE INDEX idx_grid_cells_province ON grid_cells(province_id);

-- ============================================================================
-- 2. TABEL PENGAMATAN DINAMIS & TELEMETRI
-- ============================================================================

-- D. Deteksi Titik Panas Mentah Satelit (NASA FIRMS / SiPongi+)
CREATE TABLE raw_hotspot_detections (
    hotspot_id VARCHAR(64) PRIMARY KEY,
    cell_id INT REFERENCES grid_cells(cell_id) ON DELETE CASCADE,
    acq_datetime TIMESTAMPTZ NOT NULL,
    satellite_sensor VARCHAR(30) NOT NULL CHECK (satellite_sensor IN ('VIIRS_SNPP', 'VIIRS_NOAA20', 'VIIRS_NOAA21', 'MODIS_TERRA', 'MODIS_AQUA')),
    latitude NUMERIC(8, 5) NOT NULL,
    longitude NUMERIC(8, 5) NOT NULL,
    brightness_temp_k NUMERIC(6, 2) NOT NULL,
    frp_mw NUMERIC(8, 2) NOT NULL,
    confidence_level VARCHAR(10) NOT NULL CHECK (confidence_level IN ('low', 'nominal', 'high')),
    geom GEOMETRY(Point, 4326) NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_raw_hotspots_datetime ON raw_hotspot_detections(acq_datetime);
CREATE INDEX idx_raw_hotspots_cell ON raw_hotspot_detections(cell_id);
CREATE INDEX idx_raw_hotspots_geom ON raw_hotspot_detections USING GIST(geom);

-- E. Pengamatan Reanalisis Cuaca (ERA5-Land)
CREATE TABLE weather_observations (
    weather_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    cell_id INT NOT NULL REFERENCES grid_cells(cell_id) ON DELETE CASCADE,
    obs_date DATE NOT NULL,
    temperature_2m_k NUMERIC(6, 2) NOT NULL,
    temperature_2m_c NUMERIC(5, 2) NOT NULL,
    total_precipitation_m NUMERIC(7, 4) NOT NULL,
    wind_speed_ms NUMERIC(5, 2) NOT NULL,
    u10_wind_ms NUMERIC(5, 2) NOT NULL,
    v10_wind_ms NUMERIC(5, 2) NOT NULL,
    soil_moisture_0_7cm NUMERIC(5, 3),
    soil_moisture_7_28cm NUMERIC(5, 3),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cell_weather_date UNIQUE (cell_id, obs_date)
);

CREATE INDEX idx_weather_cell_date ON weather_observations(cell_id, obs_date);

-- ============================================================================
-- 3. TABEL PANEL MACHINE LEARNING (SPATIOTEMPORAL FEATURE STORE)
-- ============================================================================

CREATE TABLE spatiotemporal_panel_core (
    panel_id VARCHAR(40) PRIMARY KEY, -- Format: {cell_id}_{year}_{month}
    cell_id INT NOT NULL REFERENCES grid_cells(cell_id) ON DELETE CASCADE,
    year INT NOT NULL CHECK (year BETWEEN 2000 AND 2050),
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    obs_timestamp TIMESTAMPTZ NOT NULL,
    
    -- Metrik Titik Api Bulan Berjalan
    fire_count_lnh INT NOT NULL DEFAULT 0,
    fire_count_nh INT NOT NULL DEFAULT 0,
    fire_any_lnh SMALLINT NOT NULL DEFAULT 0 CHECK (fire_any_lnh IN (0, 1)),
    fire_any_nh SMALLINT NOT NULL DEFAULT 0 CHECK (fire_any_nh IN (0, 1)),
    frp_sum_lnh NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    frp_sum_nh NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    
    -- Cuaca Agregat Bulan Berjalan
    t2m_c NUMERIC(5, 2) NOT NULL,
    tp_m NUMERIC(7, 4) NOT NULL,
    wind_speed_ms NUMERIC(5, 2) NOT NULL,
    
    -- Fitur Lagged (Dihitung per sel)
    fire_count_nh_lag1 INT DEFAULT 0,
    fire_count_nh_lag2 INT DEFAULT 0,
    tp_lag1 NUMERIC(7, 4),
    tp_lag2 NUMERIC(7, 4),
    t2m_c_lag1 NUMERIC(5, 2),
    precip_deficit_3m NUMERIC(7, 4),
    
    -- Fitur Tetangga Spasial
    neighbor_fire_count_mean_lag1 NUMERIC(6, 2) DEFAULT 0.0,
    
    -- Target Prediksi Horizon Masa Depan (Leak-Free)
    target_fire_next_1m SMALLINT DEFAULT 0 CHECK (target_fire_next_1m IN (0, 1)),
    target_fire_next_3m SMALLINT DEFAULT 0 CHECK (target_fire_next_3m IN (0, 1)),
    
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cell_year_month UNIQUE (cell_id, year, month)
);

CREATE INDEX idx_panel_time ON spatiotemporal_panel_core(year, month);
CREATE INDEX idx_panel_cell ON spatiotemporal_panel_core(cell_id);
CREATE INDEX idx_panel_target ON spatiotemporal_panel_core(target_fire_next_1m);

-- ============================================================================
-- 4. TABEL MODEL REGISTRY & INFERENSI
-- ============================================================================

CREATE TABLE model_registry (
    model_id VARCHAR(50) PRIMARY KEY,
    algorithm_name VARCHAR(50) NOT NULL,
    version_tag VARCHAR(20) NOT NULL,
    training_start_year INT NOT NULL,
    training_end_year INT NOT NULL,
    pr_auc_score NUMERIC(5, 4) NOT NULL,
    roc_auc_score NUMERIC(5, 4) NOT NULL,
    brier_score NUMERIC(5, 4) NOT NULL,
    model_artifact_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_predictions (
    prediction_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    panel_id VARCHAR(40) REFERENCES spatiotemporal_panel_core(panel_id) ON DELETE CASCADE,
    model_id VARCHAR(50) REFERENCES model_registry(model_id) ON DELETE RESTRICT,
    forecast_month VARCHAR(7) NOT NULL, -- YYYY-MM
    predicted_probability NUMERIC(5, 4) NOT NULL CHECK (predicted_probability BETWEEN 0.0000 AND 1.0000),
    predicted_log_count NUMERIC(6, 3),
    hazard_category VARCHAR(15) NOT NULL CHECK (hazard_category IN ('LOW', 'MODERATE', 'HIGH', 'CRITICAL')),
    inference_run_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pred_forecast_month ON model_predictions(forecast_month);
CREATE INDEX idx_pred_hazard ON model_predictions(hazard_category);
```

---

## 📦 2. Skema Fisik Apache Parquet / PyArrow (Offline Panel Data)

Spesifikasi skema kolom pada file terkompresi Parquet di [`data/aml_indo_fires/`](file:///Users/jevin/https-::github.com:indri007:Karhutla/data/aml_indo_fires/):

### 2.1 `panel_core_2012_2025.parquet`
| Nama Kolom | Tipe Data PyArrow | Nullable | Keterangan |
| :--- | :--- | :---: | :--- |
| `cell_id` | `int32` | No | ID unik sel grid 0.25° |
| `year` | `int16` | No | Tahun kalender (2012–2025) |
| `month` | `int8` | No | Bulan kalender (1–12) |
| `time` | `timestamp[us]` | No | Timestamp hari pertama bulan (UTC) |
| `lon_centre` | `float64` | No | Titik bujur tengah sel (°E) |
| `lat_centre` | `float64` | No | Titik lintang tengah sel (°N) |
| `fire_count_lnh` | `int32` | No | Total titik api VIIRS SNPP (semua confidence) |
| `fire_count_nh` | `int32` | No | Titik api confidence nominal dan tinggi |
| `fire_any_lnh` | `int8` | No | Indikator biner ada titik api (0 atau 1) |
| `fire_any_nh` | `int8` | No | Indikator biner titik api nominal/tinggi (Target Latih) |
| `frp_sum_lnh` | `float64` | No | Total Fire Radiative Power (MW) |
| `frp_sum_nh` | `float64` | No | Total FRP nominal/tinggi (MW) |
| `t2m` | `float64` | No | Suhu udara 2m reanalisis ERA5 (Kelvin) |
| `tp` | `float64` | No | Akumulasi curah hujan bulanan ERA5 (meter) |
| `u10` | `float64` | No | Komponen angin U pada 10m (m/s) |
| `v10` | `float64` | No | Komponen angin V pada 10m (m/s) |
| `wind_speed` | `float64` | No | Magnitudo kecepatan angin: $\sqrt{u10^2 + v10^2}$ (m/s) |
| `era5_latitude` | `float64` | No | Titik lintang grid ERA5 terdekat |
| `era5_longitude`| `float64` | No | Titik bujur grid ERA5 terdekat |
| `cell_area_km2` | `float64` | No | Luas sel daratan ($km^2$, proyeksi EPSG:6933) |
| `peat_fraction` | `float64` | No | Fraksi tutupan lahan gambut [0.0 – 1.0] |
| `oil_palm_fraction` | `float64` | No | Fraksi izin konsesi perkebunan sawit [0.0 – 1.0] |
| `wood_fibre_fraction` | `float64` | No | Fraksi izin HTI serat kayu [0.0 – 1.0] |
| `road_length_km` | `float64` | No | Panjang jalan di dalam sel ($km$) |
| `road_density_km_per_km2` | `float64` | No | Kerapatan jalan ($km/km^2$) |
| `province` | `string` | Yes | Nama provinsi administratif (GADM level-1) |

---

### 2.2 `modelling_data_nonlinear_2012_2025.parquet` (Fitur Siap Latih LightGBM)
Tabel ini berisi fitur turunan dan lag untuk pelatihan model pohon keputusan (*Tree-based*):
* **Target Kolom:**
  * `fire_any_nh` (`int8`): Target klasifikasi biner.
  * `fire_count_nh` (`int32`): Target regresi jumlah kejadian.
* **Fitur Lag Waktu:**
  * `fire_count_nh_lag1`, `fire_count_nh_lag2`, `fire_count_nh_lag3`, `fire_count_nh_lag12` (`int32`)
  * `tp_lag1`, `tp_lag2`, `tp_lag3`, `tp_lag12` (`float64`)
  * `t2m_c_lag1`, `t2m_c_lag2` (`float64`)
* **Proksi Anomali Kekeringan:**
  * `tp_anomaly` (`float64`): Deviasi curah hujan terhadap klimatologi historis.
  * `precip_deficit_3m` (`float64`): Defisit akumulasi hujan 3 bulan terakhir.
  * `tp_3m_sum_lag1` (`float64`): Total curah hujan 3 bulan sebelumnya.
* **Fitur Autokorelasi Tetangga Spasial (*Spatial Contiguity*):**
  * `neighbor_fire_count_nh_mean_lag1` (`float64`): Rerata titik api sel sekitar pada $t-1$.
  * `neighbor_fire_any_nh_mean_lag1` (`float64`): Proporsi sel tetangga yang terbakar pada $t-1$.

---

## 🐍 3. Model Validasi Data Python (Pydantic Schema v2)

Skema validasi runtime untuk pipeline ETL dan integrasi live API:

```python
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class HotspotRecordSchema(BaseModel):
    """Skema validasi untuk data hotspot mentah dari NASA FIRMS / SiPongi+."""
    hotspot_id: str = Field(..., description="ID unik atau UUID hotspot")
    cell_id: int = Field(..., ge=1, le=10000, description="ID sel grid 0.25 derajat")
    acq_datetime: datetime = Field(..., description="Waktu akuisisi satelit")
    latitude: float = Field(..., ge=-11.0, le=6.0, description="Lintang wilayah Indonesia")
    longitude: float = Field(..., ge=95.0, le=141.0, description="Bujur wilayah Indonesia")
    brightness_temp_k: float = Field(..., ge=200.0, le=550.0, description="Suhu kecerahan (Kelvin)")
    frp_mw: float = Field(..., ge=0.0, description="Fire Radiative Power dalam MW")
    confidence_level: Literal["low", "nominal", "high"] = Field(..., description="Tingkat keyakinan deteksi")
    satellite_sensor: str = Field(..., description="Nama sensor/satelit")


class MonthlyPanelRowSchema(BaseModel):
    """Skema baris data panel bulanan untuk inferensi Machine Learning."""
    cell_id: int
    year: int = Field(..., ge=2012, le=2030)
    month: int = Field(..., ge=1, le=12)
    t2m_c: float = Field(..., ge=15.0, le=45.0, description="Suhu permukaan 2m dalam Celsius")
    tp_m: float = Field(..., ge=0.0, description="Curah hujan bulanan dalam meter")
    wind_speed_ms: float = Field(..., ge=0.0, le=60.0, description="Kecepatan angin m/s")
    peat_fraction: float = Field(..., ge=0.0, le=1.0, description="Proporsi lahan gambut")
    concession_fraction_total: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Lag Features
    tp_lag1: float = Field(..., ge=0.0)
    precip_deficit_3m: float
    neighbor_fire_count_nh_mean_lag1: float = Field(default=0.0, ge=0.0)
    
    # Target
    fire_any_nh: Optional[int] = Field(default=None, ge=0, le=1)


class PredictionOutputSchema(BaseModel):
    """Skema output inferensi probabilitas dan penentuan level bahaya."""
    cell_id: int
    forecast_month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    predicted_probability: float = Field(..., ge=0.0, le=1.0)
    hazard_category: Literal["LOW", "MODERATE", "HIGH", "CRITICAL"]

    @field_validator("hazard_category", mode="before")
    @classmethod
    def assign_category(cls, v, values):
        prob = values.data.get("predicted_probability", 0.0)
        if prob < 0.25:
            return "LOW"
        elif prob < 0.50:
            return "MODERATE"
        elif prob < 0.75:
            return "HIGH"
        return "CRITICAL"
```
