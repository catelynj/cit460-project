'''
Audio Script

Functions:
Speech Recognition for audio prompts
Text to Speech 

Speech Recognition Reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
TTS Reference: https://pypi.org/project/pyttsx3/
'''

import pyttsx3
import subprocess
import speech_recognition as sr
import time
import os

def tts(phrase):
  engine = pyttsx3.init()
  engine.setProperty('rate', 140)
  engine.setProperty('volume', 1.0)
  engine.say(".")
  engine.runAndWait()
  engine.say(phrase)
  engine.runAndWait()
  engine.stop()

#tts("hello goodbye how are you")


def listen(dur=4):
  try:
    print(f"[{time.time():.2f}] recording started")
    subprocess.run(['parecord', '--file-format=wav', '--channels=1', 'prompt_raw.wav'], timeout=dur)
    print(f"[{time.time():.2f}] recording stopped")
  except subprocess.TimeoutExpired:
    pass
  time.sleep(0.5)
  subprocess.run(['ffmpeg', '-y', '-i', 'prompt_raw.wav', 'prompt.wav'],capture_output=True)
  
  
  r = sr.Recognizer()
  try:
    prompt = sr.AudioFile('prompt.wav')
    with prompt as source:
      print(f"[{time.time():.2f}] reading audio file")
      audio = r.record(source)
    print(f"[{time.time():.2f}] sending to google")
    result = r.recognize_google(audio)
    print(f"[{time.time():.2f}] got result: {result}")
    return result
  except sr.UnknownValueError:
    print(f"[{time.time():.2f}] not recognized")
    return ""
  except sr.RequestError as e:
    print(f"[{time.time():.2f}] error: {e}")
    return ""
