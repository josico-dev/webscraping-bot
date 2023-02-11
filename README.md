# webscraping-bot
A telegram bot for webscraping a torrent site.

## Usage/Examples  
~~~
version: '3.7'
services:
  telegram-bot:
    image: telegram-bot:latest
    container_name: telegrambot
    environment:
      - TELEGRAM_TOKEN=#telegramtoken
      - PYTHONUNBUFFERED=1
      - TR_USER=#transmissionuser
      - TR_PASS=#transmissionpass
      - DOWNLOAD_DIR=#pathtodir
      - DONTORRENT_URL=#url
      - USERS=#usersIDsplitbycommas
    network_mode: 'host'
    restart: unless-stopped 
~~~  