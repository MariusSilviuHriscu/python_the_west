from enum import Enum


# Enum for supported game servers
class GameServer(Enum):
    RO = ("https://www.the-west.ro", "ro_RO")
    EN = ("https://www.the-west.net", "en_DK")
    BETA = ("https://beta.the-west.net", "en_DK")  # Beta uses a different base URL

    def __init__(self, base_url: str, locale: str):
        self.base_url = base_url
        self.locale = locale