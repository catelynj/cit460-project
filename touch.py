'''
Touch Sensor Control Script

'''
import lgpio

TOUCH_PIN = 17

h = lgpio.gpiochip_open(0) # init
lgpio.gpio_claim_input(h, TOUCH_PIN)

def read_touch(h, touch_pin):
    return lgpio.gpio_read(h, touch_pin)

