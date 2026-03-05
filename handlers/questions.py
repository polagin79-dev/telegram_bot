from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()  

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "регистрация")
async def answer_no(message: Message):
    await message.answer(
        "ждите одобрения заявки",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "покинуть бота")
async def answer_no(message: Message):
    await message.answer(
        "Удачи!",
        reply_markup=ReplyKeyboardRemove()
    )
