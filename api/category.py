from db.models import Category


def create_category(name: str):
    cat = Category.create(name=name)


def delete_category(id: int) -> bool:
    Category.delete().where(Category.id == id)
    return True


def get_category_equipment(id: int) -> list:
    res = []
    for eq in Category.get(id=id).equipment:
        res.append(eq.get_as_dict())
    return res


def get_all_categories() -> list:
    return [cat.get_as_dict() for cat in Category.select()]
