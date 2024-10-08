import time
import logging
import subprocess
from threading import Lock

# Import your modules
import colorsys
from st7735 import ST7735
from ltr559 import LTR559
from bme280 import BME280
from fonts.ttf import RobotoMedium as UserFont
from enviroplus import gas
from PIL import Image, ImageDraw, ImageFont
from target_acquisition.camera_detection import CameraDetection
import RPi.GPIO as GPIO
import atexit

FRAME_RATE = 15

def cleanup_gpio():
    GPIO.cleanup()

atexit.register(cleanup_gpio)

# Setup logging
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S")

logging.info("Starting enviro script.")

def init_hardware() -> tuple:
    # Initialize hardware
    bme280 = BME280()
    # pms5003 = PMS5003()

    ltr559 = LTR559()
    st7735_display = ST7735(
        port=0,
        cs=1,
        dc="GPIO9",
        backlight="GPIO12",
        rotation=270,
        spi_speed_hz=10000000
    )
    return bme280, ltr559, st7735_display

TOP_POS = 25
font = ImageFont.truetype(UserFont, 20)

# Function to get CPU temperature
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

# Function to display text on LCD
def display_text(st7735_display, values, variable, data, unit):
    WIDTH, HEIGHT = st7735_display.width, st7735_display.height
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Update values
    values[variable] = values[variable][1:] + [data]
    vmin = min(values[variable])
    vmax = max(values[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
    message = f"{variable[:4]}: {data:.1f} {unit}"
    # logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i, colour_val in enumerate(colours):
        colour = (1.0 - colour_val) * 0.6
        r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        draw.rectangle((i, TOP_POS, i + 1, HEIGHT), (r, g, b))
        line_y = HEIGHT - (TOP_POS + (colour_val * (HEIGHT - TOP_POS))) + TOP_POS
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735_display.display(img)

# Function to get sensor data
def get_data(bme280, ltr559):
    # get global variables
    try:
        factor = 2.25
        cpu_temp = get_cpu_temperature()
        raw_temp = bme280.get_temperature()
        temp = raw_temp - ((cpu_temp - raw_temp) / factor)
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
        light = ltr559.get_lux()
        gas_data = gas.read_all()
        gas_oxidising = gas_data.oxidising / 1000
        gas_reducing = gas_data.reducing / 1000
        gas_nh3 = gas_data.nh3 / 1000
        return {
            "temperature": temp,
            "pressure": pressure,
            "humidity": humidity,
            "light": light,
            "oxidised": gas_oxidising,
            "reduced": gas_reducing,
            "nh3": gas_nh3
        }
    except Exception as e:
        logging.error("Failed to get sensor data, error: %s", e)
    
class VideoFeed:
    def __init__(self):
        self.lock = Lock()
        self.frame = None
        self.details = {}

    def update(self, frame, details):
        with self.lock:
            self.frame = frame
            self.details = details

    def get_frame(self):
        with self.lock:
            return self.frame
    
    def get_details(self):
        with self.lock:
            return self.details

# video feed thread - constantly updates the video feed
def video_feed_loop(video_feed):
    camera = CameraDetection()
    logging.info("Starting video feed thread.")
    while True:
        try:
            image, details = camera.get_frame(rgb_only=False)
            if image:
                video_feed.update(image, details)
        except Exception as e:
            logging.error("Video feed error: %s", e)
        time.sleep(1/20)
    
def write_ip_address(display, ip_address):
    WIDTH, HEIGHT = display.width, display.height
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_size = 25
    text_colour = (255, 255, 255)
    back_colour = (0, 170, 170)
    if not ip_address:
        res = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
        message = res.replace(" ", "\n")
    else:
        message = ip_address.replace(" ", "\n")

    # Function to get the font size that fits the text within the screen width and height
    def get_fitting_font_size(message, max_width, max_height, initial_font_size):
        lines = message.split("\n")
        longest_line = max(lines, key=len)
        font_size = initial_font_size
        font = ImageFont.truetype(UserFont, font_size)
        
        while True:
            # Check width
            x1, y1, x2, y2 = font.getbbox(longest_line)
            size_x = x2 - x1
            if size_x > max_width:
                font_size -= 1
                font = ImageFont.truetype(UserFont, font_size)
                continue
            
            # Check height
            total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
            if total_height > max_height:
                font_size -= 1
                font = ImageFont.truetype(UserFont, font_size)
                continue
            
            break
        
        return font

    # Get the fitting font size
    font = get_fitting_font_size(message, WIDTH, HEIGHT, font_size)

    # Calculate text position
    lines = message.split("\n")
    total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
    y = (HEIGHT - total_height) / 2

    # Draw background rectangle and write text.
    draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)

    current_y = y
    for line in lines:
        x1, y1, x2, y2 = font.getbbox(line)
        size_x = x2 - x1
        x = (WIDTH - size_x) / 2
        draw.text((x, current_y), line, font=font, fill=text_colour)
        current_y += y2 - y1
    
    display.display(img)
    return message

# Display thread function
def display_loop(st7735_display, bme280, ltr559, video_feed):

    logging.info("Starting display loop.")

    WIDTH, HEIGHT = st7735_display.width, st7735_display.height
    factor = 2.25
    mode = 2
    last_page = 0
    delay = 0.2
    values = {"temperature": [1] * WIDTH}
    cpu_temps = [get_cpu_temperature()] * 5
    ip_address = None
    
    while True:
        try:
            proximity = ltr559.get_proximity()
        except Exception as e:
            logging.error("Failed to get proximity, error: %s", e)
            proximity = 0
        current_time = time.time()
        
        if proximity > 1500 and (current_time - last_page) > delay:
            logging.info("Changing Mode")
            mode = (mode + 1) % 3
            last_page = current_time
        try: 
            if mode == 0:
                # variable = "temperature"
                unit = "°C"
                cpu_temp = get_cpu_temperature()
                # Smooth out with some averaging to decrease jitter
                cpu_temps = cpu_temps[1:] + [cpu_temp]
                avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
                raw_temp = bme280.get_temperature()
                data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
                display_text(st7735_display, values, "temperature", data, unit)
            
            elif mode == 1:
                # IP address mode
                # img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
                # draw = ImageDraw.Draw(img)
                # font_large = ImageFont.truetype(UserFont, 25)
                # text_colour = (255, 255, 255)
                # back_colour = (0, 170, 170)
                # try:
                #     res = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
                # except subprocess.CalledProcessError:
                #     res = "IP Error"
                # message = f"{res}"
                # x1, y1, x2, y2 = font_large.getbbox(message)
                # size_x = x2 - x1
                # size_y = y2 - y1
                # x = (WIDTH - size_x) / 2
                # y = (HEIGHT / 2) - (size_y / 2)
                # draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
                # draw.text((x, y), message, font=font_large, fill=text_colour)
                # st7735_display.display(img)
                ip_address = write_ip_address(st7735_display, ip_address)
            
            elif mode == 2:
                # Camera mode
                frame = video_feed.get_frame()
                if frame:
                    image = frame.resize((WIDTH, HEIGHT))
                    st7735_display.display(image)
        except Exception as e:
            logging.error("Failed to display data, error: %s", e)
        time.sleep(0.1)
