from typing import Optional, Union

from aiogram import Router, F
from aiogram.filters import Text, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from middlewares.throttling import AntiFloodMiddleware
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


@admin_router.message(Command(commands='admin'))
async def process_admin_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LEXICON['admin'],
                         reply_markup=get_admin_kb())


@admin_router.message(Text(LEXICON['back_to_main_menu_button']))
async def go_to_main_menu(message: Message) -> None:
    await message.answer(text=LEXICON['main_menu'],
                         reply_markup=get_start_kb())


@admin_router.message(Text(text=LEXICON['download_product']))
async def process_download(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMProduct.download_photo)
    await message.answer(text=LEXICON['FSM_download_1'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(Text(text=LEXICON['cancel_fsm_button']))
async def process_cancel_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text=LEXICON['FSM_cancel'],
                         reply_markup=get_product_settings_kb())


@admin_router.message(FSMProduct.download_photo, ~F.photo)
async def sent_incorrect_photo(message: Message):
    await message.answer(LEXICON['not_photo'])


@admin_router.message(FSMProduct.download_photo, F.photo)
async def process_photo_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(FSMProduct.download_name)
    await message.answer(LEXICON['FSM_photo_sent'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(FSMProduct.download_name, F.text.isdigit() or ~F.text)
async def sent_incorrect_name(message: Message) -> None:
    await message.answer(LEXICON['incorrect_name'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(FSMProduct.download_name, F.text)
async def process_descr_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FSMProduct.download_description)
    await message.answer(text=LEXICON['FSM_descr_sent'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(FSMProduct.download_description, F.text.isdigit() or ~F.text)
async def sent_incorrect_descr(message: Message) -> None:
    await message.answer(text=LEXICON['incorrect_descr'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(FSMProduct.download_description, F.text)
async def process_price_sent(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FSMProduct.download_price)
    await message.answer(text=LEXICON['FSM_price_sent'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(FSMProduct.download_price, lambda x: not x.text.isdigit() or int(x.text) < 1)
async def sent_incorrect_price(message: Message) -> None:
    await message.answer(text=LEXICON['incorrect_price'],
                         reply_markup=cancel_fsm_kb())


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


@admin_router.callback_query(FSMProduct.download_category)
@admin_router.message(FSMProduct.download_category, F.text)
async def category_name(message: Message | CallbackQuery, state: Optional[FSMContext] = None) -> None:
    if type(message) == CallbackQuery:
        product_dict: dict[str, Union[str, int]] = await state.update_data(category=message.data.split(': ')[1])
        category: str = await Category.get_category_id(product_dict['category'])
    else:
        product_dict: dict[str, Union[str, int]] = await state.update_data(category=message.text)
        category: str = (await Category.create(name=product_dict['category'])).id

    await Product.create(photo=product_dict['photo'],
                         name=product_dict['name'],
                         description=product_dict['description'],
                         price=int(product_dict['price']),
                         category_id=int(category))

    await state.clear()

    if type(message) == CallbackQuery:
        await message.message.answer(text=LEXICON['FSM_finish'],
                                     reply_markup=get_product_settings_kb())
    else:
        await message.answer(text=LEXICON['FSM_finish'],
                             reply_markup=get_product_settings_kb())


@admin_router.message(Text(text=LEXICON['download_category']))
async def download_category(message: Message, state: FSMContext) -> None:
    await message.answer(text=LEXICON['download_category_1'],
                         reply_markup=cancel_fsm_kb())
    await state.set_state(FSMCategory.download_category)


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


@admin_router.callback_query(FSMCategory.delete_category)
async def delete_category_1(callback: CallbackQuery) -> None:
    cat_name: str = callback.data.split(': ')[1]
    cat_id: str = await Category.get_category_id(cat_name)

    await Category.delete(int(cat_id))

    categories: list = [i.name for i in await Category.get_all()]

    await callback.message.edit_reply_markup(reply_markup=delete_categories_kb(categories))

    await callback.message.answer(text=LEXICON['delete_category_3'],
                                  reply_markup=cancel_fsm_kb())


@admin_router.callback_query(FSMProduct.delete_step, Text(text='back_button'))
@admin_router.message(Text(text=LEXICON['delete_product']))
async def process_delete_product(message: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()

    categories_id: list = await Product.get_exists_categories()
    categories: list = await Category.get_exists(categories_id)

    if type(message) == CallbackQuery:
        await message.message.delete()
        await message.message.answer(text=LEXICON['delete_product_1'],
                                     reply_markup=create_catalog_kb(categories))

    else:
        await message.answer(text=LEXICON['delete_product_1'],
                             reply_markup=create_catalog_kb(categories))

    await state.set_state(FSMProduct.delete_product)


@admin_router.callback_query(FSMProduct.delete_product, Text(startswith='cat'))
async def process_delete_product_1(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()

    category_name: str = callback.data.split(': ')[1]
    category_id: str = await Category.get_category_id(category_name)
    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(category_id)

    await state.set_state(FSMProduct.delete_step)

    storage: dict[str, Union[str, int]] = await state.update_data(delete_step=1, category=category_id)

    await callback.message.answer_photo(photo=list_of_products[storage['delete_step'] - 1]['photo'],
                                        caption=f'<b> {list_of_products[storage["delete_step"] - 1]["name"]} </b>\n'
                                                f'{list_of_products[storage["delete_step"] - 1]["descr"]}\n'
                                                f'<b>{list_of_products[storage["delete_step"] - 1]["price"]} ₽</b>',
                                        reply_markup=delete_product_kb('backward',
                                                                       f'{storage["delete_step"]} / {len(list_of_products)}',
                                                                       'forward'))
    await state.update_data(product_id=int(list_of_products[storage['delete_step'] - 1]['id']))

    await callback.answer()


@admin_router.callback_query(FSMProduct.delete_step, Text(text='delete_product_button'))
@admin_router.callback_query(FSMProduct.delete_step, Text(text=['forward', 'backward']))
async def process_step_press(callback: CallbackQuery, state: FSMContext) -> None:
    storage: dict[str, Union[str, int]] = await state.get_data()

    if callback.data == 'delete_product_button':
        await Product.delete(storage['product_id'])

        await callback.answer(text=LEXICON['successful_deleted_product'])

        storage: dict[str, Union[str, int]] = await state.get_data()

    if callback.data == 'forward':
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=storage['delete_step'] + 1)
    else:
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=storage['delete_step'] - 1)

    list_of_products: list[dict[str, Union[str, int]]] = await Product.get_products_in_category(storage['category'])

    if len(list_of_products) == 0:
        await process_delete_product(callback, state)

    elif storage['delete_step'] > len(list_of_products):
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=1)

    elif storage['delete_step'] < 1:
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=len(list_of_products))

    if len(list_of_products) > 1:
        media: InputMediaPhoto = InputMediaPhoto(type='photo',
                                                 media=list_of_products[storage['delete_step'] - 1]['photo'],
                                                 caption=f'<b> {list_of_products[storage["delete_step"] - 1]["name"]} </b>\n'
                                                         f'{list_of_products[storage["delete_step"] - 1]["descr"]}\n'
                                                         f'<b>{list_of_products[storage["delete_step"] - 1]["price"]} ₽</b>')

        await callback.message.edit_media(media=media,
                                          reply_markup=delete_product_kb('backward',
                                                                         f'{storage["delete_step"]} / {len(list_of_products)}',
                                                                         'forward'))
    elif len(list_of_products) == 1 and callback.data == 'delete_product_button':

        await callback.message.edit_reply_markup(reply_markup=delete_product_kb('backward',
                                                                                f'{storage["delete_step"]} / {len(list_of_products)}',
                                                                                'forward'))

    await state.update_data(product_id=int(list_of_products[storage['delete_step'] - 1]['id']))

    await callback.answer()


@admin_router.message(Text(text=LEXICON['back_to_admin_menu_button']))
async def process_back_to_admin_menu(message: Message):
    await message.answer(text=LEXICON['back_to_admin_menu'],
                         reply_markup=get_admin_kb())


@admin_router.message(Text(text=LEXICON['product_settings']))
async def process_product_settings(message: Message) -> None:
    await message.answer(text=LEXICON['product_settings'],
                         reply_markup=get_product_settings_kb())


@admin_router.message(Text(text=LEXICON['general_settings']))
async def process_general_settings(message: Message) -> None:
    await message.answer(text=LEXICON['general_settings'],
                         reply_markup=get_general_settings())


@admin_router.message(Text(text=LEXICON['edit_help']))
async def process_edit_help(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.help)
    await message.answer(text=LEXICON['text_for_help'])


@admin_router.message(FSMSettings.help, F.text)
async def finish_edit_help(message: Message, state: FSMContext) -> None:
    info: str = message.text

    await Help.delete_help_content()
    await Help.create(help_content=info)

    await state.clear()
    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_general_settings())


@admin_router.message(Text(text=LEXICON['edit_faq']))
async def process_edit_faq(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.faq)
    await message.answer(text=LEXICON['text_for_faq'])


@admin_router.message(FSMSettings.faq, F.text)
async def finish_edit_faq(message: Message, state: FSMContext) -> None:
    info: str = message.text

    await FAQ.delete_faq_content()
    await FAQ.create(faq_content=info)

    await state.clear()
    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_general_settings())


@admin_router.message(Text(text=LEXICON['download_catalog_photo']))
async def download_catalog_photo(message: Message, state: FSMContext) -> None:
    await state.set_state(FSMSettings.photo)

    await message.answer(text=LEXICON['photo_for_catalog'],
                         reply_markup=cancel_fsm_kb())


@admin_router.message(F.photo, FSMSettings.photo)
async def successful_photo_catalog(message: Message, state: FSMContext) -> None:
    photo: str = message.photo[-1].file_id

    await CatalogPhoto.delete_photo()
    await CatalogPhoto.create(photo=photo)
    await state.clear()

    await message.answer(text=LEXICON['successful'],
                         reply_markup=get_product_settings_kb())


@admin_router.message(~F.photo, FSMSettings.photo)
async def unsuccessful_photo_catalog(message: Message) -> None:
    await message.answer(text=LEXICON['unsuccessful_photo'])


@admin_router.message(Text(text=LEXICON['statistics']))
async def process_statistics_button(message: Message) -> None:
    users: list[User] = await User.get_all()

    await message.answer(text=LEXICON['statistics_info'].format(users=len(users),
                                                                users_balance=sum(i.balance for i in users),
                                                                ref_users=sum(i.referrer_counter for i in users),
                                                                total_buys=sum(i.buy_counter for i in users)))
