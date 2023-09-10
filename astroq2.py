from astroquery.mast import Catalogs
import numpy as np

target_name = "KIC 2970804"
search_radius_deg = 0.001

# Query the TESS Input Catalog centered on HD 209458 with a 0.2 degree radius.
catalogTIC = Catalogs.query_object(target_name, radius=search_radius_deg, catalog="TIC")

# Print out the number of returned rows.
print("Number of TIC objects within %f deg of %s: %u" % (search_radius_deg, target_name, len(catalogTIC)))

# What type of objects is the returned result?
# print(type(catalogTIC))

# What columns are available from the TIC?
# print(catalogTIC.columns)

try:
    where_closest = np.argmin(catalogTIC['dstArcSec'])
except:
    print('TIC not found.')
else:
    print("Closest TIC ID to %s: TIC %s, separation of %f arcsec. and a TESS mag. of %f"%
        (target_name, catalogTIC['ID'][where_closest], catalogTIC['dstArcSec'][where_closest],
        catalogTIC['Tmag'][where_closest]))

# catalogTIC = Catalogs.query_object(target_name, catalog="TIC")
#
# print(catalogTIC)