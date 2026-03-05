import asyncio
from aiogram import Bot, Dispatcher
import os

from glob import glob

import random

from handlers import answers, different_types, start, start_reg, list_users, admin, start_user, start_send_all, start_updatedb
from settings import Settings
from mailing.photo import mailing_photo, mailing_video
from mailing.video import delete_video_all, get_random_video
from mydb.db_work import workDB, RandomPicture, RandomVideo, delete_picture_all

def get_random_file_path(source: str,name_file, ext: str):
    name=glob(source+'/**/'+name_file+'.'+ext, recursive=True)
    if len(name)==0:
        return None
    random_file=random.choice(name)
    return random_file     

# Запуск бота
async def main():

    delete_video_all()

    delete_picture_all()
    
    dp = Dispatcher()

    dp.include_routers(start_reg.router, answers.router, list_users.router, admin.router,\
                       start_user.router, start_send_all.router,\
                       start_updatedb.router, start.router)

    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await Settings.bot.delete_webhook(drop_pending_updates=True)
    try:
        f=lambda : RandomPicture('случайное фото')
        f2=lambda : get_random_video('случайное фото')
        task1=dp.start_polling(Settings.bot)
        task2 = workDB(Settings.db_path, Settings.sources)
        task3=mailing_photo(Settings.bot, f, 'случайное фото')
        #Отправка видео пока не работает так как загрузку тормозит роскомнадзор
        #task4=mailing_video(Settings.bot, f2, 'случайное фото')        
        await asyncio.gather(task1, task2, task3)#, task4)
        #await dp.start_polling(bot)
    finally:
        await Settings.bot.session.close()
    #await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
