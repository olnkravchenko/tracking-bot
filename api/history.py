from db.models import User, Equipment, History
from datetime import datetime


def add_row(equipment_id: int, source_id: int, destination_id: int) -> dict:
    row = History.create(
        source=User.get(id=source_id),
        destination=User.get(id=destination_id),
        equipment=Equipment.get(equipment_id),
        date=datetime.now()
    )
    return row.get_as_dict()


def get_row(id: int) -> dict:
    row = History.get(id=id)
    return row.get_as_dict()


def get_user_history(user_id: int, count: int = 20) -> list:
    res = []
    user = User.get(id=user_id)
    for row in History.select().where((History.source == user) | (History.destination == user)).order_by(History.id.desc()).limit(count):
        res.append(row.get_as_dict())
    return res


def get_equipment_history(equipment_id: int, count: int = 20) -> list:
    res = []
    eq = Equipment.get(id=equipment_id)
    for row in History.select().where(History.equipment == eq).order_by(History.id.desc()).limit(count):
        res.append(row.get_as_dict())
    return res


def get_last_actions(count: int) -> list:
    res = []
    for row in History.select().limit(count):
        res.append(row.get_as_dict())
    return res
