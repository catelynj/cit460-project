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
from imutils.object_detection import non_max_suppression
import pytesseract
import imutils
import cv2
import time
import numpy as np
from pathlib import Path

# -- CAMERA START --
cam = Picamera2()
camera_config = cam.create_video_configuration()
cam.set_controls({"FrameRate": 30, "ExposureTime": 0, "AnalogueGain": 0})
cam.configure(camera_config)
encoder = H264Encoder()
timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
p_filename = f"/home/c8win/Pictures/pic_{timestamp}.jpg"
v_filename = f"/home/c8win/Videos/vid_{timestamp}.h264"
output = v_filename

def take_picture():
    cam.start()
    cam.capture_file(p_filename)
    cam.stop()

def start_recording():
    cam.start_recording(encoder, output, quality=Quality.HIGH)

def stop_recording():
    cam.stop_recording()

def snapshot():
    cam.start()
    cam.capture_file("translate.jpg")
    cam.stop()

# -- CAMERA END --

# -- OPENCV & TESSERACT START --
modelPath = "frozen_east_text_detection.pb"
image_path = "kanji.jpeg"
#Path(image_path).touch(exist_ok=True)

net = None
# EAST returns 2 output layers, the 1st is used for probabilities
# and the 2nd is for bounding box coords
LAYER_NAMES = [
    "feature_fusion/Conv_7/Sigmoid",
    "feature_fusion/concat_3"
]


def load_model():
	global net
	if net is None:
		print("loading EAST model...")
		net = cv2.dnn.readNet(modelPath)

# pulled directly from OpenCV OCR & Text Recognition with Tesseract article
def decode_predictions(scores, geometry):
    # number of rows and cols from scores
    (numRows, numCols) = scores.shape[2:4]
    # initialize set of bounding boxes & confidence scores
    rects = []
    confidences = []
    for y in range(0, numRows):
        #extract scores
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]
        for x in range(0, numCols):
            if scoresData[x] < 0.5:
                continue
            # compute offset factor as resulting feature
            (offsetX, offsetY) = (x * 4.0, y * 4.0)
            # get rotation angle for prediction
            angle = anglesData[x]
            # calc sine and cosine
            cos = np.cos(angle)
            sin = np.sin(angle)
            # use geometry to get height and width of bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]
            # compute start and end coords for bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)
            # add bounding box coordinates & prob score to lists
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])
    return (rects, confidences)

# modified from OpenCV OCR & Text Recognition with Tesseract article
def detect_text_regions(image):
    load_model()
    # get image size
    (H, W) = image.shape[:2]
    # calc ratio of original image
    rW = W / float(320)
    rH = H / float(320)
    # resize image for EAST
    resized = cv2.resize(image, (320, 320))
    # convert to blob
    blob = cv2.dnn.blobFromImage(resized, 1.0, (320, 320),
        (123.68, 116.78, 103.94), swapRB=True, crop=False)
    # pass the blob to EAST and get output layers
    net.setInput(blob)
    (scores, geometry) = net.forward(LAYER_NAMES)
    # apply NMS suppression to get rid of weak/overlapping boxes
    (rects, confidences) = decode_predictions(scores, geometry)
    boxes = non_max_suppression(np.array(rects), probs=confidences)
    return boxes, rW, rH

def ocr():
    image = cv2.imread(image_path)
    if image is None:
        print("no image found")
        return []
    orig = image.copy()
    boxes, rW, rH = detect_text_regions(image)
    results = []
    for (startX, startY, endX, endY) in boxes:
        # scale boxes to original image ratios
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        # apply padding to bounding boxes
        dX = int((endX - startX) * 0.1)
        dY = int((endY - startY) * 0.1)
        startX = max(0, startX - dX)
        startY = max(0, startY - dY)
        endX = min(orig.shape[1], endX + (dX * 2))
        endY = min(orig.shape[0], endY + (dY * 2))
        # extract padded roi
        roi = orig[startY:endY, startX:endX]
        # config stuff for tesseract
        config = ("-l eng+jpn+fra+spa --oem 1 --psm 7")
        text = pytesseract.image_to_string(roi, config=config)
        # add box coords and text to results
        results.append(((startX, startY, endX, endY), text))
    # sort bounding box coords
    results = sorted(results, key=lambda r: r[0][1])
    print(results)
    for ((startX, startY, endX, endY), text) in results:
        print("OCR TEXT")
        print("========")
        print("{}\n".format(text))
    text = "".join([s.strip() for _,s in results if s.strip()])
    #print(text)
    return text

# -- OPENCV & TESSERACT END --

#ocr()
