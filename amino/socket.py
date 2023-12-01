from time import sleep, time
from json import dumps, loads, JSONDecodeError
from websocket import WebSocketApp, enableTrace
from threading import Thread
from random import randint
from traceback import format_exc
from datetime import datetime
import ssl

from .helpers.exceptions import SocketNotStarted, WrongType
from .helpers.headers import ws_headers
from .models.objects import ObjectCreator
from .models.proxy_settings import SocketProxy
from .helpers.types import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types,
	notification_types
)




class SocketHandler:
	socket_url = f"wss://ws{randint(1, 4)}.aminoapps.com"
	socket = None
	ping_time = 1.5
	socket_thread = None
	old_message = list()
	actions_list = list()
	active_live_chats = list()
	run = True


	def __init__(self, socket_proxy: SocketProxy = SocketProxy(), whitelist_communities: list = None, old_message_mode: bool = False, sock_trace: bool = False, debug: bool = False):
		enableTrace(sock_trace)
		self.debug = debug
		self.old_message_mode = old_message_mode
		self.whitelist = whitelist_communities
		self.socket_proxy = socket_proxy
		Thread(target=self.actions_loop).start()
		if old_message_mode:
			Thread(target=self.old_message_handler).start()

	def log(self, type: str, message: str):
		if self.debug:print(f"[{datetime.now()}][WS][{type}]: {message}")



	def socket_error(self, ws, err):
		self.log(type="FATAL", message=err)




	def _create_connection(self):

			deviceId = self.deviceId
			final = f"{deviceId}|{int(time() * 1000)}"
			return WebSocketApp(
				f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
				on_message = self.handle_message,
				header = ws_headers(final=final, sid=self.profile.sid, deviceId=deviceId),
				on_error = self.socket_error
			)

	def connect(self):
		try:
			self.log("Start", f"Creating a connection to {self.socket_url}")
			if self.profile.sid is None:
				self.log("StartError", f"sid is None")
				return
			self.socket = self._create_connection()
			self.socket_thread = Thread(target=self.ws_run_forever)
			self.socket_thread.start()
			self.run = True
			sleep(1.5)
			Thread(target=self.connection_support).start()
			self.log("Start", f"Connection established")
		except Exception as e:
			self.log("StartError", f"Error while starting Socket : {e}")

	def ws_run_forever(self):
		if not isinstance(self.socket_proxy, SocketProxy):raise WrongType(f"type socket_proxy != class SocketProxy")
		self.socket.run_forever(
			proxy_type=self.socket_proxy.proxy_type,
			sslopt={"cert_reqs": ssl.CERT_NONE},
			skip_utf8_validation=True,
			http_proxy_host=self.socket_proxy.http_proxy_host,
			http_proxy_port=self.socket_proxy.http_proxy_port,
			http_proxy_auth=self.socket_proxy.http_proxy_auth,
			ping_interval=self.ping_time*2,
			)

	def close(self):
		self.log("Disconnect", f"Closing Socket")
		try:
			self.socket.close()
			self.run = False
			self.socket_thread = None
			self.log("Disconnect", f"Socket closed")
		except Exception as e:
			self.log("CloseError", f"Error while closing Socket : {e}")


	def send_action(self, message_type: int, body: dict):

		self.send(dumps({
				"t": message_type,
				"o": body,
			}))

	def send(self, data):
		self.log("Send", f"Sending Data : {data}")
		if not self.socket_thread:raise SocketNotStarted()
		try:self.socket.send(data)
		except Exception as e:
			self.log("SendError", f"Error while sending data : {e}")



	def handle_message(self, ws, data):
		try:data = loads(data)
		except JSONDecodeError:
			self.log("Receive", f"An unreadable message was received")
			return
		self.log("Receive", f"Message type {data['t']} received")
		if self.whitelist:
			if data.get('o', {}).get("ndcId") not in self.whitelist:
				self.log("Whitelist", f"{data.get('o',{}).get('ndcId')} not in whitelist")
				return
		self.old_message.append((ws, data)) if self.old_message_mode else self.call(data)


	def old_message_handler(self):
		while self.run:
			for event in self.old_message:
				try:
					self.call(event[1])
				except:
					print(format_exc())
				self.old_message.remove(event)




	def actions_loop(self):
		while self.run:
			temp = self.actions_list
			for data in temp:
				try:self.send_action(message_type=304, body=data)
				except:pass
				sleep(1.5)
			sleep(self.ping_time)

	def vc_loop(self, comId: int, chatId: str, joinType: str):
		while chatId in self.active_live_chats and self.run:
			self.join_live_chat(chatId=chatId, comId=comId, as_viewer=joinType)
			sleep(self.ping_time)



	def connection_support(self):
		while self.run:
			self.send_action(116, {"threadChannelUserInfoList": []})
			sleep(self.ping_time)




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
		data_object = ObjectCreator(data["o"])
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