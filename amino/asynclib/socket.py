from aiohttp import ClientSession, WSMsgType
from asyncio import create_task, sleep

from time import time
from json import dumps
from random import randint
from traceback import format_exc



from amino.helpers.exceptions import SocketNotStarted
from amino.helpers.headers import ws_headers
from amino.models import objects
from amino.helpers.types import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types
)


class SocketHandler:
	socket_url = f"wss://ws{randint(1, 4)}.narvii.com"
	ping_time = 20
	old_message = list()
	online_list = set()
	active_live_chats = list()
	task_resolve = None
	connection = None
	connection_support_loop = None

	def __init__(self, whitelist_communities: list = None, old_message_mode: bool = False, debug: bool = False):
		self.debug = debug
		self.old_message_mode = old_message_mode
		self.whitelist = whitelist_communities


	async def connect(self):
		try:
			if self.debug:
				print(f"[socket][start] Starting Socket")
			deviceId = self.deviceId
			final = f"{deviceId}|{int(time() * 1000)}"
			self.connection = await self.session.ws_connect(f"{socket_url}/?signbody={final.replace('|', '%7C')}", headers=ws_headers(final=final, sid=self.profile.sid, deviceId=deviceId))
			self.task_resolve = create_task(self.resolve())
			self.connection_support_loop = create_task(self.connection_support())
			if self.debug:
				print(f"[socket][start] Socket Started")
		except Exception as e:
			if self.debug:
				print(f"[socket][start] Error while starting Socket : {e}")


	async def disconnect(self):
		if self.debug:
			print(f"[socket][close] Closing Socket")
		try:
			if self.task_resolve: self.task_resolve.cancel()

			if self.connection:
				await self.connection.close()
				self.connection = None

			if self.connection_support_loop:
				self.self.connection_support_loop.cancel()
				self.connection_support_loop = None

			if self.debug:
				print(f"[socket][close] Socket closed")
		except Exception as e:
			if self.debug:
				print(f"[socket][close] Error while closing Socket : {e}")



	async def resolve(self):
		while True:
			msg = await self.connection.receive()
			data = msg.data.json
			await self.call(data)


	async def send(self, data):
		if self.debug:
			print(f"[socket][send] Sending Data : {data}")
		if not self.connection:
			if self.debug:
				print(f"[socket][send][error] Socket not started !")
				return
			raise SocketNotStarted()
		await self.connection.send_str(data)

	async def send_action(self, message_type: int, body: dict):

		body["id"] = str(randint(1, 1000000))
		await self.send(dumps({
				"t": message_type,
				"o": body,
			}))


	async def connection_support(self):
		while True:
			await self.send_action(116, {"threadChannelUserInfoList": []})
			await sleep(self.ping_time)






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

	async def call(self, data):
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
				await func(data_object)
		if method in self.handlers.keys():
			for func in self.handlers[method]:
				await func(data_object)
		if ws_event:
			if ws_event in self.handlers.keys():
				for func in self.handlers[ws_event]:
					await func(data_object)