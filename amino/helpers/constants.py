from random import randint

PREFIX = bytes.fromhex("52")
SIG_KEY = bytes.fromhex("EAB4F1B9E3340CD1631EDE3B587CC3EBEDF1AFA9")
DEVICE_KEY = bytes.fromhex("AE49550458D8E7C51D566916B04888BFB8B3CA7D")

host = "service.aminoapps.com"
api = f"https://{host}/api/v1"
ws_url = f"wss://ws{randint(1, 4)}.aminoapps.com"
ws_ping_interval = 3

#aminodorks service

aminodorks_api="https://aminodorks.agency/api/v1"
gen_headers = {
    "Content-Type": "application/json; charset=utf8",
    "CONNECTION": "Keep-Alive",
}


def set_dorksapi_key(key: str):
     """
     A special access key for signature generation can be obtained through the Telegram bot.
     @aminodorks_bot
     """
     gen_headers["Authorization"] = key