"""
Programmatic High-Resolution Graphic Card & Banner Generator for Kalimantan Karhutla.
Generates:
1. Instagram Post Card (Portrait 3:4 / 1080x1440)
2. GitHub Landscape Hero Banner (16:9 / 1920x1080)
"""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Ensure UTF-8 stdout
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

INSTAGRAM_IMG = DASHBOARD_DIR / "instagram_post_portrait.png"
GITHUB_BANNER_IMG = DASHBOARD_DIR / "github_landscape_banner.png"


def create_instagram_portrait():
    """Generates a 1080x1440 high-impact Instagram portrait graphic card."""
    width, height = 1080, 1440
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#0b0f19")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    # Gradient Background Simulation (Atmospheric Smoke & Glowing Peat Embers)
    y = np.linspace(0, height, 500)
    x = np.linspace(0, width, 500)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(Y / 300) * 0.3 + np.exp(-((Y - 300) ** 2) / (2 * 250 ** 2)) * 0.8
    ax.imshow(
        Z,
        extent=[0, width, 0, height],
        origin="lower",
        cmap="inferno",
        alpha=0.45,
        aspect="auto"
    )

    # Top Tag / Category
    ax.text(
        width / 2, 1340,
        "[ INVESTIGASI SAINS DATA & EPIDEMIOLOGI LINGKUNGAN ]",
        color="#fbbf24",
        fontsize=13,
        fontweight="bold",
        ha="center",
        va="center",
        family="sans-serif"
    )

    # Main Title
    ax.text(
        width / 2, 1230,
        "NAPAS YANG TERGADAI\nDI UFUK JELAGA",
        color="#ffffff",
        fontsize=28,
        fontweight="heavy",
        ha="center",
        va="center",
        family="sans-serif",
        linespacing=1.2
    )

    # Subtitle
    ax.text(
        width / 2, 1140,
        "— Elegi Duka dan Ratap Senyap Bumi Kalimantan —",
        color="#fca5a5",
        fontsize=14,
        fontstyle="italic",
        ha="center",
        va="center",
        family="sans-serif"
    )

    # Divider
    ax.plot([140, width - 140], [1090, 1090], color="#ef4444", lw=2, alpha=0.8)

    # Poetic Quote Box
    rect_quote = patches.FancyBboxPatch(
        (100, 850), width - 200, 200,
        boxstyle="round,pad=15",
        linewidth=1.2,
        edgecolor="#ef4444",
        facecolor="#181326",
        alpha=0.9
    )
    ax.add_patch(rect_quote)

    quote_text = (
        "\"Di bawah langit yang tak lagi biru, bumi Kalimantan memuntahkan luka purbanya.\n"
        "Api tak hanya melahap gambut, tetapi juga merampas tarikan napas pertama\n"
        "bayi-bayi mungil, menenggelamkan nyanyian burung di kanopi rimba, dan\n"
        "mengganti harum tanah basah dengan bau sangit jelaga.\""
    )
    ax.text(
        width / 2, 950,
        quote_text,
        color="#e2e8f0",
        fontsize=11.5,
        fontstyle="italic",
        ha="center",
        va="center",
        family="sans-serif",
        linespacing=1.6
    )

    # 4 Key Quantitative Metrics Cards
    metrics = [
        ("34 KORBAN JIWA", "~6.460 Kematian Dini PM2.5", "#ef4444", 100, 640),
        (">1.04 JUTA ISPA", "Palangka Raya >1.980 µg/m³", "#f97316", 560, 640),
        ("99.0% MANUSIA", "Hemat Land Clearing 90%", "#eab308", 100, 440),
        ("Rp 145 TRILIUN", "Kerugian Ekonomi & Emisi", "#38bdf8", 560, 440)
    ]

    for title_m, desc_m, col_m, x_pos, y_pos in metrics:
        card = patches.FancyBboxPatch(
            (x_pos, y_pos), 420, 160,
            boxstyle="round,pad=10",
            linewidth=1,
            edgecolor=col_m,
            facecolor="#1e293b",
            alpha=0.95
        )
        ax.add_patch(card)

        ax.text(
            x_pos + 210, y_pos + 105,
            title_m,
            color=col_m,
            fontsize=18,
            fontweight="bold",
            ha="center",
            va="center",
            family="sans-serif"
        )
        ax.text(
            x_pos + 210, y_pos + 55,
            desc_m,
            color="#cbd5e1",
            fontsize=12,
            ha="center",
            va="center",
            family="sans-serif"
        )

    # Affected external regions badge
    rect_trans = patches.FancyBboxPatch(
        (100, 240), width - 200, 150,
        boxstyle="round,pad=10",
        linewidth=1,
        edgecolor="#38bdf8",
        facecolor="#0f172a",
        alpha=0.9
    )
    ax.add_patch(rect_trans)

    ax.text(
        width / 2, 335,
        "[ JANGKAUAN KABUT ASAP LINTAS BATAS / TRANSBOUNDARY HAZE ]",
        color="#38bdf8",
        fontsize=12,
        fontweight="bold",
        ha="center",
        va="center",
        family="sans-serif"
    )
    ax.text(
        width / 2, 285,
        "Sarawak (AQI 365) • Singapura (PSI 210) • Semenanjung Malaysia • Jakarta • Batam",
        color="#94a3b8",
        fontsize=11,
        ha="center",
        va="center",
        family="sans-serif"
    )

    # Footer
    ax.text(
        width / 2, 100,
        "Platform Sains Data & Ekonometrika Karhutla Borneo | GitHub: github.com/AmanSegavo",
        color="#64748b",
        fontsize=11,
        ha="center",
        va="center",
        family="sans-serif"
    )

    plt.tight_layout()
    plt.savefig(INSTAGRAM_IMG, dpi=100, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Berhasil membuat Instagram Portrait: {INSTAGRAM_IMG}")


def create_github_landscape_banner():
    """Generates a 1920x1080 high-impact GitHub Header Landscape Banner."""
    width, height = 1920, 1080
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor("#0a0d14")
    ax.set_facecolor("#0a0d14")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    # Cinematic Widescreen Gradient (Fire & Smoky Skyline)
    y = np.linspace(0, height, 600)
    x = np.linspace(0, width, 600)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((Y - 400) ** 2) / (2 * 350 ** 2)) * 0.9 + np.sin(X / 400) * 0.2
    ax.imshow(
        Z,
        extent=[0, width, 0, height],
        origin="lower",
        cmap="hot",
        alpha=0.35,
        aspect="auto"
    )

    # Top Tag
    ax.text(
        140, 960,
        "[ NASA FIRMS • OPEN-METEO • ML DBSCAN • DISASTER DAMAGE ECONOMETRICS ]",
        color="#fbbf24",
        fontsize=13,
        fontweight="bold",
        va="center",
        family="sans-serif"
    )

    # Big Hero Title
    ax.text(
        140, 840,
        "Napas yang Tergadai di Ufuk Jelaga",
        color="#ffffff",
        fontsize=38,
        fontweight="bold",
        va="center",
        family="sans-serif"
    )

    # Subtitle
    ax.text(
        140, 755,
        "Elegi Duka dan Ratap Senyap Bumi Kalimantan — Platform Sains Data Karhutla Multi-Layer",
        color="#f87171",
        fontsize=19,
        fontstyle="italic",
        va="center",
        family="sans-serif"
    )

    # Horizontal Divider Line
    ax.plot([140, width - 140], [700, 700], color="#ef4444", lw=2.5, alpha=0.9)

    # 4 Widescreen Feature Columns
    cols_data = [
        ("180 Hotspot Satelit", "95.6% Kubah Gambut (KHG)", "FRP Radiatif 62.8 MW", "#ef4444", 140),
        ("1.04 Juta Pasien ISPA", "34 Korban Langsung", "~6.460 Kematian Dini", "#f97316", 580),
        ("99.0% Antropogenik", "Hemat 90% Slash & Burn", "34.5% Dalam Konsesi", "#eab308", 1020),
        ("Rp 390 T Diselamatkan", "ROI Mitigasi 58.35x", "Net Economic Savings", "#22c55e", 1460)
    ]

    for title_c, line1_c, line2_c, col_c, x_pos in cols_data:
        box = patches.FancyBboxPatch(
            (x_pos, 420), 380, 220,
            boxstyle="round,pad=12",
            linewidth=1.2,
            edgecolor=col_c,
            facecolor="#161e2e",
            alpha=0.95
        )
        ax.add_patch(box)

        ax.text(x_pos + 190, 580, title_c, color=col_c, fontsize=17, fontweight="bold", ha="center", va="center", family="sans-serif")
        ax.text(x_pos + 190, 520, line1_c, color="#f8fafc", fontsize=13, ha="center", va="center", family="sans-serif")
        ax.text(x_pos + 190, 470, line2_c, color="#94a3b8", fontsize=12, ha="center", va="center", family="sans-serif")

    # Bottom Transboundary & Simulation Box
    bot_box = patches.FancyBboxPatch(
        (140, 160), width - 280, 190,
        boxstyle="round,pad=12",
        linewidth=1,
        edgecolor="#38bdf8",
        facecolor="#0f172a",
        alpha=0.92
    )
    ax.add_patch(bot_box)

    ax.text(
        width / 2, 290,
        "[ CAKUPAN SEBARAN KABUT ASAP LINTAS BATAS & INTERVENSI TERPADU ]",
        color="#38bdf8",
        fontsize=15,
        fontweight="bold",
        ha="center",
        va="center",
        family="sans-serif"
    )
    ax.text(
        width / 2, 230,
        "Malaysia (Sarawak AQI 365, KL) • Singapura (PSI 210) • Brunei • Thailand Selatan • DKI Jakarta • Batam/Kepri • Sulawesi",
        color="#e2e8f0",
        fontsize=13,
        ha="center",
        va="center",
        family="sans-serif"
    )
    ax.text(
        width / 2, 190,
        "Dashboard Streamlit (10 Tab) • Peta Leaflet Interaktif • 19 Dataset Terverifikasi Spasial • Model Ekonometrika VSL & SCC",
        color="#94a3b8",
        fontsize=11.5,
        ha="center",
        va="center",
        family="sans-serif"
    )

    # Footer
    ax.text(
        width / 2, 60,
        "GitHub: https://github.com/AmanSegavo/Napas-yang-Tergadai-di-Ufuk-Jelaga-Elegi-Duka-dan-Ratap-Senyap-Bumi-Kalimantan",
        color="#475569",
        fontsize=12,
        ha="center",
        va="center",
        family="sans-serif"
    )

    plt.tight_layout()
    plt.savefig(GITHUB_BANNER_IMG, dpi=100, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Berhasil membuat GitHub Landscape Banner: {GITHUB_BANNER_IMG}")


if __name__ == "__main__":
    create_instagram_portrait()
    create_github_landscape_banner()
