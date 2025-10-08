<body>
	<p align="center">
	    <a href="#"><img src="https://github.com/xXxCLOTIxXx/amino.py/blob/main/card.png"/></a>
	    <a href="https://github.com/xXxCLOTIxXx/amino.py/releases"><img src="https://img.shields.io/github/v/release/xXxCLOTIxXx/amino.py" alt="GitHub release" />
	    <a href="https://github.com/xXxCLOTIxXx/amino.py/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="licence" /></a>
	    <a href="https://pypi.org/project/amino.py.api/"><img src="https://img.shields.io/pypi/v/amino.py.api" alt="pypi" /></a>
	    <a href="https://github.com/xXxCLOTIxXx/amino.py/blob/main/docs/main.md"><img src="https://img.shields.io/website?down_message=failing&label=docs&up_color=green&up_message=passing&url=https://github.com/xXxCLOTIxXx/amino.py/blob/main/docs/main.md" alt="docs" /></a>
	<img src="https://img.shields.io/pypi/dm/amino.py.api" />
	</p>
	<div align="center">
		<a href="https://github.com/xXxCLOTIxXx/xXxCLOTIxXx/blob/main/sponsor.md">
			<img src="https://img.shields.io/badge/%D0%A1%D0%BF%D0%BE%D0%BD%D1%81%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-Donate-F79B1F?style=for-the-badge&logo=github&logoColor=FF69B4&color=FF69B4" alt="Sponsor project"/>
		</a>
<a href="https://github.com/xXxCLOTIxXx/xXxCLOTIxXx/blob/main/contacts.md"><img src="https://img.shields.io/badge/Контакты-Contacts-F79B1F?style=for-the-badge&logoColor=0077b6&color=0077b6" alt="contacts" /></a>
		<hr>
		<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=2000&pause=2000&color=3DACF7&random=false&width=200&repeat=false&lines=Installation" alt="Installation"/>
	</div>
	<h1 align="center">Git</h1>
	
```bash
pip install git+https://github.com/xXxCLOTIxXx/amino.py.git
```
<h1 align="center">pypi</h1>

```bash
pip install amino.api.py
```
</div>

<p align="center">Library for working with aminoapps servers, below you will see code examples</p>
<h1 align="center">Login example</h1>

```python
import amino

service_key = "" #get from telegram bot @aminodorks_bot
amino.set_dorksapi_key(service_key) #to generate a new signature 

client = amino.Client()
client.login(email='email', password='password')
```
<h1 align="center">Ping pong bot</h1>

```python
import amino

deviceId = None
service_key = "" #get from telegram bot @aminodorks_bot

amino.set_dorksapi_key(service_key) #to generate a new signature 
client = amino.Client(deviceId=deviceId, socket_daemon=True)



@client.event(amino.args.wsEvent.on_text_message)
def text_msg(data: amino.Event):
    if data.comId is None or data.message.author.userId == client.userId: return
    print(f"New message: {data.message.content}")
    try:
        com_client = amino.SubClient(client, data.comId)
        if data.message.content.lower().split(" ")[0] == "ping":
            com_client.send_message(data.message.chatId, "Pong!")
        elif data.message.content.lower().split(" ")[0] == "pong":
            com_client.send_message(data.message.chatId, "Ping!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    client.login(email='email', password='password')
    print(f"LOGIN: OK.")
    client.wait_socket()

```

<p align="center">
<a href="https://github.com/xXxCLOTIxXx/amino.py/blob/main/docs/main.md">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&duration=1&pause=31&color=3DACF7&random=false&width=195&lines=Read+the+documentation" alt="=Read the documentation"/>
</a>
</p>
</body>
