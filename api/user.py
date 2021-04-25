from db.models import User, History
from .exceptions import *


def create_user(id_: int, name: str, username: str, status: str = 'main_menu', role: str = 'user'):
    User.create(id=id_, name=name, username=username, status=status, role=role)


def get_user(id: int) -> dict:
    try:
        return User.get(id=id).get_as_dict()
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')


def delete_user(id: int):
    try:
        User.delete().where(User.id == id).execute()
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')


def get_user_by_username(username: str) -> dict:
    try:
        return User.get(username=username).get_as_dict()
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with username {username} does not exist')


def is_admin(id: int) -> bool:
    try:
        return User.get(id=id).role == 'admin'
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')


def is_exists(id: int) -> bool:
    try:
        User.get(id=id)
    except User.DoesNotExist:
        return False
    return True


def is_verified(id: int) -> bool:
    try:
        return User.get(id=id).role in ['member', 'admin']
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')


def verify_user(id: int) -> bool:
    try:
        u = User.get(id=id)
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')
    u.role = 'member'
    u.save()
    return True


def get_user_equipment(id: int) -> list:
    res = []
    try:
        u = User.get(id=id)
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')
    for eq in u.equipment:
        pick_date = History.select().where(History.equipment == eq).order_by(History.id.desc()).get().date.date()
        res.append({'id': eq.id, 'name': eq.name, 'picked': pick_date})
    return res


def get_admin_list() -> list:
    return [admin.get_as_dict() for admin in User.select().where(User.role == 'admin')]


def change_username(user_id: int, new_username: str):
    try:
        user = User.get(id=user_id)
    except User.DoesNotExist:
        raise UserDoesNotExist(f'User with id {id} does not exist')
    user.username = new_username
    user.save()
