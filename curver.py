import tkinter as tk
from tkinter import *
from tkinter import ttk
import numpy as np
import csv
import requests
from PIL import Image,ImageTk
from astroquery.mast import Catalogs
import lightkurve as lk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

root=tk.Tk()
root.title('TESS FFI curver 0.1')
root.resizable(False, False)
root.configure(bg='white')
frame1 = tk.Frame(master=root, width=520, height=506, bg='grey')
frame1.grid(row=0, column=0, sticky='N')
T = Text(master=frame1, height=12, width=60, bg='Light grey', bd=3, padx=10)
T.place(x=5, y=300)
# window = tk.Canvas(width=0, height=0, bg='Light grey')
# window.grid(row=0, column=1, sticky='N')

kic_ids = []
with open('kepler.csv', newline='') as csvfile:
    rowz = csv.DictReader(csvfile)
    for row in rowz:
        kic_ids.append(row['#KIC'])
    kic_ids = sorted(kic_ids)

kic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='KIC ID:', bg='grey')
kic_label.place(x=5, y=38)
kic_id_input = ttk.Combobox(frame1, value=kic_ids, width = 20)
kic_id_input.place(x=85, y=38)

obj_name = tk.StringVar()
tic_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Star/TIC ID:', bg='grey')
tic_label.place(x=5, y=10)
obj_name_entered = ttk.Entry(frame1, width=20, textvariable=obj_name)
obj_name_entered.place(x=85, y=10)


def find_tic():
    global lcf
    global period
    global t0
    global window

    for widget in root.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()

    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')

    kic_num = kic_id_input.get()

    with open('kepler.csv', newline='') as csvfile:
        rowz = csv.DictReader(csvfile)
        for row in rowz:
            if kic_id_input.get() == row['#KIC']:
                period = row['period']
                t0 = row['bjd0']
        # print(period)
        # print(t0)
        period = float(period)
        t0 = float(t0)
        print(period)
        print(t0)

    kic_id = 'KIC '+ kic_num
    if len(kic_num) == 7:  #
        url = "http://keplerebs.villanova.edu/includes/" + "0" + kic_num + ".00.lc.pf.png"  # Vytvori url na stiahnutie
    else:  # obrazku dtr krivky
        url = "http://keplerebs.villanova.edu/includes/" + kic_num + ".00.lc.pf.png"  #
    data = requests.get(url).content  # Stiahne obrazok dtr krivky
    file_name = "temp.png"  # Ulozi obrazok dtr krivky
    f = open("temp.png", 'wb')  # v prislusnom podadresari
    f.write(data)  #
    f.close()  #
    kic_phased = Image.open('temp.png')
    kic_ph_resized = kic_phased.resize((520,375))
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
    window.create_image(250, 188, image=img)
    window.create_text(250, 400, text = kic_id + '\n' + 'Period: ' + str(period) + '\n' + 'M0: '+ str(t0), font=('Times 10 bold'), justify='left')
    # # window.create_text(270, 870, text = 'Period: '+ str(period), font=('Times 10 bold'))
    # # window.create_text(270, 890, text= 'M0: '+ str(t0), font=('Times 10 bold'))
    # window.update()
    window.mainloop()

find_tic_button = ttk.Button(frame1, text='Find TIC ID', command=find_tic)
find_tic_button.place(x=235, y=36)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Sector #:', bg='grey')
sector_label.place(x=90, y=80)
sector_num = tk.IntVar()
global found_sectors
found_sectors = []
sector_num = ttk.Combobox(frame1, value=found_sectors, justify=CENTER, width = 3)
sector_num.place(x=150, y=82)
size_entry = tk.Spinbox(master=frame1, from_=11, to=201, increment=10, justify=CENTER, width=5)
size_entry.place(x=145, y=112)
size_entry_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Size:', bg='grey')
size_entry_label.place(x=90, y=110)


