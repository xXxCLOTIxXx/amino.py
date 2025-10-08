from __future__ import annotations

from threading import Thread
from websocket import WebSocketApp, enableTrace
from websocket import _exceptions as WSexceptions
from orjson import loads, dumps
from time import sleep
from typing import Any

from traceback import print_exc



from amino import SocketNotStarted
from amino.objects.args import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types,
	notification_types
)
from amino.objects import Event
from amino.helpers.constants import ws_url, ws_ping_interval
from amino.helpers.generator import signature
from amino.helpers.exceptions import SpecifyType
from amino import log


class EventHandler:
	"""
		class for handling socket events
	"""

	handlers = {}

	def event(self, type: str) -> Any:
		"""
		Add event handler

		@client.event(type=amino.arguments.wsEvent.on_text_message)
		"""

		def registerHandler(handler):
			if type in self.handlers:self.handlers[type].append(handler)
			else:self.handlers[type] = [handler]
			return handler

		return registerHandler
	
	def on_message(self) -> Any:
		"""
			add an event handler when receiving a new event in chat
			
			@client.on_message()
		"""

		def registerHandler(handler):
			if "chat_message" in self.handlers:self.handlers["chat_message"].append(handler)
			else:self.handlers["chat_message"] = [handler]
			return handler

		return registerHandler

	def call(self, data: dict) -> None:
		"""
		call the event handler

		**parameters**
		- data : data from web socket
		"""
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
				func(data_object)
		if method in self.handlers.keys():
			for func in self.handlers[method]:
				func(data_object)
		if ws_event:
			if ws_event in self.handlers.keys():
				for func in self.handlers[ws_event]:
					func(data_object)



class WsRequester:
	"""
	class with socket requests
	"""
	
	def ws_send(self, req_t: int, **kwargs) -> None: ...
	def ws_resolve(self, ws: Any, data: str | bytes | bytearray) -> None: ...

	def create_socket_event(self, data: str | bytes | bytearray) -> None:
		"""
		send data to event handler

		**parameters**
		- data : data to send
		"""
		return self.ws_resolve(None, data)


	def online(self, comId: int) -> None:
		"""
			this request will show you in the list of online users
			
			**parameters**
			- comId : id of the community
		"""
		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		self.ws_send(req_t=304, body=data)


	def browsing_blogs(self, comId: int, blogId: str | None = None, quizId: str | None = None) -> None:
		"""
			this request will show you in the list of blog viewers
			
			**parameters**
			- comId : id of the community
			- blogId : id of the blog
			- quizId id of the quiz
		"""
		if blogId is None and quizId is None: raise SpecifyType
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}
		self.ws_send(req_t=304, body=data)


	def typing(self, chatId: str, comId: int | None = None) -> None:
		"""
			create the illusion of typing
			
			**parameters**
			- chatId : id of the chat
			- comId : id of the community
		"""

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.ws_send(req_t=304, body=data)

	def recording(self, chatId: str, comId: int | None = None) -> None:
		"""
			create the illusion of recording audio message
			
			**parameters**
			- chatId : id of the chat
			- comId : id of the community
		"""

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		self.ws_send(req_t=304, body=data)


	def join_live_chat(self, chatId: str, comId: int | None = None, as_viewer: bool = False) -> None:
		"""
			join to live chat

			**parameters**
			- chatId : id of the chat
			- comId : id of the community
			- as_viewer : join as a viewer
		"""
		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		self.ws_send(req_t=112, body=data)


	def browsing_leader_boards(self, comId: int) -> None:
		"""
			send a request that will show you in the list of those viewing the leaderboard

			**parameters**
			- comId : id of the community
		"""
		data = {
			"o": {
				"actions": ["Browsing"],
				"target": f"ndc://x{comId}/leaderboards",
				"ndcId": int(comId),
				"params": {"duration": 859},
			}
		}
		self.ws_send(req_t=306, body=data)




class Socket(EventHandler, WsRequester):
	"""
		Socket class for amino. used in the client
	"""

	active: bool = False
	socket: WebSocketApp | None = None

	def __init__(self, sock_trace: bool = False, socket_daemon: bool = False):
		enableTrace(sock_trace)
		self.socket_daemon = socket_daemon

	def ws_connect(self, headers: dict, final: str) -> None:
		"""
			connect to amino sockets
		"""
		
		if self.socket or self.active:
			log.debug(f"[Socket] The socket is already running.")
			return
		try:
			self.socket = WebSocketApp(
				f"{ws_url}/?signbody={final.replace('|', '%7C')}",
				header = headers,
				on_message=self.ws_resolve,
				on_open=self.ws_on_open,
				on_error=self.ws_on_error,
				on_close=self.ws_on_close,
			)
			Thread(target=self.socket.run_forever, kwargs={
				"ping_interval": ws_ping_interval,
				"ping_payload": '{"t": 116, "o": {"threadChannelUserInfoList": []}}'
			}, daemon=self.socket_daemon).start()
			sleep(1.5)
		except Exception as e:
			log.debug(f"[Socket] Error while starting Socket : {e}")


	def ws_disconnect(self) -> None:
		"""
			disconnect from amino sockets
		"""

		if self.socket is not None and self.active:
			log.debug(f"[Socket] closing socket...")
			try:
				self.socket.close()
			except Exception as e:
					log.debug(f"[Socket] Error while closing Socket : {e}")
		else:
			log.debug(f"[Socket] Socket not running.")

	def ws_send(self, req_t: int, **kwargs) -> None:
		"""
			send data to amino socket
		"""

		if not self.active or self.socket is None:raise SocketNotStarted
		data = dumps(dict(t=req_t, **kwargs))
		log.debug(f"[Socket] Sending Data : {data}")
		try:return self.socket.send(data)
		except WSexceptions.WebSocketConnectionClosedException:
			log.debug(f"[Socket] Socket not available : {data}")



	def ws_resolve(self, ws: Any, data: str | bytes | bytearray | dict) -> None:
		if isinstance(data, (bytes, bytearray, str)):d: dict = loads(data)
		elif isinstance(data, dict):d = data
		else:return
		self.call(d)



	def ws_on_close(self, ws: Any, data: str, status: int) -> None:
		self.active = False
		log.debug(f"[Socket] Socket closed: {data} [status: {status}]")

	def ws_on_error(self, ws: Any, error: Any) -> None:
		print_exc()
		log.error(f"[Socket] Error: {error}")

	def ws_on_open(self, ws: Any) -> None:
		self.active = True
		log.debug(f"[Socket] Socket started")
	

	def ws_headers(self, sid: str | None, final: str, deviceId: str | None) -> dict:
		return {
					"NDCDEVICEID": deviceId,
					"NDCAUTH": f"sid={sid}",
					"NDC-MSG-SIG": signature(final)
				}