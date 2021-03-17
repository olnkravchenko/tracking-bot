from db.models import *
from os import listdir, remove

if 'db.sqlite3' in listdir():
    remove('db/db.sqlite3')

db.create_tables([User, Equipment, Category, History, Transfer])
User.create(id=1, name='Штаб', username='Штаб', status='Штаб', role='Штаб')
