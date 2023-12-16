from datetime import datetime
import tkinter as tk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import numpy as np
from astropy.modeling import models, fitting
import pandas as pd
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
# from PyQt5.QtGui import QPixmap
from tkinter import ttk
from tkinter import*


root = Tk()
root.geometry("300x525")
root.resizable(width=False, height=False)

def open_file():
    global JD, mag, err
    global ax
    file_path = fd.askopenfilename(initialdir="C:\\Users\chobo\OneDrive\Документы\MaturitnyProjekt",
                                   filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    f = open(file_path, 'r')
    if file_path:
        with f:
            lines = f.readlines()

            JD = []     #cas
            mag = []    #jasnost
            err = []    #chyba merania

            for i in range (2, len(lines)):
                 if lines[i][16:18] != '99':
                       JD.append(float(lines[i][0:15]))
                       if(lines[i]) == '-':
                        mag.append(float(lines[i][16:25]))
                        err.append(float(lines[i][25:32]))
                       else:
                        mag.append(float(lines[i][16:24]))
                        err.append(float(lines[i][24:31]))
                 else:
                       pass

    fig, ax = plt.subplots()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ax.plot(JD, mag, 'b',  marker='o', linestyle='dashed', linewidth=1, markersize=4)
    ax.invert_yaxis()

    plt.show()

global vlines
vlines = 0

def onclick(event):
    global ax, JDstart, JDend
    global JD, mag, err
    global vlines, vline1, vline2
    ix, iy = float(event.xdata), float(event.ydata)
    if vlines == 0:
        vline1 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 1
        JDstart = ix
    elif vlines == 1:
        vline2 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 2
        JDend = ix
    elif vlines == 2:
        vline1.remove()
        vline2.remove()
        vline1 = ax.axvline(x=ix, color='r', linestyle='--')
        vlines = 1
        JDstart = ix
    plt.draw()
    # print(JDstart, JDend)


Gaussian = IntVar()
Lorentzian = IntVar()
checkboxGauss = tk.Checkbutton(master=root, text=' Gaussian', variable=Gaussian, onvalue=1, offvalue=0, bg="white")
checkboxGauss.place(x=5, y=100)
checkboxLorentz = tk.Checkbutton(master=root, text=' Lorentzian', variable=Lorentzian, onvalue=1, offvalue=0, bg="white")
checkboxLorentz.place(x=5, y=120)


def fit_curve():
    fxx = []
    fyy = []
    gfitt = []
    lfitt = []
    for i in range(0, len(JD)):
        if JDstart < JD[i] and JD[i] < JDend:
            fxx.append(JD[i])
            fyy.append(mag[i])
    Maxmagvalue = np.max(mag, axis = 0)
    Minmagvalue = np.min(mag, axis = 0)
    magscale = Maxmagvalue - Minmagvalue
    # print(fxx)
    # print(fyy)
    # print(Minmagvalue, Maxmagvalue, magscale)

    if Gaussian.get() == 1:  # fitting and drawing Gaussian model
        sd = (JDend - JDstart) / 2
        g_init = models.Gaussian1D(amplitude=magscale, mean=fxx[len(fxx) // 2], stddev=sd)
        print('amplitude:', magscale, 'mean:', str(fxx[len(fxx) // 2]), 'stdev:', sd)
        fit_g = fitting.LevMarLSQFitter()
        fitted_g = fit_g(g_init, fxx, fyy)

        for i in range (0, len(fxx)):
            gfitt.append(fitted_g(fxx[i]))

        GTmin = round(fitted_g.mean.value, 7)
        print('GTmin: ', GTmin)

    if Lorentzian.get() == 1:  # fitting and drawing Lorentzian model
        locmin = Minmagvalue
        index = 0
        for i in range(0, len(fyy)):
            if fyy[i] > locmin:
                locmin = fyy[i]
                index = i
        l_init = models.Lorentz1D(amplitude=Maxmagvalue, x_0=fxx[index], fwhm=(JDend - JDstart) / 2)
        fit_l = fitting.LevMarLSQFitter()
        fitted_l = fit_l(l_init, fxx, fyy)
        # print(fitted_l)

        for i in range (0, len(fxx)):
            # fitt.append(fitted_g(fxx[i]))
            lfitt.append(fitted_l(fxx[i]))

        LTmin = round(fitted_l.x_0.value, 7)
        print('Tmin (Lorentzian): ', LTmin)

    if Gaussian.get() == 1:
        ax.plot(fxx, gfitt, 'r', linestyle='-', linewidth=2, markersize=4)
    if Lorentzian.get() == 1:
        ax.plot(fxx, lfitt, 'y', linestyle='-', linewidth=2, markersize=4)
    plt.show()



btn1= ttk.Button(root, text="Open",command=open_file)
btn1.place(x=5,y=5)

fit_button = ttk.Button(root, text="Fit Curve",command=fit_curve)
fit_button.place(x=100,y=5)

root.mainloop()

