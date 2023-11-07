from amino import Client, CommunityClient

#============settings============

email = "email@gmail.com" #account email
password = "password" #account password
white_list = [] #comId of the communities in which the bot will respond to events (optional)

#================================

client = Client(socket_whitelist_communities=white_list or None)


def auth():
	try:
		client.login(email=email, password=password)
		print(f"Successful login as {email}.")
	except Exception as e:
		print(f"Error login.\n{e}")
		exit()


@client.event("on_ws_message")
def online(data):
	if data.comId:client.online(data.comId)


@client.event("on_voice_chat_start")
def on_invite_to_voice_chat_notification(data):
	client.join_live_chat(comId=data.comId, chatId=data.chatMessage.chatId)


@client.event("on_chat_invite")
def on_chat_invite(data):
	sub = CommunityClient(profile=client.profile, comId=data.comId, deviceId=client.deviceId)
	sub.join_chat(chatId=data.chatMessage.chatId)
	sub.send_message(message="Sorry, i'm a bot :(", chatId=data.chatMessage.chatId)


@client.on_message()
def text_message(data):
	if data.chatMessage.content:
		sub = CommunityClient(profile=client.profile, comId=data.comId, deviceId=client.deviceId)
		chatId = data.chatMessage.chatId
		content = data.chatMessage.content
		messageId = data.chatMessage.messageId
		split_content = content.split(" ")
		
		if split_content[0][0] == "/":
			if split_content[0][1:].lower() == "ping":
				sub.send_message(message="Pong!", chatId=chatId, replyTo=messageId)
			elif split_content[0][1:].lower() == "pong":
				sub.send_message(message="Ping!", chatId=chatId, replyTo=messageId)




if __name__ == "__main__":
	auth()