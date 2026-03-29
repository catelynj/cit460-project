"""
Modified from Raspberry Pi Touch Sensor Tutorial by newbiely.com
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-touch-sensor

"""
import os
import numpy as np
import time
# my scripts
from api import wolfram, translate 
from audio import tts, listen 
from touch import read_touch, close_touch
from camera import start_recording,stop_recording,take_picture,snapshot,ocr

#touch sensor
touch_count = 0
TIMEOUT = 0.5
PRESS_WAIT = 0.4
last_press = time.time()
last_state = 0
recording = False

print("awaiting input...")
try:
    while True:
        current_state = read_touch()

        if current_state == 1 and last_state == 0:
            if time.time() - last_press > TIMEOUT:
                touch_count = 0
            touch_count += 1
            last_press = time.time()

        if recording and touch_count >= 3:
            stop_recording()
            recording = False
            tts("beep")
            touch_count = 0

        elif touch_count > 0 and time.time() - last_press > PRESS_WAIT:
            if touch_count == 1:
                print("listening for prompt...")
                val = listen()
                val = val.lower() # 'translate' auto capitalizes 
                print(f"heard: {val}")
                
                if val is None:
                    tts("sorry, i didn't catch that.")
                else:
                    if 'exit' in val:
                        tts("shutting down")
                        break
                    elif 'ask' in val  or 'question' in val:
                        tts("state your question")
                        time.sleep(2.0)
                        print("listening...")
                        question = listen(dur=10)
                        print(f"heard: {question}")
                        print("calling wolfram")
                        answer = wolfram(question)
                        print(answer)
                        tts(answer)
                    elif 'translate' in val:
                        print("'translate' heard")
                        #snapshot() # hardcoded for testing
                        #tts("picture taken, please wait for translation")
                        tts("wait for translation")
                        #print("picture taken, calling ocr")
                        text = ocr()
                        print("ocr called. calling translate")
                        translation = translate(text)
                        tts(translation)
                        print("translation completed: " + translation)
                    else:
                        tts("command not recognized")
                        print("command not recognized, exiting prompt")
            elif touch_count == 2:
                take_picture()
            elif touch_count >= 3:
                start_recording()
                recording = True
                tts("beep")
            touch_count = 0

        last_state = current_state
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    close_touch()
