# Telegram Crypto Bot
A friendly Telegram bot created for the ORE Network. Written in Python using aiogram.

# Installation

## Developer Requirements:
* Docker Version: 20.10.8, build 3967b7d or greater
* Python Version: 3.10.1
* VS Studio Code Version: 1.63.2
* Skaffold Version: 1.32.0
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
If you will be deploying to Kubernetes you will also have to rename ```configmap-example.yaml``` to ```configmap.yaml```.  And, edit the contents of ```configmap.yaml```.  
## Run the Telegram bot for development

### Locally starting a redis server 
When running locally, you will need to provide your own Redis server.  You can easily get a Redis server on Mac by:
```shell
# Install Redis using Home-brew
brew install redis

# Start the Redis server
brew services start redis

# Delete all key:value pairs on the Redis server
redis-cli FLUSHALL

# Stopping the Redis server
brew services stop redis
```
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

### On a Kubernetes cluster
Launch with skaffold
```shell
# First deploy the Redis database 
skaffold dev -p init-deploy-dev

# Now, deploy the Telegram app
skaffold dev -p development
```
Skaffold will now watch for changes to the app and build

## Running in Production

### On a production-ready Kubernetes cluster
Launch with skaffold
```shell
# First deploy the Redis database 
skaffold run -p init-deploy

# Now, deploy the Telegram app
skaffold run -p production
```