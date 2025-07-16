import pvlib
import os
import sys
import subprocess

def get_pvlib_data_path():
    # First try to get the pvlib/data folder inside bundled resources (PyInstaller _MEIPASS)
    if hasattr(sys, '_MEIPASS'):
        bundled_data_dir = os.path.join(sys._MEIPASS, 'pvlib', 'data')
        if os.path.exists(bundled_data_dir):
            return bundled_data_dir

    # Fallback: get pvlib/data folder from the installed package location
    pvlib_dir = os.path.dirname(pvlib.__file__)
    data_dir = os.path.join(pvlib_dir, 'data')
    if os.path.exists(data_dir):
        return data_dir

    return None

def format_add_data_argument(src_path, dest_folder):
    # PyInstaller wants src;dest on Windows, src:dest on Unix
    if sys.platform.startswith('win'):
        separator = ';'
    else:
        separator = ':'
    return f'{src_path}{separator}{dest_folder}'

def main():
    data_path = get_pvlib_data_path()
    if not data_path:
        print("Could not find pvlib 'data' directory.")
        sys.exit(1)

    pvlib_add_data = format_add_data_argument(data_path, 'pvlib/data')

    # Bundle worldcities.csv into resources folder
    resources_csv_path = os.path.abspath('resources/worldcities.csv')
    resources_logo_path = os.path.abspath('resources/pvlib_powered_logo_horiz.png')

    if not os.path.exists(resources_csv_path):
        print(f"Could not find {resources_csv_path}")
        sys.exit(1)

    resources_add_data = format_add_data_argument(resources_csv_path, 'resources')
    resources_logo_add_data = format_add_data_argument(resources_logo_path, 'resources')

    pyinstaller = [
    sys.executable, '-m', 'PyInstaller',
    '--noconfirm',
    '--onefile',      
    '--windowed',     # comment if you want console window during testing
    '--add-data', pvlib_add_data,
    '--add-data', resources_add_data,
    '--add-data', resources_logo_add_data,
    '--distpath', '.',   # output folder is current directory
    'main.py'
    ]

    print("Running PyInstaller with command:")
    print(' '.join(pyinstaller))

    try:
        subprocess.run(pyinstaller, check=True)
        print("PyInstaller build finished successfully.")
    except subprocess.CalledProcessError as e:
        print("PyInstaller failed with error:")
        print(e)

if __name__ == '__main__':
    main()
