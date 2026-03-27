'''
EAST Syntax From: https://opencv.org/blog/text-detection-and-removal-using-opencv/

PiCamera Reference: 
https://pip-assets.raspberrypi.com/categories/652-raspberry-pi-camera-module-2/documents/RP-008156-DS-2-picamera2-manual.pdf?disposition=inline

OpenCV & Tesseract Setup:
https://pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/

'''
from datetime import datetime
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput
import pytesseract
import imutils
import argparse
import cv2
import time
import numpy as np

# picam
cam = Picamera2()
camera_config = cam.create_video_configuration()
cam.set_controls({"FrameRate": 30, "ExposureTime": 0, "AnalogueGain": 0})
cam.configure(camera_config)
encoder = H264Encoder()
timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
p_filename = f"/home/c8win/Pictures/pic_{timestamp}.jpg"
v_filename = f"/home/c8win/Videos/vid_{timestamp}.h264"
output = v_filename

# opencv
modelPath = "frozen_east_text_detection.pb"
image_path = "stop_sign.jpg"
_image = cv2.imread(image_path)
image = cv2.resize(_image, (320,320))
anno_image = image.copy()
orig_EAST_img = image.copy()

# EAST params
inputSize = (320,320)
conf_thresh = 0.8
nms_thresh = 0.4
EAST = cv2.dnn_TextDetectionModel_EAST(modelPath)
EAST.setConfidenceThreshold(conf_thresh)
EAST.setNMSThreshold(nms_thresh)
EAST.setInputParams(1.0,inputSize,(123.68,116.78,103.94),True)

# camera controls
def take_picture():
	cam.start()
	cam.capture_file(p_filename)
	return p_filename

def start_recording():
	cam.start_recording(encoder, output, quality=Quality.HIGH)
	
def stop_recording():
	cam.stop_recording()
	
# opencv & tesseract
def ocr(anno_image):
	# TODO: implement ocr (duh)
	return ""
	
def text_detection(picture):
	print("detecting...")
	boxes, _ = EAST.detect(picture)
	for box in boxes:
		cv2.polylines(anno_image,[np.array(box,np.int32)], isClosed=True, color=(255,0,255), thickness=1)
	print("showing image...")
	cv2.imshow('EAST', anno_image)
	print("waiting for exit key...")
	cv2.waitKey(0) # waits for key press to exit (indefinite)
	cv2.destroyAllWindows()
	return anno_image

