from .client import Client
from amino.helpers import exceptions

from asyncio import get_event_loop, new_event_loop

class CommunityClient(Client):
	def __init__(self,
		comId: int = None,
		community_link: str = None,
		aminoId: str = None, 
		profile = None,
		language: str = "en", 
		user_agent: str = "Apple iPhone12,1 iOS v15.5 Main/3.12.2", 
		auto_user_agent:  bool = False, 
		deviceId: str = None, 
		auto_device: bool = False, 
		proxies: dict = None, 
		certificate_path = None, 
		http_connect: bool = True, 
		requests_debug: bool = False
		):
			Client.__init__(self, language=language, user_agent=user_agent, auto_user_agent=auto_user_agent, deviceId=deviceId, auto_device=auto_device, socket_enabled=False, proxies=proxies, certificate_path=certificate_path, http_connect=http_connect, requests_debug=requests_debug)
			if profile:self.profile=profile
			self.comId = comId
			self.aminoId = aminoId
			self.community_link = community_link
	

	def __await__(self):
		return self.__set_comId().__await__()

	async def __set_comId(self):
		if self.comId:pass
		elif self.community_link:
			info = await self.get_from_link(self.community_link)
			self.comId=info.comId
		elif self.aminoId:
			info = await self.get_from_link(f"http://aminoapps.com/c/{self.aminoId}")
			self.comId=info.comId
		else:
			raise exceptions.NoCommunity("Provide a link to the community, comId or aminoId.")


	def __del__(self):
		try:
			loop = get_event_loop()
			loop.create_task(self._close_session())
		except RuntimeError:
			loop = new_event_loop()
			loop.run_until_complete(self._close_session())

	async def _close_session(self):
		if not self.session.closed: await self.session.close()