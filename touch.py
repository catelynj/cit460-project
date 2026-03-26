'''
Touch Sensor Control Script

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
