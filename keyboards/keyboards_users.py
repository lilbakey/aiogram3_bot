from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


def get_start_kb() -> ReplyKeyboardMarkup:
    kb: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text=LEXICON['catalog']))
    kb.row(KeyboardButton(text=LEXICON['profile']), KeyboardButton(text=LEXICON['basket']))
    kb.row(KeyboardButton(text=LEXICON['replenish_balance']), KeyboardButton(text=LEXICON['FAQ_button']))
    return kb.as_markup(resize_keyboard=True)


def create_catalog_kb(categories: list) -> InlineKeyboardMarkup:

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(text=cat, callback_data=f'cat: {cat}')

    builder.adjust(2)


    return builder.as_markup()


def create_product_kb(*buttons: str) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=LEXICON['add_to_basket'],
                                     callback_data='add_to_basket_button'))


    for button in buttons:
        if button in LEXICON:
            builder.button(text=LEXICON[button], callback_data=button)
        else:
            builder.button(text=button, callback_data=button)

    builder.row(InlineKeyboardButton(text=LEXICON['back'],
                                     callback_data='back_button'))

    builder.adjust(1, 3, 1)

    return builder.as_markup()


def back_to_catalog() -> InlineKeyboardMarkup:

    back_button: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['back'],
                                                             callback_data='back_button')

    back_kb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])

    return back_kb

def get_basket_kb() -> InlineKeyboardMarkup:

    pay_button: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['pay'],
                                                            callback_data='pay_button')
    edit_button: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['edit_basket'],
                                                             callback_data='edit_button')
    back: InlineKeyboardButton = InlineKeyboardButton(text=LEXICON['back'],
                                                      callback_data='back_button')

    basket_kb: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[pay_button], [edit_button], [back]])

    return basket_kb

def create_edit_basket_kb(products: list) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for num, item in enumerate(sorted(products, key=lambda x: x[1]), 1):
        builder.row(InlineKeyboardButton(
            text=f'❌ {num} - {item[0]}',
            callback_data=f'del: {item[1]}'
        ))

    builder.row(InlineKeyboardButton(text=LEXICON['back'],
                                     callback_data='back_to_basket'))

    return builder.as_markup()


def get_accept_payment_kb() -> ReplyKeyboardMarkup:
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=LEXICON['yes']), KeyboardButton(text=LEXICON['no']))

    return builder.as_markup(resize_keyboard=True)