import utime

import device
from util.judge import is_wifi_usable  # noqa: F401
from util.wifi import prepare_wifi
from util.errors import TimeoutError
from util.logging import CustomLogging


if is_wifi_usable():
    import uasyncio

    wlan = uasyncio.run(prepare_wifi())

logger = CustomLogging()

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
        try:
            list_distance = []
            for angle in [-60, -30, 0, 30, 60]:
                servo_motor.set_angle(angle)
                list_distance += [sensor.measure()]
                utime.sleep(0.2)
            print(f"list_distance{list_distance}")
        except TimeoutError:
            logger.write("TimeoutError")
            motor_driver.stop()
        else:  # 正常に終了した場合
            if list_distance[2] < 20:
                if list_distance[0] < 10 and list_distance[4] < 10:
                    motor_driver.backward()
                if list_distance[0] < list_distance[4]:
                    motor_driver.left()
                else:
                    motor_driver.right()
            else:
                motor_driver.forward()

        utime.sleep(1)


try:
    run()
except Exception as e:
    logger.write(str(e))
    raise e
finally:
    motor_driver.stop()
