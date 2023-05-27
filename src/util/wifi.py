import network
import uasyncio
from src.secret import WIFI_SSID, WIFI_PASS
from src.errors import WifiConnectionTimeoutError


async def prepare_wifi():
    """wifiの設定を行うためのモジュール

    Example:
        >>> import urequests
        >>> r = urequests.get('https://umayadia-apisample.azurewebsites.net/api/persons/Shakespeare')
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(WIFI_SSID, WIFI_PASS)

    for i in range(10):
        status = wlan.status()
        if wlan.status() < 0 or wlan.status() >= network.STAT_GOT_IP:
            break
        print(f'Waiting for connection... status={status}')
        uasyncio.sleep(1)
    else:  # breakしなかった場合
        raise WifiConnectionTimeoutError('Wifi connection timed out.')

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise WifiConnectionTimeoutError(
            'Wi-Fi connection failed. status={}'.format(wlan_status))

    print('Wi-fi ready. ifconfig:', wlan.ifconfig())
    return wlan
