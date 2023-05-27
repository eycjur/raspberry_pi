import utime


def get_time() -> tuple:
    return utime.localtime()


def get_time_str() -> str:
    return timetuple2str(get_time())


def timetuple2str(timetuple: tuple) -> str:
    return f"{timetuple[0]}-{timetuple[1]}-{timetuple[2]} {timetuple[3]}:{timetuple[4]}:{timetuple[5]}"
