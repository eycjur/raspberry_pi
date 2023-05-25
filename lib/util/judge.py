import sys


def is_wifi_usable() -> bool:
    """wifiが使えるかどうかを判定する

    Returns:
        bool: wifiが使えるかどうか
    """
    try:
        import urequests  # noqa: F401
        return True
        print("use wifi")
    except ImportError:
        return False
        print("not use wifi")


def is_micropython() -> bool:
    """micropythonかどうかを判定する

    Returns:
        bool: micropythonかどうか
    """
    return "MicroPython" in sys.version
