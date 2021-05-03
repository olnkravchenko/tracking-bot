from datetime import timedelta, datetime
from asyncio import get_event_loop
import logging

from interface.init_bot import bot
from interface.parse_data import parse_my_equipment_data
from api.user import get_admin_list
from db.models import History, User, Equipment


def get_taking_history() -> list:
    """
    Get history that was created more than 24 hours ago but
    less than a week ago and source is a storehouse
    """
    return (row.get_as_dict() for row in History.select().where(
        (History.date < (datetime.now() - timedelta(days=1))) &
        (History.date > (datetime.now() - timedelta(days=7))) &
        (History.source == User.get(id=1))))


def is_transfered(eq_row: dict, user_row: dict, date: datetime) -> list:
    """
    Get history of specific equipment and with specific source after
    specific date, sorted by date descending
    """
    return (row.get_as_dict() for row in History.select().where(
        (History.date > date) &
        (History.equipment == Equipment.get(id=eq_row['id'])) &
        (History.source == User.get(id=user_row['id']))))


def find_final_holder(eq_row: dict, holder: dict, date: datetime) -> dict:
    if holder['id'] != 1 and not is_empty(is_transfered(eq_row, holder, date)):
        transfers = is_transfered(eq_row, holder, date)
        holder, date = transfers[0]['destination'], transfers[0]['date']
        holder = find_final_holder(eq_row, holder, date)
    return holder


def is_empty(source: list) -> bool:
    try:
        _ = next(source)
    except Exception:
        return True
    return False


def find_unreturned() -> dict:
    """
    Find users which didn't return the equipment
    """
    users = {}
    history_data = ([row['equipment'], row['destination'], row['date']]
                    for row in get_taking_history())
    for row in history_data:
        holder = find_final_holder(*row)
        if holder['id'] != 1:
            add_into_dict(users, row)
    return users


def add_into_dict(source: dict, value: list):
    if str(value[1]['id']) not in source:
        source[str(value[1]['id'])] = [value[0]]
    else:
        source[str(value[1]['id'])].append(value[0])


async def main():
    users = find_unreturned()
    logging.info(f'Requesting to return the equipment from: \n{users}')
    for key in users:
        user_eq = parse_my_equipment_data(users[key])
        user = User.get(id=int(key)).get_as_dict()
        username = user['username']
        await bot.send_message(
            chat_id=int(key),
            text=f'Вы не вернули данную технику:\n{user_eq}')
        for admin in get_admin_list():
            await bot.send_message(
                chat_id=admin['id'],
                text='{} не вернул(а) данную технику:\n{}'.format(
                    f'@{username}' if username is not None
                    else f'[{int(key)}](tg://user?id={key})',
                    user_eq))
