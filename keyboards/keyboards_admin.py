from aiogram.types import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardRemove)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


def get_admin_kb() -> ReplyKeyboardMarkup:

    product_settings: KeyboardButton = KeyboardButton(text=LEXICON['product_settings'])

    statistics: KeyboardButton = KeyboardButton(text=LEXICON['statistics'])

    general_settings: KeyboardButton = KeyboardButton(text=LEXICON['general_settings'])

    main_menu_button: KeyboardButton = KeyboardButton(text=LEXICON['back_to_main_menu_button'])

    admin_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[product_settings], [statistics], [general_settings],
                                                                  [main_menu_button]],
                                                        resize_keyboard=True,
                                                        input_field_placeholder=LEXICON['admin_menu_placeholder'])

    return admin_kb


def get_general_settings() -> ReplyKeyboardMarkup:

    help: KeyboardButton = KeyboardButton(text=LEXICON['edit_help'])

    faq: KeyboardButton = KeyboardButton(text=LEXICON['edit_faq'])

    back: KeyboardButton = KeyboardButton(text=LEXICON['back_to_admin_menu_button'])

    gen_set_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[help], [faq], [back]],
                                                          resize_keyboard=True)
    return gen_set_kb




def get_product_settings_kb() -> ReplyKeyboardMarkup:

    download_catalog_photo: KeyboardButton = KeyboardButton(text=LEXICON['download_catalog_photo'])

    download_button: KeyboardButton = KeyboardButton(text=LEXICON['download_product'])

    delete_button: KeyboardButton = KeyboardButton(text=LEXICON['delete_product'])

    category_download_button: KeyboardButton = KeyboardButton(text=LEXICON['download_category'])

    category_delete_button: KeyboardButton = KeyboardButton(text=LEXICON['delete_category'])

    admin_menu_button: KeyboardButton = KeyboardButton(text=LEXICON['back_to_admin_menu_button'])

    settings: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[[category_download_button, category_delete_button], [download_catalog_photo],
                  [download_button, delete_button], [admin_menu_button]],
        resize_keyboard=True,
        input_field_placeholder=LEXICON['admin_menu_placeholder'])

    return settings


def cancel_fsm_kb() -> ReplyKeyboardMarkup:
    cancel_button: KeyboardButton = KeyboardButton(text=LEXICON['cancel_fsm_button'])

    cancel_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[[cancel_button]],
                                                         resize_keyboard=True)

    return cancel_kb


def remove_kb() -> ReplyKeyboardRemove:
    kb: ReplyKeyboardRemove = ReplyKeyboardRemove()

    return kb


def create_categories_kb(categories: list) -> InlineKeyboardMarkup:

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(text=cat, callback_data=f'cat: {cat}')

    builder.adjust(2)

    return builder.as_markup()


def delete_categories_kb(categories: list) -> InlineKeyboardMarkup:

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(text=f'❌ {cat}', callback_data=f'cat: {cat}')

    builder.adjust(2)

    return builder.as_markup()


def delete_product_kb(*buttons: str) -> InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=LEXICON['delete_product_2'],
                                     callback_data='delete_product_button'))

    for button in buttons:
        if button in LEXICON:
            builder.button(text=LEXICON[button], callback_data=button)
        else:
            builder.button(text=button, callback_data=button)

    builder.row(InlineKeyboardButton(text=LEXICON['back'],
                                     callback_data='back_button'))

    builder.adjust(1, 3, 1)

    return builder.as_markup()


def create_catalog_kb(categories: list) -> InlineKeyboardMarkup:

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    for cat in categories:
        builder.button(text=cat, callback_data=f'cat: {cat}')

    builder.adjust(2)


    return builder.as_markup()
