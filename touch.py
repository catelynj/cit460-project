'''
Touch Sensor Control Script

'''
import lgpio

TOUCH_PIN = 17
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, TOUCH_PIN)

def read_touch():
    return lgpio.gpio_read(h, TOUCH_PIN)

