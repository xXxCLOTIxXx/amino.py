from ..objects.auth_data import auth_data
from ..helpers.generator import signature, generate_deviceId
from ..objects.constants import (
	host, api
)
from .exceptions import check_exceptions, SpecifyType
from ..objects.reqObjects import MediaObject
from ..objects.dynamic_object import DynamicObject
from ..objects.args import UploadType


from requests import Session
from aiohttp import ClientSession
from ujson import dumps
from typing import BinaryIO, Union
from aiofiles.threadpool.binary import AsyncBufferedReader
from mimetypes import guess_type
from time import time


def header(uid: str = None, sid: str = None, user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", language: str = "en", deviceId: str = None, data: bytes = None, content_type: str = "application/json"):
	headers = {
		"NDCDEVICEID": deviceId if deviceId else generate_deviceId(),
		"NDCLANG": language.lower(),
		"Accept-Language": f"{language.lower()}-{language.upper()}",
		"User-Agent": user_agent,
		"Host": host,
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
	session: Session
	proxies: dict

	def __init__(self, profile: auth_data, proxies: dict = None):
		self.profile = profile
		self.proxies = proxies
		self.session = Session()


	def request(self, method: str, endpoint: str, data: Union[str, bytes, dict] = None, successfully: int = 200, timeout=None, base_url: str = api, content_type= "application/json") -> DynamicObject:
		if isinstance(data, dict):
			data["timestamp"] = int(time() * 1000)
			data = dumps(data)
		if method.lower() == "post":content_type=content_type if data is not None else "application/x-www-form-urlencoded"
		else:content_type = None

		resp = self.session.request(method.upper(), f"{base_url}{endpoint}", data=data, headers=header(
			uid=self.profile.uid, sid=self.profile.sid, deviceId=self.profile.deviceId,
			user_agent=self.profile.user_agent, language=self.profile.language,
			data=data, content_type=content_type),
			timeout=timeout, proxies=self.proxies)
		return check_exceptions(resp.text, resp.status_code) if resp.status_code != successfully else DynamicObject(resp.json())



	def upload_media(self, file: BinaryIO) -> MediaObject:
		fileType = guess_type(file.name)[0]
		if fileType not in UploadType.all: raise SpecifyType(fileType)
		return MediaObject(self.request("POST", "/g/s/media/upload", file.read(), content_type=fileType))



class AsyncRequestsBuilder:
	profile: auth_data
	session: ClientSession
	proxies: dict

	def __init__(self, profile: auth_data, proxies: dict = None):
		self.profile = profile
		self.proxies = proxies
		self.session = ClientSession()


	async def request(self, method: str, endpoint: str, data: Union[str, bytes] = None, successfully: int = 200, timeout=None, base_url: str = api, content_type= "application/json") -> dict:
		if isinstance(data, dict): data = dumps(data)
		if method.lower() == "post":content_type=content_type if data is not None else "application/x-www-form-urlencoded"
		else:content_type = None

		resp = await self.session.request(method.upper(), f"{base_url}{endpoint}", data=data, headers=header(
			uid=self.profile.uid, sid=self.profile.sid, deviceId=self.profile.deviceId,
			user_agent=self.profile.user_agent, language=self.profile.language,
			data=data, content_type=content_type),
			timeout=timeout, proxy=self.proxies)
		return check_exceptions(await resp.text(), resp.status) if resp.status != successfully else DynamicObject(await resp.json())



	async def upload_media(self, file: AsyncBufferedReader) -> MediaObject:
		fileType = guess_type(file.name)[0]
		if fileType not in UploadType.all: raise SpecifyType(fileType)
		return MediaObject(self.request("POST", "/g/s/media/upload", await file.read(), content_type=fileType))
