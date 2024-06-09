
from threading import Thread
from websocket import WebSocketApp, enableTrace
from websocket import _exceptions as WSexceptions
from ujson import loads, dumps
from time import sleep



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

	def call(self, data):
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

	def create_socket_event(self, data):
		return self.ws_resolve(None, data)


	def online(self, comId: int):

		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		self.ws_send(req_t=304, body=data)


	def browsing_blogs(self, comId: int, blogId: str = None, quizId: str = None):
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}
		self.ws_send(req_t=304, body=data)


	def typing(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.ws_send(req_t=304, body=data)

	def recording(self, chatId: str, comId: int = None):

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		self.ws_send(req_t=304, body=data)


	def join_live_chat(self, chatId: str, comId: int = None, as_viewer: bool = False):

		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		self.ws_send(req_t=112, body=data)


	def browsing_leader_boards(self, comId: int):

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
	active: bool = False
	debug: bool = False
	socket = None

	def __init__(self, sock_trace: bool = False, debug: bool = False):
		self.debug=debug
		enableTrace(sock_trace)


	def socket_log(self, message: str):
		if self.debug:print(f"[Socket]{message}")

	def ws_connect(self, headers: dict, final: str):
		if self.socket or self.active:
			self.socket_log(f"[start] The socket is already running.")
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
			}).start()
			sleep(1.5)
		except Exception as e:
			self.socket_log(f"[start] Error while starting Socket : {e}")


	def ws_disconnect(self):
		if self.socket or self.active:
			self.socket_log(f"[stop] closing socket...")
			try:
				self.socket.close()
				self.active = False
			except Exception as e:
					self.socket_log(f"[stop] Error while closing Socket : {e}")
		else:
			self.socket_log(f"[stop] Socket not running.")

	def ws_send(self, req_t: int, **kwargs):
		if not self.active:raise SocketNotStarted
		data = dumps(dict(t=req_t, **kwargs))
		self.socket_log(f"[send] Sending Data : {data}")
		try:return self.socket.send(data)
		except WSexceptions.WebSocketConnectionClosedException:
			self.socket_log(f"[send] Socket not available : {data}")



	def ws_resolve(self, ws, data):
		try:data = loads(data)
		except:
			self.socket_log(f"[recive] The socket received an unreadable message: {data}")
			return
		self.socket_log(f"[recive]: {data}")
		self.call(data)



	def ws_on_close(self, ws, data, status):
		self.socket_log(f"[close] Socket closed: {data} [status: {status}]")

	def ws_on_error(self, ws, error):
		self.socket_log(f"[on_error]: {error}")

	def ws_on_open(self, ws):
		self.active = True
		self.socket_log(f"[start] Socket Started")
	

	def ws_headers(self, sid: str, final: str, deviceId: str = None):
		return {
					"NDCDEVICEID": deviceId if deviceId else generate_deviceId(),
					"NDCAUTH": f"sid={sid}",
					"NDC-MSG-SIG": signature(final)
				}




class Callbacks:
	def __init__(self):
		self.handlers = {}

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

	def call(self, data):
		data_object = data["o"]
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