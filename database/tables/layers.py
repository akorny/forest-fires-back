from datetime import date
from peewee import Model, CharField, DateTimeField
from database.db import database

class Layers(Model):
    datetime = DateTimeField()
    type = CharField(10)
    method = CharField(3)
    hex = CharField(10)

    class Meta:
        database = database

database.create_tables([Layers])