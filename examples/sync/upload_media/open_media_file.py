
from amino import Client

email = "email@gmail.com"
password = "password"
icon="amino_api_icon.png"
client = Client(socket_enabled=False)


client.login(email=email, password=password)
with open(icon, "rb") as file:
	print(client.upload_media(file=file, fileType="image"))