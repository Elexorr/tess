import sys
import numpy as np

if len(sys.argv) < 2:
    print("Použitie: python convert.py subor")
    sys.exit(1)

subor = sys.argv[1]
print(f"Otvorím súbor: {subor}")

# with open(subor, "r", encoding="utf-8") as f:
#     obsah = f.read()
#     print(obsah)

readf = open(subor, 'r')
lines = readf.readlines()
# print(lines)

JD = []  # cas
flux = []  # jasnost
sigma = []  # chyba

for i in range(0, len(lines)):

    # JD.append(round(float(lines[i].split(',')[0]),7))
    JD.append(float(lines[i].split(',')[0]))
    flux.append(float(lines[i].split(',')[1]))
    sigma.append(float(lines[i].split(',')[2]))

norm_flux = flux/np.max(flux)
norm_sigma = sigma/np.max(flux)

for i in range(0, len(lines)):
    # print(f"{JD[i]:.7f}",'',norm_flux[i],'',norm_sigma[i])
    print(f"{JD[i]:.7f}",'',f"{norm_flux[i]:.5f}",'',f"{norm_sigma[i]:.5f}")
    # print(JD[i]"{x:.7f}",'',flux[i],'',sigma[i])

readf.close()

txtcurve = str(subor + '_normalized.txt')
writef1 = open(txtcurve, 'w')
for i in range(0, len(lines)):
    writef1.write(f"{JD[i]:.7f}"+' '+f"{norm_flux[i]:.7f}"+' '+f"{norm_sigma[i]:.7f}"+"\n")
writef1.close()
txtcurve = str(subor + '_normalized_inv.txt')
writef2 = open(txtcurve, 'w')
for i in range(0, len(lines)):
    writef2.write(f"{JD[i]:.7f}"+' '+f"{-1*norm_flux[i]:.7f}"+' '+f"{norm_sigma[i]:.7f}"+"\n")
writef2.close()
txtcurve = str(subor + '_fluxes.txt')
writef3 = open(txtcurve, 'w')
for i in range(0, len(lines)):
    writef3.write(f"{JD[i]:.7f}"+' '+f"{flux[i]:.7f}"+' '+f"{sigma[i]:.7f}"+"\n")
writef3.close()


