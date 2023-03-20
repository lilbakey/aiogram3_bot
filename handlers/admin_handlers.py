from typing import Union

from aiogram import Router, F
from aiogram.filters import Text, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from middlewares.throttling import AntiFloodMiddleware
from utils.utils import get_input_media
from services.services import update_storage
from states.FSMProduct import FSMProduct
from states.FSMCategory import FSMCategory
from states.FSMSettings import FSMSettings
from lexicon.lexicon import LEXICON
from .user_handlers import get_start_kb
from keyboards.keyboards_admin import (get_admin_kb, get_product_settings_kb, cancel_fsm_kb, create_categories_kb,
                                       delete_categories_kb, create_catalog_kb, delete_product_kb, get_general_settings)

from filters.is_admin import IsAdmin, admins_id

from models import (CatalogPhoto, Category, FAQ, Help, Product, User)

admin_router: Router = Router()
admin_router.message.filter(IsAdmin(admins_id))
admin_router.callback_query.filter(IsAdmin(admins_id))
admin_router.message.middleware(AntiFloodMiddleware())
admin_router.callback_query.middleware(AntiFloodMiddleware())


# Хэндлер срабатывающий на команду /admin
@admin_router.message(Command(commands='admin'))
async def process_admin_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LEXICON['admin'],
                         reply_markup=get_admin_kb())


# Хендлер срабатывающий на кнопку назад в главное меню
@admin_router.message(Text(LEXICON['back_to_main_menu_button']))
async def go_to_main_menu(message: Message) -> None:
    await message.answer(text=LEXICON['main_menu'],
                         reply_markup=get_start_kb())


