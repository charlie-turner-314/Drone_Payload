#!/usr/bin/env python3

import colorsys
import sys
import time
<<<<<<< HEAD
<<<<<<< HEAD
import cv2
=======

>>>>>>> 6a17c87 (structure)
=======

>>>>>>> 21831fe (maybe)
import st7735

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

import logging
from bme280 import BME280
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
from pms5003 import PMS5003
from pms5003 import ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
import subprocess
<<<<<<< HEAD
<<<<<<< HEAD
import depthai as dai
from PIL import Image , ImageDraw , ImageFont
from fonts.ttf import RobotoMedium as UserFont
=======
>>>>>>> 6a17c87 (structure)
=======
>>>>>>> 21831fe (maybe)

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("""Loop through required screens on EnviroLCD

Press Ctrl+C to exit!

""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Create ST7735 LCD display class
st7735 = st7735.ST7735(
    port=0,
    cs=1,
    dc="GPIO9",
    backlight="GPIO12",
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 20
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25


# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):
<<<<<<< HEAD
<<<<<<< HEAD
    # Set up canvas and font
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = 20
    font = ImageFont.truetype(UserFont, font_size)
=======
>>>>>>> 6a17c87 (structure)
=======
>>>>>>> 21831fe (maybe)
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    # Scale the values for the variable between 0 and 1
    vmin = min(values[variable])
    vmax = max(values[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
    # Format the variable name and value
    message = f"{variable[:4]}: {data:.1f} {unit}"
    logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i in range(len(colours)):
        # Convert the values to colours from red to blue
        colour = (1.0 - colours[i]) * 0.6
        r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        # Draw a 1-pixel wide rectangle of colour
        draw.rectangle((i, top_pos, i + 1, HEIGHT), (r, g, b))
        # Draw a line graph in black
        line_y = HEIGHT - (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    # Write the text at the top in black
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735.display(img)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

delay = 0.5  # Debounce the proximity tap
mode = 0     # The starting mode
last_page = 0
light = 1

# Create a values dict to store the data
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
# Create a values dict to store the data
variables = ["temperature"]
=======
variables = ["temperature",
            ]
>>>>>>> 6a17c87 (structure)
=======
=======
>>>>>>> 21831fe (maybe)
# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]
<<<<<<< HEAD
>>>>>>> 1531158 (what)
=======
>>>>>>> 21831fe (maybe)

values = {}

for v in variables:
    values[v] = [1] * WIDTH

# The main loop
try:
    while True:
        proximity = ltr559.get_proximity()

        # If the proximity crosses the threshold, toggle the mode
        if proximity > 1500 and time.time() - last_page > delay:
            mode += 1
            mode %= 3
            last_page = time.time()

        # One mode for each variable
        if mode == 0:
            # variable = "temperature"
            unit = "°C"
            cpu_temp = get_cpu_temperature()
            # Smooth out with some averaging to decrease jitter
            cpu_temps = cpu_temps[1:] + [cpu_temp]
            avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
            raw_temp = bme280.get_temperature()
            data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
<<<<<<< HEAD
<<<<<<< HEAD
            display_text("temperature", data, unit)
=======
            display_text(variables[mode], data, unit)
>>>>>>> 6a17c87 (structure)
=======
            display_text(variables[mode], data, unit)
>>>>>>> 21831fe (maybe)

        if mode == 1:
            #IP address
            # New canvas to draw on.
            img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Text settings.
            font_size = 25
            font = ImageFont.truetype(UserFont, font_size)
            text_colour = (255, 255, 255)
            back_colour = (0, 170, 170)
            res = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
            print(res)
            message = f"{res}"
            x1, y1, x2, y2 = font.getbbox(message)
            size_x = x2 - x1
            size_y = y2 - y1
            # Calculate text position
            x = (WIDTH - size_x) / 2
            y = (HEIGHT / 2) - (size_y / 2)
            # Draw background rectangle and write text.
            draw.rectangle((0, 0, 160, 80), back_colour)
            draw.text((x, y), message, font=font, fill=text_colour)
            st7735.display(img)

        if mode == 2:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 1531158 (what)
=======
>>>>>>> 21831fe (maybe)
            pipeline = dai.Pipeline()
            # Define source and output
            camRgb = pipeline.create(dai.node.ColorCamera)
            xoutRgb = pipeline.create (dai.node.XLinkOut)
            xoutRgb.setStreamName("rgb")
            # Properties
            camRgb.setPreviewSize(WIDTH,HEIGHT)
            camRgb.setInterleaved(False)
            camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
            # Linking
            camRgb.preview.link(xoutRgb.input)
            # Connect to device and start pipeline
            with dai.Device(pipeline) as device :
                qRgb = device.getOutputQueue (name="rgb", maxSize =4 , blocking = False)
<<<<<<< HEAD
<<<<<<< HEAD
                while True:
                    proximity = ltr559.get_proximity()
                    # If the proximity crosses the threshold, toggle the mode
                    if proximity > 1500 and time.time() - last_page > delay:
                        print("Changing mode")
                        mode += 1
                        mode %= 3
                        last_page = time.time()
                        break
=======
                while True :
>>>>>>> 1531158 (what)
=======
                while True :
>>>>>>> 21831fe (maybe)
                    inRgb = qRgb.get()
                    img = inRgb.getCvFrame()
                    img = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
                    im_pil = Image.fromarray(img)
                    # Resize the image
                    im_pil = im_pil.resize ((WIDTH,HEIGHT))
                    # display image on lcd
                    st7735.display(im_pil)
                    if cv2.waitKey(1) == ord('q') :
                        break
<<<<<<< HEAD
<<<<<<< HEAD
=======
            # Detection
            unit = "%"
            data = bme280.get_humidity()
            display_text(variables[mode], data, unit)
>>>>>>> 6a17c87 (structure)
=======
>>>>>>> 1531158 (what)
=======
>>>>>>> 21831fe (maybe)

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
