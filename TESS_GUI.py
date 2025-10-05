import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog as fd
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
from astropy.modeling.fitting import Fitter
import csvtodat
import requests
# import pandas as pd


root = tk.Tk()
root.title('TESS project v0.5')
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
    fromfile = False
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


global fitted, fromfile
fitted = False
fromfile = False


def opencurvefile():
    clear_JD()
    global filex
    global filey
    global fromfile, file_name, f, lines

    file_path = fd.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    print(file_path)

    file_name = os.path.basename(file_path)
    print(file_name)
    T.insert(INSERT, '\n')
    T.insert(INSERT, 'Opened file ' + file_name)
    T.see(tk.END)

    f = open(file_path, 'r')

    lines = f.readlines()

    filex = []    #cas
    filey = []    #jasnost

    # for line in lines:
    #     filex.append(float(line.split(' ')[0]))
    #     filey.append(float(line.split(' ')[1]))

    # for i in range(1, len(lines)):
    #     if float(lines[i].split(' ')[0]) > 2457000:
    #         filex.append(float(lines[i].split(' ')[0])) ## -2457000
    #     else:
    #         filex.append(float(lines[i].split(' ')[0]))
    #     if 5 < float(lines[i].split(' ')[1]) < 20:
    #         filey.append(float(lines[i].split(' ')[1])/10-1)
    #     else:
    #         filey.append(float(lines[i].split(' ')[1]))

    for i in range(1, len(lines)):
        filex.append(float(lines[i].split(' ')[0]))
        filey.append(float(lines[i].split(' ')[1]))


    fromfile = True

    # if file_path:
    #     with f:
    #         lines = f.readlines()
    #
    #         # Definicia premennych casovej serie
    #         x = []     #cas
    #         y = []    #jasnost
    #         # err = []    #chyba merania
    #
    #         # Ulozenie hodnot do casovej serie
    #         for i in range (0, len(lines)):
    #              if lines[i][16:18] != '99':
    #                  x.append(float(lines[i][0:16]))
    #                  y.append(float(lines[i][19:27]))



                 #     if(lines[i][16]) == '-':
                 #         mag.append(1+float(lines[i][16:24]))
                 #         err.append(float(lines[i][25:32]))
                 #     else:
                 #         mag.append(1+float(lines[i][16:23]))
                 #         err.append(float(lines[i][24:31]))
                 # else:
                 #       pass

open_file_button = ttk.Button(frame1, text='Open File', command=opencurvefile)
open_file_button.place(x=10, y=100)

def curve_plot():
    global fitted
    global fig
    global lcf
    global window
    global canvas
    global ax
    global x, filex
    global y, filey
    global fromfile
    global xx
    global yy
    global vlines

    vlines = 0

    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')

    if fitted == False:
        # print(lcf)

        if fromfile == True:
            x = filex
            y = filey
        else:
            x = lcf[int(sector_num.get())].time.value
            y = lcf[int(sector_num.get())].flux.value


        print('Hello')
        # for i in range(0,10):
        #     print(y[i])

        # T.insert(INSERT, '\n')
        # T.insert(INSERT, 'Data sample: ' + str(x[0]) + ' ' + str(y[0]))
        # T.see(tk.END)

        # if y[1] > 20:
        #     divisor = 100000
        #     result = [(a / divisor - 2) for a in y]
        #     y = result

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
            xx = x
            yy = y
            # xx = lcf[int(sector_num.get())].time.value
            # yy = lcf[int(sector_num.get())].flux.value


        # EXPERIMENTAL ROWS
        # for i in range (0,len(yy)):
        #     zz.append(yy[i]+0.1)
        # EXPERIMENTAL ROWS

        # lcf[int(sector_num.get())].to_csv(path_or_buf='lightcurve.csv', overwrite=True)

        # savecsvename = str(obj_name.get()) + '_' + str(author_selection.get()) + '_' + str(exptime_selection.get()) + '.csv'
        # lcf[int(sector_num.get())].to_csv(path_or_buf= savecsvename, overwrite=True)

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
    ax.set_xlabel('TESS_GUI.py', fontsize=20)
    ax.set_ylabel('Normalizovaný tok', fontsize=20)
    plt.xlabel('X-ová os')
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