# Хендлер срабатывающий на кнопку добавить товар
@admin_router.message(Text(text=LEXICON['download_product']))
async def process_download(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMProduct.download_photo)
    await message.answer(text=LEXICON['FSM_download_1'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на кнопку отмены
@admin_router.message(Text(text=LEXICON['cancel_fsm_button']))
async def process_cancel_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LEXICON['FSM_cancel'],
                         reply_markup=get_product_settings_kb())


# Хендлер срабатывающий на отправку не фотографии для загрузки товара
@admin_router.message(FSMProduct.download_photo, ~F.photo)
async def sent_incorrect_photo(message: Message):
    await message.answer(LEXICON['not_photo'])


# Хендлер срабатывающий на корректное присланное фото для товара
@admin_router.message(FSMProduct.download_photo, F.photo)
async def process_photo_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(FSMProduct.download_name)
    await message.answer(LEXICON['FSM_photo_sent'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на некорректное имя товара
@admin_router.message(FSMProduct.download_name, F.text.isdigit() or ~F.text)
async def sent_incorrect_name(message: Message) -> None:
    await message.answer(LEXICON['incorrect_name'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на корректное описание товара
@admin_router.message(FSMProduct.download_name, F.text)
async def process_descr_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FSMProduct.download_description)
    await message.answer(text=LEXICON['FSM_descr_sent'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на некорректное описание товара
@admin_router.message(FSMProduct.download_description, F.text.isdigit() or ~F.text)
async def sent_incorrect_descr(message: Message) -> None:
    await message.answer(text=LEXICON['incorrect_descr'],
                         reply_markup=cancel_fsm_kb())


# Хендлер требующий отправить цену товара
@admin_router.message(FSMProduct.download_description, F.text)
async def process_price_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FSMProduct.download_price)
    await message.answer(text=LEXICON['FSM_price_sent'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на некорректную цену для товара
@admin_router.message(FSMProduct.download_price, lambda x: not x.text.isdigit() or int(x.text) < 1)
async def sent_incorrect_price(message: Message) -> None:
    await message.answer(text=LEXICON['incorrect_price'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на корректно отправленную цену
@admin_router.message(FSMProduct.download_price, lambda x: x.text.isdigit and int(x.text) > 1)
async def sent_correct_price(message: Message, state: FSMContext) -> None:
    await state.update_data(price=message.text)

    categories: list = [i.name for i in await Category.get_all()]

    if categories:

        await message.answer(text=LEXICON['choice_category'],
                             reply_markup=create_categories_kb(categories))
        await message.answer(text=LEXICON['text_name_category'],
                             reply_markup=cancel_fsm_kb())
    else:
        await message.answer(text=LEXICON['no_category'],
                             reply_markup=cancel_fsm_kb())

    await state.set_state(FSMProduct.download_category)


# Хендлер срабатывающий на КоллБэк от существующей категории при создании товара
@admin_router.callback_query(FSMProduct.download_category)
async def cb_category_name(callback: CallbackQuery, state: FSMContext) -> None:
    product_dict: dict[str, Union[str, int]] = await state.update_data(category=callback.data.split(': ')[1])
    category_id: str = await Category.get_category_id(product_dict['category'])

    await Product.create(photo=product_dict['photo'],
                         name=product_dict['name'],
                         description=product_dict['description'],
                         price=int(product_dict['price']),
                         category_id=int(category_id))

    await state.clear()

    await callback.message.answer(text=LEXICON['FSM_finish'],
                                  reply_markup=get_product_settings_kb())


# Хендлер срабатывающий на сообщение с названием новой категории при создании товара
@admin_router.message(FSMProduct.download_category, F.text)
async def msg_category_name(message: Message, state: FSMContext) -> None:
    is_name_in_base: bool = await Category.check_name_in_base(message.text)

    if not is_name_in_base:
        product_dict: dict[str, Union[str, int]] = await state.update_data(category=message.text)
        category_id: str = (await Category.create(name=product_dict['category'])).id

        await Product.create(photo=product_dict['photo'],
                             name=product_dict['name'],
                             description=product_dict['description'],
                             price=int(product_dict['price']),
                             category_id=int(category_id))

        await state.clear()

        await message.answer(text=LEXICON['FSM_finish'],
                             reply_markup=get_product_settings_kb())
    else:
        await message.answer(text=LEXICON['exists_category'],
                             reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на кнопку загрузки новой категории
@admin_router.message(Text(text=LEXICON['download_category']))
async def download_category(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON['download_category_1'],
                         reply_markup=cancel_fsm_kb())
    await state.set_state(FSMCategory.download_category)


# Хендлер проверяющий на существование введеное название категории
@admin_router.message(FSMCategory.download_category)
async def download_category_1(message: Message, state: FSMContext) -> None:
    is_name_in_base: bool = await Category.check_name_in_base(message.text)

    if not is_name_in_base:
        await Category.create(name=message.text)

        await state.clear()

        await message.answer(text=LEXICON['successful_name_cat'],
                             reply_markup=get_product_settings_kb())
    else:
        await message.answer(text=LEXICON['exists_category'],
                             reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий при нажатии кнопки удалить категорию
@admin_router.message(Text(text=LEXICON['delete_category']))
async def delete_category(message: Message, state: FSMContext) -> None:
    categories: list = [i.name for i in await Category.get_all()]

    if categories:

        await state.set_state(FSMCategory.delete_category)

        await message.answer(text=LEXICON['delete_category_1'],
                             reply_markup=delete_categories_kb(categories))

        await message.answer(text=LEXICON['delete_category_2'],
                             reply_markup=cancel_fsm_kb())
    else:
        await message.answer(text=LEXICON['no_exists_category'])


# Хендлер срабатывающий на КоллБэк для удаления категории
@admin_router.callback_query(FSMCategory.delete_category)
async def delete_category_1(callback: CallbackQuery) -> None:
    cat_name: str = callback.data.split(': ')[1]
    cat_id: str = await Category.get_category_id(cat_name)

    await Category.delete(int(cat_id))

    categories: list = [i.name for i in await Category.get_all()]

    await callback.message.edit_reply_markup(reply_markup=delete_categories_kb(categories))

    await callback.message.answer(text=LEXICON['delete_category_3'],
                                  reply_markup=cancel_fsm_kb())


# Хендлер показывающий категории, срабатывает на КоллБэк "назад"
# и при удалении всех товаров из категории
@admin_router.callback_query(FSMProduct.delete_step, Text(text='back_button'))
async def cb_process_delete_product(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    categories_id: list = await Product.get_exists_categories()
    categories: list = await Category.get_exists(categories_id)

    await callback.message.delete()
    await callback.message.answer(text=LEXICON['delete_product_1'],
                                  reply_markup=create_catalog_kb(categories))

    await state.set_state(FSMProduct.delete_product)


# Хендлер показывающий категории, срабатывает на кнопку "удалить товар"
@admin_router.message(Text(text=LEXICON['delete_product']))
async def process_delete_product(message: Message, state: FSMContext) -> None:
    await state.clear()

    categories_id: list = await Product.get_exists_categories()
    categories: list = await Category.get_exists(categories_id)

    await message.answer(text=LEXICON['delete_product_1'],
                         reply_markup=create_catalog_kb(categories))

    await state.set_state(FSMProduct.delete_product)


# Хендлер показывающий меню с товарами для удаления
@admin_router.callback_query(FSMProduct.delete_product, Text(startswith='cat'))
async def process_delete_product_1(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()

    category_name: str = callback.data.split(': ')[1]
    category_id: str = await Category.get_category_id(category_name)
    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(category_id)

    await state.set_state(FSMProduct.delete_step)

    storage: dict[str, Union[str, int]] = await state.update_data(delete_step=1, category=category_id)
    content = list_of_products[storage['delete_step'] - 1]

    await callback.message.answer_photo(photo=content['photo'],
                                        caption=f'<b> {content["name"]} </b>\n'
                                                f'{content["descr"]}\n'
                                                f'<b>{content["price"]} ₽</b>',
                                        reply_markup=delete_product_kb('backward',
                                                                       f'{storage["delete_step"]} /'
                                                                       f' {len(list_of_products)}',
                                                                       'forward'))
    await state.update_data(product_id=int(content['id']))

    await callback.answer()


# Хендлер срабатывающий на удаление товара
@admin_router.callback_query(FSMProduct.delete_step, Text(text='delete_product_button'))
async def show_menu_for_delete(callback: CallbackQuery, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()

    await Product.delete(storage['product_id'])
    await callback.answer(text=LEXICON['successful_deleted_product'])

    storage: dict[str, Union[str, int]] = await state.get_data()
    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(storage['category'])
    length = len(list_of_products)

    if length == 0:
        await cb_process_delete_product(callback, state)

    storage: dict[str, Union[str, int]] = await update_storage(length, storage, state)
    content: dict[str, Union[str, int]] = list_of_products[storage['delete_step'] - 1]
    if length > 1:
        media: InputMediaPhoto = get_input_media(content)
        await callback.message.edit_media(media=media,
                                          reply_markup=delete_product_kb('backward',
                                                                         f'{storage["delete_step"]} / {length}',
                                                                         'forward'))
    elif length == 1:
        await callback.message.edit_reply_markup(reply_markup=delete_product_kb('backward',
                                                                                f'{storage["delete_step"]} / {length}',
                                                                                'forward'))
    await state.update_data(product_id=int(content['id']))
    await callback.answer()


# Хендлер срабатывающий на кнопку "вперед" или "назад"
@admin_router.callback_query(FSMProduct.delete_step, Text(text=['forward', 'backward']))
async def process_step_press(callback: CallbackQuery, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()
    if callback.data == 'forward':
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=storage['delete_step'] + 1)
    else:
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=storage['delete_step'] - 1)

    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(storage['category'])
    length = len(list_of_products)

    storage: dict[str, Union[str, int]] = await update_storage(length, storage, state)
    content: dict[str, Union[str, int]] = list_of_products[storage['delete_step'] - 1]

    media: InputMediaPhoto = get_input_media(content)

    await callback.message.edit_media(media=media,
                                      reply_markup=delete_product_kb('backward',
                                                                     f'{storage["delete_step"]} / {length}',
                                                                     'forward'))
    await state.update_data(product_id=int(content['id']))

    await callback.answer()


# Хендлер срабатывающий на кнопку "назад в меню администратора"
@admin_router.message(Text(text=LEXICON['back_to_admin_menu_button']))
async def process_back_to_admin_menu(message: Message):
    await message.answer(text=LEXICON['back_to_admin_menu'],
                         reply_markup=get_admin_kb())


# Хендлер срабатывающий на кнопку "управление товарами"
@admin_router.message(Text(text=LEXICON['product_settings']))
async def process_product_settings(message: Message) -> None:
    await message.answer(text=LEXICON['product_settings'],
                         reply_markup=get_product_settings_kb())


# Хендлер срабатывающий на кнопку "общие настройки"
@admin_router.message(Text(text=LEXICON['general_settings']))
async def process_general_settings(message: Message) -> None:
    await message.answer(text=LEXICON['general_settings'],
                         reply_markup=get_general_settings())


# Хендлер срабатывающий на кнопку "редактировать help"
@admin_router.message(Text(text=LEXICON['edit_help']))
async def process_edit_help(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.help)
    await message.answer(text=LEXICON['text_for_help'])


# Хендлер срабатывающий на успешное редактирование кнопки help
@admin_router.message(FSMSettings.help, F.text)
async def finish_edit_help(message: Message, state: FSMContext) -> None:
    info: str = message.text

    await Help.delete_help_content()
    await Help.create(help_content=info)

    await state.clear()
    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_general_settings())


# Хендлер срабатывающий на кнопку "редактировать FAQ"
@admin_router.message(Text(text=LEXICON['edit_faq']))
async def process_edit_faq(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.faq)
    await message.answer(text=LEXICON['text_for_faq'])


# Хендлер срабатывающий на успешное редактирование кнопки FAQ
@admin_router.message(FSMSettings.faq, F.text)
async def finish_edit_faq(message: Message, state: FSMContext) -> None:
    info: str = message.text

    await FAQ.delete_faq_content()
    await FAQ.create(faq_content=info)

    await state.clear()
    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_general_settings())


# Хендлер срабатвающий на кнопку "загрузить фото для каталога"
@admin_router.message(Text(text=LEXICON['download_catalog_photo']))
async def download_catalog_photo(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.photo)

    await message.answer(text=LEXICON['photo_for_catalog'],
                         reply_markup=cancel_fsm_kb())


# Хендлер срабатывающий на успешное добавление фото для каталога
@admin_router.message(F.photo, FSMSettings.photo)
async def successful_photo_catalog(message: Message, state: FSMContext) -> None:
    photo: str = message.photo[-1].file_id

    await CatalogPhoto.delete_photo()
    await CatalogPhoto.create(photo=photo)
    await state.clear()

    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_product_settings_kb())


# Хендлер срабатывающий на неудачное добавление фото для каталога
@admin_router.message(~F.photo, FSMSettings.photo)
async def unsuccessful_photo_catalog(message: Message) -> None:
    await message.answer(text=LEXICON['unsuccessful_photo'])


# Хендлер срабатывающий на кнопку "статистика"
@admin_router.message(Text(text=LEXICON['statistics']))
async def process_statistics_button(message: Message) -> None:
    users: list[User] = await User.get_all()

    await message.answer(text=LEXICON['statistics_info'].format(users=len(users),
                                                                users_balance=sum(i.balance for i in users),
                                                                ref_users=sum(i.referrer_counter for i in users),
                                                                total_buys=sum(i.buy_counter for i in users)))
