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
import speech_recognition as sr

TOUCH_PIN = 17

h = lgpio.gpiochip_open(0) # init
lgpio.gpio_claim_input(h, TOUCH_PIN)

def read_touch(h, touch_pin):
    return lgpio.gpio_read(h, touch_pin)

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
