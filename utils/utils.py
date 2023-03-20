from typing import Union

from aiogram.types import InputMediaPhoto


def get_input_media(content: dict[str, Union[str, int]]) -> InputMediaPhoto:
    return InputMediaPhoto(type='photo',
                           media=content['photo'],
                           caption=f'<b> {content["name"]} </b>\n'
                                   f'{content["descr"]}\n'
                                   f'<b>{content["price"]} ₽</b>')

