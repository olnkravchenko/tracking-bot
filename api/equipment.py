from db.models import Equipment, Category
from .qr_code import new_qr_code
from string import ascii_letters
from random import choice


def add_equipment(
    category_id: int,
    name: str,
    owner: int = 1,
    description: str = "",
    qr_code_version: int = 2,
):
    control = "".join([choice(ascii_letters) for _ in range(6)])
    eq = Equipment.create(
        name=name,
        holder=owner,
        owner=owner,
        description=description,
        category=Category.get(id=category_id),
        control=control,
    )
    filename = f"{eq.id}_qr.png"
    new_qr_code(
        data_=f"{eq.id} {control}", ver=qr_code_version, size=qr_code_version, filename=filename
    )
    return filename


def get_equipment(id: int) -> dict:
    eq = Equipment.get(id=id)
    return eq.get_as_dict()


def get_holder(id: int) -> dict:
    eq = Equipment.get(id=id)
    return eq.holder.get_as_dict()


def get_owner(id: int) -> dict:
    eq = Equipment.get(id=id)
    return eq.owner.get_as_dict()


def delete_equipment(id: int) -> bool:
    Equipment.delete().where(Equipment.id == id)
    return True


def change_equipment_description(id: int, new_description: str) -> bool:
    eq = Equipment.get(id=id)
    eq.description = new_description
    eq.save()
    return True


def change_equipment_category(id: int, new_category: int) -> bool:
    eq = Equipment.get(id=id)
    eq.category = Category.get(id=new_category)
    eq.save()
    return True


def validate_control_sum(id: int, sum: str) -> bool:
    eq = Equipment.get(id=id)
    return sum == eq.control
