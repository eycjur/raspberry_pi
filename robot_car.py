import utime

from src import device
from src.errors import UltrasonicSensorTimeoutError, TemperatureExtremeError
from src.dataclasses import Distance
from src.const import ALLOW_TEMPERATURE_MAX
from src.util.judge import is_wifi_usable  # noqa: F401
from src.util.logging import CustomLogging

if is_wifi_usable():
    import uasyncio
    from src.util.wifi import prepare_wifi

    wlan = uasyncio.run(prepare_wifi())

logger = CustomLogging()

temperature_sensor = device.TemperatureSensor(num_in=4)
servo_motor = device.ServoMotor(num_pwm=1)
sensor = device.UltrasonicSensor(num_trigger=14, num_echo=15)
motor_driver = device.MotorDriver(
    num_a_in_1=19,
    num_a_in_2=18,
    num_b_in_1=17,
    num_b_in_2=16
)


def run():
    while True:
        temperature = temperature_sensor.measure()
        logger.write(temperature)
        if temperature > ALLOW_TEMPERATURE_MAX:  # 温度が上がりすぎたら停止
            raise TemperatureExtremeError(
                f"Temperature is too high: {temperature}℃"
            )

        try:
            list_distance = []
            for angle in [-60, 0, 60]:
                servo_motor.set_angle(angle)
                list_distance += [sensor.measure()]
            distance = Distance(
                left=list_distance[2],
                front=list_distance[1],
                right=list_distance[0]
            )
            logger.write(distance)
        except UltrasonicSensorTimeoutError:
            logger.write("UltrasonicSensorTimeoutError")
            motor_driver.stop()
        else:  # 正常に終了した場合
            if distance.front > 40:
                motor_driver.forward()
                continue
            if distance.left < 20 and distance.right < 20:
                motor_driver.backward()
            if distance.left < distance.right:
                motor_driver.right()
            else:  # distance.left >= distance.right
                motor_driver.left()

        utime.sleep(1)


try:
    run()
except Exception as e:
    logger.write(str(e))
    raise e
finally:
    motor_driver.stop()
