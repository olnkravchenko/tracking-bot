from db.models import User, Equipment, History
from datetime import datetime, date


def add_row(equipment_id: int, source_id: int, destination_id: int):
    row = History.create(
        source=User.get(id=source_id),
        destination=User.get(id=destination_id),
        equipment=Equipment.get(equipment_id),
        date=datetime.now()
    )


def get_row(id: int) -> dict:
    return History.get(id=id).get_as_dict()


def get_user_history(user_id: int, count: int = 20) -> list:
    user = User.get(id=user_id)
    return [row.get_as_dict() for row in History.select().where((History.source == user) | (History.destination == user)).order_by(History.id.desc()).limit(count)]


def get_equipment_history(equipment_id: int, count: int = 20) -> list:
    eq = Equipment.get(id=equipment_id)
    return [row.get_as_dict() for row in History.select().where(History.equipment == eq).order_by(History.id.desc()).limit(count)]


def get_equipment_history_by_date(equipemnt_id: int, start_day: int, start_month: int, start_year: int, end_day: int, end_month: int, end_year: int) -> list:
    eq = Equipment.get(id=equipemnt_id)
    return [row.get_as_dict() for row in History.select().where((History.equipment == eq) & (date(day=start_day, month=start_month, year=start_year) <= History.date <= date(day=end_day, month=end_month, year=end_year)))]


def get_history_by_period(start_day: int, start_month: int, start_year: int, end_day: int, end_month: int, end_year: int) -> list:
    eq = Equipment.get(id=equipemnt_id)
    return [row.get_as_dict() for row in History.select().where(date(day=start_day, month=start_month, year=start_year) <= History.date <= date(day=end_day, month=end_month, year=end_year))]



def get_last_actions(count: int) -> list:
    return [row.get_as_dict() for row in History.select().limit(count)]
