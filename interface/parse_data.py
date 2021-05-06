from api.equipment import get_equipment, validate_control_sum


def parse_category_equipment_data(source: list) -> str:
    """
    Parse data from category table from DB in format
    \nn. equipment_name
        \nowner
        \nholder
        \ndescrition
    """
    transformed_data = []
    for i, value in enumerate(source):
        owner_username = value['owner']['username']
        owner_user_id = value['owner']['id']
        owner = f'@{owner_username}' if owner_username is not None\
            else f'[{owner_user_id}](tg://user?id={owner_user_id})'

        holder_username = value['holder']['username']
        holder_user_id = value['holder']['id']
        holder = f'@{holder_username}' if holder_username is not None\
            else f'[{holder_user_id}](tg://user?id={holder_user_id})'

        transformed_data.append(f"<b>{i+1}. {value['name']}\
</b>\nВладелец техники {owner}\n\
Сейчас техника у {holder}\n\
Описание: {value['description']}")
    return '\n\n'.join(transformed_data), len(transformed_data)


def parse_history_data(source: list) -> str:
    """
    Parse data from history table from DB in format
    \nn. equipment name
        \nsource
        \ndestination
        \ndate and time
    """
    transformed_data = []
    for i, value in enumerate(source):
        source_username = value['source']['username']
        source_user_id = value['source']['id']
        source_user = f'@{source_username}' if source_username is not None\
            else f'[{source_user_id}](tg://user?id={source_user_id})'

        dest_username = value['destination']['username']
        dest_user_id = value['destination']['id']
        dest = f'@{dest_username}' if dest_username is not None\
            else f'[{dest_user_id}](tg://user?id={dest_user_id})'

        transformed_data.append(f"<b>{i+1}. {value['equipment']['name']}\
</b>\nВзято у {source_user}\n\
Передано {dest}\n\
Дата и время: {isoformat_to_informal(value['date'])}")
    return '\n'.join(transformed_data)


def parse_equipment_history_data(source: list) -> str:
    """
    Parse data from history table from DB in format
    \nn.date and time
        \nsource
        \ndestination
    """
    transformed_data = []
    for i, value in enumerate(source):
        source_username = value['source']['username']
        source_user_id = value['source']['id']
        source_user = f'@{source_username}' if source_username is not None\
            else f'[{source_user_id}](tg://user?id={source_user_id})'

        dest_username = value['destination']['username']
        dest_user_id = value['destination']['id']
        dest = f'@{dest_username}' if dest_username is not None\
            else f'[{dest_user_id}](tg://user?id={dest_user_id})'
        transformed_data.append(f"<b>{i+1}. {isoformat_to_informal(value['date'])}\
</b>\nВзято у {source_user}\nПередано {dest}")
    return source[0]['equipment']['name']+'\n'+'\n'.join(transformed_data)


def parse_qr_code_data(source: str) -> str:
    """
    Parse data from QR code in format
    \n equipment name
    """
    try:
        equipment_data = get_equipment(int(source.split()[0]))
        return f"{equipment_data['name']}"
    except Exception:
        return 'Данной техники нет в базе данных'


def parse_my_equipment_data(source: list) -> str:
    """
    Parse data from list of user's equipment
    \n equipment name
    """
    return '\n'.join([f"{i+1}. {value['name']}"
                     for i, value in enumerate(source)])


isoformat_to_informal = lambda datetime: f'{datetime.day}.{datetime.month}.\
{datetime.year}, {datetime.hour}:{datetime.minute}'


def validate_qr_code(qr_code_data: str) -> bool:
    """
    Validate control sum of the QR code
    """
    # get equipment id and control sum from the QR code data
    split_data = qr_code_data.split()
    if len(split_data) == 2 and qr_code_data.split()[0].isdigit():
        equipment_id = int(qr_code_data.split()[0])
        control_sum = qr_code_data.split()[1]
        try:
            return validate_control_sum(equipment_id, control_sum)
        except Exception:
            return False
    else:
        return False
