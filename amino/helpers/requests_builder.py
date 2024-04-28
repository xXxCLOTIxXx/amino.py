from ..objects.auth_data import auth_data
from ..helpers.generator import signature, generate_deviceId
from ..objects.constants import (
	host, api
)
from .exceptions import check_exceptions

from typing import Union
from requests import Session
from aiohttp import ClientSession
from ujson import dumps


def header(uid: str = None, sid: str = None, user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", language: str = "en", deviceId: str = None, data: bytes = None, content_type: str = "application/json"):
	headers = {
		"NDCDEVICEID": deviceId if deviceId else generate_deviceId(),
		"NDCLANG": language.lower(),
		"Accept-Language": f"{language.lower()}-{language.upper()}",
		"User-Agent": user_agent,
		"Host": "service.aminoapps.com",
		"Accept-Encoding":  "gzip, deflate",
		"Accept": "*/*",
		"Connection": "keep-alive",
		}
	if data:
		headers["Content-Length"] = str(len(data))
		headers["NDC-MSG-SIG"] = signature(data=data)
		
	if sid:headers["NDCAUTH"] = f"sid={sid}"
	if uid: headers["AUID"] = uid
	if content_type: headers["Content-Type"] = content_type
	return headers






class requestsBuilder:
	profile: auth_data
	session: Session = Session()
	proxies: dict

	def __init__(self, profile: auth_data, proxies: dict = None):
		self.profile = profile
		self.proxies = proxies


	def request(self, method: str, endpoint: str, data: Union[str, bytes] = None, successfully: int = 200, timeout=None, base_url: str = api) -> dict:
		if isinstance(data, dict): data = dumps(data)
		if method.lower() == "post":content_type= "application/json" if data is not None else "application/x-www-form-urlencoded"
		else:content_type = None

		resp = self.session.request(method.upper(), f"{base_url}{endpoint}", data=data, headers=header(
			uid=self.profile.uid, sid=self.profile.sid, deviceId=self.profile.deviceId,
			user_agent=self.profile.user_agent, language=self.profile.language,
			data=data, content_type=content_type),
			timeout=timeout, proxies=self.proxies)
		return check_exceptions(resp.text, resp.status_code) if resp.status_code != successfully else resp.json()


class AsyncRequestsBuilder:
	profile: auth_data
	session: ClientSession = ClientSession()
	proxies: dict

	def __init__(self, profile: auth_data, proxies: dict = None):
		self.profile = profile
		self.proxies = proxies


	async def request(self, method: str, endpoint: str, data: Union[str, bytes] = None, successfully: int = 200, timeout=None, base_url: str = api) -> dict:
		if isinstance(data, dict): data = dumps(data)
		if method.lower() == "post":content_type= "application/json" if data is not None else "application/x-www-form-urlencoded"
		else:content_type = None

		resp = await self.session.request(method.upper(), f"{base_url}{endpoint}", data=data, headers=header(
			uid=self.profile.uid, sid=self.profile.sid, deviceId=self.profile.deviceId,
			user_agent=self.profile.user_agent, language=self.profile.language,
			data=data, content_type=content_type),
			timeout=timeout, proxy=self.proxies)
		return check_exceptions(await resp.text(), resp.status) if resp.status != successfully else await resp.json()