import cv2
import random


def get_enviro_data():
    return [
        random.uniform(10, 30),
        random.uniform(900, 1100),
        random.uniform(10, 90),
        random.uniform(0, 100),
        random.uniform(0, 100),
        random.uniform(0, 100),
        random.uniform(0, 100),
    ]


def get_imagery_data():
    idx = random.randint(0, 5)
    if idx == 0:
        return [random.choice([True, False]), None, None, None, None]
    elif idx == 1:
        return [
            None,
            random.randint(0, 1000),
            random.uniform(0, 100),
            random.uniform(0, 100),
            None,
        ]
    elif idx == 2:
        return [None, None, None, None, random.uniform(0, 100)]
    else:
        return [None, None, None, None, None]


class Video:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)

    def get_frame(self):
        if not self.cam.isOpened():
            return None
        _, frame = self.cam.read()
        return cv2.imencode(".jpg", frame)[1].tobytes()

    def __del__(self):
        self.cam.release()
