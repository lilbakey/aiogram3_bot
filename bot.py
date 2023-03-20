import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config_data.config import Config, load_config
from keyboards.set_menu import main_menu_commands
from handlers.user_handlers import user_router
from handlers.admin_handlers import admin_router
from handlers.other_handlers import other_router
from models.data_base import async_db_session

# Инициализируем логгер
logger: logging = logging.getLogger(__name__)


# Функция для инициализации БД
async def init_db():
    await async_db_session.init()
    await async_db_session.create_all()


# Функция для включения роутеров
def includes_all_routers(dp: Dispatcher) -> None:
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(other_router)



# Функция конфигурирования и запуска бота
async def main() -> None:
    # Конфигурируем логгирование
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о запуске бота
    logging.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config('.env')

    # Создаем объекты бота и диспетчера
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())

    # Запускаем БД
    await init_db()

    await main_menu_commands(bot)

    # Регистрируем все хэндлеры
    includes_all_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        # Запускаем функция main
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Выводим в консоль сообщение об ошибке
        logger.error('Bot stopped!')
