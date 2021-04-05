from db.models import Category
from .exceptions import *


def create_category(name: str):
    cat = Category.create(name=name)


def delete_category(id: int) -> bool:
    Category.delete().where(Category.id == id)
    return True


def get_category_equipment(id: int) -> list:
    try:
        return [eq.get_as_dict() for eq in Category.get(id=id).equipment]
    except Category.DoesNotExist:
        raise CategoryDoesNotExist(f'Category with id {id} does not exist')


def get_all_categories() -> list:
    return [cat.get_as_dict() for cat in Category.select()]
