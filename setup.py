from setuptools import setup, find_packages


info = {
	"name": "amino.py.api",
	"version": "0.4.7",
	"github_page": "https://github.com/xXxCLOTIxXx/amino.py",
	"download_link": "https://github.com/xXxCLOTIxXx/amino.py/archive/refs/heads/main.zip",
	"license": "MIT",
	"author": "Xsarz",
	"author_email": "xsarzy@gmail.com",
	"description": "Library for creating amino bots and scripts.",
	"long_description": None,
	"long_description_file": "README.md",
	"long_description_content_type": "text/markdown",
	"keywords": [
		"aminoapps",
		"aminoxz",
		"amino",
		"amino-bot",
		"pymino",
		"python-amino",
		"amino.py",
		"amino.api",
		"narvii",
		"api",
		"python",
		"python3",
		"python3.x",
		"xsarz",
		"official",
		"amino.py.api",
		"amino.fix",
		"amino.light",
		"amino.ligt.py",
		"AminoLightPy",
		"medialab",
		"aminolightpy",
	],

	"install_requires": [
		"requests",
		"aiohttp",
		"websocket-client==1.3.1",
		"websockets",
		"ujson",
		"json_minify"

	]

}


if info.get("long_description"):
	long_description=info.get("long_description")
else:
	with open(info.get("long_description_file"), "r") as file:
		long_description = file.read()

setup(
	name = info.get("name"),
	version = info.get("version"),
	url = info.get("github_page"),
	download_url = info.get("download_link"),
	license = info.get("license"),
	author = info.get("author"),
	author_email = info.get("author_email"),
	description = info.get("description"),
	long_description = long_description,
	long_description_content_type = info.get("long_description_content_type"),
	keywords = info.get("keywords"),
	install_requires = info.get("install_requires"),
	packages = find_packages(),
    	classifiers=[
	        "Intended Audience :: Developers",
	        "License :: OSI Approved :: MIT License",
	        "Programming Language :: Python :: 3.9",
	        "Programming Language :: Python :: 3.10",
	        "Programming Language :: Python :: 3.11",
	        "Programming Language :: Python :: 3.12",
    ],
)
