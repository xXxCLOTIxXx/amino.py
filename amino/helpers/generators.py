from typing import Union
from hmac import new
from hashlib import sha1
from base64 import b64encode, urlsafe_b64decode
from json import loads, load, dump
from json.decoder import JSONDecodeError
from os import urandom
from time import time as timestamp
from time import strftime, gmtime
from uuid import uuid4
from random import randrange



PREFIX = bytes.fromhex("19")
SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")


def signature(data: Union[str, bytes]):
	data = data if isinstance(data, bytes) else data.encode("utf-8")
	return b64encode(PREFIX + new(SIG_KEY, data, sha1).digest()).decode("utf-8")


def generate_deviceId():
	ur = PREFIX + (urandom(20))
	mac = new(DEVICE_KEY, ur, sha1)
	return f"{ur.hex()}{mac.hexdigest()}".upper()


def timezone():
	localhour = strftime("%H", gmtime())
	localminute = strftime("%M", gmtime())
	UTC = {
			"GMT0": '+0', "GMT1": '+60', "GMT2": '+120', "GMT3": '+180', "GMT4": '+240', "GMT5": '+300', "GMT6": '+360',
			"GMT7": '+420', "GMT8": '+480', "GMT9": '+540', "GMT10": '+600', "GMT11": '+660', "GMT12": '+720',
			"GMT13": '+780', "GMT-1": '-60', "GMT-2": '-120', "GMT-3": '-180', "GMT-4": '-240', "GMT-5": '-300',
			"GMT-6": '-360', "GMT-7": '-420', "GMT-8": '-480', "GMT-9": '-540', "GMT-10": '-600', "GMT-11": '-660'
	}

	hour = [localhour, localminute]
	if hour[0] == "00": tz = UTC["GMT-1"];return int(tz)
	if hour[0] == "01": tz = UTC["GMT-2"];return int(tz)
	if hour[0] == "02": tz = UTC["GMT-3"];return int(tz)
	if hour[0] == "03": tz = UTC["GMT-4"];return int(tz)
	if hour[0] == "04": tz = UTC["GMT-5"];return int(tz)
	if hour[0] == "05": tz = UTC["GMT-6"];return int(tz)
	if hour[0] == "06": tz = UTC["GMT-7"];return int(tz)
	if hour[0] == "07": tz = UTC["GMT-8"];return int(tz)
	if hour[0] == "08": tz = UTC["GMT-9"];return int(tz)
	if hour[0] == "09": tz = UTC["GMT-10"];return int(tz)
	if hour[0] == "10": tz = UTC["GMT13"];return int(tz)
	if hour[0] == "11": tz = UTC["GMT12"];return int(tz)
	if hour[0] == "12": tz = UTC["GMT11"];return int(tz)
	if hour[0] == "13": tz = UTC["GMT10"];return int(tz)
	if hour[0] == "14": tz = UTC["GMT9"];return int(tz)
	if hour[0] == "15": tz = UTC["GMT8"];return int(tz)
	if hour[0] == "16": tz = UTC["GMT7"];return int(tz)
	if hour[0] == "17": tz = UTC["GMT6"];return int(tz)
	if hour[0] == "18": tz = UTC["GMT5"];return int(tz)
	if hour[0] == "19": tz = UTC["GMT4"];return int(tz)
	if hour[0] == "20": tz = UTC["GMT3"];return int(tz)
	if hour[0] == "21": tz = UTC["GMT2"];return int(tz)
	if hour[0] == "22": tz = UTC["GMT1"];return int(tz)
	if hour[0] == "23": tz = UTC["GMT0"];return int(tz)



def timers():
	return [
			{
				'start': int(timestamp()), 'end': int(timestamp()) + 300
			} for _ in range(50)
		]

def decode_sid(SID: str):return loads(urlsafe_b64decode(SID + "=" * (4 - len(SID) % 4))[1:-20])

def sid_to_uid(SID: str): return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str): return decode_sid(SID)["4"]

def sid_created_time(SID: str): return decode_sid(SID)["5"]

def sid_to_client_type(SID: str): return decode_sid(SID)["6"]
