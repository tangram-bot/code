from pkgutil import extend_path
from threading import Thread

from tkinter import *
from tkinter import ttk

from numpy import cos, pi, sin


TRIANGLE_POINTS = [(0, 0), (40, 0), (0, 40)]
RECT_POINTS = [(0, 0), (40, 0), (40, 40), (0, 40)]
RECT_POINTS = [(0, 0), (40, 0), (40, 40), (0, 40)]
PARALLELOGRAM_POINTS = [(0, 0), (40, 0), (60, 20), (20, 20)]
CENTER_POINT_RADIUS = 2

def create_window(name):
    root = Tk()
    root.title('CYK')
    root.geometry('700x700')

    frm = ttk.Frame(root, padding=10)
    
    
    frm.grid()
    
    # ttk.Label(frm, text="Hello World!").grid(column=0, row=0)

    c = Canvas(master=frm, bg="white")
    c.pack(anchor=CENTER, expand=True)

    draw_triangle(35, 35, 0, c)
    draw_rect(60, 60, pi/4, c)
    draw_parallelogram(100, 200, 0, c)

    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

    root.mainloop()


def center_offset(points):
    sum_x = 0
    sum_y = 0

    for p in points:
        sum_x += p[0]
        sum_y += p[1]
    
    return sum_x / len(points), sum_y / len(points)


def draw_points(input_points, x, y, rot, c):

    offset_x, offset_y = center_offset(input_points)
    points_around_origin = []
    rotated_points = []
    points = []

    # move points around origin
    for p in input_points:
        points_around_origin.append((p[0] - offset_x, p[1] - offset_y))

    #rotate points around origin
    for p in points_around_origin:
        x2 = p[0] * cos(rot) - p[1] * sin(rot)
        y2 = p[0] * sin(rot) + p[1] * cos(rot)
        rotated_points.append((x2, y2))

    # move points to x and y
    for p in rotated_points:
        points.append((p[0] + x, p[1] + y))

    print(x, y)
    c.create_polygon(points,           outline='#000', fill='#f00')
    c.create_oval(
        x - CENTER_POINT_RADIUS, 
        y - CENTER_POINT_RADIUS, 
        x + CENTER_POINT_RADIUS, 
        y + CENTER_POINT_RADIUS, outline="#000", fill="#00f")


def draw_rect(x, y, rot, c):
    draw_points(RECT_POINTS, x, y, rot, c)


def draw_triangle(x, y, rot, c):
    draw_points(TRIANGLE_POINTS, x, y, rot, c)


def draw_parallelogram(x, y, rot, c):
    draw_points(PARALLELOGRAM_POINTS, x, y, rot, c)


t = Thread(target=create_window, args=(1,))
t.start()
