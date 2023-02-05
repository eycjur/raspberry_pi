import device_for_circuitpython as device
import time


# button = device.Button(num_in=16)
# led = device.LED(num_out=15)
# while True:
#     if button.is_push():
#         led.turn_on()
#     else:
#         led.turn_off()
#     utime.sleep(1)

# motion_sensor = device.MotionSensor(num_in=20)

display = device.Display(num_sda=12, num_scl=13)
amedas = device.AMeDAS(num_sda=12, num_scl=13)

while True:
    print(amedas.measure())
    display.print(amedas.measure())
    time.sleep(1)
