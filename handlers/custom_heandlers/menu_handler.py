# import re
#
# from telebot.types import Message
#
# from database.models import User, Menu, Product, DishItems, Dish
# from keyboards.inline.menu_inline import menu_markup, dish_or_product_markup, dish_time_of_day
# from loader import bot
# from states.menu_info import MenuState
#
#
# def get_dishes(message: Message) -> dict:
#     with bot.retrieve_data(message.chat.id, message.chat.id) as menu_data:
#         dishes_data = menu_data.get("menu", None)
#         if dishes_data is not None:
#             return dishes_data
#         cur_user = User.get_or_none(User.user_id == message.chat.id)
#         menu: Menu = Menu.get_or_none(Menu.user == cur_user)
#         dishes = menu.dishes.select().where(Dish.menu == menu)
#         dishes_data = {index + 1: dish for index, dish in
#                        enumerate([dish.name for dish in dishes])}
#         menu_data["menu"] = dishes_data
#
#     return dishes_data
#
#
# def set_dishes(message: Message, cur_text, new_text=None, delete_product=False,
#                new_product=False):
#     """ Функция для обновления кеша """
#     with bot.retrieve_data(message.chat.id, message.chat.id) as menu_data:
#         menu = menu_data.get("menu", None)
#         if menu:
#             if new_product:
#                 menu[cur_text] = new_text
#                 return
#             values_list = list(menu.values())
#             if cur_text in values_list:
#                 if delete_product:
#                     cur_key = values_list.index(cur_text) + 1
#                     menu.pop(cur_key)
#                     new_menu = menu.copy()
#                     for key, value in menu.items():
#                         if key >= cur_key:
#                             if key < len(new_menu):
#                                 new_menu[key] = new_menu[key + 1]
#                             else:
#                                 new_menu.pop(key)
#                     return
#                 menu[values_list.index(cur_text) + 1] = new_text
#
#
# def get_grouped_menu(dishes: dict):
#     if len(dishes):
#         text = "Ваше меню:\n"
#         breakfast_dishes = [f"{index} - {dish}" for index, dish in dishes_data.items()]
#         "\n".join(
#             [f"{index} - {dish}" for index, dish in dishes_data.items()]
#     else:
#         return None
#
#
# @bot.message_handler(commands=["menu"])
# def get_command_menu(message: Message) -> None:
#     """ Хендлер, ловит команду menu """
#     cur_user = User.get_or_none(User.user_id == message.from_user.id)
#     if cur_user is None:
#         bot.reply_to(message, "Вы не зарегистрированы в системе. Напишите /start")
#         return
#     menu: Menu = Menu.get_or_none(Menu.user == cur_user)
#     dishes = menu.dishes.select().where(Dish.menu == menu).first()
#     if dishes is None:
#         bot.send_message(message.from_user.id, "У вас пустое меню. Чтобы добавить продукт, нажмите на кнопку.",
#                          reply_markup=menu_markup(is_dishes=False))
#     else:
#         bot.send_message(message.from_user.id, "Что вы хотите сделать? Нажмите на кнопку внизу.",
#                          reply_markup=menu_markup())
#     bot.set_state(message.from_user.id, MenuState.print_menu)
#
#
# @bot.callback_query_handler(func=None, state=MenuState.print_menu)
# def check_menu(call) -> None:
#     """ Обработчик Inline кнопок для направления пользователя по
#     состояниям в зависимости от выбранной кнопки.
#     """
#     if call.data == "add_dish":
#         bot.send_message(call.message.chat.id, "Хорошо, выберите, когда нужно готовить это блюдо",
#                          reply_markup=dish_time_of_day())
#         bot.set_state(call.message.chat.id, MenuState.choose_time)
#     else:
#         if call.data == "view_dish":
#             dishes_data = get_dishes(call.message)
#             with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as menu_data:
#                 menu_data["menu"] = dishes_data
#             if len(dishes_data):
#                 bot.send_message(call.message.chat.id, "Ваше меню:\n" + "\n".join(
#                     [f"{index} - {dish}" for index, dish in dishes_data.items()]
#                 ), reply_markup=menu_markup())
#             else:
#                 bot.send_message(call.message.chat.id, "У вас пустое меню. Чтобы добавить блюдо, нажмите на кнопку.",
#                                  reply_markup=menu_markup(is_dishes=False))
#         else:
#             dishes = get_dishes(call.message)
#             if dishes:
#                 bot.send_message(call.message.chat.id, "Ваше меню:\n" + "\n".join(
#                     [f"{index} - {dish}" for index, dish in dishes.items()]
#                 ))
#             else:
#                 bot.send_message(call.message.chat.id, "У вас пустое меню. Чтобы добавить блюдо, нажмите на кнопку.",
#                                  reply_markup=menu_markup(is_dishes=False))
#                 return
#         if call.data == "update_dish":
#             bot.send_message(call.message.chat.id, "Отлично, напишите номер блюда, которое вы хотите изменить.")
#             bot.set_state(call.message.chat.id, MenuState.update_dish)
#         elif call.data == "delete_dish":
#             bot.send_message(call.message.chat.id, "Введите номер блюда, которое надо удалить")
#             bot.set_state(call.message.chat.id, MenuState.delete_dish)
#
#
# @bot.callback_query_handler(func=None, state=MenuState.choose_time)
# def choose_time(call) -> None:
#     with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as menu_data:
#         menu_data["result_time"] = call.data
#     bot.send_message(call.message.chat.id, "Отлично, теперь напишите название блюда")
#     bot.set_state(call.message.chat.id, MenuState.add_dish)
#
#
# @bot.message_handler(state=MenuState.add_dish)
# def add_dish(message: Message) -> None:
#     menu = Menu.get_or_none(Menu.user == message.from_user.id)
#     try:
#         with bot.retrieve_data(message.chat.id, message.chat.id) as menu_data:
#             result_time = menu_data["result_time"]
#         dish = Dish.create(name=message.text, menu=menu, time_of_day=result_time)
#         bot.send_message(message.from_user.id, f'Блюдо "{dish.name}" успешно добавлено в ваше меню. '
#                                                f"Напишите продукты, которые нужны для приготовления этого блюда.")
#         bot.set_state(message.from_user.id, MenuState.add_product)
#     except Exception:
#         dish = Dish.get(Dish.name == message.text)
#         bot.send_message(message.from_user.id, "Это блюдо уже есть в вашем меню! Введите еще раз")
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as menu_data:
#         menu_data["new_dish"] = dish.id
#
#
# @bot.message_handler(state=MenuState.add_product)
# def app_product_to_dish(message: Message) -> None:
#     products = re.findall(r"[\w']+", message.text)
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as menu_data:
#         dish_id = menu_data.get("new_dish")
#         dish = Dish.get_by_id(dish_id)
#     for product in products:
#         try:
#             product_obj = Product.create(name=product)
#         except Exception:
#             product_obj = Product.get(Product.name == product)
#         DishItems.create(dish=dish_id, product=product_obj)
#     bot.send_message(message.from_user.id, "Хорошо, блюдо с такими продуктами создано.",
#                      reply_markup=menu_markup())
#     set_dishes(message, len(get_dishes(message)) + 1, dish.name, new_product=True)
#     bot.set_state(message.from_user.id, MenuState.print_menu)
#
#
# @bot.message_handler(state=MenuState.update_dish)
# def check_action(message: Message) -> None:
#     dishes = get_dishes(message)
#     if message.text.isdigit():
#         dish_name = dishes.get(int(message.text), None)
#     else:
#         dish_name = list(dishes.values())[list(dishes.values()).index(message.text)]
#     if dish_name is None:
#         bot.send_message(message.from_user.id, "Такое блюдо не найдено! Попробуйте еще раз")
#         return
#
#     dish = Dish.select().where(Dish.name == dish_name).first()
#
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as menu_data:
#         menu_data["refreshing_dish"] = dish.id
#         bot.send_message(message.from_user.id, "Вы хотите изменить имя блюда или продукты в нем? Выберите кнопку",
#                          reply_markup=dish_or_product_markup())
#         bot.set_state(message.from_user.id, MenuState.dish_or_product)
#
#
# @bot.callback_query_handler(func=None, state=MenuState.dish_or_product)
# def dish_or_product(call):
#     with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as menu_data:
#         dish_id = menu_data["refreshing_dish"]
#         dish = Dish.get_by_id(dish_id)
#     if call.data == "dish":
#         bot.send_message(call.message.chat.id, f'Хорошо, введите новое название блюда, вместо "{dish.name}"')
#         bot.set_state(call.message.chat.id, MenuState.update_dish_name)
#     elif call.data == "products":
#         cur_products = '\n'.join([dish_items.product.name for dish_items in dish.products])
#         bot.send_message(call.message.chat.id, f"Существующие продукты для {dish.name}:\n{cur_products}")
#         bot.send_message(call.message.chat.id, f'Напишите новые продукты для "{dish.name}"')
#         bot.set_state(call.message.chat.id, MenuState.update_products)
#
#
# @bot.message_handler(state=MenuState.update_dish_name)
# def update_dish_name(message: Message) -> None:
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as menu_data:
#         dish_id = menu_data["refreshing_dish"]
#         dish = Dish.get_by_id(dish_id)
#         dish_name = dish.name
#         dish.name = message.text
#         dish.save()
#         set_dishes(message, dish_name, message.text)
#         bot.send_message(message.from_user.id, f"Название блюда {dish_name} успешно обновлено на {message.text}",
#                          reply_markup=menu_markup())
#         bot.set_state(message.from_user.id, MenuState.print_menu)
#
#
# @bot.message_handler(state=MenuState.update_products)
# def update_products(message: Message) -> None:
#     with bot.retrieve_data(message.from_user.id, message.chat.id) as menu_data:
#         dish_id = menu_data["refreshing_dish"]
#         dish = Dish.get_by_id(dish_id)
#         products = re.findall(r"[\w']+", message.text)
#         cur_products = [dish_items for dish_items in dish.products]
#         delete_products = list()
#         for product in products:
#             try:
#                 product_obj = Product.create(name=product)
#                 DishItems.create(dish=dish_id, product=product_obj)
#             except Exception:
#                 product_obj = Product.get(Product.name == product)
#                 dish_items = DishItems.select().where(DishItems.dish == dish_id).first()
#                 delete_products.append(dish_items.product.name)
#                 dish_items.product = product_obj
#                 dish_items.save()
#         for cur_product in cur_products:
#             if cur_product.product.name not in delete_products:
#                 dish_items = DishItems.get_by_id(cur_product)
#                 dish_items.delete_instance()
#         bot.send_message(message.from_user.id, f"Хорошо, блюдо {dish.name} теперь содержит такие продукты:"
#                                                f" {', '.join(products)}",
#                          reply_markup=menu_markup())
#         bot.set_state(message.from_user.id, MenuState.print_menu)
#
#
# @bot.message_handler(state=MenuState.delete_dish)
# def delete_dish(message: Message) -> None:
#     dishes = get_dishes(message)
#     if message.text.isdigit():
#         dish_name = dishes.get(int(message.text), None)
#     else:
#         dish_name = list(dishes.values())[list(dishes.values()).index(message.text)]
#     if dish_name is None:
#         bot.send_message(message.from_user.id, "Такое блюдо не найдено! Попробуйте еще раз")
#         return
#
#     dish = Dish.select().where(Dish.name == dish_name).first()
#     dish_name = dish.name
#     dish.delete_instance(recursive=True)
#     set_dishes(message, dish_name, delete_product=True)
#     bot.send_message(message.from_user.id, f"Блюдо {dish_name} успешно удалено.",
#                      reply_markup=menu_markup())
#     bot.set_state(message.from_user.id, MenuState.print_menu)
#
# # Короче че на завтра:
# #
# # 1. Продумать структуру Юзер - Меню - Блюдо - Продукт  +
# # 2. Исправить соответственно код       +
# # 3. Сделать все обработчики reply кнопок   inline
# # 4. Насчет переноса базы данных - надо будет запустить этот код у ба, узнать
# # Телеграмм user parameters, перенести туда базу данных и заменить мои
# # параметры на ее.
#
# # 5. Сделать вывод по завтраку \ обеду \ ужину
# # 6. Настроить уведомления асинхронно
#
#
# # Базовые функции бота:
# # 1. Умеет брать блюда из базы данных и предлагать их в 8:00, 12:00 и 16:00
# # 2. Умеет каждую субботу планировать блюда на каждый день, выдавать только продукты
# # 3. Для развития: определять блюдо по продуктам и выдавать продукты для блюда
# # 4. Для развития: привязать стоимость продукта и выдавать инт. рецепты (стороннее API)
