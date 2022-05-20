# Importing the required libraries
import os, shutil
import time

# For accessing the values from the .env file
from dotenv import dotenv_values

config = dotenv_values(".env")
TOR_BROWSER_PATH = config['TOR_BROWSER_PATH']

# Starting Tor Browser
def open_tor_browser():

    output("Starting Tor Browser...", True)

    os.startfile(TOR_BROWSER_PATH)
    time.sleep(10)

    output("Tor Browser Started.", False)

# Calculate time difference
def time_difference(start_time, end_time):
    time_diff = end_time - start_time
    minutes = divmod(time_diff.total_seconds(), 60) 
    return f'{int(minutes[0])} minutes, {int(minutes[1])} seconds'
            
# Clearing the results folder
def clear_results_directory():

    output("Clearing the results directory...", True)

    folder = os.path.join(os.path.dirname( __file__ ), '..', 'results')

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    output("Results directory cleared.", False)

# Creating directory for outputing images
def create_directory_for_images(number):

    output("Creating the directory for images...", True)

    try:
        os.mkdir(os.path.join(os.path.dirname( __file__ ), '..', 'results', 'images', str(number)))
        output("Image directory created.", False)
    except:
        output("Folder already created.", False)

# Printing the information
def output(text, start):

    if start:
        print("-" * 20)
    
    print(text)
    
    if not start:
        print("-" * 20)
    