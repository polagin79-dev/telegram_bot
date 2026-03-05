from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove


class Registration(StatesGroup):
    registration = State()

class RegistrationNew(StatesGroup):
    reg_id = State()
    reg_full_name = State()
    reg_fio = State()

