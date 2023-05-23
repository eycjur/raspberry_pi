import sys

USE_WIFI = False

if "MicroPython" in sys.version:
    print("use micropython")
    from for_micropython import device
    from for_micropython import util  # noqa: F401
    if USE_WIFI:
        from for_micropython import util4w  # noqa: F401

else:
    print("use circuitpython")
    from for_circuitpython import device  # noqa: F401
