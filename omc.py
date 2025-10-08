print("Skript sa spustil.")
import sys
import numpy as np
import matplotlib.pyplot as plt


if len(sys.argv) < 2:
    print("Použitie: python omc.py subor")
    sys.exit(1)

subor = sys.argv[1]
print(f"Otvorím súbor: {subor}")

readf = open(subor, 'r')
lines = readf.readlines()
# print(lines)

period = float(input('Zadaj periodu:\n'))

o = []   # observed minima
c = []   # calculated minima
omc = []  # o minus c

for i in range(1, len(lines)):
    # print(lines[i].split(' ')[0])
    o.append(float(lines[i].split(' ')[0]))

for i in range(0, len(o)):
    E_frac = (o[i] - o[100]) / period
    E = np.rint(E_frac).astype(int)
    # E = np.floor(E_frac)
    # print(E_frac,E)
    c.append((o[0]) + period*E)
    omc.append(round(o[i] - c[i], 5))

# print(len(o), len(c))

for i in range(len(omc)):
    print(omc[i])

# print(o)
# print(c)

plt.scatter(o, omc)
plt.show()
