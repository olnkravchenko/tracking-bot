from db.models import Transfer, User, Equipment
from api import history
from .exceptions import *


def create_transfer(equipment_id: int, source_id: int, destination_id: int):
    try:
        source = User.get(id=source_id)
    except User.DoesNotExist:
        raise UserDoesNotExists(f'User with id {source_id} does not exists')
    try:
        destination = User.get(id=destination_id)
    except User.DoesNotExist:
        raise UserDoesNotExists(f'User with id {destination_id} does not exists')
    try:
        Transfer.create(equipment=Equipment.get(id=equipment_id), source=source, destination=destination)
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExists(f'Equipment with id {equipment_id} does not exists')


def get_transfer(id: int) -> dict:
    try:
        return Transfer.get(id=id).get_as_dict()
    except Transfer.DoesNotExist:
        raise TransferDoesNotExists(f'Transfer with id {id} does not exists')


def get_active_transfers(user_id: int) -> list:
    try:
        return [t.get_as_dict() for t in Transfer.select().where(Transfer.destination == User.get(id=user_id))]
    except User.DoesNotExist:
        raise UserDoesNotExists(f'User with id {user_id} does not exists')


def verify_transfer(id: int) -> bool:
    try:
        t = Transfer.get(id=id)
    except Transfer.DoesNotExist:
        raise TransferDoesNotExists(f'Transfer with id {id} does not exists')
    history.add_row(equipment_id=t.equipment.id, source_id=t.source.id, destination_id=t.destination.id)
    eq = Equipment.get(id=t.equipment.id)
    eq.holder = t.destination
    eq.save()
    t.delete_instance()
    return True


def delete_transfer(id: int):
    try:
        Transfer.delete().where(Transfer.id == id).execute()
    except Transfer.DoesNotExist:
        raise TransferDoesNotExists(f'Transfer with id {id} does not exists')


def get_transfer_by_equipment_id(id: int) -> dict:
    try:
        eq = Equipment.get(id=id)
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExists(f'Equipment with id {id} does not exists')
    try:
        transfer = Transfer.get(equipment=eq)
    except Transfer.DoesNotExist:
        raise TransferDoesNotExists(f'Transfer with equipment with id {id} does not exists')
    return transfer.get_as_dict()
