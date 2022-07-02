import requests
from constants import PORT__ms, ENDPOINT__ms_reload, ENDPOINT__reset_cooldowns


class Management:

    def reload(self):
        requests.post("http://127.0.0.1:" + str(PORT__ms) + ENDPOINT__ms_reload)

    def reset_cooldowns(self):
        requests.post("http://127.0.0.1:" + str(PORT__ms) + ENDPOINT__reset_cooldowns)
