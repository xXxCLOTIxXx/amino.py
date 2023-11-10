
from amino.asynclib import Client
from asyncio import get_event_loop
from aiofiles import open as async_open

email = "email@gmail.com"
password = "password"
icon="amino_api_icon.png"
client = Client(socket_enabled=False)

async def main():
	await client.login(email=email, password=password)
	print(await client.upload_media(file=await async_open(icon, "rb"), fileType="image"))



if __name__ == '__main__':
	loop = get_event_loop()
	loop.run_until_complete(main())