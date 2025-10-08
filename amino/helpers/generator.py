from os import urandom
from orjson import dumps, loads
from time import time as timestamp
from hashlib import sha1
from hmac import new
from base64 import b64encode, urlsafe_b64decode
from time import strftime, gmtime
from requests import Session
from aiohttp import ClientSession

from amino import DorksAPIError
from amino.helpers.constants import DEVICE_KEY, SIG_KEY, PREFIX, gen_headers, aminodorks_api
from amino.helpers import log


def req_time() -> int: return int(timestamp() * 1000)

def clientrefid() -> int: return int(timestamp() / 10 % 1000000000)

def gen_deviceId(data: bytes | str | None = None) -> str:
	if isinstance(data, str): data = bytes(data, 'utf-8')
	identifier = PREFIX + (data or urandom(20))
	mac = new(DEVICE_KEY, identifier, sha1)
	return f"{identifier.hex()}{mac.hexdigest()}".upper()

def update_deviceId(device: str) -> str:
    return gen_deviceId(bytes.fromhex(device[2:42]))

def signature(data: str | bytes | dict) -> str:
	if isinstance(data, dict):data = dumps(data)
	if isinstance(data, str): data = data.encode("utf-8")

	return b64encode(PREFIX + new(SIG_KEY, data, sha1).digest()).decode("utf-8")


def timezone() -> int | None:
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
		generate timers for send_active_object (in sub_client)
	"""
	return [
			{
				'start': int(timestamp()), 'end': int(timestamp()) + 300
			} for _ in range(50)
		]

def decode_sid(SID: str) -> dict:
	"""
	get data from authorization sid
		args:
		
		- sid: str
	"""
	return loads(urlsafe_b64decode(SID + "=" * (4 - len(SID) % 4))[1:-20])

def sid_to_uid(SID: str) -> str:
	"""
	get an ID account from the authorization sid
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["2"]

def sid_to_ip_address(SID: str) -> str:
	"""
	get an ip address from the authorization sid
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["4"]

def sid_to_created_time(SID: str) -> int:
	"""
	get created time from the authorization sid
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["5"]

def sid_to_client_type(SID: str) -> int:
	"""
	get client type from the authorization sid
		args:
		
		- sid: str
	"""
	return decode_sid(SID)["6"]





def get_certs(userId: str | None, proxy: dict[str,str] | None = None):
	if userId is None: return None
	with Session() as session:
		log.debug("[dorks-api]: Getting credentials...")
		try:
			response=session.request("GET", f"{aminodorks_api}/signature/credentials/{userId}",headers=gen_headers, proxies=proxy)
			return response.json().get("credentials")
		except Exception as e:
			raise DorksAPIError(e)

async def get_certs_a(userId: str | None, proxy: str):
	if userId is None: return None
	async with ClientSession() as asyncSession:
		log.debug("[dorks-api]: Getting credentials...")
		try:
			response=await asyncSession.request("GET", f"{aminodorks_api}/signature/credentials/{userId}",headers=gen_headers, proxy=proxy)
			return (await response.json()).get("credentials")
		except Exception as e:
			raise DorksAPIError(e)

def new_sig(data: str, userId: str, proxy: dict[str, str] | None = None):
	body={
		"payload":data,
		"userId":userId
	}
	with Session() as session:
		log.debug("[dorks-api]: Generate ecdsa signature...")
		try:
			response=session.request("POST", f"{aminodorks_api}/signature/ecdsa",headers=gen_headers, json=body, proxies=proxy)
			return response.json().get("ECDSA")
		except Exception as e:
			raise DorksAPIError(e)

async def new_sig_a(data: str, userId: str, proxy: str | None = None):
	body={
		"payload":data,
		"userId":userId
	}
	async with ClientSession() as asyncSession:
		log.debug("[dorks-api]: Generate ecdsa signature...")
		try:
			response=await asyncSession.request("POST", f"{aminodorks_api}/signature/ecdsa",headers=gen_headers, json=body, proxy=proxy)
			return (await response.json()).get("ECDSA")
		except Exception as e:
			raise DorksAPIError(e)