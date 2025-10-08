from amino.helpers.requester import Requester
from amino.helpers.generator import gen_deviceId
from amino.helpers import log
from amino.api.sync import *
from amino.ws import Socket
from amino.sub_client import SubClient, _Client
from amino.helpers.constants import gen_headers
from sys import exit
from time import sleep




class Client(
	Socket,
	AccountModule,
	GlobalUsersModule,
	GlobalCommunitiesModule,
	GlobalOtherModule,
	GlobalStoreModule,
	GlobalCommentsModule,
	GlobalChatsModule,
	GlobalBlogsModule,
	_Client):

	def __init__(self,
			  deviceId: str | None = None,
			  user_agent: str = "Dalvik/2.1.0 (Linux; U; Android 10; M2006C3MNG Build/QP1A.190711.020;com.narvii.amino.master/4.3.3121)",
			  accept_language: str = "en-us",
			  community_language: str = "en",
			  socket_enable: bool = True,
			  socket_error_trace: bool = False,
			  socket_daemon: bool = False,
			  proxies: dict[str, str] | None = None,
			  ssl_verify: bool | str | None = None,
			  dorks_api_proxies: dict[str,str] | None = None):
	
		
		Socket.__init__(self, socket_error_trace, socket_daemon)
		self.socket_enable = socket_enable
		if deviceId is None:
			deviceId=gen_deviceId()
			log.warning(f"You didn't explicitly specify a device ID in the client.\nA new device ID was generated for you: {deviceId}.\nSave it for future use.")
		self.req = Requester(user_agent, deviceId, community_language, accept_language, proxies, ssl_verify, dorks_api_proxies)

		if gen_headers.get("Authorization") is None:
			log.critical(f"You haven't specified a key for the signature generation service.\nYou can get one through the Telegram bot: @aminodorks_bot.\nuse: amino.set_dorksapi_key")
			exit()

		self.community = SubClient(self)




	def __str__(self):
		return f"amino.Client <deviceId={self.deviceId}, socket_enable={self.socket_enable}>"
	
	def __repr__(self):
		return (f"amino.Client(deviceId={self.deviceId!r}, user_agent{self.user_agent!r}, language={self.language!r}, "
				f"socket_enable={self.socket_enable!r}"
				f"SID={self.sid!r})")


	def set_default_comId(self, comId: str | None, aminoId: str | None = None):
		"""
		To avoid manually passing comId to each method when working with communities, you can set it as a default value at the class level.
		This will allow all methods to automatically use self.comId.
		"""

		if comId:
			self.community.comId = comId
		elif aminoId:
			link = f"http://aminoapps.com/c/{aminoId}"
			self.community.comId = self.get_from_link(link).comId
		self.community.comId = None


	def wait_socket(self):
		"""
		Holds the main thread alive until Ctrl+C is pressed, used when the socket is running in a daemon thread.

		This function is intended for cases where the socket is launched as a daemon (self.socket_daemon = True).
		Since daemon threads are terminated when the main thread exits, calling this function prevents the program
		from closing immediately and allows the socket to stay active.

		If self.socket_daemon is False, the socket runs in a regular thread and this function is not required —
		the socket will continue running independently of the main thread.
		"""
		try:
			while self.socket_enable:
				sleep(1.5)
		except KeyboardInterrupt:
			exit()