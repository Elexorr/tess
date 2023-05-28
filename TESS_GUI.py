import tkinter as tk
from tkinter import *
from tkinter import ttk

root = tk.Tk()
root.title('TESS project')
root.resizable(True, False)

screen_x = root.winfo_screenwidth()
screen_y = root.winfo_screenheight()

window = tk.Canvas(master=root, width=screen_x-500, height=screen_y-70, bg='white')
window.grid(row=0, column=1, sticky='E')
frame1 = tk.Frame(master=root, width=500, height=screen_y-70, bg='grey')
frame1.grid(row=0, column=0, sticky='W')
T = Text(master=frame1, height=13, width=58, bg='Light grey', bd=3, padx=10)
T.place(x=5, y=screen_y-305)
T.insert(END, 'Hello TESS')


root.mainloop()