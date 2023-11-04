from amino.asynclib import Client
from asyncio import get_event_loop

email = "email@gmail.com"
password = "password"
client = Client(socket_enabled=False)

async def main():
	info = await client.login(email=email, password=password)
	print(info.json)



if __name__ == '__main__':
	loop = get_event_loop()
	loop.run_until_complete(main())