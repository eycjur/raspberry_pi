from machine import I2C, Pin, PWM, ADC
import utime

from src.errors import ConnectionError, UltrasonicSensorTimeoutError
from src.const import (
    SERVO_MOTOR_WAIT_TIME_SEC,
    ULTRASONIC_SENSOR_MEASURE_INTERVAL_SEC,
    I2C_FREQUENCY_HZ,
    PWM_FREQUENCY_HZ,
    ULTRASONIC_SENSOR_MAX_TRY
)


class TemperatureSensor:
    """基板上の温度センサから温度情報を取得するクラス

    Examples:
        >>> temperature = device.Temperature(num_in=4)
        >>> temperature.measure()
        25.0
    """
    conversion_factor = 3.3 / (65535)

    def __init__(self, num_in: int) -> None:
        self.adc = ADC(num_in)

    def measure(self) -> float:
        """温度を測定する

        Returns:
            float: 温度
        """
        # 整数値から電圧に変換
        reading = self.adc.read_u16() * self.conversion_factor
        # 27℃のときの電圧が0.706V、温度が1℃上がると電圧が0.001721V減少する
        return 27 - (reading - 0.706) / 0.001721


class LED:
    """LED（発光ダイオード）を制御するクラス

    - 基板上のLEDを利用する場合は、num_outに25を指定する

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
        """LEDを点灯する"""
        self.pin.value(1)

    def turn_off(self) -> None:
        """LEDを消灯する"""
        self.pin.value(0)


class Button:
    """ボタンを制御するクラス

    Examples:
        >>> button = device.Button(num_in=16)
        >>> button.is_push()
        True

    Hint:
        3V3(OUT) → ボタン → GPIO16の順に接続
    """
    def __init__(self, num_in: int) -> None:
        self.pin = Pin(num_in, Pin.IN, Pin.PULL_DOWN)

    def is_push(self) -> bool:
        """ボタンが押されているかを返す

        Returns:
            bool: ボタンが押されているか
        """
        return self.pin.value()


class MotionSensor:
    """モーションセンサーを制御するクラス

    Examples:
        >>> motion_sensor = device.MotionSensor(num_in=17)
        >>> motion_sensor.is_detect()
        True
    """
    def __init__(self, num_in: int) -> None:
        self.pin = Pin(num_in, Pin.IN, Pin.PULL_DOWN)

    def is_detect(self) -> bool:
        """モーションを検知しているかを返す

        Returns:
            bool: モーションを検知しているか
        """
        return self.pin.value()


class AMeDASMeasurement:
    """気圧、温度、湿度を表すクラス"""
    def __init__(self, values: list) -> None:
        temperature, pressure, humidity = values
        self.pressure = float(pressure[:-3])
        self.temperature = float(temperature[:-1])
        self.humidity = float(humidity[:-1])

    def __str__(self):
        return (
            f"{self.pressure:.02f}hPa, {self.temperature:.02f}C, "
            + f"{self.humidity:.02f}%"
        )


class AMeDAS:
    """気圧、温度、湿度を測定するクラス

    Examples:
        >>> amedas = device.AMeDAS(num_sda=12, num_scl=13)
        >>> amedas.measure()
        1013.25hPa, 25.00C, 50.00%

    Hint:
        | BME280 | Pico     |
        | ------ | -------- |
        | VCC    | 3V3(OUT) |
        | GND    | GND      |
        | SCL    | GP13     |  # 利用できるピンが限られているので注意
        | SDA    | GP12     |
        | CSB    |          |
        | SDO    | GND      |  # I2CかSPIかを決めるピン。GNDでI2C
    """
    def __init__(self, num_sda: int, num_scl: int) -> None:
        import bme280  # need: micropython-bme280

        i2c = I2C(
            id=0, sda=Pin(num_sda), scl=Pin(num_scl), freq=I2C_FREQUENCY_HZ
        )
        if not i2c.scan():
            raise ConnectionError("i2cの接続が正しくありません")
        self.bme = bme280.BME280(i2c=i2c)

    def measure(self) -> AMeDASMeasurement:
        """気圧、温度、湿度を測定する

        Returns:
            AMeDASMeasurement: 気圧、温度、湿度を表すクラス
        """
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
        | LCD | Pico     |
        | --- | -------- |
        | VCC | 3V3(OUT) |
        | GND | GND      |
        | SDA | GP12     |
        | SCL | GP13     |
    """

    def __init__(self, num_sda: int, num_scl: int) -> None:
        from machine_i2c_lcd import I2cLcd

        I2C_ADDR = 0x27
        i2c = I2C(
            id=0, sda=Pin(num_sda), scl=Pin(num_scl), freq=I2C_FREQUENCY_HZ
        )
        if not i2c.scan():
            raise ConnectionError("i2cの接続が正しくありません")
        self.lcd = I2cLcd(i2c, I2C_ADDR, num_lines=2, num_columns=16)
        self.clear()

    def print(self, value) -> None:
        """LCDに文字列を表示する

        Args:
            value (str): 表示する文字列
        """
        self.clear()
        self.lcd.putstr(str(value))

    def clear(self) -> None:
        """LCDに表示されている文字列を消去する"""
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
        | SG90    | Pico     |
        | ------- | -------  |
        | VCC(赤) | 3V3(OUT) |
        | GND(茶) | GND      |
        | PWM(黃) | GP1      |
    """
    def __init__(self, num_pwm: int) -> None:
        self.pwm = PWM(Pin(num_pwm))
        self.pwm.freq(PWM_FREQUENCY_HZ)

    def _degree2servo_value(self, degree):
        """角度をサーボモーターの値に変換する

        Args:
            degree (int): 角度(-90~90)
                負の値は右に、正の値は左に回転する

        Returns:
            int: サーボモーターの値
        """
        duty_ms = (degree + 90) / 180 * 1.9 + 0.5
        duty_ratio = duty_ms / (1000 / PWM_FREQUENCY_HZ)
        return int(duty_ratio * 65535)

    def set_angle(self, degree: int) -> None:
        """サーボモーターの角度を設定する

        Args:
            degree (int): 角度(-90~90)
        """
        self.pwm.duty_u16(self._degree2servo_value(degree))
        utime.sleep(SERVO_MOTOR_WAIT_TIME_SEC)  # サーボモーターが回転するのを待つ


class UltrasonicSensor:
    """超音波センサーを制御するクラス

    References:
        https://akizukidenshi.com/download/ds/rainbow_e-technology/hc-sr04_v20.pdf

    Examples:
        >>> sensor = device.UltrasonicSensor(num_trigger=14, num_echo=15)
        >>> sensor.measure()
        0.0

    Hint:
        | HC-SR04 | Pico     |
        | ------- | -------  |
        | VCC     | 3V3(OUT) |
        | GND     | GND      |
        | TRIG    | GP14     |
        | ECHO    | GP15     |  # 5Vの信号を受け取るので分圧が必要
        ECHO -> 1kΩ -> 2kΩ -> GND
                    └> GP15
    """
    def __init__(self, num_trigger: int, num_echo: int) -> None:
        self.trigger = Pin(num_trigger, Pin.OUT)
        self.echo = Pin(num_echo, Pin.IN)

    def measure(self) -> float:
        """距離を測定する

        - 3回の測定のうち、中央値を返す

        Returns:
            float: 距離（単位：cm）
        """
        distances = []
        for _ in range(3):
            distances.append(self._measure_once())
            utime.sleep(ULTRASONIC_SENSOR_MEASURE_INTERVAL_SEC)
        distances = sorted(distances)
        return distances[1]

    def _measure_once(self) -> float:
        """一回距離を測定する

        Returns:
            float: 距離（単位：cm）
        """
        self.trigger.low()
        utime.sleep_us(2)
        self.trigger.high()
        utime.sleep(0.00001)
        self.trigger.low()

        for i in range(ULTRASONIC_SENSOR_MAX_TRY):
            if self.echo.value() != 0:
                signaloff = utime.ticks_us()
                break
            utime.sleep_us(1)
        else:  # breakしなかった場合
            raise UltrasonicSensorTimeoutError("センサーの値を読み取れませんでした")
        for i in range(ULTRASONIC_SENSOR_MAX_TRY):
            if self.echo.value() != 1:
                signalon = utime.ticks_us()
                break
            utime.sleep_us(1)
        else:  # breakしなかった場合
            raise UltrasonicSensorTimeoutError("センサーの値を読み取れませんでした")

        timepassed_s = (signalon - signaloff) / 1000 / 1000  # μs -> s
        distance_m = (timepassed_s * 342.62) / 2  # 20℃
        return distance_m * 100  # m -> cm


class IndividualMotorDriver:
    """個別のモーターを制御するクラス"""
    def __init__(self, num_in_1, num_in_2) -> None:
        self.in_1 = Pin(num_in_1, Pin.OUT)
        self.in_2 = Pin(num_in_2, Pin.OUT)

    def forward_rotation(self) -> None:
        """正転"""
        self.in_1.value(1)
        self.in_2.value(0)

    def reverse_rotation(self) -> None:
        """逆転"""
        self.in_1.value(0)
        self.in_2.value(1)

    def brake(self) -> None:
        """ブレーキ"""
        self.in_1.value(1)
        self.in_2.value(1)

    def idle(self) -> None:
        """空転"""
        self.in_1.value(0)
        self.in_2.value(0)


class MotorDriver:
    """モータードライバーを制御するクラス

    References:
        https://akizukidenshi.com/download/ds/akizuki/AE-DRV8835-S_20210526.pdf

    Examples:
        >>> motor_driver = device.MotorDriver(
        >>>     num_a_in_1=15, num_a_in_2=14, num_b_in_1=13, num_b_in_2=12
        >>> )
        >>> motor_driver.forward()
        >>> motor_driver.right()
        >>> motor_driver.left()
        >>> motor_driver.backward()
        >>> motor_driver.stop()
        >>> motor_driver.release()

    Hint:
        | DRV8835 | Pico       |
        | ------- | ---------- |
        | VM      | 3V3(OUT)   |
        | AOUT1   | motor(左上) |
        | AOUT2   | motor(左下) |
        | BOUT1   | motor(右上) |
        | BOUT2   | motor(右下) |
        | GND     | GND        |
        | VCC     | Vbus       |
        | MODE    | GND        |  # 0でIN/INモード、1でPH/ENモード
        | AIN1    | GP15       |
        | AIN2    | GP14       |
        | BIN1    | GP13       |
        | BIN2    | GP12       |
    """
    def __init__(self, num_a_in_1, num_a_in_2, num_b_in_1, num_b_in_2) -> None:
        self.motor_left = IndividualMotorDriver(num_a_in_1, num_a_in_2)
        self.motor_right = IndividualMotorDriver(num_b_in_1, num_b_in_2)

    def forward(self) -> None:
        """前進"""
        self.motor_left.forward_rotation()
        self.motor_right.forward_rotation()

    def right(self) -> None:
        """右に進む"""
        self.motor_left.forward_rotation()
        self.motor_right.reverse_rotation()

    def left(self) -> None:
        """左に進む"""
        self.motor_left.reverse_rotation()
        self.motor_right.forward_rotation()

    def backward(self) -> None:
        """後進"""
        self.motor_left.reverse_rotation()
        self.motor_right.reverse_rotation()

    def stop(self) -> None:
        """停止"""
        self.motor_left.brake()
        self.motor_right.brake()

    def release(self) -> None:
        """慣性で回転"""
        self.motor_left.idle()
        self.motor_right.idle()
