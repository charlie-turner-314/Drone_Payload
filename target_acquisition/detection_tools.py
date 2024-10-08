from ultralytics.engine.results import Results, Boxes
import numpy as np
from PIL import Image
import logging

class CLASSES:
    BASE = 0
    MAXIMUM = 1
    MINIMUM = 2
    TIP = 3

import numpy as np

def get_pressure_from_detections(detections:Boxes, min_value=0, max_value=1):
    base, maximum, minumum, tip = None, None, None, None
    for id, c in enumerate(detections.cls):
        if c == CLASSES.BASE: base = detections.xywh[id][:2]
        if c == CLASSES.MAXIMUM: maximum = detections.xywh[id][:2]
        if c == CLASSES.MINIMUM: minimum = detections.xywh[id][:2]
        if c == CLASSES.TIP: tip = detections.xywh[id][:2]
    
    if not (detections.cls == CLASSES.BASE).any() or not (detections.cls == CLASSES.TIP).any() or not (detections.cls == CLASSES.MINIMUM).any() or not (detections.cls == CLASSES.MINIMUM).any():
        logging.error("Missing one of the required detections")
        return None

    pressure = calculate_pressure(base, tip, minimum, maximum, min_value, max_value)
    return pressure

def angle_between(a, b, c):
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return angle

def calculate_sweep_angle(needle_base, min_coord, max_coord):
    """
    Calculate the sweep angle from min to max centered around base
    """
    angle = angle_between(min_coord, needle_base, max_coord )
    sweep_angle = 2*np.pi-angle
    return sweep_angle

def calculate_pressure(needle_base, needle_tip, min_coord, max_coord, min_value, max_value):
    """
    Calculate the pressure indicated by the needle on the gauge.
    
    :param needle_base: Tuple of (x, y) coordinates for the base of the needle.
    :param needle_tip: Tuple of (x, y) coordinates for the tip of the needle.
    :param min_coord: Tuple of (x, y) coordinates for the minimum value on the gauge.
    :param max_coord: Tuple of (x, y) coordinates for the maximum value on the gauge.
    :param min_value: The minimum pressure value (e.g., 0 psi).
    :param max_value: The maximum pressure value (e.g., 200 psi).
    :return: The calculated pressure.
    """
    # Calculate the angle of the needle relative to the custom horizontal axis
    
    # The total sweep angle between min and max positions is defined as the full sweep
    total_sweep_angle = calculate_sweep_angle(needle_base, min_coord, max_coord)
    
    # Calculate angle between base min and tip
    angle = angle_between(min_coord, needle_base, needle_tip)

    needle_position = angle / total_sweep_angle
    
    # Interpolate the pressure value
    pressure = min_value + needle_position * (max_value - min_value)
    
    return pressure


if __name__ == "__main__":
    # Any code to test/try out this module in isolation
    image = Image.open("test_data/image5.png")
    res = detect(image)
    # save the annotated image
    boxes = res[0].boxes
    pressure = get_pressure_from_detections(boxes, min_value=-1, max_value=10)
    print("Got pressure:", pressure)

 
