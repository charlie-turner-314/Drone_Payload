#!/usr/bin/env python3

import colorsys
import sys
import time

import st7735

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

import logging
from subprocess import PIPE, Popen

from bme280 import BME280
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
from pms5003 import PMS5003
from pms5003 import ReadTimeoutError as pmsReadTimeoutError
from pms5003 import SerialTimeoutError

from enviroplus import gas

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""Get required readings from enviroplus
""")

#Real-Time Flight Information: The main section of the interface displays real-time
#information which includes the following variables:
#a. Temperature: A temperature gauge or numerical value indicating the current
#temperature.
#b. Atmospheric Pressure: A pressure gauge or numerical value indicating the
#current atmospheric pressure.
#c. Humidity: A humidity gauge or a numerical value indicating the current
#humidity level.
#d. Light: A visual representation or numerical value indicating the ambient light
#intensity.
#e. Gas Sensors: A section displaying readings from gas sensors, either in
#numerical or graphical format

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()
time.sleep(1.0)

message = ""

# The position of the top bar
top_pos = 25

# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3"]

units = ["C",
         "hPa",
         "%",
         "Lux",
         "kO",
         "kO",
         "kO"]

# Define your own warning limits
# The limits definition follows the order of the variables array
# Example limits explanation for temperature:
# [4,18,28,35] means
# [-273.15 .. 4] -> Dangerously Low
# (4 .. 18]      -> Low
# (18 .. 28]     -> Normal
# (28 .. 35]     -> High
# (35 .. MAX]    -> Dangerously High
# DISCLAIMER: The limits provided here are just examples and come
# with NO WARRANTY. The authors of this example code claim
# NO RESPONSIBILITY if reliance on the following values or this
# code in general leads to ANY DAMAGES or DEATH.
limits = [[4, 18, 28, 35],
          [250, 650, 1013.25, 1015],
          [20, 30, 60, 70],
          [-1, -1, 30000, 100000],
          [-1, -1, 40, 50],
          [-1, -1, 450, 550],
          [-1, -1, 200, 300],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100],
          [-1, -1, 50, 100]]

# RGB palette for values on the combined screen
palette = [(0, 0, 255),           # Dangerously Low
           (0, 255, 255),         # Low
           (0, 255, 0),           # Normal
           (255, 255, 0),         # High
           (255, 0, 0)]           # Dangerously High

values = {}



# Saves the data to be used in the graphs later and prints to the log
def save_data(idx, data):
    variable = variables[idx]
    # Maintain length of list
    #values[variable] = values[variable][1:] + [data]
    unit = units[idx]
    message = f"{variable[:4]}: {data:.1f} {unit}"
    logging.info(message)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index("=") + 1:output.rindex("'")])

def get_data():
    # Tuning factor for compensation. Decrease this number to adjust the
    # temperature down, and increase to adjust up
    factor = 2.25

    cpu_temps = [get_cpu_temperature()] * 5

    # Everything on one screen
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    #save_data(0, raw_data)
    pressure = bme280.get_pressure()
    #save_data(1, raw_data)
    humidity = bme280.get_humidity()
    #save_data(2, raw_data)
    light = ltr559.get_lux()
    #save_data(3, raw_data)
    gas_data = gas.read_all()
    gas_oxidising = gas_data.oxidising / 1000
    gas_reducing = gas_data.reducing / 1000
    gas_nh3 = gas_data.nh3 / 1000
    #save_data(4, gas_data.oxidising / 1000)
    #save_data(5, gas_data.reducing / 1000)
    #save_data(6, gas_data.nh3 / 1000)
    return [temp, pressure, humidity, light, gas_oxidising, gas_reducing, gas_nh3]

def main():
    get_data()
    # Tuning factor for compensation. Decrease this number to adjust the
    # temperature down, and increase to adjust up
    factor = 2.25

    cpu_temps = [get_cpu_temperature()] * 5

    delay = 0.5  # Debounce the proximity tap
    mode = 10    # The starting mode
    last_page = 0

    '''
    # Everything on one screen
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    raw_data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    save_data(0, raw_data)
    raw_data = bme280.get_pressure()
    save_data(1, raw_data)
    raw_data = bme280.get_humidity()
    save_data(2, raw_data)
    raw_data = ltr559.get_lux()
    save_data(3, raw_data)
    gas_data = gas.read_all()
    save_data(4, gas_data.oxidising / 1000)
    save_data(5, gas_data.reducing / 1000)
    save_data(6, gas_data.nh3 / 1000)
'''

if __name__ == "__main__":
    main()
