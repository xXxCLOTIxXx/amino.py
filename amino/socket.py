from time import sleep, time
from json import loads, dumps
from websocket import WebSocketApp, enableTrace
from threading import Thread
from sys import _getframe as getframe
from random import randint
from traceback import format_exc


from .helpers.exceptions import SocketNotStarted
from .helpers.headers import ws_headers
from .helpers import objects
from .helpers.generators import generate_action_id



class SocketHandler:
	socket_url = "wss://ws1.narvii.com"
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
		data = loads(data)
		if self.whitelist:
			if data.get("ndcId") not in self.whitelist:
				if self.debug:
					print(f"[socket][handle_message] {data.get('ndcId')} not in whitelist")
				return
		try:
			self.old_message.append((ws, data)) if self.old_message_mode else self.resolve(data)
		except:
			print(format_exc())


	def old_message_handler(self):
		while self.run:
			for event in self.old_message:
				try:
					self.resolve(event[1])
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
		self.methods = {
			304: self._resolve_chat_action_start,
			306: self._resolve_chat_action_end,
			1000: self._resolve_chat_message
		}

		self.chat_methods = {
			"0:0": self.on_text_message,
			"0:100": self.on_image_message,
			"0:103": self.on_youtube_message,
			"1:0": self.on_strike_message,
			"2:110": self.on_voice_message,
			"3:113": self.on_sticker_message,
			"52:0": self.on_voice_chat_not_answered,
			"53:0": self.on_voice_chat_not_cancelled,
			"54:0": self.on_voice_chat_not_declined,
			"55:0": self.on_video_chat_not_answered,
			"56:0": self.on_video_chat_not_cancelled,
			"57:0": self.on_video_chat_not_declined,
			"58:0": self.on_avatar_chat_not_answered,
			"59:0": self.on_avatar_chat_not_cancelled,
			"60:0": self.on_avatar_chat_not_declined,
			"100:0": self.on_delete_message,
			"101:0": self.on_group_member_join,
			"102:0": self.on_group_member_leave,
			"103:0": self.on_chat_invite,
			"104:0": self.on_chat_background_changed,
			"105:0": self.on_chat_title_changed,
			"106:0": self.on_chat_icon_changed,
			"107:0": self.on_voice_chat_start,
			"108:0": self.on_video_chat_start,
			"109:0": self.on_avatar_chat_start,
			"110:0": self.on_voice_chat_end,
			"111:0": self.on_video_chat_end,
			"112:0": self.on_avatar_chat_end,
			"113:0": self.on_chat_content_changed,
			"114:0": self.on_screen_room_start,
			"115:0": self.on_screen_room_end,
			"116:0": self.on_chat_host_transfered,
			"117:0": self.on_text_message_force_removed,
			"118:0": self.on_chat_removed_message,
			"119:0": self.on_text_message_removed_by_admin,
			"120:0": self.on_chat_tip,
			"121:0": self.on_chat_pin_announcement,
			"122:0": self.on_voice_chat_permission_open_to_everyone,
			"123:0": self.on_voice_chat_permission_invited_and_requested,
			"124:0": self.on_voice_chat_permission_invite_only,
			"125:0": self.on_chat_view_only_enabled,
			"126:0": self.on_chat_view_only_disabled,
			"127:0": self.on_chat_unpin_announcement,
			"128:0": self.on_chat_tipping_enabled,
			"129:0": self.on_chat_tipping_disabled,
			"65281:0": self.on_timestamp_message,
			"65282:0": self.on_welcome_message,
			"65283:0": self.on_invite_message
		}

		self.chat_actions_start = {
			"Typing": self.on_user_typing_start,
		}

		self.chat_actions_end = {
			"Typing": self.on_user_typing_end,
		}

	def _resolve_chat_message(self, data):
		key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
		return self.chat_methods.get(key, self.default)(data)

	def _resolve_chat_action_start(self, data):
		key = data['o'].get('actions', 0)
		return self.chat_actions_start.get(key, self.default)(data)

	def _resolve_chat_action_end(self, data):
		key = data['o'].get('actions', 0)
		return self.chat_actions_end.get(key, self.default)(data)

	def resolve(self, data):
		self.on_ws_message(data)
		self.methods.get(data["t"], self.default)(data)

	def call(self, type, data):
		if type in self.handlers:
			for handler in self.handlers[type]:
				handler(data)

	def event(self, type):
		def registerHandler(handler):
			if type in self.handlers:
				self.handlers[type].append(handler)
			else:
				self.handlers[type] = [handler]
			return handler

		return registerHandler

	def on_text_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_image_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_youtube_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_strike_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_sticker_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_video_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_video_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_video_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_avatar_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_avatar_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_avatar_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_delete_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_group_member_join(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_group_member_leave(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_invite(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_background_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_title_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_icon_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_video_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_avatar_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_video_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_avatar_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_content_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_screen_room_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_screen_room_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_host_transfered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_text_message_force_removed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_removed_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_text_message_removed_by_admin(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_tip(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_pin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_permission_open_to_everyone(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_permission_invited_and_requested(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_voice_chat_permission_invite_only(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_view_only_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_view_only_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_unpin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_tipping_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_chat_tipping_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_timestamp_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_welcome_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_invite_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))

	def on_user_typing_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_user_typing_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))
	def on_ws_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]))

	def default(self, data): self.call(getframe(0).f_code.co_name, data)