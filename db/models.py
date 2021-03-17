from peewee import *
from playhouse.shortcuts import model_to_dict

db = SqliteDatabase('db.sqlite3')


class BaseModel(Model):
    def get_as_dict(self):
        return model_to_dict(self)

    class Meta:
        database = db


class User(BaseModel):
    name = TextField()
    username = TextField()
    status = TextField()
    role = TextField()


class Category(BaseModel):
    name = TextField()


class Equipment(BaseModel):
    name = TextField()
    holder = ForeignKeyField(User, backref='equipment')
    category = ForeignKeyField(Category, backref='equipment')
    description = TextField()
    control = TextField()


class History(BaseModel):
    source = ForeignKeyField(User, backref='source_transfers_history')
    destination = ForeignKeyField(User, backref='destination_transfers_history')
    equipment = ForeignKeyField(Equipment, backref='transfers_history')
    date = DateTimeField()


class Transfer(BaseModel):
    source = ForeignKeyField(User, backref='source_transfers')
    destination = ForeignKeyField(User, backref='destination_transfers')
    equipment = ForeignKeyField(Equipment, backref='transfers')
