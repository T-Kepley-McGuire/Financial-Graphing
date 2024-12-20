import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk

root = Tk.Tk()
root.wm_title("Embedding in TK")

# x = 1

# f = Figure(figsize=(5, 4), dpi=100)
# a = f.add_subplot(111)
# t = arange(0.0, 3.0, 0.01)
# s = sin(x*2*pi*t)

# a.plot(t, s)
def plot(x):
    f = Figure(figsize=(5, 4), dpi=100)
    a = f.add_subplot(111)
    t = arange(0.0, 3.0, 0.01)
    s = sin(x*2*pi*t)
    
    a.plot(t, s)
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

plot(1)

# a tk.DrawingArea




# def on_key_event(event):
#     print('you pressed %s' % event.key)
#     key_press_handler(event, canvas, toolbar)

# canvas.mpl_connect('key_press_event', on_key_event)



def change_pressed():
    plot(4)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

button = Tk.Button(master=root, text='Quit', command=_quit)
slider = Tk.Button(master=root, text='change', command=change_pressed)
button.pack(side=Tk.BOTTOM)
slider.pack(side=Tk.BOTTOM)

Tk.mainloop()
# If you put root.destroy() here, it will cause an error if
# the window is closed with the window manager.