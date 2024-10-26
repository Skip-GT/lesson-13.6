from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

api = ""
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())


kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text = 'Расчитать') ],
        [
            KeyboardButton(text = 'Информация')
        ]
    ], resize_keyboard = True
)


in_kb = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data = 'calories')
button_formulas = InlineKeyboardButton(text = 'Формулы расчёта', callback_data = 'formulas')
in_kb.add(button_calories, button_formulas)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup = kb)


@dp.message_handler(text = 'Расчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup = in_kb)


@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer("Формула Миффлина-Сан Жеора: 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) + 5")
    await call.answer()


@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await UserState.age.set()
    await call.message.answer("Введите свой возраст:")
    await call.answer()


@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await UserState.growth.set()
    await message.answer("Введите свой рост (в сантиметрах):")


@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = message.text)
    await UserState.weight.set()
    await message.answer("Введите свой вес (в килограммах):")


@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight = message.text)
    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f"Ваша норма калорий: {calories} ккал.")
    await state.finish()


@dp.message_handler(text = 'Информация')
async def info_mes(message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.\n"
                         "Введите команду /start, чтобы начать общение.")


@dp.message_handler()
async def all_massages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
