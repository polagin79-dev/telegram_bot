from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_reg_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="отменить")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_reg2_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="отменить")
    kb.button(text="пропустить")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

