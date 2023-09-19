import requests
import os
import csv
from PIL import Image, ImageFont, ImageDraw

os.mkdir(path='dtr_lc')
with open('kepler.csv', newline='') as csvfile:  # Otvori a nacita
    reader = csv.DictReader(csvfile)  # zoznam z Keplera
    num = 0
    for row in reader:  # Ide po KIC-kach riadok
        target_name = "KIC " + row['#KIC']  # Vytvori cele ID kicky
        if len(row['#KIC']) == 7:  #
            url = "http://keplerebs.villanova.edu/includes/" + "0" + row['#KIC'] + ".00.lc.dtr.png"  # Vytvori url na stiahnutie
        else:  # obrazku dtr krivky
            url = "http://keplerebs.villanova.edu/includes/" + row['#KIC'] + ".00.lc.dtr.png"  #

        data = requests.get(url).content  # Stiahne obrazok dtr krivky
        save_path = 'dtr_lc/'             #
        file_name = target_name + ".png"                    # Ulozi obrazok dtr krivky
        completeName = os.path.join(save_path, file_name)   # do suboru KIC_ID.png
        f = open(completeName, 'wb')                        # v prislusnom podadresari
        f.write(data)  #
        f.close()  #
        i = Image.open(completeName)
        Im = ImageDraw.Draw(i)
        # mf = ImageFont.truetype('font.ttf', 25)
        Im.text((5, 5), target_name, (255, 0, 0))
        i.save(completeName)