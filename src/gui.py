from tkinter import Frame, Canvas, BOTH
from tangram import BLOCKS

class GUI(Frame):

    def __init__(self):
        super().__init__()
        
        self.master.title('Tangram')
        self.master.geometry('700x700')
        self.pack(fill=BOTH, expand=1)

        self.init()
        self.mainloop()

    def init(self):
        canvas = Canvas(self)
        draw_blocks(canvas)
        canvas.pack(fill=BOTH, expand=1)

def draw_blocks(canvas):
    for i in range(len(BLOCKS)):
        canvas.create_polygon(
            BLOCKS[i].get_rotated_vertices((100, 100), BLOCKS[i].rotation),
            outline = '#000',
            fill = BLOCKS[i].color
        )
