from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_users_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Максим")
    kb.button(text="Катя")
    kb.button(text="Рома")
    kb.button(text="случайное фото")
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True)


def get_users2_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="фото")
    kb.button(text="видео")
    kb.button(text="вернуться")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
