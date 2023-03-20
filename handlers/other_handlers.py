from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from lexicon.lexicon import LEXICON

other_router: Router = Router()


# Хендлер срабатывающий при нажатии на кнопку администратора
# людьми не являющимися администраторами
@other_router.message(Command(commands='admin'))
async def process_not_admin(message: Message) -> None:
    await message.answer(text=LEXICON['not_admin'])


# Хендлер срабатывающий на неизвестные боту команды
@other_router.message()
async def process_other_answers(message: Message) -> None:
    await message.answer(LEXICON['other_answer'])
