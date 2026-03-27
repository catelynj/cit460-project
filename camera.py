'''
DB18 Syntax From: https://opencv.org/blog/text-detection-and-removal-using-opencv/

PiCamera Reference: 
https://pip-assets.raspberrypi.com/categories/652-raspberry-pi-camera-module-2/documents/RP-008156-DS-2-picamera2-manual.pdf?disposition=inline

Some OpenCV & Tesseract Setup:
https://pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/

Debugging issues (of which there are many) done w/ StackExchange/Reddit/etc. and Claude as a last resort
'''
from datetime import datetime
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput
import pytesseract
import imutils
import cv2
import time

#picam
cam = Picamera2()
camera_config = cam.create_video_configuration()
cam.set_controls({"FrameRate": 30, "ExposureTime": 0, "AnalogueGain": 0})
cam.configure(camera_config)
encoder = H264Encoder()
timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
p_filename = f"/home/c8win/Pictures/pic_{timestamp}.jpg"
v_filename = f"/home/c8win/Videos/vid_{timestamp}.h264"
output = v_filename

#opencv
modelPath = "DB_TD500_resnet18.onnx"
image_path = "stop_sign.jpg"
_image = cv2.imread(image_path)
image = cv2.resize(_image, (736,736))
anno_image = image.copy()
orig_db18_img = image.copy()

#db18 params
inputSize = (736,736)
bin_thresh = 0.1
poly_thresh = 0.3
mean = (122.67891434, 116.66876762, 104.00698793)
db18 = cv2.dnn_TextDetectionModel_DB(modelPath)
db18.setBinaryThreshold(bin_thresh).setPolygonThreshold(poly_thresh)
db18.setInputParams(1.0/255, inputSize, mean, True)
'''
OpenCV is giving me issues
print("detecting...")
# detect text
boxes, _ = db18.detect(image)
print(f"detected {len(boxes)} boxes")
for box in boxes:
	cv2.polylines(anno_image,[np.array(box,np.int32)], isClosed=True, color=(255,0,255), thickness=1)

print("showing image...")
cv2.imshow('DB18', anno_image)
print("waiting for exit key...")
cv2.waitKey(0) # waits for key press to exit (indefinite)
cv2.destroyAllWindows()
'''
	
def take_picture():
	cam.start()
	cam.capture_file(p_filename)
	return p_filename

def start_recording():
	cam.start_recording(encoder, output, quality=Quality.HIGH)
	
def stop_recording():
	cam.stop_recording()

