import board
import busio
import digitalio

PIN_PREFIX = "GP"
i2c = None


class ConnectionError(Exception):
    pass


class LED:
    def __init__(self, num_out: int) -> None:
        self.pin = digitalio.DigitalInOut(getattr(board, f"{PIN_PREFIX}{num_out}"))
        self.pin.direction = digitalio.Direction.OUTPUT

    def turn_on(self) -> None:
        self.pin.value = True

    def turn_off(self) -> None:
        self.pin.value = False


# class Button:
#     def __init__(self, num_in: int) -> None:
#         self.pin = digitalio.DigitalInOut(getattr(board, f"{PIN_PREFIX}{num_in}"))
#         self.pin.direction = digitalio.Direction.INPUT
#         self.pin.pull = digitalio.Pull.DOWN

#     def is_push(self) -> bool:
#         return self.pin.value


# class MotionSensor:
#     def __init__(self, num_in: int) -> None:
#         self.pin = digitalio.DigitalInOut(getattr(board, f"{PIN_PREFIX}{num_in}"))
#         self.pin.direction = digitalio.Direction.INPUT
#         self.pin.pull = digitalio.Pull.DOWN

#     def is_detect(self) -> bool:
#         return self.pin.value


class AMeDASMeasurement:
    def __init__(self, bme) -> None:
        self.pressure = bme.pressure
        self.temperature = bme.temperature
        self.humidity = bme.relative_humidity

    def __str__(self):
        return (
            f"{self.pressure:.02f}hPa, {self.temperature:.02f}C, {self.humidity:.02f}%"
        )


class AMeDAS:
    def __init__(self, num_sda: int, num_scl: int) -> None:
        # needs: adafruit-circuitpython-bme280（インストールエラーが出るのでファイルをコピーする）
        from adafruit_bme280 import basic as adafruit_bme280

        global i2c
        if not i2c:
            i2c = busio.I2C(
                getattr(board, f"{PIN_PREFIX}{num_scl}"),
                getattr(board, f"{PIN_PREFIX}{num_sda}"),
            )
            while not i2c.try_lock():
                pass

        self.bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

    def measure(self) -> AMeDASMeasurement:
        return AMeDASMeasurement(self.bme)


class Display:
    """次のコードを保存しておく
    https://github.com/dhylands/python_lcd/blob/master/lcd/circuitpython_i2c_lcd.py
    https://github.com/dhylands/python_lcd/blob/master/lcd/lcd_api.py
    """

    def __init__(self, num_sda: int, num_scl: int) -> None:
        from circuitpython_i2c_lcd import I2cLcd

        global i2c
        I2C_ADDR = 0x27
        if not i2c:
            i2c = busio.I2C(
                getattr(board, f"{PIN_PREFIX}{num_scl}"),
                getattr(board, f"{PIN_PREFIX}{num_sda}"),
            )
            while not i2c.try_lock():
                pass

        self.lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
        self.clear()

    def print(self, value) -> None:
        self.clear()
        self.lcd.putstr(str(value))

    def clear(self) -> None:
        self.lcd.clear()
