import requests
from constants import PORT__rs, ENDPOINT__rs_report, ENDPOINT__reset_cooldowns


class Reporting:

    def report(self, inputs: dict):
        requests.post("http://127.0.0.1:" + str(PORT__rs) + ENDPOINT__rs_report, json=inputs)

    def reset_cooldowns(self):
        requests.post("http://127.0.0.1:" + str(PORT__rs) + ENDPOINT__reset_cooldowns)
