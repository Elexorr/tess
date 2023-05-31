import tkinter as tk
from tkinter import *
from tkinter import ttk
import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
from astroquery.simbad import Simbad
# from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import auxiliary as aux

root = tk.Tk()
root.title('TESS project')
root.resizable(True, False)

screen_x = root.winfo_screenwidth()
screen_y = root.winfo_screenheight()
print(screen_x, screen_y)

global window
window = tk.Canvas(master=root, width=screen_x-558, height=screen_y-50, bg='white')
window.grid(row=0, column=1, sticky='N')
frame1 = tk.Frame(master=root, width=558, height=screen_y-50, bg='grey')
frame1.grid(row=0, column=0, sticky='N')
# v=Scrollbar(root, orient='vertical')
# v.pack(side=RIGHT, fill='y')
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
author_label.place(x=5, y=35)
author_name = tk.StringVar()

global found_authors
found_authors = []
author_selection = ttk.Combobox(frame1, value=found_authors)
author_selection.place(x=65, y=35)

exptime_label = tk.Label(master=frame1, font=('Helvetica', 10), text='Exptime:', bg='grey')
exptime_label.place(x=5, y=62)
exptime = tk.IntVar()

global found_exptimes
found_exptimes = []
exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
exptime_selection.place(x=65, y=62)

sector_label = tk.Label(master=frame1, font=('Helvetica', 10), text='#:', bg='grey')
sector_label.place(x=270, y=35)
sector_num = tk.IntVar()
sector_num_entered = ttk.Entry(frame1, width=3, textvariable=sector_num)
sector_num_entered.place(x=300, y=35)


def basic_search():
    search_lcf = lk.search_lightcurve(obj_name.get())
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf)
    found_authors = aux.find_authors(search_lcf.author)
    global author_selection
    author_selection = ttk.Combobox(frame1, value=found_authors)
    author_selection.place(x=65, y=35)
    found_exptimes = aux.find_exptimes(search_lcf.exptime)
    global exptime_selection
    exptime_selection = ttk.Combobox(frame1, value=found_exptimes)
    exptime_selection.place(x=65, y=62)
    #print(search_lcf.exptime[0])
    T.see(tk.END)


basic_search_button = ttk.Button(frame1, text='Basic Search', command=basic_search)
basic_search_button.place(x=205, y=5)


def refined_search():
    search_lcf_refined = lk.search_lightcurve(obj_name.get(), author=str(author_selection.get()), exptime=exptime_selection.get())
    T.insert(INSERT, '\n')
    T.insert(INSERT, search_lcf_refined)
    T.see(tk.END)
    if len(search_lcf_refined.table) != 0:
        global lcf
        lcf = search_lcf_refined.download_all()


refined_search_button = ttk.Button(frame1, text='Refined Search', command=refined_search)
refined_search_button.place(x=300, y=5)


def curve_plot():
    global window
    window = tk.Canvas(master=root, width=screen_x - 558, height=screen_y - 50, bg='white')
    window.grid(row=0, column=1, sticky='N')
    x = lcf[sector_num.get()].time.value
    y = lcf[sector_num.get()].flux
    figx = (screen_x-558)/100
    figy = (figx * 0.5625)
    fig = plt.Figure(figsize=(figx, figy), dpi = 100)
    fig.add_subplot(111).plot(x, y, "ro")
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas._tkcanvas.pack()
    global plott


curve_plot_button = ttk.Button(frame1, text='Plot Curve', command=curve_plot)
curve_plot_button.place(x=400, y=5)


root.mainloop()