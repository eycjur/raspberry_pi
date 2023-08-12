import json

from src.const import ERROR_FILE_PATH
from src.secret import WEB_HOOK_URL
from src.util.judge import is_wifi_usable
from src.util.time import Time, ntp_sync


if is_wifi_usable():
    import urequests


class CustomLogging:
    def __init__(self, console=True, file=True, slack=False):
        self.console = console
        self.file = file
        self.slack = slack

        self._write_file("\n\nnew session\n")
        try:
            ntp_sync()
        except Exception as e:
            self.write(f"ntp sync failed: {e}")

    def _format(self, message):
        return f"[{Time.now()}] {message}"

    def write(self, message):
        message = self._format(message)
        if self.console:
            self._write_console(message)
        if self.file:
            self._write_file(message)

        if self.slack and is_wifi_usable():
            self._write_slack(message)

    def _write_console(self, message):
        print(message)

    def _write_slack(self, message):
        urequests.post(WEB_HOOK_URL, data=json.dumps({
            "text": message
        }))

    def _write_file(self, message):
        with open(ERROR_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
