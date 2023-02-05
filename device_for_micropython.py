from machine import I2C, Pin


class ConnectionError(Exception):
    pass


class LED:
    def __init__(self, num_out: int) -> None:
        self.pin = Pin(num_out, Pin.OUT)

    def turn_on(self) -> None:
        self.pin.value(1)

    def turn_off(self) -> None:
        self.pin.value(0)


class Button:
    def __init__(self, num_in: int) -> None:
        self.pin = Pin(num_in, Pin.IN, Pin.PULL_DOWN)

    def is_push(self) -> bool:
        return self.pin.value()


class MotionSensor:
    def __init__(self, num_in: int) -> None:
        self.pin = Pin(20, Pin.IN, Pin.PULL_DOWN)

    def is_detect(self) -> bool:
        return self.pin.value()


class AMeDASMeasurement:
    def __init__(self, values: list) -> None:
        temperature, pressure, humidity = values
        self.pressure = float(pressure[:-3])
        self.temperature = float(temperature[:-1])
        self.humidity = float(humidity[:-1])

    def __str__(self):
        return (
            f"{self.pressure:.02f}hPa, {self.temperature:.02f}C, {self.humidity:.02f}%"
        )


class AMeDAS:
    def __init__(self, num_sda: int, num_scl: int) -> None:
        import bme280  # need: micropython-bme280

        i2c = I2C(0, sda=Pin(num_sda), scl=Pin(num_scl), freq=400000)
        if not i2c.scan():
            raise ConnectionError("i2cの接続が正しくありません")
        self.bme = bme280.BME280(i2c=i2c)

    def measure(self) -> AMeDASMeasurement:
        return AMeDASMeasurement(self.bme.values)


class Display:
    """次のコードを保存しておく
    https://github.com/dhylands/python_lcd/blob/master/lcd/machine_i2c_lcd.py
    https://github.com/dhylands/python_lcd/blob/master/lcd/lcd_api.py
    """

    def __init__(self, num_sda: int, num_scl: int) -> None:
        from machine_i2c_lcd import I2cLcd

        I2C_ADDR = 0x27
        i2c = I2C(0, sda=Pin(num_sda), scl=Pin(num_scl), freq=400000)
        if not i2c.scan():
            raise ConnectionError("i2cの接続が正しくありません")
        self.lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
        self.clear()

    def print(self, value) -> None:
        self.clear()
        self.lcd.putstr(str(value))

    def clear(self) -> None:
        self.lcd.clear()
