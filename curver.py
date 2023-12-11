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
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

root=tk.Tk()
root.title('TESS FFI curver 0.1')
root.resizable(False, False)
frame1 = tk.Frame(master=root, width=520, height=506, bg='grey')
frame1.grid(row=0, column=0, sticky='N')
T = Text(master=frame1, height=12, width=60, bg='Light grey', bd=3, padx=10)
T.place(x=5, y=300)

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
    # window.destroy()
    # if 'canvas' in globals():
    #     canvas.destroy()
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
    kic_ph_resized = kic_phased.resize((500,375))
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
    window.update()
    window.mainloop()

find_tic_button = ttk.Button(frame1, text='Find TIC ID', command=find_tic)
find_tic_button.place(x=235, y=36)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='#:', bg='grey')
sector_label.place(x=100, y=80)
sector_num = tk.IntVar()
global found_sectors
found_sectors = []
sector_num = ttk.Combobox(frame1, value=found_sectors, width = 3)
sector_num.place(x=120, y=82)


def searchffi():
    global search_ffi, ffi_data
    search_ffi = lk.search_tesscut(obj_name_entered.get())
    # search_tpf = lk.search_targetpixelfile('V523 Cas')
    # search_lcf = lk.search_lightcurve('V523 Cas')
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_ffi)
    # T.update()
    # print(search_ffi)
    found_sectors = len(search_ffi)
    nums = []
    for i in range (0, found_sectors):
        nums.append(i)
    global sector_num
    sector_num = ttk.Combobox(frame1, value=nums, width=3)
    sector_num.insert(0, 0)
    sector_num.place(x=120, y=82)
    # ffi_data = search_ffi[1].download(cutout_size=21)

    # ffi_data.plot()


def plot_ffi():
    plt.close()
    global target_mask, ffi_plot, ffi_data, window, ax
    ffi_data = search_ffi[int(sector_num.get())].download(cutout_size=31)
    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
    n_target_pixels = target_mask.sum()
    print('Number of pixels:', n_target_pixels)
    fig, ax = plt.subplots()
    ffi_plot = ffi_data.plot(ax = ax, aperture_mask=target_mask, mask_color='r')
    # ffi_plot = ffi_data.plot(aperture_mask=target_mask, mask_color='r')
    # plt.show()

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    # cid = fig.canvas.mpl_connect('button_press_event', onclick)
    canvas._tkcanvas.pack()


def plot_ffi_update():
    global ffi_plot, ax
    plt.close()
    window = tk.Canvas(master=root, width=500, height=500, bg='white')
    window.grid(row=0, column=1, sticky='N')
    target_mask = ffi_data.create_threshold_mask(threshold=threshold_entry.get(), reference_pixel='center')
    # print('Number of pixels:', n_target_pixels)
    # ffi_plot = ffi_data.plot(aperture_mask=target_mask, mask_color='r')
    # ffi_plot.update()
    fig, ax = plt.subplots()
    ffi_plot = ffi_data.plot(ax=ax, aperture_mask=target_mask, mask_color='r')
    # ffi_data.plot(aperture_mask=target_mask, mask_color='r')

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    # cid = fig.canvas.mpl_connect('button_press_event', onclick)
    canvas._tkcanvas.pack()


def plot_curve():
    plt.close()
    ffi_lc = ffi_data.to_lightcurve(aperture_mask=target_mask)
    # print(ffi_lc)
    ffi_lc.plot(label="SAP FFI")
    plt.show()


threshold_entry = tk.Spinbox(master=frame1, from_=1, to=200, increment=1,
                          command=plot_ffi_update, justify=CENTER, width=5)
threshold_entry.place(x=300, y=82)

searchffi_button = ttk.Button(frame1, text='Search FFI', command=searchffi)
searchffi_button.place(x=10, y=80)

plotffi_button = ttk.Button(frame1, text='Plot FFI', command=plot_ffi)
plotffi_button.place(x=200, y=80)

plotcurve_button = ttk.Button(frame1, text='Plot Curve', command=plot_curve)
plotcurve_button.place(x=400, y=80)


root.mainloop()