period_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Period:', bg='grey')
period_label.place(x=265, y=115)
period_entered = ttk.Entry(frame1, width=10)
period_entered.place(x=320, y=115)
t0label = tk.Label(master=frame1, font=('Helvetica', 10), text='t0:', bg='grey')
t0label.place(x=290, y=140)
t0label_entered = ttk.Entry(frame1, width=10)
t0label_entered.place(x=320, y=140)


def clear_JD():
    JDstart_entered.delete(0, END)
    JDend_entered.delete(0, END)


Gaussian = IntVar()
Lorentzian = IntVar()
checkboxGauss = tk.Checkbutton(master=frame1, text=' Gaussian', variable=Gaussian, onvalue=1, offvalue=0, bg="grey")
checkboxGauss.place(x=395, y=170)
checkboxLorentz = tk.Checkbutton(master=frame1, text=' Lorentzian', variable=Lorentzian, onvalue=1, offvalue=0, bg="grey")
checkboxLorentz.place(x=395, y=190)

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
    gfitt = []
    lfitt = []

    if JDstart_entered.get() != '':
        JDstart = float(JDstart_entered.get())
        JDend = float(JDend_entered.get())
        for i in range (0, len(x)):
            if JDstart < x[i] and  x[i] < JDend:
                fxx.append(float(x[i]))
                fyy.append(float(y[i]))
                invyy.append(1-float(y[i]))

    # Maxmagvalue = np.max(fyy, axis = 0)
    # Minmagvalue = np.min(fyy, axis = 0)

    Maxmagvalue = np.max(invyy, axis = 0)
    Minmagvalue = np.min(invyy, axis = 0)

    magscale = Maxmagvalue - Minmagvalue

    print(Maxmagvalue, Minmagvalue, magscale)
    print(invyy)

    fstart = float(JDstart_entered.get())  # getting user starting and ending point
    fend = float(JDend_entered.get())      # of fitting

    if Gaussian.get() == 1:  # fitting and drawing Gaussian model
        sd = (fend - fstart) / 4
        print('stdev:', sd)
        # sd = np.sqrt(np.sum((fxx - fxx[len(fxx) // 2]) ** 2) / (len(fxx) - 1))
        # stddev = np.sqrt(np.sum((orig_wavelength - an_mean) ** 2) / (len(orig_wavelength) - 1))
        g_init = models.Gaussian1D(amplitude=magscale, mean=fxx[len(fxx) // 2], stddev=sd)
        print('amplitude:', magscale, 'mean:', str(fxx[len(fxx) // 2]), 'stdev:', sd)
        fit_g = fitting.LevMarLSQFitter()
        # fitted_g = fit_g(g_init, fxx, invyy)
        fitted_g = fit_g(g_init, fxx, invyy)
        # print('Fit info:\n', fit_g.fit_info['param_cov'])
        paramcov = fit_g.fit_info['param_cov']
        mean_error = np.sqrt(paramcov[1][1])
        print(mean_error)

        # print(fitted_g.mean)
        # fitted_g = fit_g(g_init, fxx, fyy)

        for i in range (0, len(fxx)):
            # fitt.append(fitted_g(fxx[i]))
            gfitt.append(1-fitted_g(fxx[i]))

        GTmin = round(fitted_g.mean.value, 7)
        print('Tmin (Gaussian): ', GTmin)
        T.insert(INSERT, '\n')
        T.insert(INSERT, 'Tmin (Gaussian): ' + str(GTmin) + '(' + str(mean_error) + ')')
        FullGTmin = GTmin + 2457000.0

        # if isinstance(fit_g, Fitter) and fit_g.fit_info['param_cov'] is not None:
        #     param_cov = fit_g.fit_info['param_cov']
        #     mean_error = np.sqrt(param_cov[1][1])  # Chyba pre parameter 'mean'
        #     print(f"Chyba strednej hodnoty (mean): {mean_error}")
        # else:
        #     print("Kovariančná matica nie je k dispozícii.")


    if Lorentzian.get() == 1:  # fitting and drawing Lorentzian model
        locmin = Maxmagvalue
        index = 0
        for i in range(0, len(invyy)):
            if invyy[i] < locmin:
                locmin = invyy[i]
                index = i
        l_init = models.Lorentz1D(amplitude=Maxmagvalue, x_0=fxx[index], fwhm=(fend - fstart) / 2)
        fit_l = fitting.LevMarLSQFitter()
        fitted_l = fit_l(l_init, fxx, invyy)
        # print(fitted_l)

        for i in range (0, len(fxx)):
            # fitt.append(fitted_g(fxx[i]))
            lfitt.append(1-fitted_l(fxx[i]))

        LTmin = round(fitted_l.x_0.value, 7)
        print('Tmin (Lorentzian): ', LTmin)
        T.insert(INSERT, '\n')
        T.insert(INSERT, 'Tmin (Lorentzian): ' + str(LTmin))
        T.see(tk.END)


    fitted = True
    ax.cla()

    figx = (screen_x - 558) / 100
    figy = (figx * 0.5625)
    fig = plt.Figure(figsize=(figx, figy), dpi=100)

    ax = fig.add_subplot(111)
    # ax.plot(xx, yy, 'b', fxx, fitt, 'r', marker='o', linestyle='dashed', linewidth=1, markersize=4)
    ax.plot(xx, yy, 'b', marker='o', linestyle='dashed', linewidth=1, markersize=4)
    if Gaussian.get() == 1:
        ax.plot(fxx, gfitt, 'r', linestyle='-', linewidth=2, markersize=4)
        gminvline = ax.axvline(x=fitted_g.mean.value, color='g', linestyle='--', linewidth=0.5)
    if Lorentzian.get() == 1:
        ax.plot(fxx, lfitt, 'y', linestyle='-', linewidth=2, markersize=4)
        lminvline = ax.axvline(x=fitted_l.x_0.value, color='y', linestyle='--', linewidth=0.5)

    # ax.plot(fxx, fitt, 'r', xx, yy, 'b',  marker='o', linestyle='dashed', linewidth=1, markersize=4)


    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    # # cid = fig.canvas.mpl_connect('button_press_event', onclick)
    canvas._tkcanvas.pack()


fit_button = ttk.Button(frame1, text='Fit Selection', width = 11, command=fitprocessing)
fit_button.place(x=400, y=220)

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
    txtcurve = str(obj_name.get()) + '_selection_tess.txt'
    file = open(txtcurve, 'w')
    # print(lcf[int(sector_num.get())])
    # fluxcoef = int(exptime_selection.get())/1800
    for row in lcf[int(sector_num.get())]:
        if JDstart < float(str(row['time'].value)) < JDend:
            JDtime = row['time'] + 2457000
            mag = -2.5 * float(row['flux'].value) + 20
            # mag = -2.5 * (float(row['flux'].value)*fluxcoef) + 20
            line = str(JDtime) + ' ' + str(row['flux'].value) + ' ' + str(row['flux_err'].value) + '\n'
            # line = str(JDtime) + ' ' + str(mag) + ' ' + str(row['flux_err'].value) + '\n'
            # line = str(row['time']) + ' ' + str(mag) + ' ' + str(row['flux_err']) + '\n'
            # line = str(row['time']) + ' ' + str(row['flux']) + ' ' + str(row['flux_err']) + '\n'
            # print(line)
            file.write(line)
    file.close()


def save_cutted():
    print('spustam ukladanie')
    global file_name, lines
    # for row in lines:
    #     print(row)
    if JDstart_entered.get() != '':
        JDstart = float(JDstart_entered.get())
        JDend = float(JDend_entered.get())
    else:
        JDstart = 0
        JDend = 1000000
    cuttedcurve = 'cut_' + file_name
    filecutted = open(cuttedcurve, 'a')
    for row in lines:

        if JDstart < float(row.split()[0]) < JDend:
            print(row)
            print(float(row.split()[0]))
            filecutted.write(str(row))
    T.insert(INSERT, '\n')
    T.insert(INSERT, 'Saved file ' + cuttedcurve)
    T.see(tk.END)
    filecutted.close()


save_curve_button = ttk.Button(frame1, text='Save Curve', command=save_curve)
save_curve_button.place(x=400, y=107)

save_cutted_button = ttk.Button(frame1, text='Save Cutted', command=save_cutted)
save_cutted_button.place(x=400, y=137)


kepler_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Kepler Eclipsing Binary Catalog', bg='grey')
kepler_label.place(x=5, y=225)


kic_ids = []
with open('kepler.csv', newline='') as csvfile:
    rowz = csv.DictReader(csvfile)
    for row in rowz:
        kic_ids.append(row['#KIC'])
    kic_ids = sorted(kic_ids)


kic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='KIC ID:', bg='grey')
kic_label.place(x=5, y=250)
kic_id_input = ttk.Combobox(frame1, value=kic_ids, width = 20)
kic_id_input.place(x=65, y=250)


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
        period_entered.delete(0, END)
        period_entered.insert(0, period)
        t0 = float(t0)
        t0label_entered.delete(0, END)
        t0label_entered.insert(0, t0)
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
kic_input_button.place(x=220, y=248)

global canvas

def find_tic():
    global lcf
    global period
    global t0
    global window
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
        period_entered.delete(0, END)
        period_entered.insert(0, period)
        t0 = float(t0)
        t0label_entered.delete(0, END)
        t0label_entered.insert(0, t0)
        print(period)
        print(t0)

    kic_id = 'KIC '+ kic_num
    if len(kic_num) == 7:  #
        url = "http://keplerebs.villanova.edu/includes/" + "0" + kic_num + ".00.lc.pf.png"  # Vytvori url na stiahnutie
    else:  # obrazku dtr krivky
        url = "http://keplerebs.villanova.edu/includes/" + kic_num + ".00.lc.pf.png"  #
    print(url)
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
find_tic_button.place(x=300, y=248)


def plot_phased():
    # global period
    if period_entered.get() != '':
        period = float(period_entered.get())
        t0 = float(t0label_entered.get())
    # if 'period' in globals():
        global window
        window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
        window.grid(row=0, column=1, sticky='N')
        folded_lcf = lcf[int(sector_num.get())].fold(period, t0, epoch_phase=0.0, wrap_phase=0.5, normalize_phase=True)
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
        # fig.add_subplot(111).plot(x, y, color='blue', marker='o', linestyle='dashed',
        #  linewidth=1, markersize=4)
        ax = fig.add_subplot(111)
        ax.plot(x, y, color='blue', marker='o', linestyle='dashed', linewidth=1, markersize=4)
        # ax.plot(xx, yy, 'b', marker='o', linestyle='dashed', linewidth=1, markersize=4)
        ax.set_xlabel('Fáza', fontsize=20)
        ax.set_ylabel('Normalizovaný tok', fontsize=20)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        canvas._tkcanvas.pack()
    else:
        showinfo(title='Plot phased', message='Period and M0 not defined')

def plot_phased_from_file():
    global filex
    global filey
    phases = []  # fázy

    if 'filex' in globals():
        print(filex)
        print(filey)
    else:
        showinfo(title='Plot phased', message='No File Loaded')

    if period_entered.get() != '':
        period = float(period_entered.get())
        t0 = float(t0label_entered.get())

        for time in filex:
            phase = ((time - t0) / period) % 1
            if phase > 0.5:
                phase = phase - 1
            phases.append(phase)
        print('Phases:')
        print(phases)

        # ak chceš -1 → +1
        # phases = phases * 2
        global window
        window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
        window.grid(row=0, column=1, sticky='N')

        figx = (screen_x-558)/100
        figy = (figx * 0.5625)
        fig = plt.Figure(figsize=(figx, figy), dpi = 100)
        #fig.add_subplot(111).plot(x, y, "ro")
        # fig.add_subplot(111).plot(x, y, color='blue', marker='o', linestyle='dashed',
        #  linewidth=1, markersize=4)
        ax = fig.add_subplot(111)
        # ax.plot(phases, filey, color='blue', marker='o', linestyle='dashed', linewidth=1, markersize=4)
        ax.plot(phases, filey, color='blue', marker='o', linestyle = 'None', markersize=4)
        # ax.plot(xx, yy, 'b', marker='o', linestyle='dashed', linewidth=1, markersize=4)
        ax.set_xlabel('Fáza', fontsize=20)
        ax.set_ylabel('Normalizovaný tok', fontsize=20)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(canvas, window)
        toolbar.update()
        canvas._tkcanvas.pack()


    else:
        showinfo(title='Plot phased', message='Period and M0 not defined')


plot_phased_from_file_button = ttk.Button(frame1, text='From File', command=plot_phased_from_file)
plot_phased_from_file_button.place(x=400, y=65)


def frame():
    # global search_ffi
    global search_tpf
    # search_ffi = lk.search_tesscut(obj_name.get())
    search_tpf = lk.search_tesscut(obj_name.get())
    # T.insert(INSERT, '\n')
    # T.insert(INSERT, search_ffi)
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_tpf)
    # found_sectors = len(search_ffi)
    # nums = []
    # for i in range (0, found_sectors):
    #     nums.append(i)
    # global sector_num
    # sector_num = ttk.Combobox(frame1, value=nums, width=3)
    # sector_num.insert(0, 0)
    # sector_num.place(x=340, y=8)
    found_sectors = len(search_tpf)
    nums = []
    for i in range (0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=340, y=8)

def plot_frame():
    # global found_sectors, search_ffi
    global found_sectors, search_tpf, window
    # ffi_data = search_ffi[int(sector_num.get())].download(cutout_size=10)
    tpf_data = search_tpf[int(sector_num.get())].download(cutout_size=10)
    # ffi_data.plot()
    # plt.show()
    # temptpf = tpf_data.plot()
    tpf_data.plot().figure.savefig('temptpf.png')
    tpfpng = Image.open('temptpf.png')
    # img2 = PhotoImage(file='temptpf.png')
    # img2 = tpfpng.resize((240, 180))
    tpfpng_crop = tpfpng.crop((230, 0, 760, 400))
    img2 = ImageTk.PhotoImage(tpfpng_crop.resize((239, 180)))
    # img2crop = img2.crop((100, 0, 340, 180))
    # window.create_image((screen_x-558)//2.2, (screen_y-50)//4, image=img2)
    window.create_image(475, 900, image=img2)
    window.update()
    # tpf_data.plot()
    # plt.show()



frame_button = ttk.Button(frame1, text='Full Frame Image', command=frame)
frame_button.place(x=10, y=150)

plot_frame_button = ttk.Button(frame1, text='Plot FF Image', command=plot_frame)
plot_frame_button.place(x=120, y=150)


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


crossid_button = ttk.Button(frame1, text='  Crossidentification  ', command=crossid, state='disabled')
crossid_button.place(x=8, y=650)

curve_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
curve_plot_button.place(x=400, y=5)

plot_phased_button = ttk.Button(frame1, text='Plot Phased', command=plot_phased)
plot_phased_button.place(x=400, y=35)

# kic_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
# kic_plot_button.place(x=400, y=5)



root.mainloop()