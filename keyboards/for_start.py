from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="регистрация")
    kb.button(text="покинуть бота")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_reg_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="зарегистр-ть")
    kb.button(text="отклонить")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
