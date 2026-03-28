
'''
API RESPONSE TEST SCRIPT
'''
from dotenv import load_dotenv
import os
import requests
import translators as ts
import wolframalpha

load_dotenv()
app_id = os.getenv("APP_ID")

def translate(text):
	#_ = ts.preaccelerate_and_speedtest() # caching available will work on adding later
	translation = ts.translate_text(query_text=text, translator="google")
	print(translation)

def wolfram(prompt):
	client = wolframalpha.Client(app_id)
	params = {
		"appid": app_id,
		"i": prompt
	}
	response = requests.get("http://api.wolframalpha.com/v1/result", params=params)
	print(response.text)


