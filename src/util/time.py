import utime
import ntptime


class Time:
    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
    ) -> None:
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second

    def __str__(self) -> str:
        return (
            f"{self._year:04d}-{self._month:02d}-{self._day:02d} "
            + f"{self._hour:02d}:{self._minute:02d}:{self._second:02d}"
        )

    @classmethod
    def from_string(cls, time_string: str) -> "Time":
        year_month_day, hour_minute_second = time_string.split(" ")
        year, month, day = year_month_day.split("-")
        hour, minute, second = hour_minute_second.split(":")
        return cls(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second),
        )

    @classmethod
    def now(cls) -> "Time":
        """現在時刻を取得する"""
        now = utime.localtime()
        return cls(now[0], now[1], now[2], now[3], now[4], now[5])

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day

    @property
    def hour(self) -> int:
        return self._hour

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def second(self) -> int:
        return self._second


def ntp_sync() -> None:
    """NTPサーバーと時刻を同期する

    Caution:
        NTPサーバーから取得した時刻はUTCである
    """
    ntptime.host = "ntp.nict.jp"
    ntptime.settime()
