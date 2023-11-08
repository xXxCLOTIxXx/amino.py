from typing import Union
from aiohttp import ClientSession
from requests import Session
from .exceptions import check_exceptions

#thanks to August for help with the fix "Max retries exceeded with url" (http_connect add)
#Telegram: @augustlight

class Requester:
	api = "https://service.aminoapps.com/api/v1"

	def __init__(self, session: Session, proxies: dict = None, verify = None, http_connect: bool = False):
		self.session = session
		self.proxies = proxies
		self.verify = verify
		if http_connect is True:
			self.api = "http://service.aminoapps.com:80/api/v1"
			self.verify = False
		self.session.verify = self.verify
		



	def make_request(self, method: str, endpoint: str, data = None, successfully: int = 200, headers = None, timeout=None):
		response = self.session.request(method, f"{self.api}{endpoint}", proxies=self.proxies, verify=self.verify, data=data, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(response.text, response.status_code) if response.status_code != successfully else response
		return response



class AsyncRequester:
	api = "https://service.aminoapps.com/api/v1"

	def __init__(self, session: ClientSession, proxies: dict = None, verify = None, http_connect: bool = False):
		self.session = session
		self.proxies = proxies
		self.verify = verify
		if http_connect is True:
			self.api = "http://service.aminoapps.com:80/api/v1"
			self.verify = False
		self.session.verify = self.verify


	async def make_request(self, method: str, endpoint: str, data = None, successfully: int = 200, headers = None, timeout=None):
		response = await self.session.request(method, f"{self.api}{endpoint}", data=data, headers=headers, timeout=timeout)
		if successfully: return check_exceptions(await response.text(), response.status) if response.status != successfully else response
		return response