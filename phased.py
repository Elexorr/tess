import lightkurve as lk
from lightkurve import search_lightcurve
import matplotlib.pyplot as plt

# Nahraďte identifikátorom cieľa alebo súradnicami
target = "TIC 240706234"

# Stiahnite lightkurve
search_result = search_lightcurve(target)
print(search_result)
lc = search_result.download_all()

# print(lc[0])

# known_period = 0.233689935  # Nahraďte vašou známou periódou
# known_base_phase =  2446708.7773  # Nahraľte vašou známou fázou základného minima

period = 0.233689935
t0 = 2446708.7773

lk.LightCurve.scatter(lc[0])

folded_lc = lc[0].fold(period, t0)
# folded_lc

print(folded_lc.phase)


lk.LightCurve.scatter(folded_lc)
plt.show()