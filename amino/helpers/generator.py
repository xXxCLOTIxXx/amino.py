from __future__ import annotations

from hmac import new
from hashlib import sha1
from base64 import b64encode, urlsafe_b64decode
from json import loads
from os import urandom
from time import time as timestamp
from time import strftime, gmtime
from random import randint, choice

from ..objects.constants import (
	PREFIX, SIG_KEY, DEVICE_KEY
)


def clientrefid() -> int: return int(timestamp() / 10 % 1000000000)

def signature(data: str | bytes) -> str:
	"""
		signature generator based on request data

		args:
		
		- data: str or bytes
	"""
	data = data if isinstance(data, bytes) else data.encode("utf-8")
	return b64encode(PREFIX + new(SIG_KEY, data, sha1).digest()).decode("utf-8")


def generate_deviceId() -> str:
	"""
		device id generator
	"""
	ur = PREFIX + (urandom(20))
	mac = new(DEVICE_KEY, ur, sha1)
	return f"{ur.hex()}{mac.hexdigest()}".upper()


def generate_user_agent() -> str:
	"""
	iphone user agent generator
	"""

	models = [
		'iPhone6,1', 'iPhone6,2', 'iPhone7,1', 'iPhone7,2', 'iPhone8,1', 'iPhone8,2', 
		'iPhone9,1', 'iPhone9,2', 'iPhone10,1', 'iPhone10,2', 'iPhone11,2', 'iPhone11,4', 
		'iPhone11,6', 'iPhone12,1', 'iPhone12,3', 'iPhone12,5', 'iPhone13,1', 'iPhone13,2', 
		'iPhone13,3', 'iPhone13,4', 'iPhone14,2', 'iPhone14,3', 'iPhone14,4', 'iPhone14,5'
	]
	ios_versions = [
		'14.0', '14.1', '14.2', '14.3', '14.4', '14.5', '14.6', '14.7', '14.8', '15.0', 
		'15.1', '15.2', '15.3', '15.4', '15.5', '15.6', '15.7', '15.8', '16.0', '16.1', 
		'16.2', '16.3', '16.4', '16.5'
	]

	app_version = f"{randint(1, 5)}.{randint(0, 9)}.{randint(0, 9)}"
	model = choice(models)
	ios_version = choice(ios_versions)
	
	return f"Apple {model} iOS v{ios_version} Main/{app_version}"




def timezone() -> int:
	"""
	time zone generator
	"""

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



def timers() -> list[dict]:
	"""
		generate timers for send_active_object (in CommunityClient)
	"""
	return [
			{
				'start': int(timestamp()), 'end': int(timestamp()) + 300
			} for _ in range(50)
		]

def decode_sid(SID: str) -> dict:
	"""
	get data from authorization seed
		args:
		
		- sid: str
	"""
	return loads(urlsafe_b64decode(SID + "=" * (4 - len(SID) % 4))[1:-20])

def sid_to_uid(SID: str) -> str:
	"""
	get an ID account from the authorization seed
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str:
	"""
	get an ip address from the authorization seed
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["4"]

def sid_created_time(SID: str) -> int:
	"""
	get created time from the authorization seed
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["5"]

def sid_to_client_type(SID: str) -> int:
	"""
	get client type from the authorization seed
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["6"]