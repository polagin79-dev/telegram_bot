from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command#, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
#from aiogram.enums.chat_member_status import ChatMemberStatus
#from aiogram import html
#from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
#from aiogram.fsm.state import StatesGroup, State

from keyboards.for_send_all import get_send_all_kb
from keyboards.for_users import get_users_kb
#from handlers.stats_registration import RegistrationNew
#from tools.save import save
from settings import Settings
from handlers.stats_send_all import SendAll
from admins.control_panel import send_message_all, is_admin
from tools.safe_message import message_answer_safe


router = Router()

text_send_all = 'Введите текст сообщения для отправки всем пользователям'

@router.message(Command("send_all"))  
async def cmd_admin(message: Message, bot: Bot, state: FSMContext):
    if await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        await message_answer_safe(message, text_send_all, reply_markup=get_send_all_kb())
        # Устанавливаем пользователю состояние "ввод id"
        await state.set_state(SendAll.input_send)


@router.message(SendAll.input_send, F.text.lower() == "отменить")  
async def cmd_admin(message: Message, bot: Bot, state: FSMContext):
    await message_answer_safe(message, "отмена отправки", reply_markup=get_users_kb())
    # Устанавливаем пользователю состояние "ввод id"
    await state.clear()


@router.message(SendAll.input_send)  
async def cmd_admin(message: Message, bot: Bot, state: FSMContext):    
    #await message.answer("users_start.txt", reply_markup=ReplyKeyboardRemove())
    r = get_users_kb()
    await send_message_all(bot, message.text, reply_markup2=get_users_kb())
    # Устанавливаем пользователю состояние "ввод id"
    await state.clear()
