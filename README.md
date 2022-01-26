# Telegram Crypto Bot
A friendly Telegram bot created for the ORE Network. Written in Python using aiogram.

# Installation

## Developer Requirements:
* Docker Version: 20.10.8, build 3967b7d or greater
* Python Version: 3.10.1
* VS Studio Code Version: 1.63.2
* Flake8 Linter (can ignore E501-line too long)
* Redis server
* CoinMarketCap [API Key](https://coinmarketcap.com/api/documentation/v1/#section/Introduction)
* Telegram Bot [API Key](https://stackoverflow.com/questions/43291868/where-to-find-the-telegram-api-key)

## Download Repo & Prepare for Deployment
```shell
git clone https://github.com/boyroywax/ore-tip-bot-telegram
```
Rename the ```.env-example``` to ```.env``` and fill in API Keys and Test info.
```shell
cp .env-example .env
```
## Run the Telegram bot:
### Locally using .venv
Start up your local virtual environment
```shell
source .venv/bin/activate
```
Build the dependencies
```shell
pip3 install -r requirements.txt
```
Run main.py
```shell
python3 src/main.py
```
The Bot should now be connected and outputting info to your terminal.

### Locally using docker
Build with Docker
```shell
docker build . -t githubuser/ore-tip-bot
```
Run with Docker
```shell
docker run githubuser/ore-tip-bot
```
The Bot should now be connected and outputting info to your terminal.
