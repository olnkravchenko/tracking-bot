from db.models import Equipment, Category, User
from .qr_code import new_qr_code
from string import ascii_letters
from random import choice
from os import remove
from .exceptions import *


def add_equipment(
    category_id: int,
    name: str,
    owner: int = 1,
    description: str = "",
    qr_code_version: int = 2,
):
    control = "".join([choice(ascii_letters) for _ in range(6)])
    try:
        eq = Equipment.create(
            name=name,
            holder=User.get(id=owner),
            owner=User.get(id=owner),
            description=description,
            category=Category.get(id=category_id),
            control=control,
        )
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {owner} does not exist')
    except Category.DoesNotExist:
        raise CategoryDoesNotExist(f'Category with id {category_id} does not exist')
    filename = f'{eq.id}_qr.png'
    new_qr_code(
        data_=f'{eq.id} {control}', ver=qr_code_version, size=qr_code_version, filename=filename
    )
    return filename


def get_equipment(id: int) -> dict:
    try:
        return Equipment.get(id=id).get_as_dict()
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')


def get_holder(id: int) -> dict:
    try:
        return Equipment.get(id=id).holder.get_as_dict()
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')


def get_owner(id: int) -> dict:
    try:
        return Equipment.get(id=id).owner.get_as_dict()
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')


def delete_equipment(id: int):
    try:
        Equipment.delete().where(Equipment.id == id).execute()
        remove(f'./images/qr_codes/{id}_qr.png')
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')


def change_equipment_description(id: int, new_description: str) -> bool:
    try:
        eq = Equipment.get(id=id)
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')
    eq.description = new_description
    eq.save()
    return True


def change_equipment_category(id: int, new_category: int) -> bool:
    try:
        eq = Equipment.get(id=id)
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')
    eq.category = Category.get(id=new_category)
    eq.save()
    return True


def validate_control_sum(id: int, sum: str) -> bool:
    try:
        return sum == Equipment.get(id=id).control
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with id {id} does not exist')


def get_equipment_by_holder(id: int) -> list:
    try:
        holder = User.get(id=id)
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')
    return [eq.get_as_dict() for eq in holder.equipment]


def get_equipment_by_name(name: str) -> dict:
    try:
        return Equipment.get(name=name).get_as_dict()
    except Equipment.DoesNotExist:
        raise EquipmentDoesNotExist(f'Equipment with name {name} does not exist')
