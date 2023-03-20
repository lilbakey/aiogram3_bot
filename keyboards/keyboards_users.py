from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


def get_start_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text=LEXICON['catalog_button']))
    kb.row(KeyboardButton(text=LEXICON['profile']), KeyboardButton(text=LEXICON['basket_button']))
    return kb.as_markup(resize_keyboard=True)


def get_catalog_kb() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
