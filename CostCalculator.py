import mplcursors as m
import pandas as pd
from scipy import optimize as o
import math
import sys
from collections.abc import Callable
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from numpy import arange, sin, pi, where
import matplotlib
from matplotlib.ticker import FuncFormatter
matplotlib.use('TkAgg')

if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
    from tkinter import DoubleVar

# Initialize Tkinter window
root = Tk.Tk()
root.wm_title("Embedding in TK")

hv = pd.read_csv('average-home-value.csv')
rp = pd.read_csv('average-rent.csv')

v = {
    "Home Value": {
        "variable": DoubleVar(value=hv['Price'].mean()),
        # Lower bound for rent in smaller markets
        "start": max(0, hv["Price"].mean() - 2 * hv["Price"].std()),
        # Upper bound for a high-end home price
        "stop": hv["Price"].mean() + 2 * hv["Price"].std(),
        "unit": "Dollars"
    },
    "Down Payment": {
        "variable": DoubleVar(value=0.2),  # hv["Price"].mean() * 0.2),
        "start": 0,           # Lower bound for no down payment
        # hv["Price"].max() * 0.2,       # Upper bound assuming a large down payment on a high-value home
        "stop": 1,
        "unit": "Percentage"
    },
    "Interest Rate": {
        "variable": DoubleVar(value=0.07),
        "start": 0.01,        # Lower bound of 1% interest rate
        "stop": 0.20,         # Upper bound of 20% for high interest rates
        "unit": "Percentage"
    },
    "Loan Term (Years)": {
        "variable": DoubleVar(value=30),
        "start": 5,           # Lower bound for a short-term loan
        "stop": 60,           # Upper bound for an extended-term loan
        "unit": "Unitless"
    },
    "Yearly Tax Rate": {
        "variable": DoubleVar(value=0.01),
        "start": 0,           # Lower bound of 0% for tax rates
        "stop": 0.05,         # Upper bound of 5% for tax rates
        "unit": "Percentage"
    },
    "Yearly Maintenance": {
        "variable": DoubleVar(value=6000),
        "start": 0,           # Lower bound for minimal maintenance costs
        "stop": 20000,        # Upper bound for larger maintenance costs on large properties
        "unit": "Dollars"
    },
    "Monthly Rent": {
        "variable": DoubleVar(value=rp['Price'].mean()),
        # Lower bound for rent in smaller markets
        "start": max(0, rp["Price"].mean() - 2 * rp["Price"].std()),
        # Upper bound for high-demand areas
        "stop": rp["Price"].mean() + 2 * rp["Price"].std(),
        "unit": "Dollars"
    }
}


fig = Figure(figsize=(7, 5), dpi=100)
allPlots = fig.add_subplot(111)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)


def y_axis_formatter(x, pos):
    return f'${x/1000:,.0f}k'


def x_axis_formatter(x, pos):
    return f'{int(x)}'


def format_annotation(x, y, m):
    return f"Years: {x:,.0f}\nTotal: ${(y//10)*10:,}\nMonthly: ${m:,.0f}"


allPlots.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
allPlots.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))

allPlots.set_xlabel('Years')
allPlots.set_ylabel('Expendature')
allPlots.set_title('Projected Costs of Housing')
allPlots.legend()


