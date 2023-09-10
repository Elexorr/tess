from astroquery.vizier import Vizier

# Definujte KIC identifikátor pre vašu hviezdu
kic_id = "KIC 10417986"  # Nahraďte skutočným KIC identifikátorom

# Inicializujte Vizier
vizier = Vizier(columns=["TIC"])

# Vyhľadajte TIC identifikátor pre KIC identifikátor
# result = vizier.query_object(kic_id, catalog="TIC")
#
# if result is not None and len(result) > 0:
#     tic_id = result[0]["TIC"]
#     print(f"{kic_id} matches {tic_id}")
# else:
#     print(f"Star {kic_id} not found in TIC.")

# result = vizier.query_object(kic_id)
# print(result)

result = Vizier.query_object(kic_id)

print(result)

# if result is not None and len(result) > 0:
#     tic_id = result[0]["TIC"]
#     print(f"{kic_id} matches {tic_id}")
# else:
#     print(f"Star {kic_id} not found in TIC.")