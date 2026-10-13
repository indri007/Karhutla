"""
Geospatial Visualizer for Kalimantan Forest Fire Monitoring.
Builds an interactive Leaflet/Folium dashboard with multi-layer overlays:
Satellite Hotspots, Peatland Zones, Provincial Boundaries, Weather Stations, and DBSCAN Clusters.
"""
import json
import folium
from folium.plugins import MarkerCluster, HeatMap, MiniMap, Fullscreen
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

try:
    from src.config import (
        PROVINCES_GEOJSON_PATH,
        PEATLANDS_GEOJSON_PATH,
        DASHBOARD_DIR
    )
except ImportError:
    from config import (
        PROVINCES_GEOJSON_PATH,
        PEATLANDS_GEOJSON_PATH,
        DASHBOARD_DIR
    )


class MapVisualizer:
    """Builds interactive HTML geospatial map for Kalimantan Fire Intelligence."""

    def __init__(self):
        # Kalimantan center coordinates
        self.center_lat = -0.5
        self.center_lon = 114.0
        self.default_zoom = 6

    def generate_map(
        self,
        df_hotspots: pd.DataFrame,
        df_weather: pd.DataFrame,
        clusters: List[Dict[str, Any]],
        output_filename: str = "kalimantan_fire_geodashboard.html"
    ) -> str:
        """Creates the complete multi-layer interactive Leaflet map."""
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=self.default_zoom,
            tiles="CartoDB dark_matter",
            name="Dark Theme (Rekomendasi Karhutla)",
            control_scale=True
        )

        # Additional Basemaps
        folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="Satelit Citra Bumi (Esri Satellite)"
        ).add_to(m)

        folium.TileLayer(
            "OpenStreetMap",
            name="OpenStreetMap Standar"
        ).add_to(m)

        folium.TileLayer(
            "CartoDB positron",
            name="Light Theme"
        ).add_to(m)

        # 1. Provincial Boundaries Layer
        prov_group = folium.FeatureGroup(name="1. Batas 5 Provinsi Kalimantan", show=True)
        if PROVINCES_GEOJSON_PATH.exists():
            with open(PROVINCES_GEOJSON_PATH, "r", encoding="utf-8") as f:
                prov_geojson = json.load(f)

            folium.GeoJson(
                prov_geojson,
                style_function=lambda feature: {
                    "fillColor": "#3b82f6",
                    "color": "#60a5fa",
                    "weight": 2.2,
                    "fillOpacity": 0.08,
                    "dashArray": "4, 4"
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["state", "capital", "area_km2"],
                    aliases=["Provinsi:", "Ibukota:", "Luas Wilayah (km²):"],
                    localize=True,
                    sticky=True
                )
            ).add_to(prov_group)
        prov_group.add_to(m)

        # 2. Peatlands / KHG Layer
        peat_group = folium.FeatureGroup(name="2. Zona Ekosistem Lahan Gambut (KHG)", show=True)
        if PEATLANDS_GEOJSON_PATH.exists():
            with open(PEATLANDS_GEOJSON_PATH, "r", encoding="utf-8") as f:
                peat_geojson = json.load(f)

            folium.GeoJson(
                peat_geojson,
                style_function=lambda feature: {
                    "fillColor": "#78350f",
                    "color": "#d97706",
                    "weight": 2.0,
                    "fillOpacity": 0.35
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["name", "province", "peat_depth", "vulnerability"],
                    aliases=["Kubah Gambut (KHG):", "Provinsi:", "Kedalaman Gambut:", "Kerentanan Api:"],
                    localize=True,
                    sticky=True
                ),
                popup=folium.GeoJsonPopup(
                    fields=["name", "province", "peat_depth", "vulnerability", "carbon_stock_mt", "description"],
                    aliases=["Nama KHG:", "Provinsi:", "Kedalaman:", "Kerentanan Kebakaran:", "Stok Karbon (Mt):", "Deskripsi Wilayah:"],
                    labels=True
                )
            ).add_to(peat_group)
        peat_group.add_to(m)

        # 3. HeatMap Layer
        heat_group = folium.FeatureGroup(name="3. Heatmap Kepadatan & Daya Termal (FRP)", show=True)
        if not df_hotspots.empty:
            heat_data = [[row["latitude"], row["longitude"], float(row.get("frp", 10.0))] for _, row in df_hotspots.iterrows()]
            HeatMap(
                heat_data,
                radius=18,
                blur=14,
                max_zoom=10,
                gradient={0.2: '#3b82f6', 0.4: '#10b981', 0.6: '#f59e0b', 0.8: '#f97316', 1.0: '#ef4444'}
            ).add_to(heat_group)
        heat_group.add_to(m)

        # 4. Active Hotspots (Clustered & Styled Markers)
        hotspot_group = folium.FeatureGroup(name="4. Titik Panas Aktif (Hotspots Satelit)", show=True)
        marker_cluster = MarkerCluster(
            name="Cluster Titik Api",
            options={"maxClusterRadius": 35, "spiderfyOnMaxZoom": True}
        )

        for _, row in df_hotspots.iterrows():
            lat = row["latitude"]
            lon = row["longitude"]
            frp = row.get("frp", 0.0)
            bright = row.get("brightness", 320.0)
            conf = row.get("confidence_pct", 70)
            land = row.get("land_type", "Tanah Mineral")
            hazard_score = row.get("hazard_score", 50)
            hazard_color = row.get("hazard_color", "#f97316")
            prov = row.get("province", "Kalimantan")
            peat_name = row.get("peatland_name", "-")
            sat = row.get("satellite", "VIIRS")
            acq_time = row.get("acq_datetime", "")

            popup_html = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 240px; font-size: 12px; color: #1e293b;">
                <div style="background: {hazard_color}; color: white; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px; font-weight: bold;">
                    🔥 {row.get('hotspot_id', 'HOTSPOT')}
                </div>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="color: #64748b;">Lokasi:</td><td><b>{prov}</b></td></tr>
                    <tr><td style="color: #64748b;">Tipe Lahan:</td><td><b style="color: {'#b45309' if 'Gambut' in land else '#0f766e'};">{land}</b></td></tr>
                    <tr><td style="color: #64748b;">Unit Gambut:</td><td>{peat_name}</td></tr>
                    <tr><td style="color: #64748b;">FRP (Daya Radiasi):</td><td><b style="color: #e11d48;">{frp} MW</b></td></tr>
                    <tr><td style="color: #64748b;">Suhu Kecerahan:</td><td><b>{bright} K</b></td></tr>
                    <tr><td style="color: #64748b;">Tingkat Keyakinan:</td><td><b>{conf}%</b></td></tr>
                    <tr><td style="color: #64748b;">Satelit/Sensor:</td><td>{sat} ({row.get('instrument', 'VIIRS')})</td></tr>
                    <tr><td style="color: #64748b;">Waktu Deteksi:</td><td>{acq_time}</td></tr>
                    <tr><td style="color: #64748b;">Skor Bahaya (0-100):</td><td><b style="color: {hazard_color};">{hazard_score} ({row.get('hazard_severity', '')})</b></td></tr>
                </table>
            </div>
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=6.5 if frp < 25 else 9.5,
                color="#ffffff",
                weight=1.2,
                fill=True,
                fill_color=hazard_color,
                fill_opacity=0.88,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row.get('hotspot_id', '')} | {land} | FRP: {frp}MW"
            ).add_to(marker_cluster)

        marker_cluster.add_to(hotspot_group)
        hotspot_group.add_to(m)

        # 5. DBSCAN Epicenter Clusters
        cluster_group = folium.FeatureGroup(name="5. Episentrum & Klaster DBSCAN", show=True)
        for c in clusters:
            folium.Circle(
                location=[c["centroid_lat"], c["centroid_lon"]],
                radius=12000 + (c["hotspot_count"] * 250),
                color=c["risk_color"],
                weight=2.5,
                fill=True,
                fill_color=c["risk_color"],
                fill_opacity=0.22,
                dash_array="6, 6",
                tooltip=f"<b>{c['name']}</b><br>Jumlah Hotspot: {c['hotspot_count']}<br>Total FRP: {c['total_frp_mw']} MW",
                popup=f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 220px; font-size: 12px;">
                    <h4 style="margin: 0 0 6px 0; color: {c['risk_color']};">{c['name']}</h4>
                    <p style="margin: 2px 0;"><b>Tipe:</b> {c['cluster_type']}</p>
                    <p style="margin: 2px 0;"><b>Total Titik Api:</b> {c['hotspot_count']} titik</p>
                    <p style="margin: 2px 0;"><b>Total Radiasi Termal (FRP):</b> {c['total_frp_mw']} MW</p>
                    <p style="margin: 2px 0;"><b>Persentase Gambut:</b> {c['peat_percentage']}%</p>
                    <p style="margin: 2px 0;"><b>Suhu Maksimum:</b> {c['max_brightness_k']} K</p>
                </div>
                """
            ).add_to(cluster_group)
        cluster_group.add_to(m)

        # 6. Weather Monitoring Stations
        weather_group = folium.FeatureGroup(name="6. Stasiun Cuaca Realtime & Indeks Bahaya Cuaca", show=True)
        if not df_weather.empty:
            for _, stn in df_weather.iterrows():
                fdr_color = stn.get("fire_danger_color", "#10b981")
                stn_html = f"""
                <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 250px; font-size: 12px; color: #1e293b;">
                    <div style="background: {fdr_color}; color: white; padding: 6px 10px; border-radius: 4px; font-weight: bold; margin-bottom: 6px;">
                        🌤️ Stasiun: {stn['station_name']}
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="color: #64748b;">Provinsi:</td><td><b>{stn['province']}</b></td></tr>
                        <tr><td style="color: #64748b;">Kategori Wilayah:</td><td>{stn.get('station_type', '-')}</td></tr>
                        <tr><td style="color: #64748b;">Suhu Udara (2m):</td><td><b>{stn['temperature_c']} °C</b></td></tr>
                        <tr><td style="color: #64748b;">Kelembaban Relatif:</td><td><b>{stn['relative_humidity_pct']}%</b></td></tr>
                        <tr><td style="color: #64748b;">Kelembaban Tanah (0-7cm):</td><td><b>{stn['soil_moisture_m3_m3']} m³/m³</b></td></tr>
                        <tr><td style="color: #64748b;">Kecepatan Angin:</td><td><b>{stn['wind_speed_kmh']} km/jam</b></td></tr>
                        <tr><td style="color: #64748b;">Presipitasi / Hujan:</td><td><b>{stn['precipitation_mm']} mm</b></td></tr>
                        <tr><td style="color: #64748b;">Indeks Bahaya Cuaca (0-100):</td><td><b style="color: {fdr_color};">{stn['fire_danger_score']} ({stn['fire_danger_category']})</b></td></tr>
                    </table>
                </div>
                """

                # Station icon
                folium.Marker(
                    location=[stn["lat"], stn["lon"]],
                    icon=folium.Icon(color="darkblue" if stn["fire_danger_score"] < 50 else "red", icon="cloud", prefix="fa"),
                    popup=folium.Popup(stn_html, max_width=320),
                    tooltip=f"Stasiun {stn['station_name']} | Bahaya: {stn['fire_danger_score']}/100"
                ).add_to(weather_group)
        weather_group.add_to(m)

        # Add Controls
        folium.LayerControl(position="topright", collapsed=False).add_to(m)
        Fullscreen(position="topleft").add_to(m)
        MiniMap(toggle_display=True, position="bottomright").add_to(m)

        # Inject Glassmorphism Header and Legend HTML into template
        total_hotspots = len(df_hotspots)
        peat_pct = round(((df_hotspots['land_type'] == 'Lahan Gambut').sum() / max(1, total_hotspots)) * 100, 1) if not df_hotspots.empty else 0
        total_frp = round(df_hotspots['frp'].sum(), 1) if not df_hotspots.empty else 0
        n_clusters = len(clusters)

        floating_ui = f"""
        <div style="
            position: fixed;
            top: 15px;
            left: 55px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 12px 18px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            color: white;
            font-family: 'Segoe UI', Roboto, sans-serif;
            max-width: 440px;
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 20px;">🛰️</span>
                <div>
                    <h3 style="margin: 0; font-size: 15px; font-weight: 700; color: #f8fafc; letter-spacing: 0.3px;">
                        KALIMANTAN FIRE GEOSPATIAL INTELLIGENCE
                    </h3>
                    <p style="margin: 0; font-size: 11px; color: #94a3b8;">
                        Pemantauan Titik Api & Cuaca Rentang Awal Kebakaran (Near Real-Time)
                    </p>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 8px; text-align: center;">
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 4px;">
                    <div style="font-size: 16px; font-weight: bold; color: #f87171;">{total_hotspots}</div>
                    <div style="font-size: 9px; color: #cbd5e1;">Titik Api</div>
                </div>
                <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 4px;">
                    <div style="font-size: 16px; font-weight: bold; color: #fbbf24;">{peat_pct}%</div>
                    <div style="font-size: 9px; color: #cbd5e1;">Lahan Gambut</div>
                </div>
                <div style="background: rgba(225, 29, 72, 0.15); border: 1px solid rgba(225, 29, 72, 0.3); border-radius: 6px; padding: 4px;">
                    <div style="font-size: 16px; font-weight: bold; color: #fb7185;">{total_frp}</div>
                    <div style="font-size: 9px; color: #cbd5e1;">Total FRP (MW)</div>
                </div>
                <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 6px; padding: 4px;">
                    <div style="font-size: 16px; font-weight: bold; color: #818cf8;">{n_clusters}</div>
                    <div style="font-size: 9px; color: #cbd5e1;">Klaster Spasial</div>
                </div>
            </div>
        </div>

        <div style="
            position: fixed;
            bottom: 25px;
            left: 20px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 10px 14px;
            border-radius: 10px;
            color: #e2e8f0;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 11px;
            line-height: 1.6;
            max-width: 250px;
        ">
            <div style="font-weight: bold; margin-bottom: 4px; color: #f1f5f9; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 2px;">
                🗺️ Legenda Lapisan Geospasial
            </div>
            <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#dc2626;margin-right:6px;"></span> Hotspot Kritis / Gambut</div>
            <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f97316;margin-right:6px;"></span> Hotspot Bahaya Tinggi</div>
            <div><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f59e0b;margin-right:6px;"></span> Hotspot Bahaya Sedang</div>
            <div><span style="display:inline-block;width:12px;height:10px;background:#78350f;opacity:0.6;margin-right:6px;border:1px solid #d97706;"></span> Kubah Gambut (KHG)</div>
            <div><span style="display:inline-block;width:12px;height:10px;border:2px dashed #60a5fa;margin-right:6px;"></span> Batas Provinsi Kalimantan</div>
            <div><span style="display:inline-block;width:12px;height:10px;border:2px dashed #f97316;margin-right:6px;"></span> Episentrum DBSCAN</div>
        </div>
        """

        m.get_root().html.add_child(folium.Element(floating_ui))

        output_path = DASHBOARD_DIR / output_filename
        m.save(str(output_path))
        return str(output_path)


if __name__ == "__main__":
    from nasa_firms_collector import NasaFirmsCollector
    from geospatial_processor import GeospatialProcessor
    from weather_collector import WeatherCollector
    from cluster_analyzer import ClusterAnalyzer

    print("[PIPELINE] Running Visualizer Test...")
    collector = NasaFirmsCollector()
    df_raw = collector.collect()

    geo_proc = GeospatialProcessor()
    df_proc, _ = geo_proc.process(df_raw)

    weather_proc = WeatherCollector()
    df_weather = weather_proc.collect_all_stations()

    analyzer = ClusterAnalyzer()
    df_clustered, clusters = analyzer.perform_dbscan_clustering(df_proc)

    visualizer = MapVisualizer()
    saved_path = visualizer.generate_map(df_clustered, df_weather, clusters)
    print(f"[SUCCESS] Interactive Map Dashboard generated at: {saved_path}")
