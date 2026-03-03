from aiogram.fsm.state import StatesGroup, State

class StartStates(StatesGroup):
    choose_lang = State()
    sub_check = State()

class OrderStates(StatesGroup):
    district = State()
    address = State()
    kg = State()
    location = State()

    receiver_name = State()
    receiver_phone = State()
    passport_front = State()
    passport_back = State()

    banned_confirm = State()
    items_list_photo = State()

    contact = State()

    payment_choose = State()
    payment_screenshot = State()