'''
Audio Script

Functions:
Speech Recognition for audio prompts
Text to Speech 

Speech Recognition Reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
TTS Reference: https://pypi.org/project/pyttsx3/
'''

import pyttsx3
import speech_recognition as sr


def tts():
	#engine = pyttsx3.init()
	#engine.say("hello, world")
	#engine.runAndWait()


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
