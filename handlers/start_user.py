from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
import copy

import glob
import random

from keyboards.for_users import get_users_kb, get_users2_kb
from handlers.stats_user import UserState
from settings import Settings#, bot
from tools.safe_message import message_answer_safe, bot_send_photo_safe, bot_send_video_safe
from mydb.db_work import RandomPicture, RandomVideo, SetIdPict, SetIdVideo, RemoveIdPicture, RemoveIdVideo, ReduceImage
from mailing.video import get_random_video
from tools.save import save_message_media, save_error

router = Router()

def prepare_photo(path_media, user_id:int):
    #print('prepare_photo: start')
    result = copy.deepcopy(path_media)
    if user_id == 5:#Для Максима фото поменьше if user_id == 5221532379:#Для Максима фото поменьше
        #print('prepare_photo: уменьшаем для Максима')
        path = ReduceImage(path_media[2], 150, 150)
        result = ["NON", path_media[1], path]
    return result

async def send_photo(path_media, user_id:int, name_btn:str, text = None, reply_markup=None):
    #print('send_photo: start')
    #print('send_photo: path_media=', path_media)
    path_media2 = prepare_photo(path_media, user_id)
    #print('send_photo: path_media2=', path_media2)
    if path_media2[0] == "NON":
        path_media2[2] = ReduceImage(path_media2[2], 1000, 1000)        
        file = FSInputFile(path_media2[2])
    else:
        file = path_media2[0]
    #print('send_photo: file=', file)
    for i in range(1, 3):#2 попытки отправить один файл
        #print('send_photo: bot_send_photo_safe start')
        caption = ''
        if text == None:
            caption=name_btn
        else:
            caption=text
        result = await bot_send_photo_safe(Settings.bot, user_id, file, caption2=caption, reply_markup2 = reply_markup)
        #print('send_photo: result[1]=', result[1])
        #print('send_rnd_photo: bot_send_photo_safe result=', result)
        if result[1] == 0:
            save_message_media(user_id, path_media[3], result[0].message_id)
            if path_media[0] == "NON":
                SetIdPict(result[0].photo[-1].file_id, path_media[1], name_btn)
                path_media[0] = result[0].photo[-1].file_id
            break
        elif result[1] == 2:
            RemoveIdPicture(path_media[1], name_btn)
            file = path_media2[2]
        else:
            break
    return [path_media, result[1]]    
            
async def send_rnd_photo(name_btn:str, user_id:int):
    #print('send_rnd_photo: start')
    result = None
    for rnd_i in range(1, 11):#10 попыток отправить разные файлы
        user_name = Settings.users[str(user_id)]['name_btn']
        path_media = RandomPicture(name_btn, user_name)
        if path_media != None:            
            result = await send_photo(path_media, user_id, name_btn)
            if result[1] == 0:
                break                
                
    if path_media == None:
        return [False, 0]
    if result[1] != 0:
        return [False, 1]
    return [True, 0]

@router.message(UserState.select_media, F.text.lower() == "фото")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    #print('кнопка фото: start')
    if not str(message.from_user.id) in Settings.users.keys():
        return
    user_data = await state.get_data()
    name_btn = user_data['name_btn']
    #await message_answer_safe(
    #    message,
    #    "Ждите..."
    #    )
    result = await send_rnd_photo(name_btn, message.from_user.id)
    if not result[0]:
        if result[1] == 0:
            await message_answer_safe(
                message,
                "Нет данных для отправки"
                )
        else:
            await message_answer_safe(
                message,
                "Неудалось отправить фото"
                )

def prepare_video(path_media, user_id:int):
    #print('prepare_video: start')
    result = copy.deepcopy(path_media)
    return result

async def send_video(path_media, user_id:int, name_btn:str, text = None, reply_markup=None, number=1):
    #print('send_video: start')
    #print('send_video: path_media=', path_media)
    path_media2 = prepare_video(path_media, user_id)
    #print('send_video: path_media2=', path_media2)
    if path_media2[0] == "NON":
        #path_media2[2] = ReduceImage(path_media2[2], 750, 750)        
        file = FSInputFile(path_media2[2])
    else:
        file = path_media2[0]
    #print('send_photo: file=', file)
    for i in range(1, 3):#2 попытки отправить один файл
        #print('send_video: bot_send_video_safe start')
        caption = ''
        if text == None:
            caption=name_btn
        else:
            caption=text
        #print('send_video: user_id=', user_id)
        result = await bot_send_video_safe(Settings.bot, user_id, file, caption2=caption, reply_markup2 = reply_markup)
        #print('send_video: result[1]=', result[1])
        #print('send_rnd_photo: bot_send_photo_safe result=', result)
        if result[1] == 0:
            save_message_media(user_id, path_media2[3], result[0].message_id)
            if path_media[0] == "NON":
                SetIdVideo(result[0].video.file_id, path_media[1], name_btn, number)
                path_media[0] = result[0].video.file_id
            if path_media[4] != None:
                await send_video(path_media[4], user_id, name_btn, text, reply_markup, number + 1)
            break
        elif result[1] == 2:
            RemoveIdVideo(path_media[1], name_btn)
            file = path_media2[2]
        else:
            break
    return [path_media, result[1]]

