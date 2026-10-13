"""
Social Network Analysis (SNA) & Discourse Graph Generator for Karhutla Indonesia.
Generates NodeXL-style actor interaction, media framing, and legal enforcement graphs.
Outputs:
1. data/processed/karhutla_sna_nodes.csv
2. data/processed/karhutla_sna_edges.csv
3. data/processed/karhutla_sna_summary.json
4. dashboard/karhutla_sna_network_graph.html (Standalone Vis.js Interactive Web Canvas)
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import networkx as nx
import pandas as pd
import numpy as np

try:
    from src.config import PROCESSED_DIR, DASHBOARD_DIR
except ImportError:
    from config import PROCESSED_DIR, DASHBOARD_DIR


class KarhutlaActorNetworkGenerator:
    """Constructs and analyzes the complex actor, regulatory, and media discourse network of Karhutla."""

    def __init__(self):
        self.nodes_data = [
            # Group 1: Pemerintah & Penegak Hukum (Regulator & State Actors)
            {"id": "G_KLHK", "label": "KLHK (Kementerian Kehutanan)", "group": "Pemerintah & Penegak Hukum", "role": "Regulator & Pengawas Hutan", "influence": 95},
            {"id": "G_GAKKUM", "label": "Ditjen Gakkum KLHK", "group": "Pemerintah & Penegak Hukum", "role": "Penyidik & Eksekutor Segel Lahan", "influence": 90},
            {"id": "G_BNPB", "label": "BNPB Indonesia", "group": "Pemerintah & Penegak Hukum", "role": "Komando Tanggap Darurat & Water Bombing", "influence": 88},
            {"id": "G_BMKG", "label": "BMKG Stasiun Klimatologi", "group": "Pemerintah & Penegak Hukum", "role": "Penyedia Telemetri Cuaca & Hotspot", "influence": 82},
            {"id": "G_BRGM", "label": "Badan Restorasi Gambut & Mangrove", "group": "Pemerintah & Penegak Hukum", "role": "Restorasi 3R & Sekat Kanal", "influence": 84},
            {"id": "G_POLRI", "label": "Polda & Bareskrim Polri", "group": "Pemerintah & Penegak Hukum", "role": "Penyidikan Pidana Karhutla", "influence": 80},
            {"id": "G_MANGGALA", "label": "Manggala Agni & TNI", "group": "Pemerintah & Penegak Hukum", "role": "Pasukan Pemadam Darat Gambut", "influence": 85},
            {"id": "G_PEMDA_KT", "label": "Pemprov Kalimantan Tengah", "group": "Pemerintah & Penegak Hukum", "role": "Pemerintah Daerah Wilayah Rentan", "influence": 76},

            # Group 2: Korporasi Konsesi & Pelaku Ekonomi (Industry & Economic Actors)
            {"id": "C_GAPKI", "label": "GAPKI (Gabungan Pengusaha Sawit)", "group": "Sektor Industri & Korporasi", "role": "Asosiasi Perkebunan Kelapa Sawit", "influence": 86},
            {"id": "C_APHI", "label": "APHI (Pengusaha Hutan Tanaman)", "group": "Sektor Industri & Korporasi", "role": "Asosiasi Pemegang IUPHHK-HTI", "influence": 78},
            {"id": "C_KORPORASI_SAWIT", "label": "Korporasi Sawit Pemegang HGU", "group": "Sektor Industri & Korporasi", "role": "Pemilik Konsesi Lahan Gambut", "influence": 89},
            {"id": "C_KORPORASI_HTI", "label": "Korporasi HTI Serat Kayu", "group": "Sektor Industri & Korporasi", "role": "Kanalisasi & Pengeringan Lahan", "influence": 82},
            {"id": "C_SPEKULAN", "label": "Spekulan Lahan & Cukong Lokal", "group": "Sektor Industri & Korporasi", "role": "Pengupah Pembakaran Liar Murah", "influence": 75},
            {"id": "C_KONTRAKTOR", "label": "Kontraktor Land Clearing Pihak Ketiga", "group": "Sektor Industri & Korporasi", "role": "Pelaksana Pembersihan Lahan Murah", "influence": 68},

            # Group 3: LSM & Masyarakat Sipil (Civil Society & Environmental NGOs)
            {"id": "N_WALHI", "label": "WALHI (Wahana Lingkungan Hidup)", "group": "LSM & Koalisi Sipil", "role": "Gugatan Hukum & Advokasi Publik", "influence": 92},
            {"id": "N_GREENPEACE", "label": "Greenpeace Indonesia", "group": "LSM & Koalisi Sipil", "role": "Investigasi Satelit Deforestasi", "influence": 89},
            {"id": "N_PANTAU_GAMBUT", "label": "Pantau Gambut", "group": "LSM & Koalisi Sipil", "role": "Audit Kerentanan Kubah KHG", "influence": 87},
            {"id": "N_AURIGA", "label": "Yayasan Auriga Nusantara", "group": "LSM & Koalisi Sipil", "role": "Analisis Spasial Kepemilikan Lahan", "influence": 84},
            {"id": "N_ICEL", "label": "ICEL (Hukum Lingkungan)", "group": "LSM & Koalisi Sipil", "role": "Eksaminasi Peradilan Lingkungan", "influence": 77},

            # Group 4: Riset & Media Massa (Media & Research Institutions)
            {"id": "M_KOMPAS", "label": "Harian Kompas & Kompas.com", "group": "Media Massa & Riset", "role": "Jurnalisme Investigasi Lingkungan", "influence": 85},
            {"id": "M_TEMPO", "label": "Majalah Tempo & Investigasi", "group": "Media Massa & Riset", "role": "Liputan Khusus Mafia Karhutla", "influence": 88},
            {"id": "M_MONGABAY", "label": "Mongabay Indonesia", "group": "Media Massa & Riset", "role": "Jurnalisme Lingkungan Internasional", "influence": 80},
            {"id": "M_IPB_UGM", "label": "Pusat Studi Gambut IPB / UGM", "group": "Media Massa & Riset", "role": "Riset Ilmiah Hidrologi & Emisi CO2", "influence": 83},
            {"id": "M_ANTARA", "label": "LKBN Antara", "group": "Media Massa & Riset", "role": "Kantor Berita Resmi Nasional", "influence": 72},

            # Group 5: Publik Terdampak & Isu Transboundary (Victims & Transboundary Corridor)
            {"id": "V_WARGA_PLK", "label": "Warga Palangka Raya (Korban ISPA)", "group": "Publik & Transboundary ASEAN", "role": "Korban Paparan Partikulat PM2.5", "influence": 88},
            {"id": "V_ADAT_DAYAK", "label": "Masyarakat Adat Dayak", "group": "Publik & Transboundary ASEAN", "role": "Penjaga Kearifan Lokal Peladang", "influence": 81},
            {"id": "V_SARAWAK", "label": "Pemerintah Negeri Sarawak (Malaysia)", "group": "Publik & Transboundary ASEAN", "role": "Penerima Asap Lintas Batas (AQI 365)", "influence": 84},
            {"id": "V_SINGAPURA", "label": "National Environment Agency Singapore", "group": "Publik & Transboundary ASEAN", "role": "Monitoring Haze Corridor (PSI 210)", "influence": 86}
        ]

        self.edges_data = [
            # 1. Penegakan Hukum & Investigasi (Enforcement & Legal Actions)
            {"source": "G_GAKKUM", "target": "C_KORPORASI_SAWIT", "type": "Penyegelan Konsesi & Sanksi Cabut Izin", "weight": 9, "sentiment": "Konflik / Penegakan"},
            {"source": "G_GAKKUM", "target": "C_KORPORASI_HTI", "type": "Gugatan Ganti Rugi Perdata Karhutla", "weight": 8, "sentiment": "Konflik / Penegakan"},
            {"source": "G_POLRI", "target": "C_SPEKULAN", "type": "Penetapan Tersangka Pembakaran Sengaja", "weight": 8, "sentiment": "Penegakan Hukum"},
            {"source": "G_POLRI", "target": "C_KONTRAKTOR", "type": "Pemeriksaan Modus Land Clearing Murah", "weight": 7, "sentiment": "Penegakan Hukum"},
            {"source": "N_WALHI", "target": "G_KLHK", "type": "Gugatan Warga Negara (Citizen Lawsuit)", "weight": 9, "sentiment": "Kritik / Advokasi"},
            {"source": "N_WALHI", "target": "C_KORPORASI_SAWIT", "type": "Rilis Daftar Hitam Korporasi Pembakar", "weight": 9, "sentiment": "Konflik / Ekspose"},
            {"source": "N_ICEL", "target": "G_GAKKUM", "type": "Eksaminasi Eksekusi Putusan Inkrah Pengadilan", "weight": 8, "sentiment": "Kolaborasi Yuridis"},

            # 2. Investigasi Satelit & Audit Gambut (Data & Monitoring Flow)
            {"source": "N_GREENPEACE", "target": "C_KORPORASI_SAWIT", "type": "Publikasi Laporan Spasial Deforestasi", "weight": 9, "sentiment": "Ekspose Publik"},
            {"source": "N_PANTAU_GAMBUT", "target": "G_BRGM", "type": "Audit Efektivitas Sekat Kanal Gambut", "weight": 8, "sentiment": "Evaluasi Ilmiah"},
            {"source": "N_AURIGA", "target": "M_TEMPO", "type": "Suplai Data Spasial Investigasi HGU Bermasalah", "weight": 9, "sentiment": "Kolaborasi Media"},
            {"source": "G_BMKG", "target": "G_BNPB", "type": "Peringatan Dini Anomali Cuaca & Hotspot VIIRS", "weight": 9, "sentiment": "Koordinasi Operasional"},
            {"source": "G_BMKG", "target": "G_MANGGALA", "type": "Data Real-time Arah Angin & Kekeringan Tanah", "weight": 9, "sentiment": "Dukungan Taktis"},
            {"source": "G_BRGM", "target": "G_MANGGALA", "type": "Koordinasi Operasi Pembasahan Cepat Gambut", "weight": 8, "sentiment": "Koordinasi"},
            {"source": "M_IPB_UGM", "target": "G_KLHK", "type": "Policy Paper Emisi Karbon Gambut Terbakar", "weight": 7, "sentiment": "Rekomendasi Riset"},

            # 3. Operasi Darurat & Penyelamatan Lapangan (Emergency Actions)
            {"source": "G_BNPB", "target": "G_MANGGALA", "type": "Dukungan Water Bombing & Helikopter Patroli", "weight": 10, "sentiment": "Operasi Darurat"},
            {"source": "G_BNPB", "target": "G_PEMDA_KT", "type": "Penyaluran Dana Siap Pakai & Posko Bencana", "weight": 8, "sentiment": "Dukungan Pemda"},
            {"source": "G_MANGGALA", "target": "V_WARGA_PLK", "type": "Pemadaman Api Lapisan Bawah Tanah Gambut", "weight": 9, "sentiment": "Perlindungan Warga"},
            {"source": "G_PEMDA_KT", "target": "V_WARGA_PLK", "type": "Pemberian Masker N95 & Ruang Oksigen Gratis", "weight": 7, "sentiment": "Layanan Darurat"},

            # 4. Dinamika Industri & Pembelaan (Industrial Defense & Lobby)
            {"source": "C_GAPKI", "target": "G_KLHK", "type": "Klaim Kepatuhan Standard ISPO & Fire-Free", "weight": 7, "sentiment": "Lobi / Klarifikasi"},
            {"source": "C_GAPKI", "target": "M_KOMPAS", "type": "Klarifikasi Dalih Api Merembet dari Luar Konsesi", "weight": 7, "sentiment": "Hubungan Media"},
            {"source": "C_APHI", "target": "G_KLHK", "type": "Laporan Patroli Regu Pemadam Kebakaran Mandiri", "weight": 6, "sentiment": "Laporan Kepatuhan"},
            {"source": "C_KORPORASI_SAWIT", "target": "C_KONTRAKTOR", "type": "Perjanjian Outsourcing Pembersihan Lahan Murah", "weight": 8, "sentiment": "Transaksi Ekonomi"},

            # 5. Liputan Media & Advokasi Korban (Media Coverage & Public Discourse)
            {"source": "M_TEMPO", "target": "C_KORPORASI_SAWIT", "type": "Liputan Investigatif Konsesi Berulang Terbakar", "weight": 9, "sentiment": "Liputan Kritis"},
            {"source": "M_KOMPAS", "target": "V_WARGA_PLK", "type": "Pemberitaan Krisis Kesehatan & Bayi Terpapar ISPA", "weight": 9, "sentiment": "Human Interest"},
            {"source": "M_MONGABAY", "target": "N_GREENPEACE", "type": "Wawancara Analisis Hilangnya Habitat Orangutan", "weight": 8, "sentiment": "Liputan Global"},
            {"source": "M_ANTARA", "target": "G_BNPB", "type": "Rilis Resmi Jumlah Titik Api & Luas Area Terbakar", "weight": 8, "sentiment": "Informasi Publik"},
            {"source": "V_ADAT_DAYAK", "target": "G_PEMDA_KT", "type": "Tuntutan Perlindungan Hukum Peladang Tradisional", "weight": 8, "sentiment": "Tuntutan Hak"},
            {"source": "N_WALHI", "target": "V_WARGA_PLK", "type": "Pendampingan Hukum Gugatan Korban Polusi Asap", "weight": 9, "sentiment": "Bantuan Hukum"},

            # 6. Dampak Asap Lintas Batas ASEAN (Transboundary Haze Corridor)
            {"source": "V_SARAWAK", "target": "G_KLHK", "type": "Nota Diplomatik Pencemaran Asap Lintas Batas", "weight": 9, "sentiment": "Protes Diplomatik"},
            {"source": "V_SINGAPURA", "target": "G_KLHK", "type": "Aktivasi Transboundary Haze Pollution Act (THPA)", "weight": 9, "sentiment": "Tuntutan Regulasi"},
            {"source": "V_SINGAPURA", "target": "C_KORPORASI_SAWIT", "type": "Pemantauan Satelit terhadap Direksi Korporasi Sawit", "weight": 8, "sentiment": "Penyelidikan Ekstrateritorial"},
            {"source": "M_MONGABAY", "target": "V_SARAWAK", "type": "Liputan Kualitas Udara Berbahaya di Perbatasan", "weight": 7, "sentiment": "Liputan Regional"}
        ]

    def build_network_graph(self) -> nx.DiGraph:
        """Builds directed NetworkX graph and computes all centrality & modularity metrics."""
        G = nx.DiGraph()

        # Add nodes with attributes
        for n in self.nodes_data:
            G.add_node(
                n["id"],
                label=n["label"],
                group=n["group"],
                role=n["role"],
                influence=n["influence"]
            )

        # Add edges with attributes
        for e in self.edges_data:
            G.add_edge(
                e["source"],
                e["target"],
                type=e["type"],
                weight=e["weight"],
                sentiment=e["sentiment"]
            )

        # Calculate Centrality Metrics
        deg_centrality = nx.degree_centrality(G)
        in_degree = nx.in_degree_centrality(G)
        out_degree = nx.out_degree_centrality(G)
        betweenness = nx.betweenness_centrality(G, weight="weight")
        closeness = nx.closeness_centrality(G)
        pagerank = nx.pagerank(G, weight="weight")

        # Set calculated metrics as node attributes
        for node_id in G.nodes():
            G.nodes[node_id]["degree_centrality"] = round(float(deg_centrality.get(node_id, 0)), 4)
            G.nodes[node_id]["in_degree"] = round(float(in_degree.get(node_id, 0)), 4)
            G.nodes[node_id]["out_degree"] = round(float(out_degree.get(node_id, 0)), 4)
            G.nodes[node_id]["betweenness_centrality"] = round(float(betweenness.get(node_id, 0)), 4)
            G.nodes[node_id]["closeness_centrality"] = round(float(closeness.get(node_id, 0)), 4)
            G.nodes[node_id]["pagerank"] = round(float(pagerank.get(node_id, 0)), 4)

        return G

    def export_data(self, G: nx.DiGraph) -> Tuple[Path, Path, Path]:
        """Exports nodes, edges, and summary JSON into data/processed/."""
        # 1. Nodes DataFrame
        nodes_list = []
        for n, d in G.nodes(data=True):
            nodes_list.append({
                "node_id": n,
                "label": d.get("label", n),
                "cluster_group": d.get("group", ""),
                "role": d.get("role", ""),
                "influence_score": d.get("influence", 50),
                "degree_centrality": d.get("degree_centrality", 0),
                "betweenness_centrality": d.get("betweenness_centrality", 0),
                "pagerank": d.get("pagerank", 0)
            })

        df_nodes = pd.DataFrame(nodes_list).sort_values(by="betweenness_centrality", ascending=False)
        nodes_csv = PROCESSED_DIR / "karhutla_sna_nodes.csv"
        df_nodes.to_csv(nodes_csv, index=False)

        # 2. Edges DataFrame
        edges_list = []
        for u, v, d in G.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "source_label": G.nodes[u].get("label", u),
                "target_label": G.nodes[v].get("label", v),
                "interaction_type": d.get("type", ""),
                "weight": d.get("weight", 1),
                "sentiment": d.get("sentiment", "")
            })

        df_edges = pd.DataFrame(edges_list)
        edges_csv = PROCESSED_DIR / "karhutla_sna_edges.csv"
        df_edges.to_csv(edges_csv, index=False)

        # 3. Summary Statistics
        summary = {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "graph_density": round(float(nx.density(G)), 4),
            "top_broker_actors": df_nodes.head(5)[["node_id", "label", "betweenness_centrality"]].to_dict(orient="records"),
            "top_influential_actors": df_nodes.sort_values(by="pagerank", ascending=False).head(5)[["node_id", "label", "pagerank"]].to_dict(orient="records"),
            "cluster_breakdown": df_nodes["cluster_group"].value_counts().to_dict()
        }

        summary_json = PROCESSED_DIR / "karhutla_sna_summary.json"
        with open(summary_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Exported SNA nodes to {nodes_csv}")
        print(f"[SUCCESS] Exported SNA edges to {edges_csv}")
        print(f"[SUCCESS] Exported SNA summary to {summary_json}")

        return nodes_csv, edges_csv, summary_json

    def generate_interactive_html(self, G: nx.DiGraph) -> Path:
        """Generates a standalone NodeXL-style interactive network graph in dashboard/ using Vis.js."""
        html_path = DASHBOARD_DIR / "karhutla_sna_network_graph.html"

        # Color mapping for groups
        group_colors = {
            "Pemerintah & Penegak Hukum": {"background": "#3b82f6", "border": "#60a5fa"},  # Blue
            "Sektor Industri & Korporasi": {"background": "#ef4444", "border": "#f87171"},  # Red
            "LSM & Koalisi Sipil": {"background": "#10b981", "border": "#34d399"},          # Green
            "Media Massa & Riset": {"background": "#a855f7", "border": "#c084fc"},          # Purple
            "Publik & Transboundary ASEAN": {"background": "#f59e0b", "border": "#fbbf24"}  # Amber
        }

        vis_nodes = []
        for n, d in G.nodes(data=True):
            colors = group_colors.get(d.get("group", ""), {"background": "#64748b", "border": "#94a3b8"})
            # Size proportional to betweenness & pagerank
            size = 18 + int(d.get("betweenness_centrality", 0) * 120)

            vis_nodes.append({
                "id": n,
                "label": d.get("label", n),
                "title": f"<b>{d.get('label')}</b><br>Klaster: {d.get('group')}<br>Peran: {d.get('role')}<br>Betweenness Centrality: {d.get('betweenness_centrality'):.4f}<br>PageRank: {d.get('pagerank'):.4f}",
                "group": d.get("group"),
                "value": size,
                "color": colors,
                "font": {"color": "#ffffff", "face": "Inter, sans-serif", "size": 13}
            })

        vis_edges = []
        for u, v, d in G.edges(data=True):
            vis_edges.append({
                "from": u,
                "to": v,
                "label": d.get("type", ""),
                "title": f"{d.get('type')} (Bobot: {d.get('weight')})",
                "width": max(1, int(d.get("weight", 1) / 2)),
                "arrows": "to",
                "color": {"color": "rgba(255, 255, 255, 0.25)", "highlight": "#f97316", "hover": "#38bdf8"},
                "font": {"color": "rgba(255, 255, 255, 0.5)", "size": 9, "align": "middle"}
            })

        html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Network Analysis (SNA) - Aktor & Wacana Karhutla Indonesia</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: #080C14;
            color: #F8FAFC;
            font-family: 'Inter', -apple-system, sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }}
        #header {{
            position: absolute;
            top: 20px;
            left: 24px;
            z-index: 100;
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 16px 22px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            max-width: 460px;
        }}
        #header h1 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #F8FAFC;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        #header p {{
            font-size: 0.82rem;
            color: #94A3B8;
            margin-top: 6px;
            line-height: 1.4;
        }}
        .legend {{
            margin-top: 12px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: #CBD5E1;
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 8px;
            border-radius: 6px;
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        #network {{
            width: 100vw;
            height: 100vh;
        }}
        #info-card {{
            position: absolute;
            bottom: 24px;
            right: 24px;
            z-index: 100;
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 18px 22px;
            border-radius: 14px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            width: 320px;
            display: none;
        }}
        #info-card h3 {{
            font-size: 1rem;
            color: #38BDF8;
            margin-bottom: 6px;
        }}
        #info-card .meta-row {{
            font-size: 0.8rem;
            color: #94A3B8;
            margin-bottom: 4px;
        }}
        #info-card .meta-row strong {{
            color: #E2E8F0;
        }}
        .btn-controls {{
            position: absolute;
            top: 20px;
            right: 24px;
            z-index: 100;
            display: flex;
            gap: 8px;
        }}
        .btn-controls button {{
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #F8FAFC;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-controls button:hover {{
            background: #F97316;
            border-color: #F97316;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🕸️ Karhutla Social Network Analysis (SNA)</h1>
        <p>Peta interaksi, penegakan hukum, investigasi media, dan koridor asap transboundary ASEAN. Diadaptasi dari pemodelan graf multi-klaster NodeXL.</p>
        <div class="legend">
            <div class="legend-item"><div class="legend-dot" style="background:#3b82f6;"></div>Pemerintah & Gakkum</div>
            <div class="legend-item"><div class="legend-dot" style="background:#ef4444;"></div>Korporasi & Cukong</div>
            <div class="legend-item"><div class="legend-dot" style="background:#10b981;"></div>LSM & Koalisi Sipil</div>
            <div class="legend-item"><div class="legend-dot" style="background:#a855f7;"></div>Media & Akademisi</div>
            <div class="legend-item"><div class="legend-dot" style="background:#f59e0b;"></div>Publik & Koridor ASEAN</div>
        </div>
    </div>

    <div class="btn-controls">
        <button onclick="network.fit({{animation: true}})">Pusatkan Graf</button>
        <button onclick="togglePhysics()">Bekukan Fisika</button>
    </div>

    <div id="network"></div>

    <div id="info-card">
        <h3 id="card-title">-</h3>
        <div class="meta-row">Klaster: <strong id="card-group">-</strong></div>
        <div class="meta-row">Peran: <strong id="card-role">-</strong></div>
        <div class="meta-row">Betweenness Centrality: <strong id="card-betweenness">-</strong></div>
        <div class="meta-row">PageRank Score: <strong id="card-pagerank">-</strong></div>
    </div>

    <script type="text/javascript">
        const nodes = new vis.DataSet({json.dumps(vis_nodes, ensure_ascii=False)});
        const edges = new vis.DataSet({json.dumps(vis_edges, ensure_ascii=False)});

        const container = document.getElementById('network');
        const data = {{ nodes: nodes, edges: edges }};
        const options = {{
            nodes: {{
                shape: 'dot',
                shadow: true
            }},
            edges: {{
                smooth: {{
                    type: 'continuous',
                    roundness: 0.2
                }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.6 }} }}
            }},
            physics: {{
                barnesHut: {{
                    gravitationalConstant: -7500,
                    centralGravity: 0.35,
                    springLength: 140,
                    springConstant: 0.04,
                    damping: 0.09
                }},
                stabilization: {{ iterations: 200 }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                navigationButtons: false,
                keyboard: true
            }}
        }};

        const network = new vis.Network(container, data, options);
        let physicsEnabled = true;

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({{ physics: {{ enabled: physicsEnabled }} }});
        }}

        network.on("click", function (params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const nodeData = nodes.get(nodeId);
                document.getElementById('card-title').innerText = nodeData.label;
                document.getElementById('card-group').innerText = nodeData.group;
                
                // Parse details from title HTML
                const parser = new DOMParser();
                const doc = parser.parseFromString(nodeData.title, 'text/html');
                const textLines = doc.body.innerText.split('\\n');
                
                document.getElementById('card-role').innerText = textLines[2]?.replace('Peran: ', '') || '-';
                document.getElementById('card-betweenness').innerText = textLines[3]?.replace('Betweenness Centrality: ', '') || '-';
                document.getElementById('card-pagerank').innerText = textLines[4]?.replace('PageRank: ', '') || '-';

                document.getElementById('info-card').style.display = 'block';
            }} else {{
                document.getElementById('info-card').style.display = 'none';
            }}
        }});
    </script>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[SUCCESS] Generated interactive network visualization: {html_path}")
        return html_path


if __name__ == "__main__":
    generator = KarhutlaActorNetworkGenerator()
    G = generator.build_network_graph()
    generator.export_data(G)
    generator.generate_interactive_html(G)
