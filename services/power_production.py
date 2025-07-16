import pvlib

def get_power_production(df, N_modules, pdc0_per_module):
    pdc0 = pdc0_per_module * N_modules
    gamma_pdc = -0.004  # -0.4% per °C

    power_dc = pvlib.pvsystem.pvwatts_dc(
        effective_irradiance=df['irradiance'],
        temp_cell=df['cell_temperature'],
        pdc0=pdc0,
        gamma_pdc=gamma_pdc
    )
    return power_dc

def get_total_power_production(power_dc):
    # Fixed interval in hours (15 minutes)
    interval_hours = 0.25

    # Energy = power * time (Wh)
    energy = power_dc * interval_hours

    # Sum energy to get total energy produced (Wh)
    total_energy = energy.sum()

    return total_energy

def get_daily_power_production(power_dc):
    interval_hours = 0.25  # 15 minutes = 0.25 hours

    # Calculate energy per time interval
    energy = power_dc * interval_hours

    # Resample by day, summing energy per day
    daily_energy = energy.resample('D').sum()

    return daily_energy
