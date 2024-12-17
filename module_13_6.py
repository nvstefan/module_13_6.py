# Домашнее задание по теме "Инлайн клавиатуры".

# Задача "Ещё больше выбора":

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = "Token"
bot = Bot(token= api)
dp = Dispatcher(bot, storage= MemoryStorage())

# Создаем клавиатуры

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ]
    ], resize_keyboard=True
)

inline_kb1 = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="Calories")
inline_kb2 = InlineKeyboardButton(text="Формулы расчёта", callback_data="Formulas")
kb = InlineKeyboardMarkup(resize_keyboard=True).row(inline_kb1, inline_kb2)



class UserState(StatesGroup):
    sex = State()
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands= 'start')
async def send_welcome(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup= start_menu)

@dp.message_handler(text= 'Информация')
async def send_information(message):
    await message.answer("Информация о боте")

@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выбери опцию: ", reply_markup=kb)

@dp.callback_query_handler(text="Formulas")
async def get_formulas(call):
    await call.message.answer('Для мужчин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст + 5,\n '
                              'Для женщин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст - 161')
    await call.answer()

@dp.callback_query_handler(text='Calories', state=None)
async def sex_form(call):
    await call.message.answer('Введите свой пол: ')
    await UserState.sex.set()
    await call.answer()


@dp.message_handler(state=UserState.sex)
async def set_age(message: types.Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await message.reply('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    # Получаем данные из состояния
    sex = str(data['sex'])
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    # Используем упрощенную формулу Миффлина - Сан Жеора для расчета нормы калорий
    if sex == 'мужской':
        calories = 10 * weight + 6.25 * growth - 5 * age + 5  # Для мужчин
    elif sex == 'женский':
        calories = 10 * weight + 6.25 * growth - 5 * age - 161 # Для женщин

    await message.answer(f'Ваша норма калорий: {calories:.2f}')
    await state.finish()

@dp.message_handler()
async def all_message(message):
    await message.answer('Привет! Введите команду /start, чтобы начать общение')




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)