from datetime import date, datetime
from api.equipment import get_equipment

def parse_category_equipment_data(source: list) -> str:
    """
    Parse data from category table from DB in format
    \nn. equipment_name
        \nowner
        \nholder
        \ndescrition
    """
    transformed_data = [f"<b>{i+1}. {value['name']}</b>\nВладелец техники @{value['owner']['username']}\nСейчас техника у @{value['holder']['username']}\nОписание: {value['description']}" for i, value in enumerate(source)]
    return '\n\n'.join(transformed_data), len(transformed_data)


def parse_history_data(source: list) -> str:
    """
    Parse data from history table from DB in format
    \nn. equipment name
        \nsource
        \ndestination
        \ndate and time
    """
    transformed_data = [f"<b>{i+1}. {value['equipment']['name']}</b>\nВзято у @{value['source']['username']}\nПередано @{value['destination']['username']}\nДата и время: {isoformat_to_informal(value['date'])}" for i, value in enumerate(source)]
    return '\n'.join(transformed_data)


def parse_equipment_history_data(source: list) -> str:
    """
    Parse data from history table from DB in format
    \nn.date and time
        \nsource
        \ndestination
    """
    transformed_data = [f"<b>{i+1}. {isoformat_to_informal(value['date'])}</b>\nВзято у @{value['source']['username']}\nПередано @{value['destination']['username']}" for i, value in enumerate(source)]
    return '\n'.join(transformed_data)


def parse_qr_code_data(source: str) -> str:
    """
    Parse data from QR code in format
    \n equipment name
    """
    return f"{get_equipment(int(source.split()[0]))['name']}"


isoformat_to_informal = lambda datetime: f'{datetime.day}.{datetime.month}.{datetime.year}, {datetime.hour}:{datetime.minute}'
