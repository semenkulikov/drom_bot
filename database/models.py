# import peewee
#
# db = peewee.SqliteDatabase("database/database.db")
#
#
# class BaseModel(peewee.Model):
#     """ Базовая модель """
#     class Meta:
#         database = db
#
#
# class Product(BaseModel):
#     """ Класс-модель продукта """
#     name = peewee.CharField()
#     price = peewee.DecimalField(null=True)
#
#
# class User(BaseModel):
#     """ Класс-модель пользователя """
#     user_id = peewee.IntegerField(primary_key=True)
#     username = peewee.CharField()
#     first_name = peewee.CharField()
#     last_name = peewee.CharField(null=True)
#
#
# class Recipe(BaseModel):
#     """ Класс-модель рецепта """
#     products = peewee.ForeignKeyField(Product, backref="recipes")
#
#
# class Menu(BaseModel):
#     """ Класс-модель меню """
#     user = peewee.ForeignKeyField(User, backref="menu")
#
#
# class Dish(BaseModel):
#     name = peewee.CharField()
#     menu = peewee.ForeignKeyField(Menu, backref="dishes")
#     time_of_day = peewee.CharField()
#
#
# class DishItems(BaseModel):
#     dish = peewee.ForeignKeyField(Dish, backref="products")
#     product = peewee.ForeignKeyField(Product, backref="dishes")
#
#
# def create_models():
#     db.create_tables(BaseModel.__subclasses__())
