import tkinter as tk
from tkinter import *
from tkinter import ttk
import os
import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
from astroquery.simbad import Simbad
# from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import auxiliary as aux
from astroquery.mast import Catalogs
import csv

root = tk.Tk()
root.title('TESS project')
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
    #print(search_lcf.exptime[0])
    T.see(tk.END)


basic_search_button = ttk.Button(frame1, text='  Basic Search  ', command=basic_search)
basic_search_button.place(x=220, y=5)


def refined_search():
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


def curve_plot():
    global window
    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')
    x = lcf[int(sector_num.get())].time.value
    y = lcf[int(sector_num.get())].flux
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
    global plott


def crossid():
    T2 = Text(master=window, height=50, width=165, bg='Light grey', bd=3, padx=10)
    T2.place(x=5, y=5)
    with open('kepler.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        os.mkdir(path='crossid')
        num = 0
        exc = 0
        for row in reader:
            num = num + 1
            target_name = "KIC "+row['#KIC']
            os.mkdir(path='crossid/'+target_name)
            search_radius_deg = 0.001
            search_result = lk.search_lightcurve(target_name, author='Kepler')
            lc_collection = search_result.download_all()
            # T2.insert(INSERT, lc_collection)
            # T2.insert(INSERT, '\n')
            i = 0
            for lc in lc_collection:
                filename = target_name+'_'+str(i)+'.csv'
                # lc.to_csv(path_or_buf=target_name/target_name+'_'+str(i)+'.csv')
                lc.to_csv(path_or_buf='crossid/'+target_name+'/'+filename)
                i=i+1
            # for lc in lc_collection:
            #     lc.to_csv(path_or_buf='test')
            # lc_collection = lc_collection.remove_nans().remove_outliers()
            # lc_collection.to_fits(path=target_name, overwrite=True)

            catalogTIC = Catalogs.query_object(target_name, radius=search_radius_deg, catalog="TIC")
            try:
                where_closest = np.argmin(catalogTIC['dstArcSec'])
            except:
                print(num, row['#KIC'], 'no TIC', row['period'], row['bjd0'])
                exc = exc + 1
            # print(catalogTIC['ID'][where_closest])
            # print("Closest TIC ID to %s: TIC %s, separation of %f arcsec. and a TESS mag. of %f" %
            #       (target_name, catalogTIC['ID'][where_closest], catalogTIC['dstArcSec'][where_closest],
            #        catalogTIC['Tmag'][where_closest]))
            else:
                tess_target_name = 'TIC '+str(catalogTIC['ID'][where_closest])
                search_result = lk.search_lightcurve(tess_target_name)
                lc_collection = search_result.download_all()
                # T2.insert(INSERT, lc_collection)
                # T2.insert(INSERT, '\n')
                i = 0
                for lc in lc_collection:
                    filename = tess_target_name + '_' + str(i) + '.csv'
                    # lc.to_csv(path_or_buf=target_name/target_name+'_'+str(i)+'.csv')
                    lc.to_csv(path_or_buf='crossid/'+target_name + '/' + filename)
                    i = i + 1
                # print(num, row['#KIC'], catalogTIC['ID'][where_closest], row['period'], row['bjd0'])
                newrow = str(num) + ' ' + target_name + ' ' + tess_target_name + ' period:' + str(row['period']) + ' m0:' + str(row['bjd0'] + ' OK')
                T2.insert(INSERT, newrow)
                T2.insert(INSERT, '\n')
                # T2.insert(INSERT, lc_collection)
                # T2.insert(INSERT, '\n')
                file = open('crossid/' + target_name + '/' + 'info.txt', "w")
                file.write(target_name + '\n')
                file.write(tess_target_name + '\n')
                file.write('period:' + str(row['period']) + '\n')
                file.write('m0:' + str(row['bjd0']) + '\n')
                file.close()
            T2.see(tk.END)
            T2.update()
        # print(exc)
    #       #print(row['KIC'], row['period'])


crossid_button = ttk.Button(frame1, text='  Crossidentification  ', command=crossid)
crossid_button.place(x=8, y=100)


curve_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
curve_plot_button.place(x=400, y=5)


root.mainloop()