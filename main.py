"""
GPIO Code Modified from Raspberry Pi Touch Sensor Tutorial by newbiely.com

https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-touch-sensor


Had to swap to using legacy gpio due to edge detection issues (annoying)
but the structure/idea of everything is still built off of this tutorial


lgpio docs:
https://abyz.me.uk/lg/py_lgpio.html

"""

import lgpio
import time
from datetime import datetime
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput


TOUCH_PIN = 17
touch_count = 0
TIMEOUT = 0.5
PRESS_WAIT = 0.4
last_press = time.time()

h = lgpio.gpiochip_open(0) # init
lgpio.gpio_claim_input(h, TOUCH_PIN)

last_state = 0

cam = Picamera2()
camera_config = cam.create_video_configuration()
cam.set_controls({"FrameRate": 30, "ExposureTime": 0, "AnalogueGain": 0})
cam.configure(camera_config)

encoder = H264Encoder()

timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
p_filename = f"/home/c8win/Pictures/pic_{timestamp}.jpg"
v_filename = f"/home/c8win/Videos/vid_{timestamp}.h264"

output = v_filename

print("awaiting input...")
try:
	while True:
		current_state = lgpio.gpio_read(h, TOUCH_PIN)

		if current_state == 1 and last_state == 0:  # rising edge
			if time.time() - last_press > TIMEOUT:
				touch_count = 0

			touch_count += 1
			last_press = time.time()

# for demo purposes this is fine, will break these into their own functions later to allow for better control
		if touch_count > 0 and time.time() - last_press > PRESS_WAIT:
			if touch_count == 1:
				print("prompt")
			elif touch_count == 2:
				cam.start()
				cam.capture_file(p_filename)
				print(f"picture taken, saved as {p_filename}")
			elif touch_count >= 3:
				print("recording 6 second video")
				cam.start_recording(encoder, output, quality=Quality.HIGH)
				time.sleep(6)
				cam.stop_recording()
				print(f"recording stopped, saved as {v_filename}")
			touch_count = 0

		last_state = current_state
		time.sleep(0.05)

except KeyboardInterrupt:
	lgpio.gpiochip_close(h)
