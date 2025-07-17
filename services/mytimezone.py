import csv
from timezonefinder import TimezoneFinder
import pycountry

def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return None

def get_latitude(selected_city, selected_country, locations_csv_path):
    tf = TimezoneFinder()
    with open(locations_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["city_ascii"].lower() == selected_city.lower() and row["country"].lower() == selected_country.lower():
                lat = float(row["lat"])
                return lat
    return

def get_longtitude(selected_city, selected_country, locations_csv_path):
    tf = TimezoneFinder()
    with open(locations_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["city_ascii"].lower() == selected_city.lower() and row["country"].lower() == selected_country.lower():
                lng = float(row["lng"])
                return lng
    return

def get_timezone(selected_city, selected_country, locations_csv_path):
    tf = TimezoneFinder()
    with open(locations_csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["city_ascii"].lower() == selected_city.lower() and row["country"].lower() == selected_country.lower():
                lat = float(row["lat"])
                lng = float(row["lng"])
                return tf.timezone_at(lat=lat, lng=lng)
    return None