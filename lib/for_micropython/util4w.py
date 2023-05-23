"""wifiの設定を行うためのモジュール

Example:
    >>> import uasyncio
    >>> import urequests
    >>> import util4w
    >>> wlan = uasyncio.run(util4w.prepare_wifi())
    >>> r = urequests.get('https://umayadia-apisample.azurewebsites.net/api/persons/Shakespeare')
"""

import network
import uasyncio
from secret import WIFI_SSID, WIFI_PASS


async def prepare_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    wlan.connect(WIFI_SSID, WIFI_PASS)

    for i in range(10):
        status = wlan.status()
        if wlan.status() < 0 or wlan.status() >= network.STAT_GOT_IP:
            break
        print(f'Waiting for connection... status={status}')
        uasyncio.sleep(1)
    else:
        raise RuntimeError('Wifi connection timed out.')

    wlan_status = wlan.status()

    if wlan_status != network.STAT_GOT_IP:
        raise RuntimeError(
            'Wi-Fi connection failed. status={}'.format(wlan_status))

    print('Wi-fi ready. ifconfig:', wlan.ifconfig())
    return wlan
