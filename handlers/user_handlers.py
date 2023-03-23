from typing import Union

from aiogram import (Router, Bot)
from aiogram.filters import (Text, Command, CommandStart)
from aiogram.types import (Message, CallbackQuery)
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from filters.is_basket_exist import IsBasketExist
from filters.is_faq_content import IsFAQContent
from filters.is_products_exists import IsProductsExists
from filters.own_ref_link import OwnRefLink
from filters.new_ref_user import NewRefUser
from filters.repeted_ref_link import RepeatedRefLink
from filters.user_in_base import UserInBase
from filters.is_catalog_photo import IsCatalogPhoto
from filters.is_help_content import IsHelpContent
from keyboards.keyboards_users import (get_start_kb, create_catalog_kb, create_product_kb, back_to_catalog,
                                       get_basket_kb, create_edit_basket_kb, get_accept_payment_kb)
from lexicon.lexicon import LEXICON
from models import (Basket, BasketProduct, CatalogPhoto, Category, FAQ, Help, Product, User)
from services.services import (format_order, update_storage)
from states.FSMMenu import FSMMenu
from states.FSMPayment import FSMPayment
from states.FSMBalance import FSMBalance
from middlewares.throttling import AntiFloodMiddleware
from utils.utils import get_input_media

user_router: Router = Router()
user_router.message.middleware(AntiFloodMiddleware())
user_router.callback_query.middleware(AntiFloodMiddleware())


