from peewee import *
from playhouse.shortcuts import ReconnectMixin

from Package.customutils import load_config, datetime_local_now

config = load_config()


class DB(ReconnectMixin, MySQLDatabase):
    pass


base = DB(
    database=config.db.database,
    user=config.db.user,
    password=config.db.password,
    host="localhost",
    port=3306,
    charset="utf8mb4",
)


class BaseModel(Model):
    class Meta:
        database = base


class User(BaseModel):
    cid = BigIntegerField(unique=True)
    name = CharField()
    username = CharField(null=True)
    phone = BigIntegerField()
    status = IntegerField(default=0)
    latitude = FloatField(default=0)
    longitude = FloatField(default=0)
    registered = DateTimeField(default=datetime_local_now)


class Place(BaseModel):
    pid = BigIntegerField(unique=True)
    name = CharField()
    address = CharField()
    description = CharField()
    category = CharField()
    latitude = FloatField(default=0)
    longitude = FloatField(default=0)
    image_url = CharField(null=True)
    rating = FloatField(default=0)
    created_at = DateTimeField(default=datetime_local_now)
    updated_at = DateTimeField(default=datetime_local_now)


class Favorite(BaseModel):
    id = IntegerField(unique=True)
    user_id = ForeignKeyField(User, backref='favorites')
    place_id = ForeignKeyField(Place, backref='favorites')
    added_at = DateTimeField(default=datetime_local_now)


class ReviewLink(BaseModel):
    place = ForeignKeyField(Place, backref='review_links')
    url = CharField()


def connect():
    base.connect()
    base.create_tables(
        [
            User,
            Place,
            ReviewLink
        ]
    )


def disconnect():
    base.close()
