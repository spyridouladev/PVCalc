import csv
from timezonefinder import TimezoneFinder
import pycountry

def get_country_name(code):
    try:
        return pycountry.countries.get(alpha_2=code).name
    except:
        return code  # fallback: show code if name not found
    
# Get country code (e.g. "Andorra" → "AD")
def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None

# Get latitude from cities500.txt
def get_latitude(selected_city, selected_country, locations_path):
    with open(locations_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 15:
                continue
            city = row[1]
            country_code = row[8]
            if city.lower() == selected_city.lower() and country_code.upper() == get_country_code(selected_country):
                return float(row[4])  # latitude
    return None

# Get longitude from cities500.txt
def get_longitude(selected_city, selected_country, locations_path):
    with open(locations_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 15:
                continue
            city = row[1]
            country_code = row[8]
            if city.lower() == selected_city.lower() and country_code.upper() == get_country_code(selected_country):
                return float(row[5])  # longitude
    return None

# Get timezone using coordinates
def get_timezone(selected_city, selected_country, locations_path):
    tf = TimezoneFinder()
    lat = get_latitude(selected_city, selected_country, locations_path)
    lng = get_longitude(selected_city, selected_country, locations_path)
    if lat is not None and lng is not None:
        return tf.timezone_at(lat=lat, lng=lng)
    return None
