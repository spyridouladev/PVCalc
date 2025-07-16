import tkinter as tk
from tkinter import ttk
from gui.left_panel import LeftPanel
from gui.middle_panel import MiddlePanel
from gui.right_panel import RightPanel
import logging

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.state('zoomed')
        self.title("PVCalc")

        # Create the main horizontal paned window
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create the left panel
        self.left_frame = LeftPanel(self, update_callback=self.update_middle_panel)
        self.paned_window.add(self.left_frame, minsize=200)  # minsize is optional

        # Create the middle panel
        self.middle_frame = MiddlePanel(self, update_callback=self.update_right_panel)
        self.paned_window.add(self.middle_frame, minsize=400)

        # Create the right panel
        self.right_frame = RightPanel(self)
        self.paned_window.add(self.right_frame, minsize=200)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_middle_panel(self, weather_data):
        self.middle_frame.update_weather(weather_data)

    def update_right_panel(self, weather_data):
        self.right_frame.update_weather(weather_data)

    def on_closing(self):
        logging.shutdown()
        self.quit()
        self.destroy()
