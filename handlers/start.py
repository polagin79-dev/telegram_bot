from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from datetime import datetime

from keyboards.for_start import get_start_kb
from keyboards.for_users import get_users_kb
from handlers.stats_registration import Registration
from tools.save import save_start
from settings import Settings
from tools.safe_message import message_answer_safe


router = Router()
    

@router.message(Command("start"))  
async def cmd_start(message: Message, state: FSMContext):
    dt_obj =datetime.now()
    dt_string = dt_obj.strftime("%d-%m-%Y (%H:%M:%S)")
    save_start(str(message.from_user.id)+" "+message.from_user.full_name+" "+dt_string)
    if not str(message.from_user.id) in Settings.users.keys():
        msg = await message_answer_safe(
            message,
            f"Привет, {html.bold(html.quote(message.from_user.full_name))}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_start_kb()
            )
    else:
        fio = Settings.users[str(message.from_user.id)]['fio']
        msg = await message_answer_safe(
            message,
            f"Привет, {html.bold(html.quote(fio))}\n",
            parse_mode=ParseMode.HTML,
            reply_markup=get_users_kb()
            )
    await state.clear()
    await state.update_data(message_id=msg.message_id)

@router.message(F.text.lower() == "вернуться")  
async def cmd_reg(message: Message, state: FSMContext):
    await message.delete()
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
    await state.update_data(message_id=msg.message_id)

#@router.message(Command("start_2"))  
#async def cmd_start(message: Message, command: CommandObject, bot: Bot):
#    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
#    bot = await bot.get_chat_member(message.chat.id, bot.id)
#    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or bot.status != ChatMemberStatus.ADMINISTRATOR:
#        await message.answer(
#        "Вы Администратор!"
#        )
#    else:
#        await message.answer(
#        "Вы не Администратор!"
#        )
