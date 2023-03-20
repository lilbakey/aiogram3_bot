from dataclasses import dataclass
from environs import Env


@dataclass
class DataBaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных
    db_port: int # Порт к базе данных


@dataclass
class TgBot:
    token: str  # Токен вашего телеграм бота
    admins_id: list[int]  # ID администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DataBaseConfig

def load_config(path: str | None) -> Config:
    # Создаем экземпляр класса Env
    env: Env = Env()

    # Добавляем в переменную данные прочитанные из виртуального окружения
    env.read_env(path)

    # Возвращаем класс Config и наполняем его данными из переменных окружения
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admins_id=list(map(int, env.list('ADMINS_ID')))),
                  db=DataBaseConfig(database=env('DATABASE'),
                                    db_host=env('DB_HOST'),
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD'),
                                    db_port=env('DB_PORT')))
