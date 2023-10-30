from amino import Client, all_ws_types
from time import time

email = "email@gmail.com"
password = "password"

client = Client()
client.login(email=email, password=password)

all_event_types = all_ws_types() #all event types
print(all_event_types)


#will trigger when there is a new message in chat (only for text message)
@client.event("on_text_message")
def on_message(data):
	print("\n\n(on_text_message))")
	print(data.json)


#will trigger when there is a new message in chat (only for stickers)
@client.event("on_strike_message")
def on_message(data):
	print("\n\n(on_strike_message))")
	print(data.json)

"""
will trigger when there is a new message in the chat (any message)

@client.on_message()
def on_message(data):
	print("\n\n(on_message))")
	print(data.json)
"""

"""
will fire on a new socket message

@client.event("on_ws_message")
def on_message(data):
	print("\n\n(on_ws_message))")
	print(data.json)


"""