import csv
from collections import defaultdict
import os
import sys

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def read_locations_csv(locations_csv_path):
    country_city_map = defaultdict(list)
    with open(locations_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row["country"]
            city = row["city_ascii"]
            country_city_map[country].append(city)
    countries = sorted(country_city_map.keys())
    return countries , country_city_map