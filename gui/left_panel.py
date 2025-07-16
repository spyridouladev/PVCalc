import tkinter as tk
from tkinter import ttk
from services.file_data import read_locations_csv
from services.file_data import get_resource_path
from services.get_weather import get_weather_data
from services.mytimezone import get_timezone
from services.utils import format_value
from services.utils import get_closest_value
from services.logger import log
import asyncio
from datetime import datetime
import pytz
import pandas as pd 
from PIL import Image, ImageTk

class LeftPanel(tk.Frame):
    def __init__(self, parent, update_callback=None):
        super().__init__(parent)
        self.update_callback = update_callback
        self.locations_csv_path = get_resource_path("resources/worldcities.csv")
        self.countries, self.country_city_map = read_locations_csv(self.locations_csv_path)

        self.selected_country = tk.StringVar()
        self.selected_city = tk.StringVar()

        self.selected_rd = tk.IntVar()

        self.tracking_mode = tk.StringVar(value="fixed")  # Added for mode selection

        self.build_ui()
        self.add_logo()

    def build_ui(self):
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10, padx=10, fill='x')

        # Country selector (full width)
        self.country_combo = ttk.Combobox(input_frame, values=self.countries, textvariable=self.selected_country)
        self.country_combo.pack(pady=10, fill='x')
        self.country_combo.set("Select a country")
        self.country_combo.bind("<<ComboboxSelected>>", self.update_cities)

        # City selector (full width)
        self.city_combo = ttk.Combobox(input_frame, textvariable=self.selected_city)
        self.city_combo.pack(pady=10, fill='x')

        # Panel data label on its own line (left aligned)
        self.panel_data = tk.Label(input_frame, text="Input Panel Data")
        self.panel_data.pack(anchor='w', pady=(10, 0))

        # RD input and unit side-by-side inside a frame
        # Dust surface density is grams per square meter (g/m²)
        rd_frame = tk.Frame(input_frame)
        rd_frame.pack(pady=5, anchor='w')

        rd_label = ttk.Label(rd_frame, text="Dust surface density:")
        rd_label.pack(side='left', padx=(0, 5))  # label on left with some space to the right

        self.rd_text_box = tk.Text(rd_frame, height=2, width=10)
        self.rd_text_box.pack(side='left')

        unit_label_g_m2 = ttk.Label(rd_frame, text="g/m²")
        unit_label_g_m2.pack(side='left', padx=(5, 0))

        # Input height of torque above ground
        height_frame = tk.Frame(input_frame)
        height_frame.pack(pady=5, anchor='w')

        height_label = ttk.Label(height_frame, text="Height of torque above ground:")
        height_label.pack(side='left', padx=(0, 5))  # label on left with some space to the right

        self.height_text_box = tk.Text(height_frame, height=2, width=10)
        self.height_text_box.pack(side='left')

        unit_label_m = ttk.Label(height_frame, text="m")
        unit_label_m.pack(side='left', padx=(5, 0))

        # Pitch input
        pitch_frame = tk.Frame(input_frame)
        pitch_frame.pack(pady=5, anchor='w')

        pitch_label = ttk.Label(pitch_frame, text="Pitch (distance between rows):")
        pitch_label.pack(side='left', padx=(0,5))

        self.pitch_text_box = tk.Text(pitch_frame, height=1, width=10)
        self.pitch_text_box.pack(side='left')

        pitch_unit_label = ttk.Label(pitch_frame, text="m")
        pitch_unit_label.pack(side='left', padx=(5,0))

        # Number of rows input
        rows_frame = tk.Frame(input_frame)
        rows_frame.pack(pady=5, anchor='w')

        rows_label = ttk.Label(rows_frame, text="Number of rows:")
        rows_label.pack(side='left', padx=(0,5))

        self.rows_text_box = tk.Text(rows_frame, height=1, width=10)
        self.rows_text_box.pack(side='left')

        # Panels per row input
        panels_frame = tk.Frame(input_frame)
        panels_frame.pack(pady=5, anchor='w')

        panels_label = ttk.Label(panels_frame, text="Panels per row:")
        panels_label.pack(side='left', padx=(0,5))

        self.panels_text_box = tk.Text(panels_frame, height=1, width=10)
        self.panels_text_box.pack(side='left')

        # Panel width input
        panel_width_frame = tk.Frame(input_frame)
        panel_width_frame.pack(pady=5, anchor='w')

        panel_width_label = ttk.Label(panel_width_frame, text="Panel width:")
        panel_width_label.pack(side='left', padx=(0,5))

        self.panel_width_text_box = tk.Text(panel_width_frame, height=1, width=10)
        self.panel_width_text_box.pack(side='left')

        panel_width_unit_label = ttk.Label(panel_width_frame, text="m")
        panel_width_unit_label.pack(side='left', padx=(5,0))

        # --- Added: Mode selection (Fixed Angle vs Tracking) ---

        mode_frame = tk.Frame(input_frame)
        mode_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(mode_frame, text="Panel mode:").pack(anchor='w')

        fixed_rb = ttk.Radiobutton(mode_frame, text="Fixed Angle", variable=self.tracking_mode, value="fixed", command=self.update_mode_inputs)
        fixed_rb.pack(side='left', padx=5)

        tracking_rb = ttk.Radiobutton(mode_frame, text="Tracking", variable=self.tracking_mode, value="tracking", command=self.update_mode_inputs)
        tracking_rb.pack(side='left', padx=5)

        # Container for dynamic inputs based on mode
        self.dynamic_inputs_frame = tk.Frame(input_frame)
        self.dynamic_inputs_frame.pack(pady=10, padx=10, fill='x')

        # Fixed angle input
        self.fixed_angle_frame = tk.Frame(self.dynamic_inputs_frame)
        fixed_angle_label = ttk.Label(self.fixed_angle_frame, text="Fixed panel tilt angle:")
        fixed_angle_label.pack(side='left', padx=(0,5))
        self.fixed_angle_text_box = tk.Text(self.fixed_angle_frame, height=1, width=10)
        self.fixed_angle_text_box.pack(side='left')
        fixed_angle_unit_label = ttk.Label(self.fixed_angle_frame, text="°")
        fixed_angle_unit_label.pack(side='left', padx=(5,0))

        # Tracking inputs
        self.tracking_frame = tk.Frame(self.dynamic_inputs_frame)
        axis_azimuth_label = ttk.Label(self.tracking_frame, text="Axis azimuth:")
        axis_azimuth_label.pack(side='left', padx=(0,5))
        self.axis_azimuth_text_box = tk.Text(self.tracking_frame, height=1, width=10)
        self.axis_azimuth_text_box.pack(side='left')
        axis_azimuth_unit_label = ttk.Label(self.tracking_frame, text="°")
        axis_azimuth_unit_label.pack(side='left', padx=(5,15))

        max_angle_label = ttk.Label(self.tracking_frame, text="Max angle:")
        max_angle_label.pack(side='left', padx=(0,5))
        self.max_angle_text_box = tk.Text(self.tracking_frame, height=1, width=10)
        self.max_angle_text_box.pack(side='left')
        max_angle_unit_label = ttk.Label(self.tracking_frame, text="°")
        max_angle_unit_label.pack(side='left', padx=(5,0))

        # Initialize to show fixed angle inputs
        self.update_mode_inputs()

        # Pdc0 per module input
        pdc0_frame = tk.Frame(input_frame)
        pdc0_frame.pack(pady=5, anchor='w')

        pdc0_label = ttk.Label(pdc0_frame, text="Pdc0 per module:")
        pdc0_label.pack(side='left', padx=(0,5))

        self.pdc0_text_box = tk.Text(pdc0_frame, height=1, width=10)
        self.pdc0_text_box.pack(side='left')

        pdc0_unit_label = ttk.Label(pdc0_frame, text="W")
        pdc0_unit_label.pack(side='left', padx=(5,0))

        # Days input
        days_frame = tk.Frame(input_frame)
        days_frame.pack(pady=5, anchor='w')

        days_label = ttk.Label(days_frame, text="Number of days:")
        days_label.pack(side='left', padx=(0,5))

        self.days_text_box = tk.Text(days_frame, height=1, width=10)
        self.days_text_box.pack(side='left')

        # Calculate button on its own line (left aligned)
        calculate_btn = tk.Button(input_frame, text="Calculate", command=self.get_weather_data)
        calculate_btn.pack(pady=10, anchor='w')

        #TEST BUTTON
        test_btn = tk.Button(input_frame, text="Test Inputs", command=self.test_inputs)
        test_btn.pack(pady=5, anchor='w')

        # Result frame (below inputs)
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(pady=20, fill='both', expand=True)

    def update_mode_inputs(self):
        # Clear dynamic inputs frame
        for widget in self.dynamic_inputs_frame.winfo_children():
            widget.pack_forget()

        mode = self.tracking_mode.get()
        if mode == "fixed":
            self.fixed_angle_frame.pack(anchor='w')
        else:
            self.tracking_frame.pack(anchor='w')

    def add_logo(self):
        logo_path = get_resource_path("resources/pvlib_powered_logo_horiz.png")

        img = Image.open(logo_path)

        # Desired width
        base_width = 150
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))

        img = img.resize((base_width, h_size), Image.LANCZOS)

        self.logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(self, image=self.logo_img)
        logo_label.pack(side='bottom', anchor='w', padx=10, pady=10) 
    
    def set_update_callback(self, callback):
        # Register callback to send weather data 
        self.update_callback = callback

    def update_cities(self, event):
        country = self.selected_country.get()
        cities = sorted(self.country_city_map.get(country, []))
        self.city_combo["values"] = cities
        if cities:
            self.city_combo.set(cities[0])
        else:
            self.city_combo.set("No cities")

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def validate_float(self, input_textbox, field_name, allow_zero=True, positive_only=True):
        value_str = input_textbox.get("1.0", 'end-1c').strip()
        if allow_zero and (value_str == "0" or value_str == "0.0"):
            return 0.0
        try:
            value = float(value_str)
            if positive_only and value <= 0:
                tk.Label(self.result_frame, text=f"Please enter a valid positive value for {field_name}.").pack()
                return None
            return value
        except Exception:
            tk.Label(self.result_frame, text=f"Please enter a valid value for {field_name}.").pack()
            return None

    def validate_int(self, input_textbox, field_name, positive_only=True):
        value_str = input_textbox.get("1.0", 'end-1c').strip()
        try:
            value = int(value_str)
            if positive_only and value <= 0:
                tk.Label(self.result_frame, text=f"Please enter a valid positive integer for {field_name}.").pack()
                return None
            return value
        except Exception:
            tk.Label(self.result_frame, text=f"Please enter a valid integer for {field_name}.").pack()
            return None

    def get_weather_data(self):
        self.clear_frame(self.result_frame)
        user_country = self.selected_country.get()
        user_city = self.selected_city.get()

        rd = self.validate_float(self.rd_text_box, "rd", allow_zero=True, positive_only=False)
        if rd is None:
            return

        height = self.validate_float(self.height_text_box, "height", allow_zero=True)
        if height is None:
            return

        pitch = self.validate_float(self.pitch_text_box, "pitch", allow_zero=False)
        if pitch is None:
            return

        panels_per_row = self.validate_int(self.panels_text_box, "panels per row")
        if panels_per_row is None:
            return

        panel_width = self.validate_float(self.panel_width_text_box, "panel width", allow_zero=False)
        if panel_width is None:
            return

        # Calculate row width
        row_width = panels_per_row * panel_width

        num_rows = self.validate_int(self.rows_text_box, "number of rows")
        if num_rows is None:
            return  
        
        # Validate country and city
        if user_country == "Select a country" or not user_country:
            tk.Label(self.result_frame, text="Please select a valid country.").pack()
            return

        if user_city == "No cities" or not user_city:
            tk.Label(self.result_frame, text="Please select a valid city.").pack()
            return
        
        pdc0_per_module = self.validate_float(self.pdc0_text_box, "pdc0 per module", allow_zero=False)
        if pdc0_per_module is None:
            return

        N_modules = panels_per_row * num_rows

        num_days = self.validate_int(self.days_text_box, "number of days")
        if num_days is None:
            return
        elif num_days > 3:
            tk.Label(self.result_frame, text="Please select 3 days or less.").pack()
            return

        # Get timezone and check if it has a valid value
        tz = get_timezone(user_city, user_country, self.locations_csv_path)
        tz_str = tz if tz else "Timezone not found"
        user_time = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S") if tz else "N/A"

        gcr = row_width / pitch

        if not (0.05 <= gcr <= 0.9):
            self.clear_frame(self.result_frame)
            msg = (f"The provided pitch and row_width values result in an unrealistic ground coverage ratio (GCR) of "
                f"{gcr:.3f}. Typically, GCR should be between 0.05 and 0.9, with row_width smaller than pitch. "
                "Please adjust these values and try again.")
            tk.Label(self.result_frame, text=msg, fg='red', justify='left', wraplength=300).pack()
            return

        # Read additional inputs depending on mode
        mode = self.tracking_mode.get()
        fixed_angle = None
        axis_azimuth = None
        max_angle = None

        if mode == "fixed":
            fixed_angle = self.validate_float(self.fixed_angle_text_box, "fixed panel tilt angle", allow_zero=False)
            if fixed_angle is None:
                return
            # Pass fixed_angle; pass None for tracking params
            weather_data = asyncio.run(get_weather_data(
                user_country, user_city, tz, self.locations_csv_path,
                rd, height, pitch, row_width, gcr, num_days,
                fixed_angle=fixed_angle,
                axis_azimuth=None,
                max_angle=None,
            ))
        else:
            axis_azimuth = self.validate_float(self.axis_azimuth_text_box, "axis azimuth", allow_zero=True)
            if axis_azimuth is None:
                return
            max_angle = self.validate_float(self.max_angle_text_box, "max angle", allow_zero=False)
            if max_angle is None:
                return
            # Pass tracking params; pass None for fixed_angle
            weather_data = asyncio.run(get_weather_data(
                user_country, user_city, tz, self.locations_csv_path,
                rd, height, pitch, row_width, gcr, num_days,
                fixed_angle=None,
                axis_azimuth=axis_azimuth,
                max_angle=max_angle
            ))

        # Get weather data from API
        df = weather_data['weather_timeseries']
        now = pd.Timestamp.now(tz=df.index.tz)

        # Send the weather data to the middle panel
        if self.update_callback:
            self.update_callback((df, pdc0_per_module, N_modules, tz))

        temperature = get_closest_value(df['temperature'], now)
        humidity = get_closest_value(df['humidity'], now)
        wind_speed = get_closest_value(df['wind_speed'], now)
        irradiance = get_closest_value(df['irradiance'], now)
        cell_temperature = get_closest_value(df['cell_temperature'], now)
        
        result_text = (
            f"Country: {user_country}\n"
            f"City: {user_city}\n"
            f"Timezone: {tz_str}\n"
            f"Local Time: {user_time}\n\n"
            f"Weather Data:\n"
            f"Temperature: {format_value(temperature, '°C')}\n"
            f"Humidity: {format_value(humidity, '%')}\n"
            f"Wind Speed: {format_value(wind_speed, 'km/h')}\n"
            f"Irradiance: {format_value(irradiance, 'W/m²')}\n"
            f"Cell Temperature: {format_value(cell_temperature, '°C')}\n"
        )
        log(result_text)
        tk.Label(self.result_frame, text=result_text, justify="left").pack()

    def test_inputs(self):
        # Clear any previous results
        self.clear_frame(self.result_frame)

        # Set country and update cities
        self.selected_country.set("Greece")
        self.update_cities(None)  # update city list for Greece

        # Set city
        if "Nikaia" in self.city_combo["values"]:
            self.selected_city.set("Nikaia")
        else:
            self.selected_city.set(self.city_combo["values"][0] if self.city_combo["values"] else "")

        # Set rd (dust surface density)
        self.rd_text_box.delete("1.0", tk.END)
        self.rd_text_box.insert(tk.END, "0.0")

        # Height of torque above ground
        self.height_text_box.delete("1.0", tk.END)
        self.height_text_box.insert(tk.END, "2.6")

        # Pitch (distance between rows)
        self.pitch_text_box.delete("1.0", tk.END)
        self.pitch_text_box.insert(tk.END, "12")

        # Number of rows
        self.rows_text_box.delete("1.0", tk.END)
        self.rows_text_box.insert(tk.END, "1")

        # Panels per row
        self.panels_text_box.delete("1.0", tk.END)
        self.panels_text_box.insert(tk.END, "1")

        # Panel width
        self.panel_width_text_box.delete("1.0", tk.END)
        self.panel_width_text_box.insert(tk.END, "2")

        # Mode to fixed and set fixed value
        self.tracking_mode.set("fixed")
        self.update_mode_inputs()

        self.fixed_angle_text_box.delete("1.0", tk.END)
        self.fixed_angle_text_box.insert(tk.END, "32")
       
        # # Mode to Tracking and set tracking values
        # self.tracking_mode.set("tracking")
        # self.update_mode_inputs()

        # # Axis azimuth
        # self.axis_azimuth_text_box.delete("1.0", tk.END)
        # self.axis_azimuth_text_box.insert(tk.END, "0")

        # # Max angle
        # self.max_angle_text_box.delete("1.0", tk.END)
        # self.max_angle_text_box.insert(tk.END, "55")

        # Pdc0 per module
        self.pdc0_text_box.delete("1.0", tk.END)
        self.pdc0_text_box.insert(tk.END, "550")

        # Number of days
        self.days_text_box.delete("1.0", tk.END)
        self.days_text_box.insert(tk.END, "1")
