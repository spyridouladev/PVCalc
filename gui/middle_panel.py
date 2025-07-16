import tkinter as tk
from tkinter import ttk
from services.power_production import get_power_production
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from services.utils import interpolate_timeseries
from services.logger import log
import matplotlib.dates as mdates
import numpy as np

class MiddlePanel(tk.Frame):
    def __init__(self, parent, update_callback=None):
        super().__init__(parent)
        self.update_callback = update_callback
        self.figure = None
        self.canvas = None

    def update_weather(self, weather_data=None):
        # Clear previous content
        for widget in self.winfo_children():
            widget.destroy()

        tz = None  # default timezone

        if isinstance(weather_data, tuple):
            df, pdc0_per_module, N_modules, tz, *rest = weather_data
        else:
            df = weather_data
            pdc0_per_module = None
            N_modules = None
            tz = None
        
        df = interpolate_timeseries(df, freq='15min')

        power_series = None
        if pdc0_per_module is not None and N_modules is not None:
            power_series = get_power_production(df, N_modules, pdc0_per_module)
        else:
            tk.Label(self, text="Missing module parameters for power calculation.", fg='red').pack()

        if power_series is not None:
            self.plot_power(power_series, tz)

        log(f"Power series:\n{power_series}")

        if self.update_callback:
            self.update_callback((df, pdc0_per_module, N_modules, tz, power_series))

    def plot_power(self, power_series, tz):
        # Clear previous widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create matplotlib figure and axis
        self.figure, ax = plt.subplots(figsize=(6, 4))  # figure size can be modest; canvas will stretch

        # Plot the power series
        ax.plot(power_series.index, power_series.values, marker='o', linestyle='-')
        ax.set_title('Power Production Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Power (watts)')
        ax.grid(True)

        # Set major ticks every hour on x-axis
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=tz))

        # Y-axis ticks every 50 watts
        min_power = np.floor(power_series.min() / 50) * 50
        max_power = np.ceil(power_series.max() / 50) * 50
        yticks = np.arange(min_power, max_power + 50, 50)
        ax.set_yticks(yticks)

        self.figure.autofmt_xdate()
        self.figure.tight_layout()

        # Embed the plot in Tkinter frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()

        # Make the canvas fill all available space vertically and horizontally
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Add a thin separator line immediately below the plot
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill=tk.X, pady=(2, 2))  # very small vertical padding, adjust if needed


    def set_update_callback(self, callback):
        # Register callback to send weather data 
        self.update_callback = callback