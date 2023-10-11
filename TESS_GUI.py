import tkinter as tk
from tkinter import *
from tkinter import ttk
import os
import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from astroquery.simbad import Simbad
# from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import auxiliary as aux
from astroquery.mast import Catalogs
import csv
from PIL import Image,ImageTk
from astropy.modeling import models, fitting
import csvtodat
import requests
import pandas as pd


root = tk.Tk()
root.title('TESS project')
root.state('zoomed')
root.resizable(True, False)

screen_x = root.winfo_screenwidth()
screen_y = root.winfo_screenheight()

global window
window = tk.Canvas(master=root, width=screen_x-558, height=screen_y-50, bg='white')
window.grid(row=0, column=1, sticky='N')
frame1 = tk.Frame(master=root, width=558, height=screen_y-50, bg='grey')
frame1.grid(row=0, column=0, sticky='N')
# v=Scrollbar(root, orient='vertical')
# v.pack(side=RIGHT, fill='y')
# global T
T = Text(master=frame1, height=18, width=65, bg='Light grey', bd=3, padx=10)
# T = Text(master=frame1, height=13, width=58, bg='Light grey', bd=3, padx=10, yscrollcommand=v.set)
T.place(x=5, y=screen_y-385)
# T.insert(END, 'Hello TESS')

obj_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Object ID:', bg='grey')
obj_label.place(x=5, y=8)
obj_name = tk.StringVar()
obj_name_entered = ttk.Entry(frame1, width=20, textvariable=obj_name)
obj_name_entered.place(x=65, y=8)

author_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Author:', bg='grey')
author_label.place(x=5, y=36)
author_name = tk.StringVar()

global found_authors
found_authors = []
author_selection = ttk.Combobox(frame1, value=found_authors)
author_selection.place(x=65, y=36)

exptime_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Exptime:', bg='grey')
exptime_label.place(x=5, y=64)
exptime = tk.IntVar()

global found_exptimes
found_exptimes = []
exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
exptime_selection.place(x=65, y=64)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='#:', bg='grey')
sector_label.place(x=320, y=8)
sector_num = tk.IntVar()


global found_sectors
found_sectors = []
sector_num = ttk.Combobox(frame1, value=found_sectors, width = 3)
sector_num.place(x=340, y=8)


def basic_search():
    global fitted
    fitted = False # Nebude vykreslovat poslednu zobrazenu krivku ale nanovo
    clear_JD() # Vymaze policka na ohranicovanie krivky
    search_lcf = lk.search_lightcurve(obj_name.get())
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf)
    found_authors = aux.find_authors(search_lcf.author)
    global author_selection
    author_selection = ttk.Combobox(frame1, value=found_authors)
    author_selection.insert(0, 'SPOC')
    author_selection.place(x=65, y=36)
    found_exptimes = aux.find_exptimes(search_lcf.exptime)
    global exptime_selection
    exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
    exptime_selection.insert(0, 120)
    exptime_selection.place(x=65, y=64)
    T.see(tk.END)


basic_search_button = ttk.Button(frame1, text='  Basic Search  ', command=basic_search)
basic_search_button.place(x=220, y=5)


def refined_search():
    global lcf
    search_lcf_refined = lk.search_lightcurve(obj_name.get(), author=str(author_selection.get()), exptime=int(exptime_selection.get()))
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf_refined)
    T.see(tk.END)
    global found_sectors
    found_sectors = len(search_lcf_refined)
    nums = []
    for i in range (0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=340, y=8)
    if len(search_lcf_refined.table) != 0:
        global lcf
        lcf = search_lcf_refined.download_all()


refined_search_button = ttk.Button(frame1, text='Refined Search', command=refined_search)
refined_search_button.place(x=220, y=35)


global fig
global canvas
global ax
global Maxmagvalue
global Minmagvalue
global xx
global yy


global fitted
fitted = False

