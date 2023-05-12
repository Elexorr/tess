import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

id = input('Object ID: ')
search_lcf = lk.search_lightcurve(id)
#search_lcf = lk.search_lightcurve('TIC 233310793')
print(search_lcf)
auth = input('author: ')
exp = int(input('exptime: ' ))
#search_lcf_refined = lk.search_lightcurve('TIC 233310793', author = 'SPOC', exptime = 120)
search_lcf_refined = lk.search_lightcurve(id, author = auth, exptime = exp)
print(search_lcf_refined)
lcf = search_lcf_refined.download_all()
#print(lcf[0])
#print(lcf[0])
choose = int(input('number: '))
#adu = lcf[]
#print(adu)

lcf[choose].plot()
plt.show()