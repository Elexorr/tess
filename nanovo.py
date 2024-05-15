import lightkurve as lk
from lightkurve import search_targetpixelfile
import matplotlib.pyplot as plt
# from IPython.display import display
# import IPython
# IPython.embed()

search_ffi = lk.search_tesscut('TIC 158554559')

# print(search_ffi)
ffi_data = search_ffi[1].download(cutout_size=21)

# ffi_data.plot()

tpf = search_targetpixelfile('KIC 8462852', mission='Kepler', cadence='long').download()
# target_mask = ffi_data.create_threshold_mask(threshold=5, reference_pixel='center')
# n_target_pixels = target_mask.sum()
# print(n_target_pixels)
plt.figure()
tpf.plot(interactive=True)
# ffi_data.plot(interactive=True)
# ffi_data.interact()

# ffi_lc = ffi_data.to_lightcurve(aperture_mask=target_mask)
# print(ffi_lc)
# ffi_lc.plot(label="SAP FFI")



plt.show()