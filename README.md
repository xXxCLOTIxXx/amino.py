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
		<hr>
		<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=2000&pause=2000&color=3DACF7&random=false&width=200&repeat=false&lines=Installation" alt="Installation"/>
	<p>Git</p>
	
```bash
pip install git+https://github.com/xXxCLOTIxXx/amino.py.git
```
<p>pypi</p>

```bash
pip install amino.api.py
```
</div>

<p align="center">Library for working with aminoapps servers, below you will see code examples, for more examples see the documentation or the examples folder</p>
<h1 align="center">Login example</h1>

```python
import amino

client = amino.Client()
client.login(email='email', password='password')
```
<h1 align="center">Ping pong bot</h1>

```python
import amino

client = amino.Client()
client.login(email='email', password='password')
print(f"LOGIN: OK.")


@client.event(amino.arguments.wsEvent.on_text_message)
def text_msg(data: amino.objects.Event):
    if data.comId is None or data.message.author.uid == client.userId: return
    print(f"New message: {data.message.content}")
    try:
        com_client = amino.CommunityClient(client.profile, data.comId)
        if data.message.content.lower().split(" ")[0] == "ping":
            com_client.send_message(data.message.threadId, "Pong!", replyTo=data.message.messageId)
        elif data.message.content.lower().split(" ")[0] == "pong":
            com_client.send_message(data.message.threadId, "Ping!", replyTo=data.message.messageId)
    except Exception as e:
        print(e)


```

<p align="center">
<a href="https://github.com/xXxCLOTIxXx/amino.py/blob/main/docs/main.md">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&duration=1&pause=31&color=3DACF7&random=false&width=195&lines=Read+the+documentation" alt="=Read the documentation"/>
</a>
</p>
</body>