def curve_plot():
    global fitted
    global fig
    global lcf
    global window
    global canvas
    global ax
    global x
    global y
    global xx
    global yy

    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')

    if fitted == False:

        x = lcf[int(sector_num.get())].time.value
        y = lcf[int(sector_num.get())].flux.value

        xx = []
        yy = []

        if JDstart_entered.get() != '':
            JDstart = float(JDstart_entered.get())
            JDend = float(JDend_entered.get())
            for i in range (0, len(x)):
                if JDstart < x[i] and  x[i] < JDend:
                    # print(x[i],y[i])
                    # print(float(x[i]))
                    xx.append(float(x[i]))
                    # print(float(y[i]))
                    yy.append(float(y[i]))
        else:
            xx = lcf[int(sector_num.get())].time.value
            yy = lcf[int(sector_num.get())].flux


        # EXPERIMENTAL ROWS
        # for i in range (0,len(yy)):
        #     zz.append(yy[i]+0.1)
        # EXPERIMENTAL ROWS

        lcf[int(sector_num.get())].to_csv(path_or_buf='lightcurve.csv', overwrite=True)

        # txtcurve = str(obj_name.get()) + '_tess.txt'
        # file = open(txtcurve, 'w')
        # for row in lcf[int(sector_num.get())]:
        #     mag = -2.5 * float(row['flux']) + 20
        #     line = str(row['time']) + ' ' + str(mag) + ' ' + str(row['flux_err']) + '\n'
        #     # line = str(row['time']) + ' ' + str(row['flux']) + ' ' + str(row['flux_err']) + '\n'
        #     # print(line)
        #     file.write(line)
        # file.close()

        # with open('lightcurve.csv', newline='') as csvfile:
        #     rowz = csv.DictReader(csvfile)
        #     for row in rowz:
        #         line = str(row['time']) +  ' ' + str(row['flux']) + ' ' + str(row['flux_err'])
        #         print(line)
        # df = pd.read_csv('lightcurve.csv', header=None, index_col=0)
        # # print(df)
        # content = str(df)
        # print(content)
        # print(content, file=open('lightcurve.txt', 'w'))
        # savedlc = open('light_curve.txt', 'wb')
        # savedlc.write(lcf[int(sector_num.get())])
        # savedlc.close()
        figx = (screen_x-558)/100
        figy = (figx * 0.5625)
        fig = plt.Figure(figsize=(figx, figy), dpi = 100)
        #fig.add_subplot(111).plot(x, y, "ro")

    figx = (screen_x-558)/100
    figy = (figx * 0.5625)
    fig = plt.Figure(figsize=(figx, figy), dpi = 100)
    ax = fig.add_subplot(111)
    ax.plot(xx, yy, 'b', marker='o', linestyle='dashed', linewidth=1, markersize=4)
    # EXPERIMENTAL ROWS TO ADD FIT CURVE / ked bude treba
    # ax = fig.add_subplot(111).plot(xx, yy, 'b', xx, zz, 'r', marker='o', linestyle='dashed',
    #  linewidth=1, markersize=4)
    # EXPERIMENTAL ROWS TO ADD FIT CURVE / ked bude traba
    # BACKUP ROWS
    # fig.add_subplot(111).plot(xx, yy, color='blue', marker='o', linestyle='dashed',
    #  linewidth=1, markersize=4)
    # BACKUP ROWS
    fitted = False
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    canvas._tkcanvas.pack()


JDstart_label = tk.Label(master=frame1, font=('Helvetica', 10), text='JD start:', bg='grey')
JDstart_label.place(x=260, y=65)
JDstart_entered = ttk.Entry(frame1, width=10)
JDstart_entered.place(x=320, y=65)
JDend_label = tk.Label(master=frame1, font=('Helvetica', 10), text='JD end:', bg='grey')
JDend_label.place(x=260, y=90)
JDend_entered = ttk.Entry(frame1, width=10)
JDend_entered.place(x=320, y=90)


def clear_JD():
    JDstart_entered.delete(0, END)
    JDend_entered.delete(0, END)


