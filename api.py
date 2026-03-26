
'''
API RESPONSE TEST SCRIPT

Speech Recognition Reference: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
'''
from dotenv import load_dotenv
import os
import requests
import translators as ts
import wolframalpha
import pyttsx3
import speech_recognition as sr

load_dotenv()

app_id = os.getenv("APP_ID")

# translate test
q_text = "hello, goodbye"

#_ = ts.preaccelerate_and_speedtest() # caching available will work on adding later
translation = ts.translate_text(query_text=q_text, translator="google", to_language="ja")
print(translation)

# text to speech test (NOT WORKING YAY)
#engine = pyttsx3.init()
#engine.say("hello, world")
#engine.runAndWait()


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

# wolfram test
client = wolframalpha.Client(app_id)
query = "What is the temperature in Williamsport, PA?"
params = {
"appid": app_id,
"i": query
}

response = requests.get("http://api.wolframalpha.com/v1/result", params=params)

print(response.text)




 
