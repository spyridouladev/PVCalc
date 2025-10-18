from gui.main_window import MainApp
from countryinfo import CountryInfo

country = CountryInfo('Greece')
print("Capital:", country.capital())

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()