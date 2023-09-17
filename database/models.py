import peewee

db = peewee.SqliteDatabase("database/database.db")


class BaseModel(peewee.Model):
    """ Базовая модель """
    class Meta:
        database = db


class Interval(BaseModel):
    """ Класс-модель интервал """
    interval = peewee.IntegerField()


class Account(BaseModel):
    """ Класс-модель аккаунта """
    login = peewee.CharField()
    password = peewee.CharField()


class MailingTime(BaseModel):
    start_time = peewee.TimeField()
    end_time = peewee.TimeField()


def create_models():
    db.create_tables(BaseModel.__subclasses__())


# Что нужно сохранять:
# Интервал рассылки
# Время рассылки
# Аккаунты (логин \ пароль)
