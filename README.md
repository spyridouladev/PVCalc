# PVCalc

PVCalc is a Python application that analyzes and calculates solar energy potential production based on forecast data from geographical inputs. It integrates various data sources and uses the `pvlib` Python library for solar irradiance modeling.

---

## Features

- Retrieve and display weather data for selected locations worldwide.
- Calculate solar irradiance and other relevant solar energy metrics.
- Support for dust surface density input to refine calculations.
- Interactive GUI built with Tkinter.
- Data sourced from reputable dataset on world cities.
- Power production visualization for selected time periods.

---

## Installation

Before running the application from source make sure you have python 3.8+ installed, if not you can install python from [Python Download](https://www.python.org/downloads/).

1. Clone the repository
```bash
git clone https://github.com/spyridouladev/PVCalc.git
cd PVCalc
```
2. Create and activate virtual enviroment (recommended)
```bash
python -m venv venv
```
```bash
source venv/bin/activate      # On Linux/macOS
venv\Scripts\activate.bat     # On Windows
venv\Scripts\Activate.ps1     # On Powershell
```
3. Upgrade pip and install dependencies
```bash
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Run the application
```bash
python main.py
```
---
## Usage

First, input the data for the PV farm you want to calculate for.  
Keep in mind that the weather data is based on forecasts, so it will not be 100% accurate.

### Example: 3-Day Power Production

<div align="center">
  <img src="images/3_days.png" alt="3 days" width="600">
</div>

---

### Fixed Angle Mode

You can choose between **fixed angle** and **single-axis tracker**.

**Fixed angle input interface:**

<div align="center">
  <img src="images/fixed_angle.png" alt="fixed angle" width="500">
</div>

**Graph for fixed angle:**

<div align="center">
  <img src="images/fixed_angle_graph.png" alt="fixed angle graph" width="600">
</div>

---

### Single-Axis Tracker Mode

**Tracking input interface:**

<div align="center">
  <img src="images/tracking.png" alt="tracking" width="500">
</div>

**Graph for tracking:**

<div align="center">
  <img src="images/tracking_graph.png" alt="tracking graph" width="600">
</div>

---

### Results and Forecast

**Estimated production (⚠️ Not precise due to limited forecast data):**

<div align="center">
  <img src="images/results.png" alt="results" width="600">
</div>

**Live weather data display beneath input fields:**

<div align="center">
  <img src="images/weather.png" alt="weather" width="500">
</div>

## Attribution and License

### Cell Temperature model
This project incorporates concepts and correlation models derived from:

> Gholami, A., Ameri, M., Zandi, M., Gavagsaz Ghoachani, R., Jafarzadegan Gerashi, S., Kazem, H. A., & Al-Waeli, A. H. A. (2023). *Impact of harsh weather conditions on solar photovoltaic cell temperature: Experimental analysis and thermal-optical modeling*. Solar Energy, 252, 176–194. https://doi.org/10.1016/j.solener.2023.01.039

### Data Sources

This project uses geographical data from [GeoNames](https://download.geonames.org/).

The GeoNames data is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The data is provided "as is" without any warranty.

You are free to use, modify, and distribute this data, including for commercial purposes, provided that appropriate credit is given to GeoNames.

A copy of the GeoNames license is included in the `licenses/` directory of this project and you can view it [here](licenses/ccby4.txt).

For more details and to download the data, visit [https://download.geonames.org/](https://download.geonames.org/).

---

### Software Library (licensed under BSD 3-Clause)

This project uses **pvlib python**, licensed under the [BSD 3-Clause License](licenses/BSD3.txt). The copyright and license notice for pvlib are included with this project.

