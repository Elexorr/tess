import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt

search_ffi = lk.search_tesscut('DI Cam')
# search_tpf = lk.search_targetpixelfile('V523 Cas')
# search_lcf = lk.search_lightcurve('V523 Cas')

print(search_ffi)
ffi_data = search_ffi[1].download(cutout_size=10)

# ffi_data.plot()

target_mask = ffi_data.create_threshold_mask(threshold=50, reference_pixel='center')
n_target_pixels = target_mask.sum()
print(n_target_pixels)
ffi_data.plot(aperture_mask=target_mask, mask_color='r')

ffi_lc = ffi_data.to_lightcurve(aperture_mask=target_mask)
print(ffi_lc)
ffi_lc.plot(label="SAP FFI")



plt.show()