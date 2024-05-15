import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import csv
import requests
from PIL import Image, ImageTk
from astroquery.mast import Catalogs
import lightkurve as lk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

root = tk.Tk()
root.title('TESS FFI curver 0.1')
root.resizable(False, False)
root.configure(bg='white')
frame1 = tk.Frame(master=root, width=542, height=506, bg='grey')
frame1.grid(row=0, column=0, sticky='N')
T = Text(master=frame1, height=12, width=63, bg='Light grey', bd=3, padx=10)
T.place(x=5, y=300)

kic_ids = []
with open('kepler.csv', newline='') as csvfile:
    rowz = csv.DictReader(csvfile)
    for row in rowz:
        kic_ids.append(row['#KIC'])
    kic_ids = sorted(kic_ids)

kic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='KIC ID:', bg='grey')
kic_label.place(x=5, y=38)
kic_id_input = ttk.Combobox(frame1, value=kic_ids, width=20)
kic_id_input.place(x=85, y=38)

obj_name = tk.StringVar()
tic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Star/TIC ID:', bg='grey')
tic_label.place(x=5, y=10)
obj_name_entered = ttk.Entry(frame1, width=20, textvariable=obj_name)
obj_name_entered.place(x=85, y=10)


def create_output_window():
    global output_window
    output_window = tk.Canvas(master=root, width=500, height=500, bg='white')
    output_window.grid(row=0, column=1, sticky='N')


def embed_plot(maskcolor):
    global search
    fig, ax = plt.subplots()
    if search == 'ffi':
        ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color=maskcolor)
    elif search == 'tpf':
        tpf_plot = tpf_data.plot(ax=ax, aperture_mask=target_mask, mask_color=maskcolor)
    canvas = FigureCanvasTkAgg(fig, master=output_window)
    canvas.draw()
    canvas._tkcanvas.pack()


def find_tic():
    global lcf
    global period
    global t0
    global output_window

    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()

    kic_num = kic_id_input.get()

    with open('kepler.csv', newline='') as csvfile:
        rowz = csv.DictReader(csvfile)
        for row in rowz:
            if kic_id_input.get() == row['#KIC']:
                period = row['period']
                t0 = row['bjd0']
        period = float(period)
        t0 = float(t0)

    kic_id = 'KIC ' + kic_num
    if len(kic_num) == 7:  #
        url = "http://keplerebs.villanova.edu/includes/" + "0" + kic_num + ".00.lc.pf.png"  # Vytvori url na stiahnutie
    else:                                                                                   # obrazku dtr krivky
        url = "http://keplerebs.villanova.edu/includes/" + kic_num + ".00.lc.pf.png"  #
    data = requests.get(url).content        # Stiahne obrazok dtr krivky
    f = open("temp.png", 'wb')              # Ulozi obrazok dtr krivky v prislusnom podadresari
    f.write(data)  #
    f.close()  #
    kic_phased = Image.open('temp.png')
    kic_ph_resized = kic_phased.resize((520, 375))
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
        
    create_output_window()
    output_window.create_image(250, 188, image=img)
    output_window.create_text(250, 400, text=kic_id + '\n' + 'Period: ' + str(period) + '\n' + 'M0: ' + str(t0),
                              font='Times 10 bold', justify='left')
    output_window.mainloop()


find_tic_button = ttk.Button(frame1, text='Find TIC ID', command=find_tic)
find_tic_button.place(x=235, y=36)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Sector #:', bg='grey')
sector_label.place(x=90, y=80)
sector_num = tk.IntVar()
global found_sectors
found_sectors = []
sector_num = ttk.Combobox(frame1, value=found_sectors, justify=CENTER, width=3)
sector_num.place(x=150, y=82)
size_entry = tk.Spinbox(master=frame1, from_=11, to=201, increment=10, justify=CENTER, width=5)
size_entry.place(x=145, y=112)
size_entry_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Size:', bg='grey')
size_entry_label.place(x=90, y=110)

global search

def searchffi():
    global search, search_ffi, ffi_data
    search_ffi = lk.search_tesscut(obj_name_entered.get())
    # search_tpf = lk.search_targetpixelfile(obj_name_entered.get())
    # search_lcf = lk.search_lightcurve('V523 Cas')
    T.insert(INSERT, 'SearchResult for ' + obj_name_entered.get() + '\n')
    T.insert(INSERT, search_ffi)
    # T.insert(INSERT, '\n')
    T.insert(INSERT, '\n--------------------------------------------------------------')
    T.insert(INSERT, '\n')
    T.see(tk.END)

    found_sectors = len(search_ffi)
    nums = []
    for i in range(0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=150, y=82)
    search = 'ffi'


def searchtpf():
    global search, search_tpf, tpf_data
    search_tpf = lk.search_targetpixelfile(obj_name_entered.get())

    T.insert(INSERT, 'SearchResult for ' + obj_name_entered.get() + '\n')
    T.insert(INSERT, search_tpf)
    # T.insert(INSERT, '\n')
    T.insert(INSERT, '\n--------------------------------------------------------------')
    T.insert(INSERT, '\n')
    T.see(tk.END)

    found_sectors = len(search_tpf)
    nums = []
    for i in range(0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=150, y=82)
    search = 'tpf'


coordinates_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Frame position:', bg='grey')
coordinates_label.place(x=10, y=228)
dec_output = ttk.Entry(master=frame1, text='', width=10, font="Times 10 bold")
dec_output.place(x=50, y=250)
dec_output_label = tk.Label(master=frame1, font=('Helvetica', 10), text='DEC:', bg='grey')
dec_output_label.place(x=10, y=250)
ra_output = ttk.Entry(master=frame1, text='', width=10, font="Times 10 bold")
ra_output.place(x=50, y=275)
ra_output_label = tk.Label(master=frame1, font=('Helvetica', 10), text='RA:', bg='grey')
ra_output_label.place(x=10, y=275)


