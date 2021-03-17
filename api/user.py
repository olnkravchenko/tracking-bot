from db.models import User, History


def create_user(name: str, username: str, status: str = 'main_menu', role: str = 'user') -> dict:
    u = User.create(name=name, username=username, status=status, role=role)
    return u.get_as_dict()


def get_user(id: int) -> dict:
    u = User.get(id=id)
    return u.get_as_dict()


def get_user_by_username(username: str) -> dict:
    u = User.get(username=username)
    return u.get_as_dict()


def is_admin(id: int) -> bool:
    u = User.get(id=id)
    return u.role == 'admin'


def is_verified(id: int) -> bool:
    u = User.get(id=id)
    return u.role in ['member', 'admin']


def verify_user(id: int) -> bool:
    u = User.get(id=id)
    u.role = 'member'
    u.save()
    return True


def get_user_equipment(id: int) -> list:
    res = []
    u = User.get(id=id)
    for eq in u.equipment:
        pick_date = History.select().where(History.equipment == eq).order_by(History.id.desc()).get().date.date()
        res.append({'id': eq.id, 'name': eq.name, 'picked': pick_date})
    return res


def set_user_status(id: int, status: str) -> str:
    u = User.get(id=id)
    u.status = status
    u.save()
    return status


def get_user_status(id: int) -> str:
    u = User.get(id=id)
    return u.status


def get_admin_list() -> list:
    res = []
    for admin in User.select().where(User.role == 'admin'):
        res.append(admin.get_as_dict())
    return res
