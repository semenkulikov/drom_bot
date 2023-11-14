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


class Proxy(BaseModel):
    """ Класс-модель для прокси """
    proxy = peewee.CharField()
    account = peewee.ForeignKeyField(Account)


class MailingTime(BaseModel):
    start_time = peewee.TimeField()
    end_time = peewee.TimeField()


class Answer(BaseModel):
    """ Класс-модель для объявления """
    text = peewee.CharField(unique=True)
    active = peewee.BooleanField(default=True)


def create_models():
    db.create_tables(BaseModel.__subclasses__())


def delete_answers():
    Answer.delete().execute()
