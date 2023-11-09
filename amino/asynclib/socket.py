from aiohttp import WSMsgType, ClientWebSocketResponse
from asyncio import create_task, sleep
from time import time
from json import dumps, loads, JSONDecodeError
from random import randint
from datetime import datetime

from amino.helpers.exceptions import SocketNotStarted
from amino.helpers.headers import ws_headers
from amino.models.objects import ObjectCreator
from amino.helpers.types import (
	ws_message_methods,
	ws_chat_action_start,
	ws_chat_action_end,
	ws_message_types,
	notification_types
)


class SocketHandler:
	socket_url = f"wss://ws{randint(1, 4)}.aminoapps.com"
	ping_time = 1.5
	actions_list = list()
	active_live_chats = list()
	connection = None
	connection_support_loop = None
	_actions_loop = None
	_reslove = None

	def __init__(self, whitelist_communities: list = None, debug: bool = False):
		self.debug = debug
		self.whitelist = whitelist_communities


	def log(self, type: str, message: str):
		if self.debug:print(f"[{datetime.now()}][WS][{type}]: {message}")

	async def _create_connection(self) -> ClientWebSocketResponse:
		deviceId = self.deviceId
		final = f"{deviceId}|{int(time() * 1000)}"
		connection = await self.session.ws_connect(
			f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
			headers=ws_headers(
				final=final,
				sid=self.profile.sid,
				deviceId=deviceId
				)
			)
		return connection


	async def connect(self):
		try:
			self.log("Start", f"Creating a connection to {self.socket_url}")
			if self.profile.sid is None:
				self.log("StartError", f"sid is None")
				return
			self.connection = await self._create_connection()
			self.connection_support_loop = create_task(self.connection_support())
			self._actions_loop = create_task(self.actions_loop())
			self.log("Start", f"Connection established")
		except Exception as e:
			self.log("StartError", f"Error while starting Socket : {e}")
			return



	async def disconnect(self):
		self.log("Disconnect", f"Closing Socket")
		try:
			await self.connection.close()
			self.connection = None
			self.connection_support_loop.cancel()
			self._actions_loop.cancel()
			self.active_live_chats = list()
			self.log("Disconnect", f"Socket closed")
		except Exception as e:
			self.log("CloseError", f"Error while closing Socket : {e}")


	async def receive(self):

		async for raw_message in self.connection:
			if raw_message.type == WSMsgType.ping:
				await self.connection.pong()
				continue
			if raw_message.type != WSMsgType.text:
				self.log("Receive", f"A message of an unprocessed type was received. [{raw_message.type}]")
				continue
			try:data = loads(raw_message.data)
			except JSONDecodeError:
				self.log("Receive", f"An unreadable message was received")
				continue
			self.log("Receive", f"Message type {data['t']} received")
			if self.whitelist:
				if data.get('o',{}).get("ndcId") not in self.whitelist:
					self.log("Whitelist", f"{data.get('o',{}).get('ndcId')} not in whitelist")
					return
			await self.call(data)
		self.log("ConnectionError", f"Connection lost")

	async def send(self, data):

		self.log("Send", f"Sending Data : {data}")
		if not self.connection:raise SocketNotStarted()
		try:await self.connection.send_str(data)
		except Exception as e:
			self.log("SendError", f"Error while sending data : {e}")


	async def send_action(self, message_type: int, body: dict):

		await self.send(dumps({
				"t": message_type,
				"o": body,
			}))

	async def connection_support(self):
		while True:
			await sleep(self.ping_time)
			await self.send_action(116, {"threadChannelUserInfoList": []})



	async def actions_loop(self):
		while True:
			temp = self.actions_list
			for data in temp:
				try: await self.send_action(message_type=304, body=data)
				except:pass
				await sleep(1.5)
			await sleep(self.ping_time)


	async def vc_loop(self, comId: int, chatId: str, joinType: str):
		while chatId in self.active_live_chats:
			await self.join_live_chat(chatId=chatId, comId=comId, as_viewer=joinType)
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
				await func(data_object)
		if method in self.handlers.keys():
			for func in self.handlers[method]:
				await func(data_object)
		if ws_event:
			if ws_event in self.handlers.keys():
				for func in self.handlers[ws_event]:
					await func(data_object)