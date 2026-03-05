from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
#from aiogram.enums.chat_member_status import ChatMemberStatus
#from aiogram import html
#from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
#from aiogram.fsm.context import FSMContext
#from aiogram.fsm.state import StatesGroup, State

#from keyboards.for_reg import get_reg_kb, get_reg2_kb
#from handlers.stats_registration import RegistrationNew
#from tools.save import save
from settings import Settings
from admins.control_panel import is_admin
from tools.safe_message import message_answer_safe


router = Router()

text_admin = "/reg - регистрация нового пользователя\n"+\
             "/list_users - список зарегистрированных пользователей\n"+\
             "/send_all - отправить сообщение всем пользователям\n"+\
             "/last_media - последнее отправленное фото/видео, можно передать параметр(число фото)\n"+\
             "/delete_msg - удалить отправленное. Передаётся два числа: id user и id сообщения\n"+\
             "/updatedb - обновить базу"

@router.message(Command("admin"))  
async def cmd_admin(message: Message, bot: Bot):
    if await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        await message_answer_safe(message, text_admin)
   

@router.message(Command("last_media"))  
async def cmd_admin(message: Message, bot: Bot, command: CommandObject):
    if await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        count=1
        if not command.args is None:
            if not command.args.isdigit():
                await message_answer_safe(message, "некорректный id\nповторите ввод!")
                return 
            count=int(command.args)
        l=len(Settings.send_media)
        if count<1:
            count=1
        count=min(100, count)
        #if count>100:
        #    count=100
        count=min(l, count)
        #if count > len(Settings.send_media):
        #    count=len(Settings.send_media)
        if not Settings.send_media:
                await message_answer_safe(message, "нет данных")
                return
        for i in range(count, 0, -1):#обратная последовательность чисел
            data = Settings.send_media[l-i]
            text='фио:'+data['fio']+'\nid_message:'+str(data['id_msg'])+'\nid_user: '+str(data['id_user'])+'\nвремя: '+str(data['time'])+\
                  '\nфайл: '+str(data['path'])
            await message_answer_safe(message, text)

@router.message(Command("delete_msg"))  
async def cmd_admin(message: Message, bot: Bot, command: CommandObject):
    if not (await is_admin(message, bot) or message.from_user.id in Settings.admin_id):
        return
    if command.args is None:
        return
    msg=command.args.split(' ')
    if not msg[0].isdigit():
            await message_answer_safe(message, "некорректный id")
            return
    if not str(msg[0]) in Settings.users.keys():
        return
    first = msg[1].split('-')
    if len(first) > 1:
        if not first[1].isdigit():
            await message_answer_safe(message, "некорректный id")
            return
    if not first[0].isdigit():
            await message_answer_safe(message, "некорректный id")
            return

    if len(first) >1:
        for el in range(int(first[0]), int(first[1])+1):
            try:
                await bot.delete_message(msg[0], el)
            except Exception:
                pass
    else:
        await bot.delete_message(msg[0], first[0])
    
