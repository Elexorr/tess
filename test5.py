import tkinter as tk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import numpy as np
from astropy.modeling import models, fitting
from tkinter import ttk
from tkinter import*
import auxiliary as aux
import lightkurve as lk # Stahovanie kriviek zo satelitu TESS


# Vytvori graficke rozhranie
root = Tk()
root.geometry("555x525")
root.title('MP - Lightcurves')
root.resizable(width=False, height=False)
frame1 = tk.Frame(master=root, width=560, height=300, bg='gray64')
frame1.grid(row=0, column=0, sticky='N')
T = Text(master=root, height=13, width=65, bg='Light grey', bd=3, padx=10)
T.place(x=5, y=305)


# Otvorenie suboru so svetelnou krivkou a jej vizualizacia
def open_file():
    global JD, mag, err
    global ax
    file_path = fd.askopenfilename(filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    f = open(file_path, 'r')
    if file_path:
        with f:
            lines = f.readlines()

            # Definicia premennych casovej serie
            JD = []     #cas
            mag = []    #jasnost
            err = []    #chyba merania

            # Ulozenie hodnot do casovej serie
            for i in range (2, len(lines)):
                 if lines[i][16:18] != '99':
                     JD.append(float(lines[i][0:15]))
                     if(lines[i][16]) == '-':
                         mag.append(1+float(lines[i][16:24]))
                         err.append(float(lines[i][25:32]))
                     else:
                         mag.append(1+float(lines[i][16:23]))
                         err.append(float(lines[i][24:31]))
                 else:
                       pass

    # T.insert(INSERT, '\n')
    T.insert(INSERT, 'Lightcurve file opened: ' + file_path + '\n')
    T.see(tk.END)

    # Zobrazenie svetelnej krivky
    fig, ax = plt.subplots()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    ax.plot(JD, mag, 'b',  marker='o', linestyle='dashed', linewidth=1, markersize=4)
    plt.xlabel("JD (Julian Date)")
    plt.ylabel("Differential magnitude")
    ax.invert_yaxis()
    plt.show()

global vlines
vlines = 0

JDstart = tk.StringVar()
JDend = tk.StringVar()
interval = tk.StringVar()
amp = tk.StringVar()

#Vykreslovanie niektorych prvkov do rozhrania
st_label = tk.Label(master=frame1, text='Start:', bg='gray64')
st_label.place(x=40, y=50)
jd_label = tk.Label(master=frame1, text='JD:', bg='gray64')
jd_label.place(x=15, y=70)
start_label = ttk.Entry(frame1, width=18, textvariable=JDstart)
start_label.place(x=40, y=70)
en_label = tk.Label(master=frame1, text='End:', bg='gray64')
en_label.place(x=160, y=50)
end_label = ttk.Entry(frame1, width=18, textvariable=JDend)
end_label.place(x=160, y=70)
interval_entry = ttk.Entry(frame1, width=7, textvariable=interval)
interval_entry.place(x=207, y=100)
interval_unit_label = tk.Label(master=frame1, text='d', bg='gray64')
interval_unit_label.place(x=260, y=100)
amp_entry = ttk.Entry(frame1, width=5, textvariable=amp)
amp_entry.place(x=207, y=130)
amp_unit_label = tk.Label(master=frame1, text='mag', bg='gray64')
amp_unit_label.place(x=250, y=130)


# Vypocet casoveho useku
def time_interval():
    interval = round((JDend-JDstart), 4)
    interval_entry.delete(0, END)
    interval_entry.insert(0, interval)
    T.insert(INSERT, 'Time interval: ' + str(interval) + ' d\n')
    T.see(tk.END)
    file = open('log.txt', "a")
    file.write('Time interval: ' + str(interval) + '\n')
    file.close()

interval_button = ttk.Button(frame1, text="Time interval",command=time_interval)
interval_button.place(x=105,y=98)


# Vypocet amplitudy
def get_amplitude():
    amp = round(np.max(mag, axis = 0) - np.min(mag, axis = 0), 2)
    amp_entry.delete(0, END)
    amp_entry.insert(0, amp)
    T.insert(INSERT, 'Amplitude: ' + str(amp) + ' mag\n')
    T.see(tk.END)
    file = open('log.txt', "a")
    file.write('Amplitude: ' + str(amp) + '\n')
    file.close()

amplitude_button = ttk.Button(frame1, text="  Amplitude  ",command=get_amplitude)
amplitude_button.place(x=105,y=128)


# Oznacovanie useku na svetelnej krivke klikanim
def onclick(event):
    global ax, JDstart, JDend
    global JD, mag, err
    global vlines, vline1, vline2
    ix, iy = float(event.xdata), float(event.ydata)
    if vlines == 0:
        vline1 = ax.axvline(x=ix, color='black', linestyle='--')
        vlines = 1
        JDstart = ix
        start_label.delete(0, END)
        start_label.insert(0, JDstart)
        print('JDstart:', JDstart)
    elif vlines == 1:
        vline2 = ax.axvline(x=ix, color='black', linestyle='--')
        vlines = 2
        JDend = ix
        end_label.delete(0, END)
        end_label.insert(0, JDend)
        print('JDend:', JDend)
    elif vlines == 2:
        vline1.remove()
        vline2.remove()
        vline1 = ax.axvline(x=ix, color='black', linestyle='--')
        vlines = 1
        JDstart = ix
        start_label.delete(0, END)
        start_label.insert(0, JDstart)
        print('JDstart:', JDstart)
    plt.draw()


# Vytvorenie niektorych premennych a prvkov rozhrania
Gaussian = IntVar()
Lorentzian = IntVar()
checkboxGauss = tk.Checkbutton(master=frame1, text=' Gaussian', variable=Gaussian, onvalue=1, offvalue=0, bg="gray64")
checkboxGauss.place(x=5, y=160)
checkboxLorentz = tk.Checkbutton(master=frame1, text=' Lorentzian', variable=Lorentzian, onvalue=1, offvalue=0, bg="gray64")
checkboxLorentz.place(x=5, y=185)
GTmin = tk.StringVar()
LTmin = tk.StringVar()
style = ttk.Style()
style.theme_use('default')
style.configure('design1.TEntry', foreground='black', fieldbackground='lightyellow')
GTmin_entry = ttk.Entry(frame1, width=15, textvariable=GTmin, style='design1.TEntry')
GTmin_entry.place(x=105, y=160)
LTmin_entry = ttk.Entry(frame1, width=15, textvariable=LTmin, style='design1.TEntry')
LTmin_entry.place(x=105, y=185)


# Fitovanie svetelnej krivky Gaussovou alebo Lorentzovou funkciou
def fit_curve():
    fxx = []
    fyy = []
    gfitt = []
    lfitt = []
    # print(JDstart, JDend)
    for i in range(0, len(JD)):
        if JDstart < JD[i] and JD[i] < JDend:
            fxx.append(JD[i])
            fyy.append(mag[i])
    Maxmagvalue = np.max(mag, axis = 0)
    Minmagvalue = np.min(mag, axis = 0)
    magscale = Maxmagvalue - Minmagvalue
    # print(fxx)
    # print(fyy)


    # Fitovanie Gaussovou funkciou
    if Gaussian.get() == 1:  # fitting and drawing Gaussian model
        sd = (JDend - JDstart) / 2
        g_init = models.Gaussian1D(amplitude=magscale, mean=fxx[len(fxx) // 2], stddev=sd)
        # print('amplitude:', magscale, 'mean:', str(fxx[len(fxx) // 2]), 'stdev:', sd)
        fit_g = fitting.LevMarLSQFitter()
        fitted_g = fit_g(g_init, fxx, fyy)

        for i in range (0, len(fxx)):
            gfitt.append(fitted_g(fxx[i]))

        GTmin = round(fitted_g.mean.value, 7)
        GTmin_entry.delete(0, END)
        GTmin_entry.insert(0, GTmin)
        # print('Tmin (Gaussian): ', GTmin)
        T.insert(INSERT, 'Tmin (Gaussian): ' + str(GTmin) + '\n')
        T.see(tk.END)
        file = open('log.txt', "a")
        file.write('GTmin: ' + str(GTmin) + '\n')
        file.close()

    # Fitovanie Lorentzovou funkciou
    if Lorentzian.get() == 1:  # fitting and drawing Lorentzian model
        locmin = Minmagvalue
        index = 0
        for i in range(0, len(fyy)):
            if fyy[i] > locmin:
                locmin = fyy[i]
                index = i
        l_init = models.Lorentz1D(amplitude=magscale, x_0=fxx[index], fwhm=(JDend - JDstart) / 2)
        fit_l = fitting.LevMarLSQFitter()
        fitted_l = fit_l(l_init, fxx, fyy)

        for i in range (0, len(fxx)):
            lfitt.append(fitted_l(fxx[i]))

        LTmin = round(fitted_l.x_0.value, 7)
        LTmin_entry.delete(0, END)
        LTmin_entry.insert(0, LTmin)
        # print('Tmin (Lorentzian): ', LTmin)
        T.insert(INSERT, 'Tmin (Lorentzian): ' + str(LTmin) + '\n')
        T.see(tk.END)
        file = open('log.txt', "a")
        file.write('LTmin: ' + str(LTmin) + '\n')
        file.close()

    # Vykreslenie fitov
    if Gaussian.get() == 1:
        ax.plot(fxx, gfitt, 'r', linestyle='-', linewidth=2, markersize=4)
        Gminline = ax.axvline(x=fitted_g.mean.value, color='r', linestyle='--')
    if Lorentzian.get() == 1:
        ax.plot(fxx, lfitt, 'y', linestyle='-', linewidth=2, markersize=4)
        Tminline = ax.axvline(x=fitted_l.x_0.value, color='y', linestyle='--')

    plt.show()

# Vytvorenie niektorych premennych a prvkov rozhrania pre zobrazenie kriviek zo satelitu TESS
btn1= ttk.Button(frame1, text="Open",command=open_file)
btn1.place(x=5,y=5)

fit_button = ttk.Button(frame1, text="Fit Curve",command=fit_curve)
fit_button.place(x=100,y=5)

obj_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Object ID:', bg='gray64')
obj_label.place(x=340, y=8)
obj_name = tk.StringVar()
obj_name_entered = ttk.Entry(frame1, width=20, textvariable=obj_name)
obj_name_entered.place(x=400, y=8)

author_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Author:', bg='gray64')
author_label.place(x=340, y=36)
author_name = tk.StringVar()

global found_authors
found_authors = []
author_selection = ttk.Combobox(frame1, value=found_authors)
author_selection.place(x=400, y=36)

exptime_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Exptime:', bg='gray64')
exptime_label.place(x=340, y=64)
exptime = tk.IntVar()

global found_exptimes
found_exptimes = []
exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
exptime_selection.place(x=400, y=64)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='#:', bg='gray64')
sector_label.place(x=370, y=132)
sector_num = tk.IntVar()

global found_sectors
found_sectors = []
sector_num = ttk.Combobox(frame1, value=found_sectors, width = 3)
sector_num.place(x=393, y=132)


# Zakladne vyhladavanie podla identifikatora hviezdy
def basic_search():
    search_lcf = lk.search_lightcurve(obj_name.get())
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf)
    T.insert(INSERT, '\n')
    found_authors = aux.find_authors(search_lcf.author)
    global author_selection
    author_selection = ttk.Combobox(frame1, value=found_authors)
    author_selection.insert(0, 'SPOC')
    author_selection.place(x=400, y=36)
    found_exptimes = aux.find_exptimes(search_lcf.exptime)
    global exptime_selection
    exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
    exptime_selection.insert(0, 120)
    exptime_selection.place(x=400, y=64)
    T.see(tk.END)

basic_search_button = ttk.Button(frame1, text='  Basic Search  ', command=basic_search)
basic_search_button.place(x=340, y=98)


# Spresnene vyhladavanie so specifikaciou authora a expozicneho casu
def refined_search():
    global lcf
    search_lcf_refined = lk.search_lightcurve(obj_name.get(), author=str(author_selection.get()), exptime=int(exptime_selection.get()))
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf_refined)
    T.insert(INSERT, '\n')
    T.see(tk.END)
    global found_sectors
    found_sectors = len(search_lcf_refined)
    nums = []
    for i in range (0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=393, y=132)
    if len(search_lcf_refined.table) != 0:
        lcf = search_lcf_refined.download_all()

refined_search_button = ttk.Button(frame1, text='Refined Search', command=refined_search)
refined_search_button.place(x=440, y=98)


# Vykreslenie svetelnej krivky z TESS-u
def plottess():
    lcf[int(sector_num.get())].plot()
    plt.show()

plottess_button = ttk.Button(frame1, text='Plot TESS', command=plottess)
plottess_button.place(x=440, y=130)

root.mainloop()