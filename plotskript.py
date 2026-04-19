import numpy as np
import matplotlib.pyplot as plt

# =========================
# NASTAVENIA
# =========================

filename = "IR Cas_TESS_spot_phased.txt"

xlabel_base = "JD"
ylabel = "Normalized flux"

fontsize_labels = 20
fontsize_ticks = 18

# offset (mozes zmenit manuálne alebo nechat auto)
JD_offset = None


# =========================
# NACITANIE DAT
# =========================

data = np.loadtxt(filename, delimiter=" ")

x = data[:, 0]
y = data[:, 1]


# =========================
# SKRATENIE JD
# =========================

if JD_offset is None:
    JD_offset = int(np.floor(np.min(x)))

x_short = x - JD_offset


# =========================
# PLOT
# =========================

plt.figure(figsize=(8, 5))

plt.plot(x_short, y, ".", markersize=3)

# popisy osí
# plt.xlabel(f"{xlabel_base} - {JD_offset}", fontsize=fontsize_labels)
plt.xlabel("Phase", fontsize=fontsize_labels)
plt.ylabel(ylabel, fontsize=fontsize_labels)

# veľkosť čísel na osiach
plt.xticks(fontsize=fontsize_ticks)
plt.yticks(fontsize=fontsize_ticks)

plt.tight_layout()
plt.show()