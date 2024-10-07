
import depthai as dai
from PIL import Image , ImageDraw , ImageFont
from .detection_tools import calculate_pressure
from sampling import sampling_tube
import cv2
import numpy as np
import json


class CameraDetection:
    def __init__(self):
        self._init_camera_intrinsics()
        self._init_aruco()
        self.nn_path = "/home/team6/Drone/target_acquisition/model/best_openvino_2022.1_6shave.blob"
        self.pipeline = self.setup_camera()
        # self.get_camera_intrinsics()
        self.device = dai.Device(self.pipeline)
        self.device.startPipeline() 
        self.rgb_queue = self.device.getOutputQueue("rgb", maxSize=8, blocking=False)
        self.detection_queue = self.device.getOutputQueue("nn", maxSize=8, blocking=False)
    
    def _restart_pipeline(self):
        """
        Safely restarts the DepthAI pipeline and reinitializes the device and output queues.
        """
        try:
            print("Restarting pipeline...")
            # Close the existing device connection
            self.device.close()
            # Reinitialize the device with the pipeline
            self.device = dai.Device(self.pipeline)
            self.device.startPipeline()
            # Recreate the output queues
            self.rgb_queue = self.device.getOutputQueue("rgb", maxSize=8, blocking=False)
            self.detection_queue = self.device.getOutputQueue("nn", maxSize=8, blocking=False)
            # Reinitialize camera intrinsics if needed
            self._init_camera_intrinsics()
            print("Pipeline restarted successfully.")
        except Exception as e:
            print(f"Failed to restart pipeline: {e}")

    def _init_camera_intrinsics(self):
        """
        Get the camera intrinsics
        """
        # Get the camera intrinsics
        with dai.Device() as device:
            calibData = device.readCalibration()
            calibrationMatrix = calibData.getCameraIntrinsics(dai.CameraBoardSocket.RGB)
            distortion = calibData.getDistortionCoefficients(dai.CameraBoardSocket.RGB)
            self.intrinsics = {
                "calibrationMatrix": calibrationMatrix,
                "distortionCoefficients": distortion
            }

    def setup_camera(self):
        """
        Set up the camera for object detection
        The output of the camera will then be: ImgDetections, Passthrough.
            - ImgDetections: the image with the detections
            - Passthrough: the raw image
        """
        pipeline = dai.Pipeline()

        with open("/home/team6/Drone/target_acquisition/model/best.json", "r") as f:
            config = json.load(f)
        
        nnConfig = config.get("nn_config", {})

        metadata = nnConfig.get("NN_specific_metadata", {})

        classes = metadata.get("classes", {})
        coordinates = metadata.get("coordinates", {})
        anchors = metadata.get("anchors", {})
        anchorMasks = metadata.get("anchor_masks", {})
        iouThreshold = metadata.get("iou_threshold", {})
        confidenceThreshold = metadata.get("confidence_threshold", {})
        self.labels = config.get("mappings", {}).get("labels", {})

        # Setup the camera for rgb
        cam_rgb = pipeline.createColorCamera()
        cam_rgb.setPreviewSize(640, 640)
        cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        cam_rgb.setInterleaved(False)
        cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB) # maybe this
        cam_rgb.setFps(5)

        # # Setup the neural network node
        detection_nn = pipeline.createYoloDetectionNetwork()

        # Create an XLinkOut for the passthrough
        xout_rgb = pipeline.createXLinkOut()
        xout_rgb.setStreamName("rgb")

        # # Create an XLinkOut for the detections
        xout_nn = pipeline.createXLinkOut()
        xout_nn.setStreamName("nn")

        # Network specific settings
        detection_nn.setConfidenceThreshold(confidenceThreshold)
        detection_nn.setNumClasses(classes)
        detection_nn.setCoordinateSize(coordinates)
        detection_nn.setAnchors(anchors)
        detection_nn.setAnchorMasks(anchorMasks)
        detection_nn.setIouThreshold(iouThreshold)
        detection_nn.setBlobPath(self.nn_path)
        detection_nn.setNumInferenceThreads(2)
        detection_nn.input.setBlocking(False)

        # Linking
        cam_rgb.preview.link(detection_nn.input)
        detection_nn.passthrough.link(xout_rgb.input)
        detection_nn.out.link(xout_nn.input)

        return pipeline


    def _frame_norm(self, frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    def _annotate_frame(self, frame, detections):
        """
        Annotate the frame with the given detections
        """
        for detection in detections:
            bbox = self._frame_norm(frame, (detection.xmin, detection.ymin, detection.xmax, detection.ymax))
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(frame, self.labels[detection.label], (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        return frame



    def get_frame(self, rgb_only=False):
        """
        Read a frame from the camera, do object detection and processing, then return the frame and the detections

        details:
        [
            open/closed
            int aruca id
            x, y, z of aruca
            float pressure
        ]
        """
        # for now just return empty details and the raw rgb image
        details = {}
        try:
            if rgb_only:
                # get the rgb image from the camera
                rgb = self.rgb_queue.get()
                if rgb is None:
                    return None, details
                rgb = rgb.getCvFrame()
                # aruco = self._detect_aruco(rgb)
                # print(aruco)
                rgb = Image.fromarray(rgb)
                return rgb, details
            
            # get the detections
            detections_nndata = self.detection_queue.tryGet()
            # get the rgb image from the camera
            rgb = self.rgb_queue.tryGet()
            if rgb is None or detections_nndata is None:
                return None, details
            rgb = rgb.getCvFrame()
            detections = detections_nndata.detections
            annotated = self._annotate_frame(rgb, detections)
            labels = [self.labels[detection.label] for detection in detections]
            if "aruco" in labels:
                aruco = self._detect_aruco(rgb)
                print(aruco)
            # detect gauges
            if "gauge_bbox" in labels:
                required_labels = ["gauge_min", "gauge_max", "gauge_tip", "gauge_base"]
                if all(label in labels for label in required_labels):
                    # Initialize dictionary to store best detections
                    best_detections = {}
                    for detection in detections:
                        label = self.labels[detection.label]
                        if label in required_labels:
                            if label not in best_detections or detection.confidence > best_detections[label].confidence:
                                best_detections[label] = detection

                    # Proceed only if all required parts are detected
                    if all(label in best_detections for label in required_labels):
                        # Get image dimensions
                        height, width, _ = rgb.shape

                        # Helper function to calculate center coordinates
                        def get_center_coords(detection):
                            x_center = int(((detection.xmin + detection.xmax) / 2) * width)
                            y_center = int(((detection.ymin + detection.ymax) / 2) * height)
                            return np.array([x_center, y_center])

                        # Extract center coordinates
                        gauge_min_coords = get_center_coords(best_detections['gauge_min'])
                        gauge_max_coords = get_center_coords(best_detections['gauge_max'])
                        needle_tip_coords = get_center_coords(best_detections['gauge_tip'])
                        needle_base_coords = get_center_coords(best_detections['gauge_base'])

                        # Calculate pressure
                        min_value = 0
                        max_value = 10
                        pressure = calculate_pressure(
                            needle_base_coords, 
                            needle_tip_coords, 
                            gauge_min_coords, 
                            gauge_max_coords, 
                            min_value, 
                            max_value
                        )
                        
                        if pressure < 4:
                            print(pressure)
                            sampling_tube.extend()

                    else:
                        print("Not all required gauge parts were detected.")

            # convert the image to a PIL image
            annotated = Image.fromarray(annotated)
            return annotated, details
        except RuntimeError as e:
            print(f"RuntimeError occurred: {e}")
            if 'X_LINK_ERROR' in str(e):
                print("Communication error detected. Attempting to restart the device.")
                self._restart_pipeline()
                return None, details
            else:
                raise e
        except Exception as e:
            print(f"An unexpected exception occurred: {e}")
            self._restart_pipeline()
            return None, details
    

    def _init_aruco(self):
        """
        Initialize the ArUco detector.
        """
        # Load the predefined dictionary
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        
        # Initialize the detector parameters using default values
        self.parameters = cv2.aruco.DetectorParameters()

        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.parameters)
    
    def _detect_aruco(self, frame):
        """
        Detect ArUco markers in the given frame and estimate their poses.

        Parameters:
        frame (numpy.ndarray): The current camera frame.

        Returns:
        list: A list of detections and their pose estimations.
        """
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect the markers in the grayscale image
        corners, ids, rejectedImgPoints = self.aruco_detector.detectMarkers(gray)
        
        detections = []

        camera_matrix = np.array(self.intrinsics["calibrationMatrix"])
        dist_coeffs = np.array(self.intrinsics["distortionCoefficients"])
        
        # Define the 3D coordinates of the marker's corners in the marker's own reference frame
        # Assuming a square marker with side length 0.05 meters
        marker_length = 0.05
        marker_corners_3d = np.array([
            [-marker_length / 2, marker_length / 2, 0],
            [marker_length / 2, marker_length / 2, 0],
            [marker_length / 2, -marker_length / 2, 0],
            [-marker_length / 2, -marker_length / 2, 0]
        ], dtype=np.float32)

        # If markers are detected, estimate their poses
        if ids is not None:
            for i in range(len(ids)):
                # Extract the corners for the current marker
                corners_2d = corners[i][0]
                
                # Use solvePnP to estimate the pose (rvec, tvec)
                success, rvec, tvec = cv2.solvePnP(marker_corners_3d, corners_2d, camera_matrix, dist_coeffs)
                
                if success:
                    detection = {
                        'id': ids[i][0],
                        'corners': corners[i],
                        'rvec': rvec,
                        'tvec': tvec
                    }
                    detections.append(detection)
        
        return detections

