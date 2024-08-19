
import depthai as dai
from PIL import Image , ImageDraw , ImageFont
import cv2
import numpy as np
import json


class CameraDetection:
    def __init__(self):
        # self.nn_path = "/home/team6/Drone/target_acquisition/model/yolo.blob"
        self.nn_path = "/home/team6/depthai-python/examples/models/mobilenet-ssd_openvino_2021.4_6shave.blob"
        self.pipeline = self.setup_camera()
        self.get_camera_intrinsics()
        self.device = dai.Device(self.pipeline, usb2Mode=True)
        self.rgb_queue = self.device.getOutputQueue("rgb", maxSize=4, blocking=False)
        self.detection_queue = self.device.getOutputQueue("detections", maxSize=4, blocking=False)
        self.device.startPipeline() 

    def get_camera_intrinsics(self):
        """
        Get the camera intrinsics
        """
        # Get the camera intrinsics
        with dai.Device() as device:
            calibData = device.readCalibration()
            self.intrinsics = calibData.getCameraIntrinsics(dai.CameraBoardSocket.RGB)


    def setup_camera(self):
        """
        Set up the camera for object detection
        The output of the camera will then be: ImgDetections, Passthrough.
            - ImgDetections: the image with the detections
            - Passthrough: the raw image
        """
        pipeline = dai.Pipeline()

        # Setup the camera for rgb
        cam_rgb = pipeline.createColorCamera()
        cam_rgb.setPreviewSize(300, 300)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam_rgb.setInterleaved(False)
        cam_rgb.setFps(40)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)
        cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)

        # # Setup the neural network node
        detection_nn = pipeline.createNeuralNetwork()
        detection_nn.setBlobPath(self.nn_path)
        detection_nn.input.setBlocking(False)

        # Link the camera to the neural network
        cam_rgb.preview.link(detection_nn.input)

        # Create an XLinkOut for the passthrough
        xout_passthrough = pipeline.createXLinkOut()
        xout_passthrough.setStreamName("rgb")
        cam_rgb.preview.link(xout_passthrough.input)

        # # Create an XLinkOut for the detections
        xout_nn = pipeline.createXLinkOut()
        xout_nn.setStreamName("detections")
        detection_nn.out.link(xout_nn.input)


        return pipeline


    def get_frame(self, rgb_only=False):
        """
        Read a frame from the camera, do object detection and processing, then return the frame and the detections
        """
        # for now just return empty details and the raw rgb image
        details = {}
        if rgb_only:
            # get the rgb image from the camera
            rgb = self.rgb_queue.get()
            if rgb is None:
                return None, details
            rgb = rgb.getCvFrame()
            aruco = self._detect_aruco(rgb)
            print(aruco)
            # resize 640x640 to 160x80 with black bars on either side
            rgb = cv2.resize(rgb, (160, 80))
            # convert the image to a PIL image
            rgb = Image.fromarray(rgb)
            return rgb, details
        
        # get the detections
        detections = self.detection_queue.get()
        img = self.rgb_queue.get().getCvFrame()
        img = Image.fromarray(cv2.resize(img, (160, 80)))
        if detections is None:
            return img, details
        detections = detections.getData()
        print(detections)
        print(detections)
        if len(detections) == 0:
            return img, details

    

    def _detect_aruco(self, frame):
        """
        Detect ArUco markers in the given frame and estimate their poses.

        Parameters:
        frame (numpy.ndarray): The current camera frame.
        camera_matrix (numpy.ndarray): The camera matrix.
        dist_coeffs (numpy.ndarray): The distortion coefficients.

        Returns:
        list: A list of detections and their pose estimations.
        """
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Load the predefined dictionary
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        
        # Initialize the detector parameters using default values
        parameters = cv2.aruco.DetectorParameters_create()
        
        # Detect the markers in the grayscale image
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        
        detections = []

        camera_matrix = np.array(self.intrinsics.calibrationMatrix)
        dist_coeffs = np.array(self.intrinsics.distortionCoefficients)
        
        # If markers are detected, estimate their poses
        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
            for i in range(len(ids)):
                detection = {
                    'id': ids[i][0],
                    'corners': corners[i],
                    'rvec': rvecs[i],
                    'tvec': tvecs[i]
                }
                detections.append(detection)
        
        return detections

