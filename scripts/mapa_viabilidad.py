#!/usr/bin/env python3
"""Genera el mapa de viabilidad de cargas de trabajo (figura del TFG).

El eje horizontal es generico (intensidad normalizada por la cresta PCIe,
alpha = I_A_eff / I_A_PCIe*), de modo que la frontera cae siempre en alpha = 1.
El eje superior instancia el caso de estudio (alpha = 1 -> ~100 FLOP/Byte).

Uso:
    uv run --with matplotlib --with numpy scripts/mapa_viabilidad.py

Salidas:
    figuras/mapa_viabilidad.pdf   (vectorial, para LaTeX)
    figuras/mapa_viabilidad.png   (vista rápida)
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

RAIZ = Path(__file__).resolve().parent.parent
FIGURAS = RAIZ / "figuras"

# Cresta PCIe del caso de estudio (FLOP/Byte): media de 97 (Tesla, x16) y 103 (GTS 250, x4)
CRESTA_CASO = 100.0

plt.rcParams.update(
    {
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "font.size": 9.5,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.linewidth": 0.8,
    }
)

# --- Rejilla del mapa (coordenada generica alpha) -----------------------------
x = np.logspace(-4, 1, 700)
y = np.linspace(0.0, 1.0, 400)
X, Y = np.meshgrid(x, y)


def aptitud_intensidad(alpha):
    """Filtro de carga del documento: F_carga = min(1, alpha)."""
    return np.minimum(1.0, alpha)


def aptitud_dependencias(yy):
    """Fraccion paralela de Amdahl: f_m = 1 - c."""
    return 1.0 - yy


V = aptitud_intensidad(X) * aptitud_dependencias(Y)

cmap = LinearSegmentedColormap.from_list(
    "viabilidad", ["#b71c1c", "#e65100", "#fbc02d", "#9ccc65", "#2e7d32"]
)

fig, ax = plt.subplots(figsize=(7.4, 4.8), constrained_layout=True)

mesh = ax.pcolormesh(X, Y, V, cmap=cmap, vmin=0.0, vmax=1.0, shading="auto", rasterized=True)
ax.contour(X, Y, V, levels=[0.3, 0.6], colors="#37474f", linewidths=0.7, linestyles="--")

# Ecuacion de cada curva de nivel
for nivel, yy in ((0.6, 0.425), (0.3, 0.725)):
    ax.text(1.6, yy, f"$\\min(1,\\alpha)\\,(1-c) = {nivel}$", fontsize=7, color="#212121",
            va="bottom", zorder=7,
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=1.0))

# Crestas de referencia
ax.axvline(1.0, color="#212121", lw=1.3, ls="--", zorder=4)
ax.axvline(0.013, color="#4fc3f7", lw=1.3, ls=":", zorder=4)
ax.text(0.82, 0.60, "cresta PCIe ($\\alpha=1$)", fontsize=7.5, color="#212121",
        rotation=90, rotation_mode="anchor", ha="left", va="center")
ax.text(0.017, 0.60, "cresta VRAM ($\\alpha\\approx0.013$)", fontsize=8, color="#4fc3f7",
        rotation=90, rotation_mode="anchor", ha="left", va="center")
ax.text(1.4e-4, 0.42, "transfer-bound", fontsize=7.5, color="#7f0000", fontweight="bold",
        rotation=90, rotation_mode="anchor", ha="left", va="center",
        bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=1.0))
ax.text(1.18, 0.42, "compute-bound", fontsize=7.5, color="#1b5e20", fontweight="bold",
        rotation=90, rotation_mode="anchor", ha="left", va="center",
        bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=1.0))
ax.text(2.6e-4, 0.13, "INVIABLE POR DEPENDENCIAS ($c\\to1$)", fontsize=7.5, color="#7f0000",
        fontweight="bold", rotation=90, rotation_mode="anchor", ha="left", va="center",
        bbox=dict(facecolor="white", alpha=0.65, edgecolor="none", pad=1.0))

# --- Cargas de ejemplo (coordenada alpha = I_A_eff / I_A_PCIe*) ----------------
cargas = [
    (1.3e-4, 0.045, "bandwidthTest\n(Fase 4)", (8, 6), "left", True),
    (1.7e-2, 0.145, "vídeo en streaming", (8, 5), "left", False),
    (1.7e-3, 0.050, "SAXPY", (-8, 3), "right", False),
    (1.7e-3, 0.240, "SpMV", (8, 4), "left", False),
    (4.1e-3, 0.100, "stencil 7 puntos", (0, 10), "center", False),
    (3.1e-2, 0.470, "FFT ($N=1024$)", (8, 0), "left", False),
    (1.70, 0.050, "SAXPY residente\n($K=10^3$)", (8, 6), "left", False),
    (0.10, 0.860, "reducción global\niterativa", (8, -10), "left", False),
    (5.0e-3, 0.960, "pointer chasing /\nrecursivo", (-8, 0), "right", False),
]
for cx, cy, etiqueta, (dx, dy), ha, medido in cargas:
    vi = float(aptitud_intensidad(cx) * aptitud_dependencias(cy))
    ax.scatter([cx], [cy], s=36, color=cmap(vi), edgecolor="black", linewidth=0.6,
               marker="D" if medido else "o", zorder=6)
    ax.annotate(etiqueta, xy=(cx, cy), xytext=(dx, dy), textcoords="offset points",
                fontsize=7.0, color="#212121", ha=ha, va="center", zorder=7)

# Familia GEMM: trayectoria parametrica alpha = K*N/600 (no un unico punto)
ax.annotate(
    "",
    xy=(8.0, 0.20),
    xytext=(0.03, 0.20),
    arrowprops=dict(arrowstyle="-|>", color="#212121", lw=1.3),
    zorder=5,
)
ax.text(0.45, 0.245, "GEMM ($N\\times N$): $\\alpha = K\\,N/600$", fontsize=7, color="#212121",
        ha="center", zorder=7,
        bbox=dict(facecolor="white", alpha=0.55, edgecolor="none", pad=1.0))
ax.text(1.05, 0.165, "cruce en $N\\approx600$ ($K=1$)", fontsize=7, color="#212121",
        ha="left", va="top", zorder=7)

# Distincion medida / referencia analitica
handles = [
    Line2D([], [], marker="o", ls="", color="#9e9e9e", markeredgecolor="black",
           markersize=5, label="referencia (calculada)"),
    Line2D([], [], marker="D", ls="", color="#9e9e9e", markeredgecolor="black",
           markersize=5, label="Fase 4 (medida)"),
]
ax.legend(handles=handles, loc="upper right", bbox_to_anchor=(1.0, 1.0), fontsize=7,
          framealpha=0.85, ncol=2, handletextpad=0.4, columnspacing=1.0, borderaxespad=0.3)

# Amortizacion por residencia
ax.annotate(
    "",
    xy=(1.70, 0.05),
    xytext=(1.7e-3, 0.05),
    arrowprops=dict(arrowstyle="-|>", color="#212121", lw=1.3),
    zorder=5,
)
ax.text(0.08, 0.095, "amortización por residencia ($K$ iteraciones)", fontsize=7.5,
        color="#212121", ha="center",
        bbox=dict(facecolor="white", alpha=0.5, edgecolor="none", pad=1.0))

# --- Ejes y colorbar ----------------------------------------------------------
ax.set_xscale("log")
ax.set_xlim(1e-4, 1e1)
ax.set_ylim(0.0, 1.0)
ax.set_xticks([1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1])
ax.set_xticklabels(["0.0001", "0.001", "0.01", "0.1", "1", "10"])
ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["0", "0.25", "0.5", "0.75", "1"], fontsize=8)
ax.set_xlabel("intensidad normalizada $\\alpha = I_A^{\\mathrm{eff}} / I_{A,\\mathrm{PCIe}}^*$")
ax.set_ylabel("grado de acoplamiento $c$")
ax.annotate("EP puro ($c=0$)", xy=(1.0, 0.0), xycoords="axes fraction",
            xytext=(0, -22), textcoords="offset points", fontsize=7.5, color="#1b5e20",
            ha="right", va="top", annotation_clip=False)
ax.text(1.2e-4, 0.955, "secuencial ($c=1$)", fontsize=7.5, color="#7f0000", ha="left", va="center",
        bbox=dict(facecolor="white", alpha=0.55, edgecolor="none", pad=1.2), zorder=7)

# Eje superior: instanciacion del caso de estudio (alpha = 1 -> ~100 FLOP/Byte)
secax = ax.secondary_xaxis(
    "top", functions=(lambda a: a * CRESTA_CASO, lambda v: v / CRESTA_CASO)
)
secax.set_xscale("log")
secax.set_xticks([0.01, 0.1, 1, 10, 100, 1000])
secax.set_xticklabels(["0.01", "0.1", "1", "10", "100", "1000"])
secax.tick_params(labelsize=9)
secax.set_xlabel("intensidad efectiva en el caso de estudio [FLOP/Byte]")

cbar = fig.colorbar(mesh, ax=ax, pad=0.015)
cbar.set_label("viabilidad de la carga", fontsize=8.5)
cbar.ax.tick_params(labelsize=8)

FIGURAS.mkdir(exist_ok=True)
fig.savefig(FIGURAS / "mapa_viabilidad.pdf")
fig.savefig(FIGURAS / "mapa_viabilidad.png", dpi=200)
print(f"Generadas {FIGURAS / 'mapa_viabilidad.pdf'} y .png")
