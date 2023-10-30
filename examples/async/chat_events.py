from amino.asynclib import Client
from amino import all_ws_types
from asyncio import get_event_loop

email = "email@gmail.com"
password = "password"
client = Client()

all_event_types = all_ws_types() #all event types
print(all_event_types)

async def main():
	await client.login(email=email, password=password)


#will trigger when there is a new message in chat (only for text message)
@client.event("on_text_message")
async def on_message(data):
	print("\n\n(on_text_message))")
	print(data.json)


#will trigger when there is a new message in chat (only for stickers)
@client.event("on_strike_message")
async def on_message(data):
	print("\n\n(on_strike_message))")
	print(data.json)
	prin(data.comId)

"""
will trigger when there is a new message in the chat (any message)

@client.on_message()
async def on_message(data):
	print("\n\n(on_message))")
	print(data.json)
"""

"""
will fire on a new socket message

@client.event("on_ws_message")
async def on_message(data):
	print("\n\n(on_ws_message))")
	print(data.json)


"""



if __name__ == '__main__':
	loop = get_event_loop()
	loop.run_until_complete(main())