def searchffi():
    global search_ffi, ffi_data
    search_ffi = lk.search_tesscut(obj_name_entered.get())
    # search_tpf = lk.search_targetpixelfile(obj_name_entered.get())
    # search_lcf = lk.search_lightcurve('V523 Cas')
    T.insert(INSERT, 'SearchResult for ' + obj_name_entered.get() + '\n')
    T.insert(INSERT, search_ffi)
    T.insert(INSERT, '\n')
    T.insert(INSERT, '\n')
    T.see(tk.END)
    # T.update()
    # print(search_ffi)
    found_sectors = len(search_ffi)
    nums = []
    for i in range (0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=150, y=82)
    # ffi_data = search_ffi[1].download(cutout_size=21)

    # ffi_data.plot()

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
    plt.close()
    global search_ffi, target_mask, ffi_plot, ffi_data, window, ax, plotwidth, plotheight
    ffi_data = search_ffi[int(sector_num.get())].download(cutout_size=int(size_entry.get()))
    rows = cutout_size=int(size_entry.get())
    # ffi_data.show_properties()
    plotwidth = ffi_data.column - 0.5
    plotheight = ffi_data.row - 0.5
    # print(plotwidth, plotheight)
    # print(ffi_data)

    dec_output.delete(0, END)
    dec_output.insert(0, str(round(ffi_data.dec, 6)))
    ra_output.delete(0, END)
    ra_output.insert(0, str(round(ffi_data.ra, 6)))

    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
    fig, ax = plt.subplots()
    # ffi_plot = ffi_data.plot(ax = ax, aperture_mask=target_mask, mask_color='r')
    ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color='r')
    plt.close()
    # print(target_mask)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, window)
    # toolbar.update()
    canvas._tkcanvas.pack()


def plot_ffi_update():
    global ffi_plot, ax
    global target_mask
    global window
    plt.close()

    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
    fig, ax = plt.subplots()
    ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color='r')

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, window)
    # toolbar.update()
    canvas._tkcanvas.pack()


def makeownmask():
    global target_mask
    global window
    plt.close()

    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    target_mask = ffi_data.create_threshold_mask(threshold=1000, reference_pixel='center')
    # print(target_mask)
    fig, ax = plt.subplots()
    ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color='#0000FF')
    cid = plt.gcf().canvas.mpl_connect('button_press_event', setmaskpixel)
    canvas = FigureCanvasTkAgg(fig, master=window)
    # canvas.draw()
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, window)
    # toolbar.update()
    canvas._tkcanvas.pack()


makeownmask_button = ttk.Button(frame1, text='Set Mask', command=makeownmask)
makeownmask_button.place(x=200, y=110)

def setmaskpixel(event):
    global target_mask
    global window
    ix, iy = event.xdata, event.ydata
    # print(f'x = {ix}, y = {iy}')
    mask_y = int((ix - plotwidth)//1)
    mask_x = int((iy - plotheight)//1)
    # print(mask_x, mask_y)
    # print(target_mask[mask_x, mask_y])
    if target_mask[mask_x, mask_y] == False:
        target_mask[mask_x, mask_y] = True
    else:
        target_mask[mask_x, mask_y] = False
    plt.close()

    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    fig, ax = plt.subplots()
    ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color='#0000FF')
    cid = plt.gcf().canvas.mpl_connect('button_press_event', setmaskpixel)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    # canvas.get_tk_widget().pack()
    # toolbar = NavigationToolbar2Tk(canvas, window)
    # toolbar.update()
    canvas._tkcanvas.pack()


def plot_curve():
    global ffi_lc
    plt.close()
    # print(target_mask)
    ffi_lc = ffi_data.to_lightcurve(aperture_mask=target_mask)
    ffi_lc.plot(label="SAP FFI")
    plt.show()

def save_curve():
    # global ffi_lc
    txtcurve = str(obj_name.get()) + '_ffi.txt'
    file = open(txtcurve, 'w')
    print(ffi_lc)
    # fluxcoef = int(exptime_selection.get())/1800
    for row in ffi_lc:
        line = str(row['time']) + ' ' + str(row['flux'].value) + ' ' + str(row['flux_err'].value) + '\n'
        file.write(line)
    file.close()


threshold_entry = tk.Spinbox(master=frame1, from_=1, to=200, increment=1,
                          command=plot_ffi_update, justify=CENTER, width=5)
threshold_entry.place(x=350, y=82)
threshold_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Threshold:', bg='grey')
threshold_label.place(x=280, y=80)

searchffi_button = ttk.Button(frame1, text='Search FFI', command=searchffi)
searchffi_button.place(x=10, y=80)

plotffi_button = ttk.Button(frame1, text='Plot FFI', command=plot_ffi)
plotffi_button.place(x=200, y=80)

updateffi_button = ttk.Button(frame1, text='Update FFI', command=plot_ffi_update)
updateffi_button.place(x=405, y=80)

plotcurve_button = ttk.Button(frame1, text='Plot Curve', command=plot_curve)
plotcurve_button.place(x=405, y=36)

plotcurve_button = ttk.Button(frame1, text='Save Curve', command=save_curve)
plotcurve_button.place(x=405, y=6)


root.mainloop()