from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command#, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums.chat_member_status import ChatMemberStatus
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

def make_list_users()->str:
    spisok = ""
    for (user_id, user_info) in Settings.users.items():
        spisok = spisok+str(user_id)+'/'+user_info['full_name']+\
                 '/'+user_info['fio']+'\n'
    if len(spisok.strip())==0:
        return "список пуст"
    spisok = "user_id/full_name/ФИО\n"+spisok
    return spisok

@router.message(Command("list_users"))  
async def cmd_list_users(message: Message, bot: Bot):
    if await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        spisok = make_list_users()
        await message_answer_safe(message, spisok)
   