def updatePlot():
    allPlots.clear()
    allPlots.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    allPlots.xaxis.set_major_formatter(FuncFormatter(x_axis_formatter))

    allPlots.set_xlabel('Years')
    allPlots.set_ylabel('Expendature')
    allPlots.set_title('Projected Costs of Housing')

    # Get the frequency and amplitude from the slider and entry
    homeValue = v["Home Value"]["variable"].get()
    downPayment = v["Down Payment"]["variable"].get() * homeValue
    principal = homeValue - downPayment
    interestRate = v["Interest Rate"]["variable"].get()
    loanTerm = v["Loan Term (Years)"]["variable"].get()
    numPayments = loanTerm * 12.0
    monthlyInterest = interestRate / 12.0

    # Calculate monthly payment
    monthlyPayment = monthlyInterest * principal * \
        (1 + monthlyInterest)**numPayments / \
        ((1 + monthlyInterest)**numPayments - 1)

    taxRate = v["Yearly Tax Rate"]["variable"].get()
    maintenance = v["Yearly Maintenance"]["variable"].get()
    sunkYearly = maintenance + homeValue * taxRate

    monthlyRent = v["Monthly Rent"]["variable"].get()

    def calcOwnerPaid(t):
        return where(t > loanTerm, 12 * monthlyPayment * loanTerm + sunkYearly *
                     t + downPayment, 12 * monthlyPayment * t + sunkYearly * t + downPayment)

    def calcOwnerSunk(t):
        return where(
            t > loanTerm,
            (principal * monthlyInterest - monthlyPayment) *
            ((1 + monthlyInterest) ** (12 * loanTerm) - 1) / monthlyInterest
            + 12 * monthlyPayment * loanTerm + sunkYearly * t,
            (principal * monthlyInterest - monthlyPayment) *
            ((1 + monthlyInterest) ** (12 * t) - 1) / monthlyInterest
            + 12 * monthlyPayment * t + sunkYearly * t
        )

    def calcRenterPaid(t):
        return t * 12 * monthlyRent

    def rentingCrossOwnerPaid(t):
        return calcRenterPaid(t) - calcOwnerPaid(t)

    def rentingCrossOwnerSunk(t):
        return calcRenterPaid(t) - calcOwnerSunk(t)

    t = arange(0, 60, 1)

    ownerPaid = calcOwnerPaid(t)
    ownerSunk = calcOwnerSunk(t)
    renterPaid = calcRenterPaid(t)

    # Redraw the plot with the new sine wave
    ohp = allPlots.plot(t, ownerPaid, label="Owner has paid")
    ohs = allPlots.plot(t, ownerSunk, label="Owner has sunk")
    rhs = allPlots.plot(t, renterPaid, label="Renter has sunk")


    
    ohpc = m.cursor(ohp)
    ohpc.connect("add", lambda sel: sel.annotation.set_text(f"Owner has paid:\n{
                 format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcOwnerPaid(sel.annotation.xy[0] + 1) - calcOwnerPaid(sel.annotation.xy[0]))/12)}"))
    ohsc = m.cursor(ohs)
    ohsc.connect("add", lambda sel: sel.annotation.set_text(f"Owner has sunk:\n{
                 format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcOwnerSunk(sel.annotation.xy[0] + 1) - calcOwnerSunk(sel.annotation.xy[0]))/12)}"))
    rhsc = m.cursor(rhs, multiple=False)
    rhsc.connect("add", lambda sel: sel.annotation.set_text(f"Renter has sunk:\n{
                 format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcRenterPaid(sel.annotation.xy[0] + 1) - calcRenterPaid(sel.annotation.xy[0]))/12)}"))
#     ohpc = m.cursor(ohp)
#     ohpc.connect("add", lambda sel: [
#         clear_active_annotation(),
#         setattr(sel.annotation, "text", f"Owner has paid:\n{format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcOwnerPaid(sel.annotation.xy[0] + 1) - calcOwnerPaid(sel.annotation.xy[0]))/12)}"),
#         setattr(sel.annotation, "visible", True),
#         setattr(globals(), "active_annotation", sel.annotation)
#     ])

#     ohsc = m.cursor(ohs)
#     ohsc.connect("add", lambda sel: [
#         clear_active_annotation(),
#         setattr(sel.annotation, "text", f"Owner has sunk:\n{format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcOwnerSunk(sel.annotation.xy[0] + 1) - calcOwnerSunk(sel.annotation.xy[0]))/12)}"),
#         setattr(sel.annotation, "visible", True),
#         setattr(globals(), "active_annotation", sel.annotation)
#     ])

#     rhsc = m.cursor(rhs)
#     rhsc.connect("add", lambda sel: [
#         clear_active_annotation(),
#         setattr(sel.annotation, "text", f"Renter has sunk:\n{format_annotation(sel.annotation.xy[0], sel.annotation.xy[1], (calcRenterPaid(sel.annotation.xy[0] + 1) - calcRenterPaid(sel.annotation.xy[0]))/12)}"),
#         setattr(sel.annotation, "visible", True),
#         setattr(globals(), "active_annotation", sel.annotation)
#       ])


    allPlots.fill_between(t, ownerPaid, ownerSunk, alpha=0.2, label="Equity")
    try:
        rentingExceedsPaid = o.bisect(
            rentingCrossOwnerPaid, 1, v["Loan Term (Years)"]["stop"])
        allPlots.plot(rentingExceedsPaid, calcRenterPaid(
            rentingExceedsPaid), 'ro')
    except ValueError:
        print("No zeros found on this interval")
    try:
        rentingExceedsSunk = o.bisect(
            rentingCrossOwnerSunk, 1, v["Loan Term (Years)"]["stop"])
        allPlots.plot(rentingExceedsSunk, calcRenterPaid(
            rentingExceedsSunk), 'ro')
    except ValueError:
        print("No zeros found on this interval")

    allPlots.legend(shadow=True)

    canvas.draw()


