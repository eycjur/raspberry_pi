import utime


def get_time():
    timestamp = utime.time()
    return utime.localtime(timestamp)
