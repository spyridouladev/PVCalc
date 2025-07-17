import csv
from collections import defaultdict
import os
import sys

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def read_locations_txt(filepath):
    country_city_map = defaultdict(list)
    
    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 9:
                continue  # Skip malformed lines
            city = row[1]         # name
            country = row[8]      # country code (e.g. "AD")
            if city and country:
                country_city_map[country].append(city)
    
    countries = sorted(country_city_map.keys())
    return countries, country_city_map
