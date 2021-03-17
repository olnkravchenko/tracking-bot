from db.models import Transfer, User, Equipment
from api import history


def create_transfer(equipment_id: int, source_id: int, destination_id: int) -> dict:
    t = Transfer.create(equipment=Equipment.get(id=equipment_id), source=User.get(id=source_id), destination=User.get(id=destination_id))
    return t.get_as_dict()


def get_transfer(id: int) -> dict:
    t = Transfer.get(id=id)
    return t.get_as_dict()


def get_active_transfers(user_id: int) -> list:
    res = []
    for t in Transfer.select().where(Transfer.destination == User.get(id=user_id)):
        res.append(t.get_as_dict())
    return res


def verify_transfer(id: int) -> bool:
    t = Transfer.get(id=id)
    history.add_row(equipment_id=t.equipment.id, source_id=t.source.id, destination_id=t.destination.id)
    eq = Equipment.get(id=t.equipment.id)
    eq.holder = t.destination
    eq.save()
    t.delete_instance()
    return True