# Хендлер срабатывающий на команду Старт для новых реферальных пользователей
@user_router.message(CommandStart(), ~UserInBase(), NewRefUser())
async def process_start_command(message: Message, bot: Bot) -> None:
    referrer_id = message.text[7:]
    telegram_id = message.from_user.id
    link: str = await create_start_link(bot=bot, payload=str(telegram_id))

    await User.create(telegram_id=int(telegram_id), username=message.from_user.username, referrer_link=link)
    await Basket.create(users_telegram_id=int(telegram_id))

    try:
        user_whose_link: User = await User.get_user(int(referrer_id))
        await User.update(id=user_whose_link.id, balance=user_whose_link.balance + 10,
                          referrer_counter=user_whose_link.referrer_counter + 1)
        await bot.send_message(chat_id=referrer_id,
                               text=LEXICON['suc_ref_link'])
    except Exception:
        pass

    await message.answer(text=LEXICON['suc_reg_link'])
    await message.answer(text=LEXICON['start'].format(name=message.from_user.first_name),
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на кнопку "Старт",
# если пользователь попытался зарегистрироваться по собственной ссылке
@user_router.message(CommandStart(), UserInBase(), OwnRefLink())
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON['own_ref_link'],
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на кнопку "Старт",
# если пользователь попытался зарегистрироваться
# повторно по реферальной ссылке
@user_router.message(CommandStart(), UserInBase(), RepeatedRefLink())
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON['repeated_ref_link'],
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на команду Старт для не зарегистрированных пользователей
@user_router.message(CommandStart(), ~UserInBase())
async def process_start_command(message: Message, bot: Bot) -> None:
    telegram_id: int = message.from_user.id
    link: str = await create_start_link(bot=bot, payload=str(telegram_id))

    await User.create(telegram_id=int(telegram_id), username=message.from_user.username, referrer_link=link)
    await Basket.create(users_telegram_id=int(telegram_id))

    await message.answer(text=LEXICON['start'].format(name=message.from_user.first_name),
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на команду Старт для зарегистрированных пользователей
@user_router.message(CommandStart(), UserInBase())
async def process_start_command(message: Message) -> None:
    await message.answer(text=LEXICON['start'].format(name=message.from_user.first_name),
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на команду "help" заполненной администратором
@user_router.message(Command(commands='help'), IsHelpContent())
async def process_help_content_command(message: Message) -> None:
    text = await Help.get_help_content()
    await message.answer(text=text,
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на команду "help" не заполненную администратором
@user_router.message(Command(commands='help'))
async def process_help_basic_command(message: Message) -> None:
    await message.answer(text=LEXICON['help_info'],
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на возврат в каталог из пустой категории с фото
@user_router.callback_query(Text(text='back_button'), IsCatalogPhoto())
async def cb_process_catalog_button(callback: CallbackQuery, state: FSMContext) -> None:
    categories: list[str] = [i.name for i in await Category.get_all()]
    photo: str = await CatalogPhoto.get_photo()
    await state.clear()

    await callback.message.delete()
    await callback.message.answer_photo(photo=photo,
                                        caption=LEXICON['catalog'],
                                        reply_markup=create_catalog_kb(categories))
    await callback.answer()


# Хендлер срабатывающий на кнопку каталог с фото
@user_router.message(Text(text=LEXICON['catalog']), IsCatalogPhoto())
async def process_catalog_button(message: Message, state: FSMContext) -> None:
    categories: list[str] = [i.name for i in await Category.get_all()]
    photo: str = await CatalogPhoto.get_photo()
    await state.clear()

    await message.answer_photo(photo=photo,
                               caption=LEXICON['catalog'],
                               reply_markup=create_catalog_kb(categories))


# Хендлер срабатывающий на кнопку каталог без фото
@user_router.message(Text(text=LEXICON['catalog']))
async def process_not_exist_catalog(message: Message) -> None:
    await message.answer(text=LEXICON['catalog_not_exist'])


# Хендлер показывающий меню с товарами
@user_router.callback_query(Text(startswith='cat'), IsProductsExists())
async def show_products(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()

    category_name: str = callback.data.split(': ')[1]
    category_id: str = await Category.get_category_id(category_name)
    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(category_id)

    await state.set_state(FSMMenu.step)

    storage: dict[str, Union[str, int]] = await state.update_data(step=1, category=category_id)
    content: dict[str, Union[str, int]] = list_of_products[storage['step'] - 1]

    await callback.message.answer_photo(photo=content['photo'],
                                        caption=f'<b> {content["name"]} </b>\n\n'
                                                f'{content["descr"]}\n\n'
                                                f'<b>{content["price"]} ₽ </b>',
                                        reply_markup=create_product_kb('backward',
                                                                       f'{storage["step"]} / {len(list_of_products)}',
                                                                       'forward'))
    await state.update_data(product_id=int(content['id']))
    await callback.answer()


# Хендлер говорящий, что в данной категории нет товаров
@user_router.callback_query(Text(startswith='cat'), ~IsProductsExists())
async def show_products(callback: CallbackQuery) -> None:
    await callback.message.delete()

    await callback.message.answer(text=LEXICON['no_products'],
                                  reply_markup=back_to_catalog())
    await callback.answer()


# Хендлер срабатывающий на кнопку "вперед" или "назад"
@user_router.callback_query(FSMMenu.step, Text(text=('forward', 'backward')))
async def process_step_press(callback: CallbackQuery, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()
    if callback.data == 'forward':
        storage: dict[str, Union[str, int]] = await state.update_data(step=storage['step'] + 1)
    else:
        storage: dict[str, Union[str, int]] = await state.update_data(step=storage['step'] - 1)

    list_of_products: list[dict] = await Product.get_products_in_category(storage['category'])
    length = len(list_of_products)

    storage: dict[str, Union[str, int]] = await update_storage(length, storage, state)
    content: dict[str, Union[str, int]] = list_of_products[storage['step'] - 1]

    if length != 1:
        media: InputMediaPhoto = get_input_media(content)
        await callback.message.edit_media(media=media,
                                          reply_markup=create_product_kb('backward',
                                                                         f'{storage["step"]} / {length}',
                                                                         'forward'))
        await state.update_data(product_id=int(content['id']))

    await callback.answer()


# Хендлер срабатывающий на копку добавить в корзину
@user_router.callback_query(Text(text='add_to_basket_button'))
async def pressed_add_button(callback: CallbackQuery, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()
    product: BasketProduct = await Product.get_object(storage['product_id'])
    basket_id: int = await Basket.get_id(telegram_id=int(callback.from_user.id))

    await BasketProduct.create(basket_id=basket_id,
                               product_id=product.id)

    await callback.answer(text=LEXICON['add_button'])


# Хендлер срабатывающий на пустую корзину
@user_router.callback_query(Text(text='back_to_basket'), ~IsBasketExist())
@user_router.message(Text(text=LEXICON['basket']), ~IsBasketExist())
async def empty_basket(message: Message | CallbackQuery) -> None:
    if isinstance(message, Message):
        await message.answer(text=LEXICON['empty_basket'])
    else:
        await message.message.delete()
        await message.message.answer(text=LEXICON['empty_basket'])


# Хендлер срабатывающий на кнопку "назад" после редактирования корзины
@user_router.callback_query(Text(text='back_to_basket'))
async def cb_process_basket(callback: CallbackQuery, state: FSMContext) -> None:
    basket: Basket = await Basket.get_basket(telegram_id=int(callback.from_user.id))
    products: list = [await Product.get_object(i.product_id) for i in basket.products]
    list_of_products: list[tuple[str, str | int]] = [(i.name, i.price) for i in products]

    await state.set_state(FSMPayment.total_amount)
    order: dict[str, Union[str, int]] = format_order(list_of_products)
    await state.update_data(total_amount=order['total_price'])

    await callback.message.delete()
    await callback.message.answer(text=LEXICON['show_basket'].format(products=order['order'],
                                                                     length=f"{'~' * order['length']}",
                                                                     total_price=order['total_price']),
                                  reply_markup=get_basket_kb())
    await callback.answer()


# Хендлер срабытвающий на кнопку "Корзина"
@user_router.message(Text(text=LEXICON['basket']), IsBasketExist())
async def process_basket_button(message: Message | CallbackQuery, state: FSMContext) -> None:
    basket: Basket = await Basket.get_basket(telegram_id=int(message.from_user.id))
    products: list = [await Product.get_object(i.product_id) for i in basket.products]
    list_of_products: list[tuple[str, str | int]] = [(i.name, i.price) for i in products]

    await state.set_state(FSMPayment.total_amount)
    order: dict[str, Union[str, int]] = format_order(list_of_products)
    await state.update_data(total_amount=order['total_price'])

    await message.answer(text=LEXICON['show_basket'].format(products=order['order'],
                                                            length=f"{'~' * order['length']}",
                                                            total_price=order['total_price']),
                         reply_markup=get_basket_kb())


# Хендлер срабатывающий на кнопку редактирования корзины
@user_router.callback_query(Text(text='edit_button'))
async def process_edit_basket(callback: CallbackQuery) -> None:
    basket: Basket = await Basket.get_basket(telegram_id=int(callback.from_user.id))
    products: list = [await Product.get_object(i.product_id) for i in basket.products]

    await callback.message.delete()

    await callback.message.answer(text=LEXICON['msg_for_edit_basket'],
                                  reply_markup=create_edit_basket_kb([(i.name, i.id) for i in products]))

    await callback.answer()


# Хендлер срабатывающий на удаление товара из корзины
@user_router.callback_query(Text(startswith='del: '), IsBasketExist())
async def delete_basket_product(callback: CallbackQuery) -> None:
    product_id: int = int(callback.data.split()[1])
    basket_product_id: int = await BasketProduct.get_id(product_id)

    await BasketProduct.delete(basket_product_id)

    basket: Basket = await Basket.get_basket(telegram_id=int(callback.from_user.id))
    products: list = [await Product.get_object(i.product_id) for i in basket.products]

    await callback.message.edit_reply_markup(reply_markup=create_edit_basket_kb([(i.name, i.id) for i in products]))
    await callback.answer(text=LEXICON['deleted_product_basket'])


# Хендлер срабатывающий на копку "Профиль"
@user_router.message(Text(text=LEXICON['profile']))
async def process_profile_button(message: Message) -> None:
    user: User = await User.get_user(int(message.from_user.id))

    await message.answer(text=LEXICON['user'].format(name=message.from_user.first_name,
                                                     balance=user.balance,
                                                     buy_counter=user.buy_counter,
                                                     ref_counter=user.referrer_counter,
                                                     reg_date=user.reg_date,
                                                     ref_link=user.referrer_link))


# Хендлер срабатывающий на кнопку "FAQ" c текстом от администратора
@user_router.message(Text(text=LEXICON['FAQ_button']), IsFAQContent())
async def process_content_faq_button(message: Message) -> None:
    text: str = await FAQ.get_faq_content()

    await message.answer(text=text)


# Хендлер срабатывающий на кнопку "FAQ"
@user_router.message(Text(text=LEXICON['FAQ_button']), ~IsFAQContent())
async def process_faq_button(message: Message) -> None:
    await message.answer(text=LEXICON['faq_info'])


# Хендлер срабатывающий на кнопку "Оплатить"
@user_router.callback_query(FSMPayment.total_amount, Text(text='pay_button'))
async def process_payment(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(FSMPayment.accept)
    await callback.message.answer(text=LEXICON['accept_payment'],
                                  reply_markup=get_accept_payment_kb())


# Хендлер подтверждающий процесс оплаты
@user_router.message(FSMPayment.accept, Text(text=LEXICON['yes']))
async def process_yes_payment(message: Message, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()
    total_amount: str = storage['total_amount']
    user: User = await User.get_user(int(message.from_user.id))
    basket: BasketProduct = await Basket.get_basket(int(message.from_user.id))

    if int(total_amount) <= int(user.balance):
        new_balance: int = int(user.balance) - int(total_amount)
        await User.update(id=user.id,
                          balance=new_balance,
                          buy_counter=user.buy_counter + 1)

        await BasketProduct.clear_basket(basket.id)

        await message.answer(text=LEXICON['successful_payment'],
                             reply_markup=get_start_kb())

    else:
        await message.answer(text=LEXICON['not_enough_money'],
                             reply_markup=get_start_kb())

    await state.clear()


# Хендлер срабатывающий на отказ от оплаты
@user_router.message(FSMPayment.accept, Text(text=LEXICON['no']))
async def process_no_payment(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LEXICON['main_menu'],
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на кнопку "Пополнить баланс"
@user_router.message(Text(text=LEXICON['replenish_balance']))
async def replenish_balance(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMBalance.replenish_balance)

    await message.answer(text=LEXICON['amount_money_for_replenish'],
                         reply_markup=get_start_kb())


# Хендлер говорящий, что пополнение баланса прошло успешно
@user_router.message(FSMBalance.replenish_balance, lambda x: x.text.isdigit() and int(x.text) > 0)
async def successful_amount(message: Message, state: FSMContext) -> None:
    user: User = await User.get_user(int(message.from_user.id))
    new_balance: int = int(user.balance) + int(message.text)
    await User.update(id=user.id,
                      balance=new_balance)
    await state.clear()

    await message.answer(text=LEXICON['successful_replenish_balance'],
                         reply_markup=get_start_kb())


# Хендлер говорящий, что пополнение баланса не получилось
@user_router.message(FSMBalance.replenish_balance, lambda x: not x.text.isdigit() or int(x.text) <= 0)
async def unsuccessful_amount(message: Message) -> None:
    await message.answer(text=LEXICON['unsuccessful_amount_for_balance'])
