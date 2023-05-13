import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

a = 1
while a != 3:
    a = int(input('0) Enter Object ID\n1) Basic search\n2) Refined search\n3) End\n>> '))
    if a == 0:
        id = input('>> Object ID: ')
    if a == 1:
        search_lcf = lk.search_lightcurve(id)
        #search_lcf = lk.search_lightcurve('TIC 233310793')
        print(search_lcf)
    if a == 2:
        auth = input('>> Author: ')
        exp = int(input('>> Exptime: ' ))
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
    #if a != 1 and a != 2 and a != 3:
    #    print('Invalid selection')
print('Bye!')
