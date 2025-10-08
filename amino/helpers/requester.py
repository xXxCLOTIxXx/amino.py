
from aiohttp import ClientSession, ClientResponse
from requests import Session, Response
from orjson import dumps

from amino.helpers.generator import signature, req_time, new_sig, new_sig_a
from amino.helpers.constants import api as api_url
from amino.helpers import log
from amino.helpers.exceptions import check_exceptions
from amino import args
from amino import InvalidProxyFormat
import ssl

class Requester:
	"""
	Main class for handling HTTPS requests in the Amino.py API library.

	This class is responsible for making HTTP requests to the Amino servers, managing headers, and providing 
	convenience methods for interaction with the API
	"""
	
	def __init__(self, user_agent: str, deviceId: str, language: str, accept_language: str, proxies: dict[str, str] | str | None, ssl_verify: bool | str | None, dorks_api_proxies: dict[str, str] | str | None):
		self.user_agent = user_agent
		self.deviceId = deviceId
		self.language = language
		self.accept_language = accept_language
		self.sid: str | None = None
		self.userId: str | None = None
		self.proxies = proxies
		self.dorks_api_proxies = dorks_api_proxies
		self.ssl_verify=ssl_verify

	def headers(self, headers: dict | None = None, content_type: str | None = None, data: dict | str | bytes | None = None) -> dict:

		default_headers = {
			"Accept-Language": self.accept_language,
			"NDCLANG": self.language,
			"Content-Type": "application/json; charset=utf-8",
			"User-Agent": self.user_agent,
			"Host": "service.aminoapps.com",
			"Accept-Encoding": "gzip, deflate, br",
			"Connection": "Keep-Alive",
		}
		if self.deviceId: default_headers["NDCDEVICEID"] = self.deviceId
		if data:
			default_headers["Content-Length"] = str(len(data))
			default_headers["NDC-MSG-SIG"] = signature(data)

		if self.sid: default_headers["NDCAUTH"] = f"sid={self.sid}"
		if self.userId:
			default_headers["AUID"] = self.userId

		if content_type: default_headers["content-type"] = content_type
		if headers: default_headers.update(headers)
		return default_headers





	def make_sync_request(self,
					   method: str,
					   endpoint: str | None = None,
					   body: str | dict | bytes | None = None,
					   allowed_code: int = 200,
					   headers: dict | None = None,
					   content_type: str | None = None,
					   timeout = None,
					   base_url: str | None = None,
					   files = None) -> Response:
		
		if self.proxies is not None and not isinstance(self.proxies, dict):
			raise InvalidProxyFormat('For a synchronous client, you need to pass the proxy as a dictionary.\nproxies = {"http": "http://127.0.0.1:8080","https": "http://127.0.0.1:8080"}')
		if self.dorks_api_proxies is not None and not isinstance(self.dorks_api_proxies, dict):
			raise InvalidProxyFormat('For a synchronous client, you need to pass the proxy as a dictionary.\ndorks_api_proxies = {"http": "http://127.0.0.1:8080","https": "http://127.0.0.1:8080"}')
			
		if isinstance(body, dict):
			body["timestamp"] = req_time()
			body = dumps(body)

		headers = self.headers(headers, data=body, content_type=content_type)
		if self.userId and content_type not in args.UploadType.all:
			headers["NDC-MESSAGE-SIGNATURE"] = new_sig(
			body if isinstance(body, str) else body.decode("utf-8") if isinstance(body, bytes) else '',
			self.userId, self.dorks_api_proxies)
		method = method.upper()

		with Session() as session:
			response: Response = session.request(method, f"{base_url or api_url}{endpoint or ''}", data=body, headers=headers, timeout=timeout, files=files, proxies=self.proxies, verify=self.ssl_verify)

			log.debug(f"[https][{method}][{base_url or ''}{endpoint or ''}][{response.status_code}]: {len(body) if isinstance(body, bytes) else body}\n-----headers-----\n{headers}\n-----------------\n")
			if response.status_code != allowed_code:check_exceptions(response.text, response.status_code)
			return response



	async def make_async_request(self,
							  method: str,
							  endpoint: str | None = None,
							  body: str | dict | bytes | None = None,
							  allowed_code: int = 200,
							  headers: dict | None = None,
							  content_type: str | None = None,
							  timeout = None,
							  base_url: str | None = None) -> ClientResponse:

		if self.proxies is not None and not isinstance(self.proxies, str):
			raise InvalidProxyFormat('For a async client, you need to pass the proxy as a string.\nproxies = "http://127.0.0.1:8080"')
		if self.dorks_api_proxies is not None and not isinstance(self.dorks_api_proxies, str):
			raise InvalidProxyFormat('For a async client, you need to pass the proxy as a string.\ndorks_api_proxies = "http://127.0.0.1:8080"')
		
		if isinstance(body, dict):
			body["timestamp"] = req_time()
			body = dumps(body)
			
		headers = self.headers(headers, data=body, content_type=content_type)
		if self.userId: headers["NDC-MESSAGE-SIGNATURE"] = await new_sig_a(
			body if isinstance(body, str) else body.decode("utf-8") if isinstance(body, bytes) else '',
			self.userId, self.dorks_api_proxies)
		method = method.upper()
		
		async with ClientSession() as asyncSession:
			
			response = await asyncSession.request(method, f"{base_url or api_url}{endpoint or ''}", data=body, headers=headers, timeout=timeout, proxy=self.proxies, ssl=self.build_aiohttp_ssl_context())
			log.debug(f"[https][{method}][{base_url if base_url else ''}{endpoint or ''}][{response.status}]: {len(body) if isinstance(body, bytes) else body}\n-----headers-----\n{headers}\n-----------------\n")
			if response.status != allowed_code:check_exceptions(await response.text(), response.status)
			return response
		

	def build_aiohttp_ssl_context(self) -> ssl.SSLContext:
		if self.ssl_verify is False:
			ctx = ssl.create_default_context()
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE
			return ctx
		elif isinstance(self.ssl_verify, str):
			return ssl.create_default_context(cafile=self.ssl_verify)
		return ssl.create_default_context()