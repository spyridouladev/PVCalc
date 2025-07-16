import tkinter as tk
from services.logger import log
from services.power_production import get_total_power_production, get_daily_power_production

class RightPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.figure = None
        self.canvas = None

    def update_weather(self, weather_data=None):
        for widget in self.winfo_children():
            widget.destroy()

        # Unpack values
        df, pdc0_per_module, N_modules, tz, power_series = weather_data

        # Total energy
        total_energy = get_total_power_production(power_series)  # Wh
        total_energy_kwh = total_energy / 1000
        total_energy_str = f"Total Energy Produced = {total_energy_kwh:.2f} kWh"  # <-- define here

        # Daily energy (Wh)
        daily_energy_wh = get_daily_power_production(power_series)

        # Convert to kWh
        daily_energy_kwh = daily_energy_wh / 1000

        # Drop last day if you want to exclude it
        if len(daily_energy_kwh) > 1:
            daily_energy_kwh = daily_energy_kwh.iloc[:-1]
        
        # Show daily energies
        tk.Label(self, text="Daily Energy Production (kWh) =", font=("Helvetica", 16, "bold")).pack(pady=(0, 5))
        for day, energy in daily_energy_kwh.items():
            label_text = f"{day.strftime('%Y-%m-%d')}: {energy:.2f} kWh"
            tk.Label(self, text=label_text, font=("Helvetica", 14)).pack()

        # Show total energy produced (including all days)
        tk.Label(self, text=f"\n{total_energy_str}", font=("Helvetica", 14, "bold")).pack(pady=(10, 0))

        power_avg = daily_energy_kwh.mean()
        tk.Label(self, text=f"Average Daily Energy = {power_avg:.2f} kWh", font=("Helvetica", 14, "bold")).pack(pady=(10, 0))

        week_power = power_avg *7
        month_string = f"Weekly Energy Production (kWh) ≈ {week_power:.2f} kWh"
        tk.Label(self, text=month_string, font=("Helvetica", 14, "bold")).pack(pady=(10, 0))

        month_power = power_avg * 30
        month_string = f"Monthly Energy Production (kWh) ≈ {month_power:.2f} kWh"
        tk.Label(self, text=month_string, font=("Helvetica", 14, "bold")).pack(pady=(10, 0))
