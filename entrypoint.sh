#!/usr/bin/env sh

# git clone https://${GIT_TOKEN}@github.com/boyroywax/resources.git $APP_HOME/tmp
# mv $APP_HOME/tmp/* $APP_HOME/
mkdir -p $APP_HOME/meme_entries
touch $APP_HOME/meme_entries/test

python3 $APP_HOME/main.py