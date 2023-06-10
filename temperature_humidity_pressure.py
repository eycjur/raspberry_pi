import utime

from src import device

amedas = device.AMeDAS(num_sda=12, num_scl=13)
display = device.Display(num_sda=12, num_scl=13)

while True:
    display.print(amedas.measure())
    utime.sleep(1)