def plot_ffi():
    # plt.close()
    global search, search_ffi, target_mask, ffi_plot, ffi_data, tpf_data, output_window, ax, plotwidth, plotheight

    if search == 'ffi':
        ffi_data = search_ffi[int(sector_num.get())].download(cutout_size=int(size_entry.get()))
        # ffi_data.show_properties()
        target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
        plotwidth = ffi_data.column - 0.5
        plotheight = ffi_data.row - 0.5
        dec_output.delete(0, END)
        dec_output.insert(0, str(round(ffi_data.dec, 6)))
        ra_output.delete(0, END)
        ra_output.insert(0, str(round(ffi_data.ra, 6)))
    elif search == 'tpf':
        tpf_data = search_tpf[int(sector_num.get())].download()
        # tpf_data.show_properties()
        target_mask = tpf_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
        plotwidth = tpf_data.column - 0.5
        plotheight = tpf_data.row - 0.5
        dec_output.delete(0, END)
        dec_output.insert(0, str(round(tpf_data.dec, 6)))
        ra_output.delete(0, END)
        ra_output.insert(0, str(round(tpf_data.ra, 6)))
    create_output_window()
    embed_plot('r')

    plt.close()
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, output_window)
    # toolbar.update()


def plot_ffi_update():
    global ffi_plot, ax
    global target_mask
    global output_window, search
    plt.close()

    if search == 'ffi':
        target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
    if search == 'tpf':
        target_mask =tpf_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')

    create_output_window()
    embed_plot('r')
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, output_window)
    # toolbar.update()


def makeownmask():
    global target_mask
    global output_window, search
    # plt.close()

    if search == 'ffi':
        target_mask = ffi_data.create_threshold_mask(threshold=1000, reference_pixel='center')
        create_output_window()
        embed_plot('#0000FF')
    elif search == 'tpf':
        target_mask = tpf_data.create_threshold_mask(threshold=1000, reference_pixel='center')
        create_output_window()
        embed_plot('#0000FF')
    plt.gcf().canvas.mpl_connect('button_press_event', setmaskpixel)
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, output_window)
    # toolbar.update()


makeownmask_button = ttk.Button(frame1, text='Set Mask', command=makeownmask)
makeownmask_button.place(x=200, y=110)


def setmaskpixel(event):
    global target_mask
    global output_window, search
    ix, iy = event.xdata, event.ydata
    # print(f'x = {ix}, y = {iy}')
    mask_y = int((ix - plotwidth)//1)
    mask_x = int((iy - plotheight)//1)

    if target_mask[mask_x, mask_y] == False:
        target_mask[mask_x, mask_y] = True
    else:
        target_mask[mask_x, mask_y] = False
    plt.close()

    create_output_window()
    if search == 'ffi':
        embed_plot('#0000FF')
    elif search == 'tpf':
        embed_plot('#0000FF')
    plt.gcf().canvas.mpl_connect('button_press_event', setmaskpixel)
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, output_window)
    # toolbar.update()


def plot_curve():
    global ffi_lc, tpf_lc, search
    plt.close()
    if search == 'ffi':
        ffi_lc = ffi_data.to_lightcurve(aperture_mask=target_mask)
        lightcurve = ffi_lc.plot(label="SAP FFI")
    elif search == 'tpf':
        tpf_lc = tpf_data.to_lightcurve(aperture_mask=target_mask)
        lightcurve = tpf_lc.plot(label="SAP TPF")
    plt.show()


def save_curve():
    global ffi_lc, tpf_lc
    if search == 'ffi':
        txtcurve = str(obj_name.get()) + ' #' + sector_num.get() + '_ffi.txt'
        file = open(txtcurve, 'w')
        for row in ffi_lc:
            line = str(row['time']) + ' ' + str(row['flux'].value) + ' ' + str(row['flux_err'].value) + '\n'
            file.write(line)
        file.close()
    if search == 'tpf':
        txtcurve = str(obj_name.get()) + ' #' + sector_num.get() + '_tpf.txt'
        file = open(txtcurve, 'w')
        for row in tpf_lc:
            line = str(row['time']) + ' ' + str(row['flux'].value) + ' ' + str(row['flux_err'].value) + '\n'
            file.write(line)
        file.close()
    T.insert(INSERT, 'Lightcurve saved to ' + txtcurve + '\n')
    T.see(tk.END)


threshold_entry = tk.Spinbox(master=frame1, from_=1, to=200, increment=1,
                             command=plot_ffi_update, justify=CENTER, width=5)
threshold_entry.place(x=350, y=82)
threshold_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Threshold:', bg='grey')
threshold_label.place(x=280, y=80)

searchffi_button = ttk.Button(frame1, text='Search FFI', command=searchffi)
searchffi_button.place(x=10, y=80)

searchtpf_button = ttk.Button(frame1, text='Search TPF', command=searchtpf)
searchtpf_button.place(x=10, y=110)

plotffi_button = ttk.Button(frame1, text='Plot FFI/TPF', command=plot_ffi)
plotffi_button.place(x=200, y=80)

updateffi_button = ttk.Button(frame1, text='Update Plot', command=plot_ffi_update)
updateffi_button.place(x=405, y=80)

plotcurve_button = ttk.Button(frame1, text='Plot Curve', command=plot_curve)
plotcurve_button.place(x=405, y=36)

plotcurve_button = ttk.Button(frame1, text='Save Curve', command=save_curve)
plotcurve_button.place(x=405, y=6)

root.mainloop()
