from aiohttp import ClientSession, WSMsgType, ClientWebSocketResponse
from asyncio import sleep, create_task
from ujson import loads, dumps


from ..helpers.exceptions import SocketNotStarted
from ..objects.ws.ws_event_types import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types,
	notification_types
)
from ..objects.constants import ws_url, ws_ping_interval
from ..helpers.generator import generate_deviceId, signature
from ..objects.reqObjects import Event



class EventHandler:
	handlers = {}

	def event(self, type):
		def registerHandler(handler):
			if type in self.handlers:self.handlers[type].append(handler)
			else:self.handlers[type] = [handler]
			return handler

		return registerHandler

	def on_message(self):
		def registerHandler(handler):
			if "chat_message" in self.handlers:self.handlers["chat_message"].append(handler)
			else:self.handlers["chat_message"] = [handler]
			return handler

		return registerHandler

	async def call(self, data):
		data_object = Event(data["o"])
		method = ws_message_methods.get(data["t"])
		if method in ("chat_action_start", "chat_action_end") :
			key = data['o'].get('actions', 0)
			ws_event = ws_chat_action_start.get(key) if method == "chat_action_start" else ws_chat_action_end.get(key)
		elif method == "chat_message":
			key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
			ws_event = ws_message_types.get(key)
		elif method == "notification":
			key = data["o"]["payload"]["notifType"]
			ws_event = notification_types.get(key)
		else:ws_event=None
		
		if "on_ws_message" in self.handlers.keys():
			for func in self.handlers["on_ws_message"]:
				await func(data_object)
		if method in self.handlers.keys():
			for func in self.handlers[method]:
				await func(data_object)
		if ws_event:
			if ws_event in self.handlers.keys():
				for func in self.handlers[ws_event]:
					await func(data_object)



class WsRequester:

	async def create_socket_event(self, data):
		await self.call(data)


	async def online(self, comId: int):

		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		await self.ws_send(req_t=304, o=data)


	async def browsing_blogs(self, comId: int, blogId: str = None, quizId: str = None):
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}
		await self.ws_send(req_t=304, o=data)


	async def typing(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		await self.ws_send(req_t=304, o=data)

	async def recording(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		await self.ws_send(req_t=304, o=data)


	async def join_live_chat(self, chatId: str, comId: int = None, as_viewer: bool = False):

		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		await self.ws_send(req_t=112, o=data)


	async def browsing_leader_boards(self, comId: int):

		data = {
			"o": {
				"actions": ["Browsing"],
				"target": f"ndc://x{comId}/leaderboards",
				"ndcId": int(comId),
				"params": {"duration": 859},
			}
		}
		await self.ws_send(req_t=306, o=data)


class AsyncSocket(EventHandler, WsRequester):

	debug: bool = False

	def __init__(self, debug: bool = False):
		self.debug=debug
		self.connection: ClientWebSocketResponse = None
		self.task_receiver = None
		self.task_pinger = None
		self.client_session = None
		self.debug=debug
	

	async def socket_log(self, message: str):
		if self.debug:print(f"[Socket]{message}")


	async def ws_connect(self, headers: dict, final: str):
		if self.connection:
			await self.socket_log(f"[start] The socket is already running.")
			return
		try:
			self.client_session = ClientSession(base_url=ws_url)
			self.connection = await self.client_session.ws_connect(f"/?signbody={final}", headers=headers)
			self.task_receiver = create_task(self.ws_resolve())
			self.task_pinger = create_task(self.ws_ping())
			await self.socket_log(f"[start] Socket Started")
		except Exception as e:
			await self.socket_log(f"[start] Error while starting Socket : {e}")


	async def ws_disconnect(self):
		if self.connection:
			await self.socket_log(f"[stop] closing socket...")
			try:
				self.task_receiver.cancel()
				self.task_pinger.cancel()
				await self.connection.close()
				self.connection = None
				await self.client_session.close()
				self.client_session = None
			except Exception as e:
					await self.socket_log(f"[stop] Error while closing Socket : {e}")
		else:
			await self.socket_log(f"[stop] Socket not running.")

	async def ws_send(self, req_t: int, **kwargs):
		if self.connection is None:raise SocketNotStarted('The socket is not running')
		data = dumps(dict(t=req_t, **kwargs))
		await self.socket_log(f"[send] Sending Data : {data}")
		try:return await self.connection.send_str(data)
		except:await self.socket_log(f"[send] Socket not available : {data}")

	async def ws_ping(self):
		while True:
			await sleep(ws_ping_interval)
			await self.connection.send_str('{"t": 116, "o": {"threadChannelUserInfoList": []}}')

	async def ws_resolve(self):
		while True:
			msg = await self.connection.receive()
			if msg.type != WSMsgType.TEXT: continue
			try:data = loads(msg.data)
			except:
				await self.socket_log(f"[recive] The socket received an unreadable message: {data}")
				continue
			await self.socket_log(f"[recive]: {data}")
			await self.call(data)




	def ws_headers(self, sid: str, final: str, deviceId: str = None):
		return {
					"NDCDEVICEID": deviceId if deviceId else generate_deviceId(),
					"NDCAUTH": f"sid={sid}",
					"NDC-MSG-SIG": signature(final)
				}