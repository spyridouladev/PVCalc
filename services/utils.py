import pandas as pd
from services.logger import log

def format_value(val, unit=""):
    try:
        return f"{float(val):.2f} {unit}"
    except (ValueError, TypeError):
        return str(val)  # e.g., "N/A"

def get_closest_value(series, target_time):
    target_time = pd.Timestamp(target_time)
    idx = series.index

    # Calculate absolute difference between target_time and each timestamp in index
    time_diffs = abs(idx - target_time)
    closest_idx_pos = time_diffs.argmin()  # position of smallest difference

    return series.iloc[closest_idx_pos]

def interpolate_timeseries(df, freq):
    # Ensure index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index, errors='coerce')
    
    log(f"Original df index (min to max): {df.index.min()} to {df.index.max()}")
    log(f"Original df index frequency (inferred): {pd.infer_freq(df.index)}")
    log(f"Original df index values:\n{df.index}")

    # Drop rows with invalid dates
    df = df.dropna(subset=[df.index.name] if df.index.name else [df.columns[0]])
    
    # Resample and interpolate
    df_resampled = df.resample(freq).interpolate(method='time')
    return df_resampled