from ultralytics import YOLO
from ultralytics.models import YOLO as YOLO_Model
import numpy as np

model: YOLO_Model = None

model = YOLO("model/yolov8n.pt")

def detect(image):
    res = model(image)
    return res


if __name__ == "__main__":
    # Any code to test/try out this module in isolation
    image = np.zeros((644, 644, 3))
    res = detect(image)
    print(res)

 
