from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from lexicon.lexicon import LEXICON

other_router: Router = Router()


@other_router.message(Command(commands='admin'))
async def process_not_admin(message: Message) -> None:
    await message.answer(text=LEXICON['not_admin'])

@other_router.message()
async def process_other_answers(message: Message) -> None:
    await message.answer(LEXICON['other_answer'])
