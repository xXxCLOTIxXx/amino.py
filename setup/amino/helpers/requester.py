from typing import Union
from aiohttp import ClientSession
from requests import Session
from .exceptions import check_exceptions


api = "https://service.narvii.com/api/v1"

class Requester:
	def __init__(self, session: Session, proxies: dict = None, verify = None):
		self.session = session
		self.proxies = proxies
		self.verify = verify


	def make_request(self, method: str, endpoint: str, body = None, successfully: int = 200, headers = None, timeout=None):
		response = self.session.request(method, f"{api}{endpoint}", proxies=self.proxies, verify=self.verify, data=body, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(response.text, response.status_code) if response.status_code != successfully else response
		return response



class AsyncRequester:
	def __init__(self, session: ClientSession, proxies: dict = None, verify = None):
		self.session = session
		self.proxies = proxies
		self.verify = verify

	async def make_request(self, method: str, endpoint: str, body = None, successfully: int = 200, headers = None, timeout=None):
		response = await self.session.request(method, f"{api}{endpoint}", data=body, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(await response.text(), response.status) if response.status != successfully else response
		return response