from collections import deque

from aiogram import Bot

from tools.read import read2list, read_users, read_send_media, read_token

class Settings:
    token: str = ''
    admin_id: int = [5221532379]
    users = {}
    users_block = []
    users_notchat = []
    send_media = []
    #admins_block = []
    #queue_send_video = deque()
    send_video = []
    db_path = "./file.db3"
    sources={
        "случайное фото":{
            'name_tbl':'picture',
            'path':'SOURCE/RANDOM_FOTO',
            'path_private':''},
            #'path':'SOURCE/RANDOM_FOTO'},
        "максим":{
            'name_tbl':'maksim',
            'path':'SOURCE/МАКСИМ',
            'path_private':'SOURCE_PRIVATE/МАКСИМ'},
        "катя":{
            'name_tbl':'katya',
            'path':'SOURCE/КАТЯ',
            'path_private':'SOURCE_PRIVATE/КАТЯ'},
        "рома":{
            'name_tbl':'roma',
            'path':'SOURCE/РОМА',
            'path_private':'SOURCE_PRIVATE/РОМА'}
        }
    bot:object

def fillSettings():
    admins_id = read2list("admins.txt")
#    print('админы ')
#    print(admins_id)
    for id in admins_id:
        if not int(id) in Settings.admin_id:
            Settings.admin_id.append(int(id))
    Settings.users = read_users()
    Settings.send_media = read_send_media()
    Settings.token = read_token()

fillSettings()

#print(Settings.users)

Settings.bot = Bot(Settings.token)

