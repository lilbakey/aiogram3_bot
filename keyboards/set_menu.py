from aiogram import Bot
from aiogram.types import BotCommand

async def main_menu_commands(bot: Bot) -> None:

    main_menu_commands = [
        BotCommand(command='/start',
                   description='Запуск'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/admin',
                   description='Меню администратора')
    ]

    await bot.set_my_commands(main_menu_commands)