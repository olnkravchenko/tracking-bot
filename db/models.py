from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('db.sqlite3')
db.pragma('foreign_keys', 1, permanent=True)


class BaseModel(Model):
    def get_as_dict(self):
        return model_to_dict(self)

    class Meta:
        database = db


class User(BaseModel):
    name = TextField()
    username = TextField(null=True)
    role = TextField()


class Category(BaseModel):
    name = TextField()


class Equipment(BaseModel):
    name = TextField()
    holder = ForeignKeyField(User, backref='equipment', on_delete='CASCADE')
    owner = ForeignKeyField(User, backref='owned_equipment', \
        on_delete='CASCADE')
    category = ForeignKeyField(Category, backref='equipment', \
        on_delete='CASCADE')
    description = TextField()
    control = TextField()


class History(BaseModel):
    source = ForeignKeyField(User, backref='source_transfers_history', \
        on_delete='CASCADE')
    destination = ForeignKeyField(User, backref='destination_transfers_history', on_delete='CASCADE')
    equipment = ForeignKeyField(Equipment, backref='transfers_history', \
        on_delete='CASCADE')
    date = DateTimeField()


class Transfer(BaseModel):
    source = ForeignKeyField(User, backref='source_transfers', \
        on_delete='CASCADE')
    destination = ForeignKeyField(User, backref='destination_transfers', \
        on_delete='CASCADE')
    equipment = ForeignKeyField(Equipment, backref='transfers', \
        on_delete='CASCADE')
