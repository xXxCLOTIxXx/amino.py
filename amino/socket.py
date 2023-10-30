from time import sleep, time
from json import dumps
from websocket import WebSocketApp, enableTrace
from threading import Thread
from random import randint
from traceback import format_exc


from .helpers.exceptions import SocketNotStarted
from .helpers.headers import ws_headers
from .models import objects
from .helpers.types import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types
)




class SocketHandler:
	socket_url = f"wss://ws{randint(1, 4)}.narvii.com"
	socket = None
	ping_time = 20
	socket_thread = None
	old_message = list()
	online_list = set()
	active_live_chats = list()
	run = True


	def __init__(self, whitelist_communities: list = None, old_message_mode: bool = False, sock_trace: bool = False, debug: bool = False):
		enableTrace(sock_trace)
		self.debug = debug
		self.old_message_mode = old_message_mode
		self.whitelist = whitelist_communities
		Thread(target=self.online_loop).start()
		if old_message_mode:
			Thread(target=self.old_message_handler).start()


	def connect(self):
		try:
			if self.debug:print(f"[socket][start] Starting Socket")
			if self.profile.sid is None:
				if self.debug:print(f"[socket][start] sid is None")
				return
			deviceId = self.deviceId
			final = f"{deviceId}|{int(time() * 1000)}"
			self.socket = WebSocketApp(
				f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
				on_message = self.handle_message,
				header = ws_headers(final=final, sid=self.profile.sid, deviceId=deviceId),
			)

			self.socket_thread = Thread(target=self.socket.run_forever)
			self.socket_thread.start()
			self.run = True
			sleep(1.5)
			if self.debug:
				print(f"[socket][start] Socket Started")
			Thread(target=self.connection_support).start()
		except Exception as e:
			if self.debug:
				print(f"[socket][start] Error while starting Socket : {e}")


	def close(self):
		if self.debug:
			print(f"[socket][close] Closing Socket")
		try:
			self.socket.close()
			self.run = False
		except Exception as closeError:
			if self.debug:
				print(f"[socket][close] Error while closing Socket : {closeError}")


	def connection_support(self):
		while self.run:
			self.send_action(116, {"threadChannelUserInfoList": []})
			sleep(self.ping_time)



	def send_action(self, message_type: int, body: dict):

		body["id"] = str(randint(1, 1000000))
		self.send(dumps({
				"t": message_type,
				"o": body,
			}))

	def send(self, data):
		if self.debug:
			print(f"[socket][send] Sending Data : {data}")
		if not self.socket_thread:
			if self.debug:
				print(f"[socket][send][error] Socket not started !")
				return
			raise SocketNotStarted()
		self.socket.send(data)



	def handle_message(self, ws, data):
		data = data.json()
		if self.whitelist:
			if data.get("ndcId") not in self.whitelist:
				if self.debug:
					print(f"[socket][handle_message] {data.get('ndcId')} not in whitelist")
				return
		try:
			self.old_message.append((ws, data)) if self.old_message_mode else self.call(data)
		except:
			print(format_exc())


	def old_message_handler(self):
		while self.run:
			for event in self.old_message:
				try:
					self.call(event[1])
				except:
					print(format_exc())
				self.old_message.remove(event)




	def online_loop(self):
		while self.run:
			for com in self.online_list:
				self.send_action(message_type=304, body={
					"actions": ["Browsing"],
					"target":f"ndc://x{com}/",
					"ndcId":com
				})
				sleep(1.5)
			sleep(self.ping_time)



	def vc_loop(self, comId: int, chatId: str, joinType: str):
		while chatId in self.active_live_chats and self.run:
			self.join_live_chat(chatId=chatId, comId=comId, as_viewer=joinType)
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
		data_object = objects.Event(data["o"])
		method = ws_message_methods.get(data["t"])
		if method in ("chat_action_start", "chat_action_end") :
			key = data['o'].get('actions', 0)
			ws_event = ws_chat_action_start.get(key) if method == "chat_action_start" else ws_chat_action_end.get(key)
		elif method == "chat_message":
			key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
			ws_event = ws_message_types.get(key)
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