class LabeledEntry:
    def __init__(self, root, label_text, tracer, start, stop, unit="Unitless"):
        """
        Initializes a labeled entry with a linked slider and entry box.

        Parameters:
            root (Tk.Tk): The root tkinter window.
            label_text (str): Text for the label.
            tracer (Tk.DoubleVar): A Tkinter DoubleVar to hold the value.
            start (float): The starting value (lower bound) for the slider.
            stop (float): The stopping value (upper bound) for the slider.
            unit (str): Unit type - "Dollars", "Unitless", "Percentage".
        """
        self.tracer = tracer
        self.unit = unit

        # Create a frame to hold the label, entry, and slider together
        self.frame = Tk.Frame(root)
        self.frame.pack(side=Tk.TOP, padx=5, pady=5)

        # Create the label
        self.label = Tk.Label(self.frame, text=label_text)
        self.label.pack(side=Tk.LEFT)

        # Create entry and slider
        self.entryDV = DoubleVar()
        self.entry = Tk.Entry(self.frame, textvariable=self.entryDV, width=10)
        self.entry.bind("<Return>", self.updateFromEntry)
        self.entry.bind("<FocusOut>", self.updateFromEntry)

        self.slider = Tk.Scale(
            self.frame, from_=start, to=stop, showvalue=False,
            resolution=self.calculateResolution(stop),
            orient=Tk.HORIZONTAL, command=self.updateFromSlider
        )
        self.slider.set(tracer.get())
        self.slider.pack(side=Tk.RIGHT)
        self.entry.pack(side=Tk.RIGHT, expand=True, fill=Tk.X)

        # Initial update to format display
        self.updateEntryDisplay()

    def calculateResolution(self, x):
        """Calculates the slider resolution for 3 significant digits."""
        if x == 0:
            return 0.001  # Arbitrary small step for zero case
        if 10 < x < 1000:
            return 1
        magnitude = 10 ** math.floor(math.log10(abs(x)))
        return magnitude / 100

    def formatValue(self, value):
        """Formats the value based on the unit type."""
        if self.unit == "Dollars":
            return f"${int(value):,}"
        elif self.unit == "Unitless":
            return f"{int(value)}"
        elif self.unit == "Percentage":
            return f"{value * 100:.2f}%"
        else:
            return str(value)  # Default case if unit type is not recognized

    def updateEntryDisplay(self):
        """Updates the entry display with the formatted value."""
        formatted_value = self.formatValue(self.tracer.get())
        self.entry.delete(0, Tk.END)
        self.entry.insert(0, formatted_value)

    def updateFromEntry(self, event):
        """Updates the slider based on the entry input."""
        try:
            value = float(self.entryDV.get())
            self.tracer.set(value)
            self.slider.set(value)
            self.updateEntryDisplay()  # Reformat after updating from entry
        except (ValueError, Tk.TclError):
            pass  # Ignore invalid input

    def updateFromSlider(self, value):
        """Updates the entry display when the slider is moved."""
        self.tracer.set(float(value))
        self.updateEntryDisplay()


# v["amplitude"].trace_add(mode="write", callback=lambda v, i, m: updatePlot())
# v['frequency'].trace_add(mode="write", callback=lambda v, i, m: updatePlot())

# e1 = createLabeledEntry(root, "Amplitude", 1, v["amplitude"])
# e2 = createLabeledEntry(root, "Frequency", 1, v["frequency"])


for key, params in v.items():
    v[key]["variable"].trace_add(
        mode="write", callback=lambda v, i, m: updatePlot())
    print(f"{key}, {v[key]['variable'].get()}")
    labeled_entry = LabeledEntry(
        root, key, v[key]["variable"],
        start=v[key]["start"],
        stop=v[key]["stop"],
        unit=v[key]["unit"]
    )


updatePlot()
root.mainloop()
