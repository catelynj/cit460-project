
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
	if not text or not text.strip():
        return ""
    try:
        translation = ts.translate_text(query_text=text, translator="google", to_language="en")
        print(translation)
        return translation
    except Exception as e:
        print(f"translation error: {e}")
        return ""

def wolfram(prompt):
	client = wolframalpha.Client(app_id)
	params = {
		"appid": app_id,
		"i": prompt
	}
	response = requests.get("http://api.wolframalpha.com/v1/result", params=params)
	return response.text