async def send_rnd_video(name_btn:str, user_id:int):
    #print('send_rnd_video: start')
    result = None
    for rnd_i in range(1, 6):#5 попыток отправить разные файлы
        path_media = await get_random_video(name_btn, user_id)
        #print('send_rnd_video: rnd_i=', rnd_i, ' path_media=', path_media) 
        if path_media != None and path_media != 'above the limit':            
            result = await send_video(path_media, user_id, name_btn)
            if result[1] == 0:
                #while path_media[4] != None:
                #    await send_video(path_media, user_id, name_btn)
                break
        elif path_media != 'above the limit':
            break

    #print('send_rnd_video: path_media=', path_media)         
    if path_media == None:
        return [False, 0]
    elif path_media == 'above the limit':
        return [False, 2]
    if result[1] != 0:
        return [False, 1]
    return [True, 0]

@router.message(UserState.select_media, F.text.lower() == "видео")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    await message_answer_safe(
        message,
        "Извините загрузка видео пока не работает!"
        )
    return 
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    #print('кнопка видео: start')
    if not str(message.from_user.id) in Settings.users.keys():
        return
    user_data = await state.get_data()
    name_btn = user_data['name_btn']
    await message_answer_safe(
        message,
        "Ждите..."
        )
    result = await send_rnd_video(name_btn, message.from_user.id)
    if not result[0]:
        if result[1] == 0:
            await message_answer_safe(
                message,
                "Нет данных для отправки"
                )
        elif result[1] == 2:
            await message_answer_safe(
                message,
                "Вы уже заказали видео."
                )
        else:
            await message_answer_safe(
                message,
                "Неудалось отправить видео"
                )

@router.message(UserState.select_media, F.text.lower() == "вернуться")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    if not str(message.from_user.id) in Settings.users.keys():
        return
    fio = Settings.users[str(message.from_user.id)]['fio']
    msg = await message_answer_safe(
        message,
        f"{html.bold(html.quote(fio))}\nвыбери нужный раздел\n",
        parse_mode=ParseMode.HTML,
        reply_markup=get_users_kb()
        )
    # очищаем пользователю состояние 
    await state.clear()
    #await state.update_data(message_id=msg.message_id)

@router.message(F.text == "Максим")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    if not str(message.from_user.id) in Settings.users.keys():
        return
    await state.update_data(name_btn=message.text.lower())
    msg = await message_answer_safe(
        message,
        "Выберите фото или видео\nВидео придётся ждать",
        reply_markup=get_users2_kb())
    # Устанавливаем пользователю состояние "ввод select_media"
    await state.set_state(UserState.select_media)
    #await state.update_data(message_id=msg.message_id)

@router.message(F.text == "случайное фото")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    if not str(message.from_user.id) in Settings.users.keys():
        return
    await state.update_data(name_btn=message.text.lower())
    msg = await message_answer_safe(
        message,
        "Выберите фото или видео\nВидео придётся ждать",
        reply_markup=get_users2_kb())
    # Устанавливаем пользователю состояние "ввод select_media"
    await state.set_state(UserState.select_media)
    #await state.update_data(message_id=msg.message_id)

@router.message(F.text == "Катя")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    if not str(message.from_user.id) in Settings.users.keys():
        return
    await state.update_data(name_btn=message.text.lower())
    msg = await message_answer_safe(
        message,
        "Выберите фото или видео\nВидео придётся ждать",
        reply_markup=get_users2_kb())
    # Устанавливаем пользователю состояние "ввод select_media"
    await state.set_state(UserState.select_media)
    #await state.update_data(message_id=msg.message_id)

@router.message(F.text == "Рома")  
async def cmd_reg(message: Message, bot: Bot, state: FSMContext):
    await message.delete()
    #user_data = await state.get_data()
    #if 'message_id' in user_data:
    #    message_id = user_data['message_id']
    #    await bot.delete_message(message.from_user.id, message_id)
    if not str(message.from_user.id) in Settings.users.keys():
        return
    await state.update_data(name_btn=message.text.lower())
    msg = await message_answer_safe(
        message,
        "Выберите фото или видео\nВидео придётся ждать",
        reply_markup=get_users2_kb())
    # Устанавливаем пользователю состояние "ввод select_media"
    await state.set_state(UserState.select_media)
    #await state.update_data(message_id=msg.message_id)


