from pkgutil import extend_path
from threading import Thread

from tkinter import *
from tkinter import ttk


def create_window(name):
    root = Tk()
    root.title('CYK')
    root.geometry('700x700')

    frm = ttk.Frame(root, padding=10)
    
    
    frm.grid()
    
    # ttk.Label(frm, text="Hello World!").grid(column=0, row=0)

    c = Canvas(master=frm)

    c.create_polygon(((10, 10), (10, 20), (30, 30), (20, 10)), outline='#000', fill='#f00')


    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    root.mainloop()


t = Thread(target=create_window, args=(1,))
t.start()
