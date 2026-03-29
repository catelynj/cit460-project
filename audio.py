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
import time
import os

def tts(phrase):
  engine = pyttsx3.init()
  engine.setProperty('rate', 150)
  engine.say(" ")
  engine.runAndWait()
  engine.say(phrase)
  engine.runAndWait()
  engine.stop()


def listen():
  # flag defs: '-d (time), -f (quality), -t (file type), -D (audio device) 
  os.system('arecord -d 4 -f cd -t wav -D pulse prompt.wav')
  r = sr.Recognizer()
  try:
    prompt = sr.AudioFile('prompt.wav')
    with prompt as source:
      audio = r.record(source)
    val = r.recognize_sphinx(audio) # Speech Recognition Engine: Sphinx (CMU)
    return val
  except sr.UnknownValueError:
    print("Audio not recognized")
    return ""
  except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
    return ""

