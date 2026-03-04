
'''
API RESPONSE TEST SCRIPT
'''
from dotenv import load_dotenv
import os
import requests
import translators as ts
import wolframalpha
import pyttsx3

load_dotenv()

app_id = os.getenv("APP_ID")

# translate test
q_text = "hello, goodbye"

#_ = ts.preaccelerate_and_speedtest() # caching available will work on adding later
# print(ts.translators_pool) # see available translators
translation = ts.translate_text(query_text=q_text, translator="google", to_language="ja")
print(translation)

# text to speech test (NOT WORKING YAY)
#engine = pyttsx3.init()
#engine.say("hello, world")
#engine.runAndWait()

# wolfram test
client = wolframalpha.Client(app_id)
query = "What is the temperature in Williamsport, PA?"
params = {
"appid": app_id,
"i": query
}

response = requests.get("http://api.wolframalpha.com/v1/result", params=params)

print(response.text)




 