Gaussian = IntVar()
Lorentzian = IntVar()
checkboxGauss = tk.Checkbutton(master=frame1, text=' Gaussian', variable=Gaussian, onvalue=1, offvalue=0, bg="grey")
checkboxGauss.place(x=395, y=120)
checkboxLorentz = tk.Checkbutton(master=frame1, text=' Lorentzian', variable=Lorentzian, onvalue=1, offvalue=0, bg="grey")
checkboxLorentz.place(x=395, y=140)

def fitprocessing():
    global ax
    global fitted
    global window

    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')

    # x = lcf[int(sector_num.get())].time.value
    # y = lcf[int(sector_num.get())].flux.value

    fxx = []
    fxx2 = []
    fyy = []
    invyy = []
    fitt = []

    if JDstart_entered.get() != '':
        JDstart = float(JDstart_entered.get())
        JDend = float(JDend_entered.get())
        for i in range (0, len(x)):
            if JDstart < x[i] and  x[i] < JDend:
                fxx.append(float(x[i]))
                fyy.append(float(y[i]))
                invyy.append(1-float(y[i]))

    Maxmagvalue = np.max(fyy, axis = 0)
    Minmagvalue = np.min(fyy, axis = 0)

    magscale = Maxmagvalue - Minmagvalue

    fstart = float(JDstart_entered.get())  # getting user starting and ending point
    fend = float(JDend_entered.get())      # of fitting

    if Gaussian.get() == 1:  # fitting and drawing Gaussian model
        sd = (fend - fstart) / 4
        g_init = models.Gaussian1D(amplitude=magscale, mean=fxx[len(fxx) // 2], stddev=sd)
        fit_g = fitting.LevMarLSQFitter()
        fitted_g = fit_g(g_init, fxx, invyy)

        for i in range (0, len(fxx)):
            fitt.append(1-fitted_g(fxx[i]))

    fitted = True
    ax.cla()

    figx = (screen_x - 558) / 100
    figy = (figx * 0.5625)
    fig = plt.Figure(figsize=(figx, figy), dpi=100)

    ax = fig.add_subplot(111)
    # ax.plot(xx, yy, 'b', fxx, fitt, 'r', marker='o', linestyle='dashed', linewidth=1, markersize=4)
    ax.plot(xx, yy, 'b', marker='o', linestyle='dashed', linewidth=1, markersize=4)
    ax.plot(fxx, fitt, 'r', linestyle='-', linewidth=2, markersize=4)
    # ax.plot(fxx, fitt, 'r', xx, yy, 'b',  marker='o', linestyle='dashed', linewidth=1, markersize=4)
    # ax.yaxis.set_major_locator(plt.NullLocator())
    # ax.xaxis.set_major_formatter(plt.NullFormatter())


    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    # # cid = fig.canvas.mpl_connect('button_press_event', onclick)
    canvas._tkcanvas.pack()


fit_button = ttk.Button(frame1, text='Fit Selection', width = 11, command=fitprocessing)
fit_button.place(x=400, y=170)

clear_JD_button = ttk.Button(frame1, text='CLR', width = 4, command=clear_JD)
clear_JD_button.place(x=220, y=75)

targetJD = 'start'
vlines = 0


def onclick(event):
    global vlines
    # global ax
    global targetJD
    global vline1
    global vline2
    ix, iy = float(event.xdata), float(event.ydata)
    # print(f'x = {ix}, y = {iy}')
    if targetJD == 'start':
        JDstart_entered.delete(0, END)
        JDstart_entered.insert(0, str(round(ix,2)))
        targetJD = 'end'
    elif targetJD == 'end':
        JDend_entered.delete(0, END)
        JDend_entered.insert(0, str(round(ix,2)))
        targetJD = 'start'
    if vlines == 0:
        vline1 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 1
    elif vlines == 1:
        vline2 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 2
    elif vlines == 2:
        vline1.remove()
        vline2.remove()
        vline1 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 1
    fig.canvas.draw()


def save_curve():
    if JDstart_entered.get() != '':
        JDstart = float(JDstart_entered.get())
        JDend = float(JDend_entered.get())
    else:
        JDstart = 0
        JDend = 1000000
    global lcf
    txtcurve = str(obj_name.get()) + '_tess.txt'
    file = open(txtcurve, 'w')
    for row in lcf[int(sector_num.get())]:
        if JDstart < float(str(row['time'])) < JDend:
            JDtime = row['time'] + 2457000
            mag = -2.5 * float(row['flux']) + 20
            line = str(JDtime) + ' ' + str(mag) + ' ' + str(row['flux_err']) + '\n'
            # line = str(row['time']) + ' ' + str(mag) + ' ' + str(row['flux_err']) + '\n'
            # line = str(row['time']) + ' ' + str(row['flux']) + ' ' + str(row['flux_err']) + '\n'
            # print(line)
            file.write(line)
    file.close()


save_curve_button = ttk.Button(frame1, text='Save Curve', command=save_curve)
save_curve_button.place(x=400, y=87)


kepler_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Kepler Eclipsing Binary Catalog', bg='grey')
kepler_label.place(x=5, y=125)


kic_ids = []
with open('kepler.csv', newline='') as csvfile:
    rowz = csv.DictReader(csvfile)
    for row in rowz:
        kic_ids.append(row['#KIC'])
    kic_ids = sorted(kic_ids)

kic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='KIC ID:', bg='grey')
kic_label.place(x=5, y=150)
kic_id_input = ttk.Combobox(frame1, value=kic_ids, width = 20)
kic_id_input.place(x=65, y=150)


def read_kic_id():
    global lcf
    global period
    global t0
    kic_num = kic_id_input.get()
    kic_id = 'KIC '+ kic_num
    with open('kepler.csv', newline='') as csvfile:
        rowz = csv.DictReader(csvfile)
        for row in rowz:
            if kic_id_input.get() == row['#KIC']:
                period = row['period']
                t0 = row['bjd0']
        print(period)
        print(t0)
        period = float(period)
        t0 = float(t0)
        print(period)
        print(t0)

    obj_name_entered.delete(0, END)
    obj_name_entered.insert(0, kic_id)
    # url = "http://keplerebs.villanova.edu/includes/" + kic_num + ".00.lc.pf.png"  #
    # data = requests.get(url).content  # Stiahne obrazok dtr krivky
    # file_name = "temp.png"  # Ulozi obrazok dtr krivky
    # f = open("temp.png", 'wb')  # v prislusnom podadresari
    # f.write(data)  #
    # f.close()  #
    # kic_phased = Image.open('temp.png')
    # kic_ph_resized = kic_phased.resize((400,300))
    # img = ImageTk.PhotoImage(kic_ph_resized)
    # window.create_image(100,100, image = img)
    # window.mainloop()


kic_input_button = ttk.Button(frame1, text='Add KIC ID', command=read_kic_id)
kic_input_button.place(x=220, y=148)

global canvas

def find_tic():
    global lcf
    global period
    global t0
    # window.destroy()
    # if 'canvas' in globals():
    #     canvas.destroy()
    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')
    kic_num = kic_id_input.get()

    with open('kepler.csv', newline='') as csvfile:
        rowz = csv.DictReader(csvfile)
        for row in rowz:
            if kic_id_input.get() == row['#KIC']:
                period = row['period']
                t0 = row['bjd0']
        print(period)
        print(t0)
        period = float(period)
        t0 = float(t0)
        print(period)
        print(t0)

    kic_id = 'KIC '+ kic_num
    url = "http://keplerebs.villanova.edu/includes/" + kic_num + ".00.lc.pf.png"  #
    data = requests.get(url).content  # Stiahne obrazok dtr krivky
    file_name = "temp.png"  # Ulozi obrazok dtr krivky
    f = open("temp.png", 'wb')  # v prislusnom podadresari
    f.write(data)  #
    f.close()  #
    kic_phased = Image.open('temp.png')
    kic_ph_resized = kic_phased.resize((240,180))
    img = ImageTk.PhotoImage(kic_ph_resized)
    search_radius_deg = 0.001
    catalogTIC = Catalogs.query_object(kic_id, radius=search_radius_deg,
                                       catalog="TIC")  # Vyhlada vsetky TIC v okoli danej KIC
    try:
        where_closest = np.argmin(catalogTIC['dstArcSec'])  # Skusi vyhladat najblizsiu TIC ku danej KIC
    except:
        tic_id = ''
        obj_name_entered.delete(0, END)
        obj_name_entered.insert(0, tic_id)
    else:
        tic_id = 'TIC ' + str(catalogTIC['ID'][where_closest])
        obj_name_entered.delete(0, END)
        obj_name_entered.insert(0, tic_id)
    window.create_image(100, 900, image=img)
    window.create_text(270, 850, text = kic_id + '\n' + 'Period: ' + str(period) + '\n' + 'M0: '+ str(t0), font=('Times 10 bold'), justify='left')
    # window.create_text(270, 870, text = 'Period: '+ str(period), font=('Times 10 bold'))
    # window.create_text(270, 890, text= 'M0: '+ str(t0), font=('Times 10 bold'))
    window.update()
    window.mainloop()


find_tic_button = ttk.Button(frame1, text='Find TIC ID', command=find_tic)
find_tic_button.place(x=300, y=148)


def plot_phased():
    global window
    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')
    folded_lcf = lcf[int(sector_num.get())].fold(period, t0)
    # print(folded_lcf)
    x = folded_lcf.time.value
    y = folded_lcf.flux
    # x = folded_lcf[int(sector_num.get())].phase.value
    # y = folded_lcf[int(sector_num.get())].flux
    # x = lcf[int(sector_num.get())].time.value
    # y = lcf[int(sector_num.get())].flux
    figx = (screen_x-558)/100
    figy = (figx * 0.5625)
    fig = plt.Figure(figsize=(figx, figy), dpi = 100)
    #fig.add_subplot(111).plot(x, y, "ro")
    fig.add_subplot(111).plot(x, y, color='blue', marker='o', linestyle='dashed',
     linewidth=1, markersize=4)
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas._tkcanvas.pack()


def crossid():
    T2 = Text(master=window, height=50, width=165, bg='Light grey', bd=3, padx=10)  # Vytvori textovu plochu
    T2.place(x=5, y=5)                                                              # pre vypisy

    os.mkdir(path='crossid')  # Vytvori priecinok kde bude ukladat

    with open('kepler.csv', newline='') as csvfile:         # Otvori a nacita
        reader = csv.DictReader(csvfile)                    # zoznam z Keplera
        num = 0
        exc = 0
        for row in reader:                                  # Ide po KIC-kach riadok
            num = num + 1                                   # po riadku, num sa pouziva vo vypise ako porad. cislo
            target_name = "KIC "+row['#KIC']                # Vytvori podadresar
            os.mkdir(path='crossid/'+target_name)           # nazvany ako cele KIC ID, kde bude ukladat data


            if len(row['#KIC']) == 7:                                                                       #
                url = "http://keplerebs.villanova.edu/includes/" + "0" + row['#KIC'] + ".00.lc.dtr.png"     # Vytvori url na stiahnutie
            else:                                                                                           # obrazku dtr krivky
                url = "http://keplerebs.villanova.edu/includes/" + row['#KIC'] + ".00.lc.dtr.png"           #

            data = requests.get(url).content                    # Stiahne obrazok dtr krivky
            save_path = 'crossid/'+target_name+'/'              #
            file_name = "dtr.png"                               # Ulozi obrazok dtr krivky
            completeName = os.path.join(save_path, file_name)   # do suboru dtr.png
            f = open(completeName, 'wb')                        # v prislusnom podadresari
            f.write(data)                                       #
            f.close()                                           #

            search_radius_deg = 0.001                                               # Nastavi radius vyhladavania TIC ku KIC
            search_result = lk.search_lightcurve(target_name, author='Kepler')      # Stiahne vsetky dostupne Keplerove krivky
            lc_collection = search_result.download_all()                            # pre danu KIC-ku
            # T2.insert(INSERT, lc_collection)
            # T2.insert(INSERT, '\n')
            i = 0
            for lc in lc_collection:                                                # Ulozi do prislusneho
                filename = target_name+'_'+str(i)+'.csv'                            # podadresara vsetky dostupne krivky
                lc.to_csv(path_or_buf='crossid/'+target_name+'/'+filename)          # pre danu KIC, jednotlivo
                # csvtodat.csv_to_dat('crossid/'+target_name+'/'+filename, input_del=",", output_path='crossid/'+target_name+'/'+target_name+'_'+str(i)+'.dat', output_del=" ", column_names=list())
                i=i+1                                                               # po suboroch

            catalogTIC = Catalogs.query_object(target_name, radius=search_radius_deg, catalog="TIC") # Vyhlada vsetky TIC v okoli danej KIC
            try:
                where_closest = np.argmin(catalogTIC['dstArcSec'])                  # Skusi vyhladat najblizsiu TIC ku danej KIC
            except:
                print(num, row['#KIC'], 'no TIC', row['period'], row['bjd0'])       # Ak nenajde dostatocne blizku TIC vypise neuspech
                exc = exc + 1                                                       # Navysi pocet neuspesnych identifikacii o 1
            # print(catalogTIC['ID'][where_closest])
            # print("Closest TIC ID to %s: TIC %s, separation of %f arcsec. and a TESS mag. of %f" %
            #       (target_name, catalogTIC['ID'][where_closest], catalogTIC['dstArcSec'][where_closest],
            #        catalogTIC['Tmag'][where_closest]))
            else:
                tess_target_name = 'TIC '+str(catalogTIC['ID'][where_closest])      # Vytvori TIC ID uspesne najdenej TIC ku danej KIC
                search_result = lk.search_lightcurve(tess_target_name)              # Stiahne vsetky dostupne TESS krivky
                lc_collection = search_result.download_all()                        # pre danu TIC

                i = 0
                for lc in lc_collection:                                                # Ulozi do prislusneho podadresara
                    filename = tess_target_name + '_' + str(i) + '.csv'                 # vsetky dostupne krivky
                    # lc.to_csv(path_or_buf=target_name/target_name+'_'+str(i)+'.csv')  # pre danu TIC, jednotlivo
                    lc.to_csv(path_or_buf='crossid/'+target_name + '/' + filename)      # po suboroch
                    i = i + 1

                # Vytvori riadok ktory sa zapise do okna vypisov
                newrow = str(num) + ' ' + target_name + ' ' + tess_target_name + ' period:' + str(row['period']) + ' m0:' + str(row['bjd0'] + ' OK')
                T2.insert(INSERT, newrow)           # Vypise v okne uspesne
                T2.insert(INSERT, '\n')       # stiahnutie a ulozenie dat

                file = open('crossid/' + target_name + '/' + 'info.txt', "w")   # V prislusnom podadresari
                file.write(target_name + '\n')                                  # vytvori subor info.txt
                file.write(tess_target_name + '\n')                             # kde ulozi ziskane KIC, TIC
                file.write('period:' + str(row['period']) + '\n')               # periodu aj m0 pre
                file.write('m0:' + str(row['bjd0']) + '\n')                     # danu KIC
                file.close()
            T2.see(tk.END)
            T2.update()
        # print(exc)
    #       #print(row['KIC'], row['period'])


crossid_button = ttk.Button(frame1, text='  Crossidentification  ', command=crossid)
crossid_button.place(x=8, y=650)

curve_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
curve_plot_button.place(x=400, y=5)

plot_phased_button = ttk.Button(frame1, text='Plot Phased', command=plot_phased)
plot_phased_button.place(x=400, y=35)

# kic_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
# kic_plot_button.place(x=400, y=5)



root.mainloop()