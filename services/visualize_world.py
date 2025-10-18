import folium
import pandas as pd
import asyncio
import pytz
from datetime import datetime
from pathlib import Path

from services.file_data import read_locations_csv, get_resource_path
from services.get_weather import get_weather_data
from countryinfo import CountryInfo
import pycountry

def get_country_capitals(countries):
    country_capital_dict = {}
    for country in countries:
        countryinfo = CountryInfo(country)
        country_capital_dict[country] = countryinfo.capital()

    return country_capital_dict

def visualize_world():
    locations_csv_path = get_resource_path("resources/worldcities.csv")
    countries, country_city_map = read_locations_csv(locations_csv_path)

    capitals = country_capital_map = get_country_capitals(countries)

    print(capitals["France"])
