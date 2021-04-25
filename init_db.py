from db.models import *
from os import listdir, remove
# if 'db.sqlite3' in listdir():
#     remove('db.sqlite3')

# db.create_tables([User, Equipment, Category, History, Transfer])

# #Create categories here
# data_source = ['cameras','light','audio','lenses','tripods','battery','power','broadcast']
# for name in data_source:
#     Category.create(name=name)

# User.create(id=1, name='Штаб', username='Штаб', role='Штаб')

db.create_tables([User, Equipment, Category, History, Transfer])
User.create(id=1, name='Штаб', username='Штаб', status='Штаб', role='Штаб')
