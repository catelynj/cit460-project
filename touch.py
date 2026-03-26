'''
Touch Sensor Control Script

GPIO Code Modified from Raspberry Pi Touch Sensor Tutorial by newbiely.com

https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-touch-sensor


Had to swap to using legacy gpio due to edge detection issues (annoying)
but the structure/idea of everything is still built off of this tutorial


lgpio docs:
https://abyz.me.uk/lg/py_lgpio.html

'''
import lgpio


TOUCH_PIN = 17
touch_count = 0
TIMEOUT = 0.5
PRESS_WAIT = 0.4
last_press = time.time()

h = lgpio.gpiochip_open(0) # init
lgpio.gpio_claim_input(h, TOUCH_PIN)

last_state = 0

def read_touch():
  print("awaiting input...")
  try:
  	while True:
  		current_state = lgpio.gpio_read(h, TOUCH_PIN)
  
  		if current_state == 1 and last_state == 0:  # rising edge
  			if time.time() - last_press > TIMEOUT:
  				touch_count = 0
  			touch_count += 1
  			last_press = time.time()
        
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


def listen():
  # speech recog
  r = sr.Recognizer()
  with sr.Microphone() as source:
  	print("Say something")
   	audio = r.listen(source)
  
  # Speech Recognition Engine: Sphinx (CMU)
  try:
  	print("What you said: " + r.recognize_sphinx(audio))
  except sr.UnknownValueError:
  	print("Audio not recognized")
  except sr.RequestError as e:
  	print("Sphinx error; {0}".format(e))
