import asyncio
from aiogram import Bot
from aiogram.types import FSInputFile#, URLInputFile, BufferedInputFile

import os
from datetime import datetime

from tools.safe_message import bot_send_photo_safe, bot_send_video_safe
from tools.save import save_message_media
from settings import Settings
from admins.control_panel import notification_error_admin
from mydb.db_work import SetIdPict, SetIdVideo

from handlers import start_user
from keyboards.for_users import get_users_kb, get_users2_kb

async def send_video(
    bot,
    id_user,
    image_from_pc,
    text
    ):
    result = await bot_send_video_safe(
        bot,
        id_user,
        image_from_pc,
        caption2=text)
    #print('send_video : result=', result)
    return result

@notification_error_admin
async def work_media(send_file, text):
    #print('work_media: start')
    for id_user in Settings.users:
        await start_user.send_photo(send_file, id_user, text, reply_markup = get_users_kb())

@notification_error_admin
async def work_video(send_file, text):
    #print('work_media: start')
    for id_user in Settings.users:
        await start_user.send_video(send_file, id_user, text, text = 'случайное видео', reply_markup = get_users_kb())

def check_send_photo():
    h_now = datetime.now().time().hour
    res = False
    res = res or ((h_now>=7)and(h_now<9))
    res = res or ((h_now>=12)and(h_now<14))
    res = res or ((h_now>=18)and(h_now<20))
    return res 

async def mailing_photo(bot: Bot, func_get_file, text):
    #print('mailing_photo: start')
    await asyncio.sleep(7)
    while(True):        
        if check_send_photo():
            random_file=func_get_file()        
            if random_file != None:
                result = await work_media(random_file, text)
        await asyncio.sleep(4200)

def check_send_video():
    h_now = datetime.now().time().hour
    res = False
    res = res or ((h_now>=9)and(h_now<10))
    res = res or ((h_now>=13)and(h_now<14))
    res = res or ((h_now>=18)and(h_now<19))
    return res

async def mailing_video(bot: Bot, func_get_file, text):
    #print('mailing_video: start')
    await asyncio.sleep(7)
    while(True):        
        if check_send_video():
            random_file=await func_get_file()        
            if random_file != None:
                result = await work_video(random_file, text)
        await asyncio.sleep(4200)

async def mailing_video2(bot: Bot, func_get_file, func_get_file_prepare, text):
    #while(True):
        send_file=await work_video(bot, func_get_file, func_get_file_prepare, send_video, text)
        #print('сжали')
        if send_file != None:
            await work_media(bot, send_file, send_video, text)
        await asyncio.sleep(15)

