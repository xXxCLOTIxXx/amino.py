
ws_message_methods = {
			304: "chat_action_start",
			306: "chat_action_end",
			1000: "chat_message",
			10: "notification"
}

ws_chat_action_start = {
	"Typing": "typing_start",
	"Recording": "recording_start" 
}

ws_chat_action_end = {
	"Typing": "typing_end",
	"Recording": "recording_end" 
}


notification_types = {
	18: "on_message_notification",
	29: "on_invite_to_voice_chat_notification",
	37: "on_invite_to_video_chat_notification",

}

ws_message_types = {
	"0:0": "on_text_message",
	"0:100": "on_image_message",
	"0:103": "on_youtube_message",
	"1:0": "on_strike_message",
	"2:110": "on_voice_message",
	"3:113": "on_sticker_message",
	"52:0": "on_voice_chat_not_answered",
	"53:0": "on_voice_chat_not_cancelled",
	"54:0": "on_voice_chat_not_declined",
	"55:0": "on_video_chat_not_answered",
	"56:0": "on_video_chat_not_cancelled",
	"57:0": "on_video_chat_not_declined",
	"58:0": "on_avatar_chat_not_answered",
	"59:0": "on_avatar_chat_not_cancelled",
	"60:0": "on_avatar_chat_not_declined",
	"100:0": "on_delete_message",
	"101:0": "on_group_member_join",
	"102:0": "on_group_member_leave",
	"103:0": "on_chat_invite",
	"104:0": "on_chat_background_changed",
	"105:0": "on_chat_title_changed",
	"106:0": "on_chat_icon_changed",
	"107:0": "on_voice_chat_start",
	"108:0": "on_video_chat_start",
	"109:0": "on_avatar_chat_start",
	"110:0": "on_voice_chat_end",
	"111:0": "on_video_chat_end",
	"112:0": "on_avatar_chat_end",
	"113:0": "on_chat_content_changed",
	"114:0": "on_screen_room_start",
	"115:0": "on_screen_room_end",
	"116:0": "on_chat_host_transfered",
	"117:0": "on_text_message_force_removed",
	"118:0": "on_chat_removed_message",
	"119:0": "on_text_message_removed_by_admin",
	"120:0": "on_chat_tip",
	"121:0": "on_chat_pin_announcement",
	"122:0": "on_voice_chat_permission_open_to_everyone",
	"123:0": "on_voice_chat_permission_invited_and_requested",
	"124:0": "on_voice_chat_permission_invite_only",
	"125:0": "on_chat_view_only_enabled",
	"126:0": "on_chat_view_only_disabled",
	"127:0": "on_chat_unpin_announcement",
	"128:0": "on_chat_tipping_enabled",
	"129:0": "on_chat_tipping_disabled",
	"65281:0": "on_timestamp_message",
	"65282:0": "on_welcome_message",
	"65283:0": "on_invite_message"
}

def all_ws_types():
	return list(ws_message_types.values()) +\
	list(ws_message_methods.values()) +\
	list(ws_chat_action_start.values()) +\
	list(ws_chat_action_end.values()) +\
	list(notification_types.values())+\
	["on_ws_message"]




renamed = {
	"ndcId": "comId",
	"threadId": "chatId",
	"uid": "userId",
	"auid": "userId",
	"api:message": "api_message",
	"api:statuscode": "api_statuscode",
	"api:duration": "api_duration",
	"api:timestamp": "api_timestamp"
}


community_modules = {
	"chat": "module.chat.enabled",
	"livechat": "module.chat.avChat.videoEnabled",
	"screeningroom": "module.chat.avChat.screeningRoomEnabled",
	"publicchats": "module.chat.publicChat.enabled",
	"posts": "module.post.enabled",
	"ranking": "module.ranking.enabled",
	"leaderboards": "module.ranking.leaderboardEnabled",
	"featured": "module.featured.enabled",
	"featuredposts": "module.featured.postEnabled",
	"featuredusers": "module.featured.memberEnabled",
	"featuredchats": "module.featured.publicChatRoomEnabled",
	"sharedfolder": "module.sharedFolder.enabled",
	"influencer": "module.influencer.enabled",
	"catalog": "module.catalog.enabled",
	"externalcontent": "module.externalContent.enabled",
	"topiccategories": "module.topicCategories.enabled"
}