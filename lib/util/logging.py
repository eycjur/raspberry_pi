import json

from util.time import get_time_str
from util.secret import WEB_HOOK_URL
from util.judge import is_wifi_usable
from util.const import ERROR_FILE_PATH


if is_wifi_usable():
    import urequests


class CustomLogging:
    def _format(self, message):
        return f"{get_time_str()} - {message}"

    def write(self, message):
        message = self._format(message)
        self._write_console(message)
        self._write_file(message)
        self._write_slack(message)

    def _write_console(self, message):
        print(message)

    def _write_slack(self, message):
        urequests.post(WEB_HOOK_URL, data=json.dumps({
            "text": message
        }))

    def _write_file(self, message):
        with open(ERROR_FILE_PATH, "a") as f:
            f.write(f"{message}\n")
