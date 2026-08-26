"""
Generate specialized Kaggle Dataset Thumbnail Banner (1280x720).
"""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_THUMBNAIL = BASE_DIR / "dashboard" / "kaggle_dataset_thumbnail.png"
OUTPUT_THUMBNAIL.parent.mkdir(parents=True, exist_ok=True)


def create_kaggle_thumbnail():
    width, height = 1280, 720
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    fig.patch.set_facecolor("#0b0f19")
    ax.set_facecolor("#0b0f19")
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.axis("off")

    # Gradient Inferno Peat Fire Embers
    y = np.linspace(0, height, 400)
    x = np.linspace(0, width, 400)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((Y - 260) ** 2) / (2 * 200 ** 2)) * 0.9 + np.sin(X / 300) * 0.2
    ax.imshow(
        Z,
        extent=[0, width, 0, height],
        origin="lower",
        cmap="hot",
        alpha=0.4,
        aspect="auto"
    )

    # Top Tag
    ax.text(
        80, 630,
        "[ BORNEO WILDFIRE DATA SCIENCE & GEOSPATIAL INTELLIGENCE ]",
        color="#fbbf24",
        fontsize=12,
        fontweight="bold",
        va="center",
        family="sans-serif"
    )

    # Main Title
    ax.text(
        80, 520,
        "Kalimantan Peatland\nWildfire Intelligence",
        color="#ffffff",
        fontsize=36,
        fontweight="bold",
        va="center",
        family="sans-serif",
        linespacing=1.2
    )

    # Subtitle
    ax.text(
        80, 400,
        "Napas yang Tergadai di Ufuk Jelaga — Multi-Layer GIS, Health & Econometric Dataset",
        color="#f87171",
        fontsize=14,
        fontstyle="italic",
        va="center",
        family="sans-serif"
    )

    # Horizontal Divider Line
    ax.plot([80, width - 80], [360, 360], color="#ef4444", lw=2, alpha=0.8)

    # 4 Compact Badges / KPIs
    badges = [
        ("NASA FIRMS", "VIIRS & MODIS Telemetry", "#ef4444", 80),
        ("ML DBSCAN", "Spatial Epicenter Clusters", "#f97316", 370),
        ("1.04M ISPA", "PM2.5 Exposure Baselines", "#eab308", 660),
        ("Rp 390T ROI", "58.35x Disaster Mitigation", "#22c55e", 950)
    ]

    for title_b, sub_b, col_b, x_pos in badges:
        card = patches.FancyBboxPatch(
            (x_pos, 180), 250, 130,
            boxstyle="round,pad=10",
            linewidth=1,
            edgecolor=col_b,
            facecolor="#161e2e",
            alpha=0.95
        )
        ax.add_patch(card)

        ax.text(x_pos + 125, 265, title_b, color=col_b, fontsize=13, fontweight="bold", ha="center", va="center", family="sans-serif")
        ax.text(x_pos + 125, 215, sub_b, color="#cbd5e1", fontsize=10, ha="center", va="center", family="sans-serif")

    # Bottom Tagline
    ax.text(
        width / 2, 80,
        "19 Structured CSV & GeoJSON Datasets • Real-Time Weather • Open-Source CC BY 4.0",
        color="#94a3b8",
        fontsize=11,
        ha="center",
        va="center",
        family="sans-serif"
    )

    plt.tight_layout()
    plt.savefig(OUTPUT_THUMBNAIL, dpi=100, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"Berhasil membuat Kaggle Thumbnail: {OUTPUT_THUMBNAIL}")


if __name__ == "__main__":
    create_kaggle_thumbnail()
