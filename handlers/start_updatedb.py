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
from keyboards.for_users import get_users_kb

from mydb import db_work 

router = Router()

@router.message(Command("updatedb"))  
async def cmd_list_users(message: Message, bot: Bot):
    if await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        db_work.flag_updatedb = True
        await message_answer_safe(message, "обновление базы запланировано", reply_markup=get_users_kb())
   
