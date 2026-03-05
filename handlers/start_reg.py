from aiogram import Router, F
#from aiogram.filters import Command
from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram import html
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.for_reg import get_reg_kb, get_reg2_kb
from keyboards.for_users import get_users_kb
from handlers.stats_registration import RegistrationNew
from tools.save import save
from admins.control_panel import add_new_user, send_admins
from settings import Settings
from tools.safe_message import bot_message_safe, message_answer_safe


router = Router()

text_reg_id = "Регистрация\n\nВведите id нового пользователя"

@router.message(Command("reg"))  
async def cmd_reg(message: Message, state: FSMContext, bot: Bot):
    if  await is_admin(message, bot) or message.from_user.id in Settings.admin_id:
        await message_answer_safe(message, text_reg_id, reply_markup=get_reg_kb())
        # Устанавливаем пользователю состояние "ввод id"
        await state.set_state(RegistrationNew.reg_id)

@router.message(RegistrationNew.reg_id, F.text.lower() == "отменить")  
async def cmd_reg_id_cancel(message: Message, state: FSMContext):
    await message_answer_safe(
        message,
        "Регистрация отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

text_reg_full_name = "Регистрация\n\nВведите full_name нового пользователя"

@router.message(RegistrationNew.reg_id)  
async def cmd_reg_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message_answer_safe(message, "некорректный id\nповторите ввод!")
        return
    await state.update_data(new_id=message.text.lower())
    await message_answer_safe(message, text_reg_full_name, reply_markup=get_reg2_kb())
    # Устанавливаем пользователю состояние "ввод full_name"
    await state.set_state(RegistrationNew.reg_full_name)

@router.message(RegistrationNew.reg_full_name, F.text.lower() == "отменить")  
async def cmd_reg_full_name_cancel(message: Message, state: FSMContext):
    await message_answer_safe(
        message,
        "Регистрация отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

text_reg_fio = "Регистрация\n\nВведите ФИО нового пользователя"

@router.message(RegistrationNew.reg_full_name, F.text.lower() == "пропустить")  
async def cmd_reg_full_name_cancel(message: Message, state: FSMContext):
    await message_answer_safe(message, text_reg_fio, reply_markup=get_reg_kb())
    await state.set_state(RegistrationNew.reg_fio)

def check_full_name(full_name: str)->bool:
    if full_name.isdigit():
        return False
    return True

@router.message(RegistrationNew.reg_full_name)  
async def cmd_full_name(message: Message, state: FSMContext):
    if not check_full_name(message.text):
        await message_answer_safe(message, "некорректный full_name\nповторите ввод!")
        return
    await state.update_data(new_full_name=message.text.lower())
    await message_answer_safe(message, text_reg_fio, reply_markup=get_reg_kb())
    # Устанавливаем пользователю состояние "ввод fio"
    await state.set_state(RegistrationNew.reg_fio)

@router.message(RegistrationNew.reg_fio, F.text.lower() == "отменить")  
async def cmd_reg_full_name_cancel(message: Message, state: FSMContext):
    await message_answer_safe(
        message,
        "Регистрация отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

def check_fio(fio: str)->bool:
    if fio.isdigit():
        return False
    fio_spisok = fio.split(' ')
    if len(fio_spisok)<2:
        return False
    for part in fio_spisok:
        if len(part)<2:
            return False
    return True

async def reg_ok(message, bot: Bot, new_id, new_full_name, new_fio):
    text_user = "вы успешно зарегистрированы"
    await bot_message_safe(bot, new_id, text_user, reply_markup=get_users_kb())
    #await bot.send_message(int(new_id), text_user, reply_markup=get_users_kb())
    text_admin = "пользователь\nid:" + str(new_id)+'\nfull_name:'+\
           new_full_name+'\nФИО:'+new_fio+'\n'+\
           "зарегистрирован"
    await send_admins(bot, text_admin)

async def reg_busy(message, bot: Bot, new_id, new_full_name, new_fio):
    text_user = "ошибка при регистрации\nобратитесь к администратору"
    await bot_message_safe(bot, new_id, text_user)
    #await bot.send_message(int(new_id), text_user)
    text_admin = "пользователь\nid:" + str(new_id)+'\nfull_name:'+\
           new_full_name+'\nФИО:'+new_fio+'\n'+\
           "уже зарегистрирован"
    await send_admins(bot, text_admin)


@router.message(RegistrationNew.reg_fio)  
async def cmd_full_name(message: Message, state: FSMContext, bot: Bot):
    if not check_fio(message.text):
        await message_answer_safe(message, "некорректные ФИО\nповторите ввод!")
        return
    user_data = await state.get_data()
    res = add_new_user(user_data['new_id'], user_data['new_full_name'],message.text.lower())
    if res == "OK":
        await reg_ok(message, bot, user_data['new_id'], user_data['new_full_name'], message.text.lower())
    if res == "BUSY":
        await reg_busy(message, bot, user_data['new_id'], user_data['new_full_name'], message.text.lower())
    # Устанавливаем пользователю состояние "ввод fio"
    await state.clear()

