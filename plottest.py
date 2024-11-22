import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from collections.abc import Callable

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
    from tkinter import DoubleVar

# Initialize Tkinter window
root = Tk.Tk()
root.wm_title("Embedding in TK")

enteredVars = {
    "amplitude": 0,
    "frequency": 0
    }

def updateEnteredVars(key, value):
    enteredVars[key] = value

    update_plot()

# Define a function to update the plot when the slider or amplitude entry changes
def update_plot():
    # Clear the previous plot
    ax.clear()

    # Get the frequency and amplitude from the slider and entry
    frequency = enteredVars["frequency"] #float(slider_frequency.get())
    # try:
    #     amplitude = float(entry_amplitude.get())
    # except ValueError:
    #     amplitude = 1.0  # Default value if input is invalid
    amplitude = enteredVars["amplitude"]
    # Generate a new sine wave with the updated frequency and amplitude
    t = arange(0.0, 2*pi, 0.01)
    y = amplitude * sin(frequency * t)

    # Redraw the plot with the new sine wave
    ax.plot(t, y)
    ax.set_title(f'Sine Wave: Amplitude = {amplitude}, Frequency = {frequency} Hz')

    # Update the canvas
    canvas.draw()

def createDoubleEntry(root: Tk.Tk, label: str, default: float, _callback: Callable[[], None]) -> Tk.Entry:

    dv = DoubleVar()
    dv.trace_add(mode="write", callback=lambda v, i, m: _callback())
    newEntry = Tk.Entry(root, textvariable=dv)
    newEntry.insert(0, default)
    newEntry.pack(side=Tk.BOTTOM, fill=Tk.X)

    newLabel = Tk.Label(root, text=label)
    newLabel.pack(side=Tk.BOTTOM)
    return newEntry

# Create a figure for plotting
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)

# Initial plot with frequency 1 Hz and amplitude 1
t = arange(0.0, 2*pi, 0.01)
y = sin(t)
ax.plot(t, y)
ax.set_title('Sine Wave with Frequency: 1 Hz, Amplitude: 1')

# Create a canvas to embed the figure in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# Add a navigation toolbar
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# Create a slider to adjust the frequency
slider_frequency = Tk.Scale(root, from_=0.1, to_=10.0, orient=Tk.HORIZONTAL, resolution=0.1, label="Frequency (Hz)", command=updateEnteredVars("frequency", ))
slider_frequency.set(1)  # Set initial value to 1 Hz
slider_frequency.pack(side=Tk.BOTTOM, fill=Tk.X)


entry_amplitude = createDoubleEntry(root, "Amplitude", 1, update_plot)


# Start the Tkinter main loop
root.mainloop()



