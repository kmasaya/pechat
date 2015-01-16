#!/usr/bin/python3

import peewee
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_filename = os.path.join(BASE_DIR, 'pechat.sqlite3')
db = peewee.SqliteDatabase(db_filename, check_same_thread=False)


class User(peewee.Model):
    username = peewee.CharField(max_length=16, unique=True)
    password = peewee.CharField(max_length=16)
    is_active = peewee.BooleanField(default=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        order_by = ('username',)


class Site(peewee.Model):
    user = peewee.ForeignKeyField(User)
    site_id = peewee.CharField(max_length=16, unique=True)
    title = peewee.CharField(default='')
    body = peewee.TextField(default='')
    is_active = peewee.BooleanField(default=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        order_by = ('title',)


class Comment(peewee.Model):
    site = peewee.ForeignKeyField(Site)
    nickname = peewee.CharField(max_length=16)
    message = peewee.CharField(max_length=128)
    is_active = peewee.BooleanField(default=True)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        order_by = ('site', 'created_at')


class Session(peewee.Model):
    user = peewee.ForeignKeyField(User)
    sid = peewee.CharField(max_length=512)
    accessed_at = peewee.DateTimeField(default=datetime.datetime.now)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


if __name__ == '__main__':
    if not os.path.exists(db_filename):
        User.create_table()
        Site.create_table()
        Comment.create_table()
        Session.create_table()

        User.create(
            username='admin',
            password='admin',
        )
