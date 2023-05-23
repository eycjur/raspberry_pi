from machine import I2C, Pin, PWM
import utime

from errors import ConnectionError


class LED:
    """LED（発光ダイオード）を制御するクラス

    Examples:
        >>> led = device.LED(num_out=15)
        >>> led.turn_on()
        >>> led.turn_off()

    Hint:
        GPIO15 → 抵抗(220Ω) → LED（長い方） → LED（短い方） → グランドの順に接続
    """
    def __init__(self, num_out: int) -> None:
        self.pin = Pin(num_out, Pin.OUT)

    def turn_on(self) -> None:
        self.pin.value(1)

    def turn_off(self) -> None:
        self.pin.value(0)


class Button:
    """ボタンを制御するクラス

    Examples:
        >>> button = device.Button(num_in=16)
        >>> button.is_push()
        True

    Hint:
        3V3 → ボタン → GPIO16の順に接続
    """
    def __init__(self, num_in: int) -> None:
        self.pin = Pin(num_in, Pin.IN, Pin.PULL_DOWN)

    def is_push(self) -> bool:
        return self.pin.value()


class MotionSensor:
    """モーションセンサーを制御するクラス

    Examples:
        >>> motion_sensor = device.MotionSensor(num_in=17)
        >>> motion_sensor.is_detect()
        True
    """
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
    """気圧、温度、湿度を表すクラス

    Examples:
        >>> amedas = device.AMeDAS(num_sda=12, num_scl=13)
        >>> amedas.measure()
        1013.25hPa, 25.00C, 50.00%

    Hint:
        | BME280 | Pico |
        | ------ | ---- |
        | VCC    | 3V3  |
        | GND    | GND  |
        | SCL    | GP13 |  # 利用できるピンが限られているので注意
        | SDA    | GP12 |
        | CSB    |      |
        | SDO    | GND  |  # I2CかSPIかを決めるピン。GNDでI2C
    """
    def __init__(self, num_sda: int, num_scl: int) -> None:
        import bme280  # need: micropython-bme280

        i2c = I2C(0, sda=Pin(num_sda), scl=Pin(num_scl), freq=400000)
        if not i2c.scan():
            raise ConnectionError("i2cの接続が正しくありません")
        self.bme = bme280.BME280(i2c=i2c)

    def measure(self) -> AMeDASMeasurement:
        return AMeDASMeasurement(self.bme.values)


class Display:
    """LCDを制御するクラス

    次のコードを保存しておく
    https://github.com/dhylands/python_lcd/blob/master/lcd/machine_i2c_lcd.py
    https://github.com/dhylands/python_lcd/blob/master/lcd/lcd_api.py

    Examples:
        >>> display = device.Display(num_sda=12, num_scl=13)
        >>> display.print("Hello, world!")

    Hint:
        | LCD | Pico |
        | --- | ---- |
        | VCC | Vbus |
        | GND | GND  |
        | SDA | GP12 |
        | SCL | GP13 |
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


class ServoMotor:
    """サーボモーター（回転を実現するモーター）を制御するクラス

    References:
        https://akizukidenshi.com/download/ds/towerpro/SG90_a.pdf

    Examples:
        >>> servo_motor = device.ServoMotor(num_pwm=1)
        >>> for ang in [-60, -30, 0, 30, 60]:
        >>>     servo_motor.set_angle(ang)
        >>>     time.sleep(1)

    Hint:
        | SG90    | Pico |
        | ----    | ---- |
        | VCC(赤) | Vbus |
        | GND(茶) | GND  |
        | PWM(黃) | GP1  |
    """
    def __init__(self, num_pwm: int) -> None:
        self.pwm = PWM(Pin(num_pwm))
        self.pwm.freq(50)

    def _degree2servo_value(self, degree):
        duty_ms = (degree + 90) / 180 * 1.9 + 0.5
        duty_ratio = duty_ms / 20  # 50Hz
        return int(duty_ratio * 65535)

    def set_angle(self, degree: int) -> None:
        self.pwm.duty_u16(self._degree2servo_value(degree))


class UltrasonicSensor:
    """超音波センサーを制御するクラス

    References:
        https://akizukidenshi.com/download/ds/rainbow_e-technology/hc-sr04_v20.pdf

    Examples:
        >>> sensor = device.UltrasonicSensor(num_trigger=14, num_echo=15)
        >>> sensor.measure()
        0.0

    Hint:
        | HC-SR04 | Pico |
        | ------- | ---- |
        | VCC     | Vsys |
        | GND     | GND  |
        | TRIG    | GP14 |
        | ECHO    | GP15 |  # 5Vの信号を受け取るので分圧が必要
        ECHO -> 1kΩ -> 2kΩ -> GND
                    └> GP15
    """
    def __init__(self, num_trigger: int, num_echo: int) -> None:
        self.trigger = Pin(num_trigger, Pin.OUT)
        self.echo = Pin(num_echo, Pin.IN)

    def measure(self) -> float:
        """距離を測定する

        Returns:
            float: 距離（単位：cm）
        """
        self.trigger.low()
        utime.sleep_us(2)
        self.trigger.high()
        utime.sleep(0.00001)
        self.trigger.low()
        while self.echo.value() == 0:
            signaloff = utime.ticks_us()
        while self.echo.value() == 1:
            signalon = utime.ticks_us()
        timepassed_s = (signalon - signaloff) / 1000000
        distance_m = (timepassed_s * 342.62) / 2  # 20℃
        return distance_m * 100
