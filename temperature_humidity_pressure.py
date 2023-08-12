import utime

from src import device
from src.util.logging import CustomLogging
from src.util.judge import is_wifi_usable  # noqa: F401

if is_wifi_usable():
    import uasyncio
    from src.util.wifi import prepare_wifi

    wlan = uasyncio.run(prepare_wifi())

logger = CustomLogging()

amedas = device.AMeDAS(num_sda=12, num_scl=13)
display = device.Display(num_sda=12, num_scl=13)


def run():
    while True:
        measurement = amedas.measure()
        display.print(measurement)
        logger.write(measurement)
        utime.sleep(10)


try:
    run()
except Exception as e:
    logger.write(str(e))
    raise e
