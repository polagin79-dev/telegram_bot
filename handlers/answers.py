from aiogram import Router, F
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from handlers.stats_registration import Registration
from admins.control_panel import send_admins
from tools.safe_message import message_answer_safe


router = Router()  


@router.message(F.text.lower() == "регистрация")
async def answer_fio(message: Message, state: FSMContext):
    await message_answer_safe(
        message,
        "Введите Фамилию Имя и Отчество",
        reply_markup=ReplyKeyboardRemove()
    )
    # Устанавливаем пользователю состояние "регистрация"
    await state.set_state(Registration.registration)


@router.message(Registration.registration)
async def registration(message: Message, state: FSMContext, bot: Bot):
    text: str = "запрос регистрации\n"+"\nid:"+str(message.from_user.id)+\
                "\nfull_name:"+str(message.from_user.full_name)+\
                "\nфио:"+str(message.text)    
    await message_answer_safe(
        message,
        "ждите одобрения заявки",
        reply_markup=ReplyKeyboardRemove()
    )
    await send_admins(bot, text)
    await state.clear()
    

@router.message(F.text.lower() == "покинуть бота")
async def answer_no(message: Message, state: FSMContext):
    await message_answer_safe(
        message,
        "Удачи!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
