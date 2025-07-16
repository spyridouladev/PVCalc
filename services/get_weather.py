import python_weather
import pvlib
import pandas as pd
from services.mytimezone import get_latitude
from services.mytimezone import get_longtitude
from services.mytimezone import get_country_code
from datetime import datetime, timedelta, time
import pytz
from services.logger import log

#using the fourth semi-empirical model
def get_cell_temp(ta,ir,ws,h,rd):
    ws = ws / 3.6
    tc = 3.408 + (0.991 * ta) + (0.026 * ir) - (1.117 * ws) - (0.028 * h) - (0.060 * rd)
    return tc

def get_irradiance(
    lat, lng, timezone, start_time, end_time, height, pitch, row_width, gcr,
    fixed_angle, axis_azimuth, max_angle
):
    print("Tracking mode:", fixed_angle)
    print("Axis Azimuth:", axis_azimuth)
    print("Max Angle:", max_angle)
    location = pvlib.location.Location(latitude=lat, longitude=lng, tz=timezone)
    times = pd.date_range(start=start_time, end=end_time, freq='1h', tz=timezone)
    
    solpos = location.get_solarposition(times)
    clearsky = location.get_clearsky(times, model='ineichen')
    dni_extra = pvlib.irradiance.get_extra_radiation(times)
    albedo = 0.20

    if fixed_angle is not None:
        surface_tilt = fixed_angle
        surface_azimuth = 180  # default south-facing
    elif axis_azimuth is not None and max_angle is not None:
        tracking_orientations = pvlib.tracking.singleaxis(
            apparent_zenith=solpos['apparent_zenith'],
            apparent_azimuth=solpos['azimuth'],
            axis_azimuth=axis_azimuth,
            max_angle=max_angle,
            backtrack=True,
            gcr=gcr,
        )
        surface_tilt = tracking_orientations['surface_tilt']
        surface_azimuth = tracking_orientations['surface_azimuth']
    else:
        raise ValueError("Must provide either fixed_angle or (axis_azimuth and max_angle).")

    irradiance = pvlib.bifacial.infinite_sheds.get_irradiance(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=solpos['apparent_zenith'],
        solar_azimuth=solpos['azimuth'],
        gcr=gcr,
        height=height,
        pitch=pitch,
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        dni=clearsky['dni'],
        albedo=albedo,
        model='haydavies',
        dni_extra=dni_extra,
        bifaciality=0.7,
    )

    irradiance_poa_global = irradiance['poa_global'].fillna(0)  # Replace NaNs with zero (e.g., at night)

    log("get_irradiance called with:")
    log(f"Latitude: {lat}, Longitude: {lng}, Timezone: {timezone}")
    log(f"Start: {start_time}, End: {end_time}")
    log(f"Height: {height} m, Pitch: {pitch} m, Row width: {row_width} m, GCR: {gcr:.3f}")
    log(f"Surface tilt: {surface_tilt}")
    log(f"Surface azimuth: {surface_azimuth}")
    log("Sample irradiance values (W/m²):")
    log(f" - Min: {irradiance_poa_global.min():.2f}")
    log(f" - Max: {irradiance_poa_global.max():.2f}")
    log(f" - Mean: {irradiance_poa_global.mean():.2f}")

    return irradiance_poa_global  # pandas Series indexed by time

def get_cloud_irradiance(weather_data):
    factor = 1 - 0.75 * (weather_data["cloud_cover"] ** 3)
    new_irradiance = weather_data['irradiance'] * factor 
    return new_irradiance

async def get_weather_data(country, city, timezone, locations_csv_path,rd, height, pitch, row_width, gcr,num_days,fixed_angle,axis_azimuth,max_angle):
    NA_values = {
        "temperature": "N/A",
        "humidity": "N/A",
        "wind_speed": "N/A",
        "irradiance": "N/A",
        "cell_temperature": "N/A",
        "weather_timeseries": "N/A",
    }
    
    tz = pytz.timezone(timezone)
    
    now = datetime.now(tz)
    
    date_only = now.date()
    start_time = tz.localize(datetime.combine(date_only, time.min))
    end_time = start_time + timedelta(days=num_days)

    try:
        lat = get_latitude(city,country,locations_csv_path)
        lng = get_longtitude(city,country,locations_csv_path)
        irradiance = get_irradiance(lat, lng, timezone, start_time, end_time, height, pitch, row_width, gcr,fixed_angle,axis_azimuth,max_angle)
    except Exception as e:
        log(f"Irradiance calculation has failed: {e}")
        return NA_values
    
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        try:    
            country_code = get_country_code(country)
            query = f"{city},{country_code}"
            weather = await client.get(query)
            records = []
            for daily in weather:
                day_date = daily.date  # get the date object for the day
                for hourly in daily:
                    # Combine date + time into a datetime.datetime object
                    dt = tz.localize(datetime.combine(day_date, hourly.time))

                    if dt < start_time or dt > end_time:
                        continue
                    records.append({
                        "datetime": dt,
                        "temperature": hourly.temperature,
                        "humidity": hourly.humidity,
                        "wind_speed": hourly.wind_speed,
                        "cloud_cover": hourly.cloud_cover,             # directly blocks solar radiation
                        # "precipitation": hourly.precipitation,
                    })
        except Exception as e:
            log(f"Weather API failed: {e}")
            return NA_values
 
    weather_df = pd.DataFrame(records).set_index("datetime")

    weather_df.index = weather_df.index.floor('1h')
    irradiance.index = irradiance.index.floor('1h')
    weather_data = pd.concat([irradiance, weather_df], axis=1)

    weather_data = pd.concat([irradiance.rename("irradiance"), weather_df], axis=1).ffill()

    weather_data['cell_temperature'] = weather_data.apply(
        lambda row: get_cell_temp(
            row['temperature'],
            row['irradiance'],
            row['wind_speed'],
            row['humidity'],
            rd
        ),
        axis=1
    )

    # Account for cloud cover
    weather_data["cloud_cover"] = weather_data["cloud_cover"] / 100.0
    # Cloud cover was in %, now its from 0 to 1
    irradiance_clouds = get_cloud_irradiance(weather_data)
    diff = irradiance_clouds - weather_data["irradiance"]

    log(f"Irradiance difference stats after cloud adjustment:")
    for timestamp, value in diff.items():
        log(f"{timestamp}: Difference in irradiance = {value:.2f} W/m²")

    weather_data["irradiance"] = irradiance_clouds

    log(f"Number of weather samples: {len(weather_df)}")
    log("Weather DataFrame:")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        log(weather_df)

    log(f"Number of irradiance samples: {len(irradiance)}")
    log("Irradiance Series:")
    with pd.option_context('display.max_rows', None):
        log(irradiance)

    log("Combined DataFrame:")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        log(weather_data)
    return {
        "temperature": weather_data["temperature"],
        "humidity": weather_data["humidity"],
        "wind_speed": weather_data["wind_speed"],
        "irradiance": weather_data["irradiance"],
        "cell_temperature": weather_data["cell_temperature"],
        "cloud_cover": weather_data["cloud_cover"],
        "weather_timeseries": weather_data,
    }