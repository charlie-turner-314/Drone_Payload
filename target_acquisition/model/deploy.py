import os
import requests
import json
import cv2
from ultralytics import YOLO
from roboflow import Roboflow
import torch

# Set up your API keys and project info
ROBOFLOW_API_KEY = "QCkJfbhGmhgwkVPnDydf"  # Replace with your Roboflow API key
ROBOFLOW_PROJECT_ID = "pressure-chste"     # Replace with your Roboflow project ID
ROBOFLOW_VERSION = "1"    # Replace with the Roboflow version
MODEL_PATH = "weights.pt"              # Path to your YOLOv8 model

# Load the model weights onto the CPU
model_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
# save model again
torch.save(model_dict, "weights_cpu.pt")

# Initialize Roboflow
rf = Roboflow(api_key=ROBOFLOW_API_KEY)
project = rf.workspace().project(ROBOFLOW_PROJECT_ID)

# Deploy the model
version = project.version(ROBOFLOW_VERSION)
version.deploy("yolov5", ".", "weights_cpu.pt")
