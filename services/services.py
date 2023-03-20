from collections import Counter
from typing import Union

from aiogram.fsm.context import FSMContext


def format_order(products: list[tuple[str, str | int]]) -> dict[str, str]:
    counter = Counter(i for i in products)

    total_price: int = 0
    length: int = 25
    d = {}
    result: list[dict[str, str]] = []

    for item, count in counter.items():
        name = item[0]
        price = item[1]

        if name not in d.values():
            d: dict[str, str] = {'name': name, 'price': str(price), 'count': str(count),
                                 'sum': str(count * price)}
            result.append(d)
            total_price += price * count

    order: str = '\n\n'.join(
        f"{str(n)}. {i['name']}  -  {i['price']}₽\nx{i['count']}шт | {i['sum']}₽" for n, i in enumerate(result, 1))

    return {'order': order,
            'length': length,
            'total_price': total_price}


async def update_storage(length: int,
                         storage: dict[str, Union[str, int]],
                         state: FSMContext) -> dict[str, Union[str, int]]:
    if storage['delete_step'] > length:
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=1)
    elif storage['delete_step'] < 1:
        storage: dict[str, Union[str, int]] = await state.update_data(delete_step=length)
    return storage
