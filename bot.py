import asyncio
import os
import re

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    FSInputFile
)

from export_excel import export_users_to_excel
from database import (
    create_database,
    add_user,
    add_receipt,
    user_exists,
    get_user_profile
)
from states import Register


load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    1589354615,
    8561874694
]


bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# КЛАВИАТУРЫ
# =========================


contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Поділитися номером телефону",
                request_contact=True
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
city_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏙️ Біла Церква"),
            KeyboardButton(text="🏙️ Сквира")
        ],
        [
            KeyboardButton(text="🏙️ Тетіїв"),
            KeyboardButton(text="🏙️ Узин")
        ],
        [
            KeyboardButton(text="🏙️ Миронівка")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🧾 Додати чек"),
            KeyboardButton(text="👤 Мій профіль")
        ],
        [
            KeyboardButton(text="📊 Експорт Excel")
        ]
    ],
    resize_keyboard=True
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🚀 Розпочати")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.clear()

    if await user_exists(message.from_user.id):

        await message.answer(
            "👋 <b>Вітаємо знову!</b>\n\n"
            "Ви вже зареєстровані у програмі лояльності ❤️\n\n"
            "Оберіть потрібну дію:",
            parse_mode="HTML",
            reply_markup=main_keyboard
        )
        return

    await message.answer(
        "🏡 <b>Ласкаво просимо до магазину «Домовичок»!</b>\n\n"
        "💚 Ми раді вітати Вас у нашій програмі лояльності.\n\n"
        "Натисніть кнопку <b>«🚀 Розпочати»</b>, щоб пройти реєстрацію.",
        parse_mode="HTML",
        reply_markup=start_keyboard
    )


@dp.message(F.text == "🚀 Розпочати")
async def start_registration(message: Message, state: FSMContext):

    await message.answer(
        "🏡 <b>Реєстрація учасника програми лояльності</b>\n\n"
        "✍️ Для початку введіть Ваше ім'я та прізвище.\n\n"
        "<b>Приклад:</b>\n"
        "Іван Петренко",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.set_state(Register.waiting_full_name)


# =========================
# ИМЯ
# =========================


@dp.message(Register.waiting_full_name)
async def get_name(message: Message, state: FSMContext):

    full_name = message.text.strip()

    if len(full_name.split()) < 2:

        await message.answer(
            "❌ Введіть ім'я та прізвище.\n\n"
            "Наприклад:\n"
            "Іван Петренко"
        )

        return


    await state.update_data(
        full_name=full_name
    )


    await message.answer(
        "✅ Дякуємо!\n\n"
        "Тепер поділіться номером телефону.",
        reply_markup=contact_keyboard
    )


    await state.set_state(
        Register.waiting_phone
    )



# =========================
# ТЕЛЕФОН
# =========================


@dp.message(Register.waiting_phone, F.contact)
async def get_phone(message: Message, state: FSMContext):

    await state.update_data(
        phone=message.contact.phone_number
    )

    await message.answer(
        "🏙️ Оберіть Ваше місто:",
        reply_markup=city_keyboard
    )

    await state.set_state(
        Register.waiting_city
    )


@dp.message(Register.waiting_city)
async def get_city(message: Message, state: FSMContext):

    city = message.text.strip()

    cities = [
        "🏙️ Біла Церква",
        "🏙️ Сквира",
        "🏙️ Тетіїв",
        "🏙️ Узин",
        "🏙️ Миронівка"
    ]

    if city not in cities:
        await message.answer(
            "❌ Оберіть місто кнопкою."
        )
        return


    await state.update_data(
        city=city
    )


    await message.answer(
        "🎂 Введіть Вашу дату народження.\n\n"
        "📅 Формат:\n"
        "<b>31.12.2000</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )


    await state.set_state(
        Register.waiting_birth_date
    )



# =========================
# ДАТА
# =========================


@dp.message(Register.waiting_birth_date)
async def get_birth_date(message: Message, state: FSMContext):

    birth_date = message.text.strip()


    if not re.fullmatch(
        r"\d{2}\.\d{2}\.\d{4}",
        birth_date
    ):

        await message.answer(
            "❌ Невірний формат.\n\n"
            "Приклад:\n"
            "31.12.2000"
        )

        return


    data = await state.get_data()


    await add_user(
    full_name=data["full_name"],
    phone=data["phone"],
    city=data["city"],
    birth_date=birth_date,
    username=message.from_user.username,
    telegram_id=message.from_user.id
)


    await state.clear()


    await message.answer(
    "<b>✅ Реєстрацію завершено!</b>\n\n"
    f"💚 Дякуємо, <b>{data['full_name']}</b>!\n\n"
    "Ласкаво просимо до програми лояльності магазину <b>Домовичок</b>. 🛒\n\n"
    "💳 Ваша бонусна картка буде створена найближчим часом.\n"
    "Після її активації Ви зможете накопичувати бонуси, отримувати бонусні бали за покупки та користуватися всіма перевагами програми лояльності.\n\n"
    "Бажаємо Вам приємних покупок! 💚",
    parse_mode="HTML",
    reply_markup=main_keyboard
)



# =========================
# ДОБАВИТЬ ЧЕК
# =========================


@dp.message(F.text == "🧾 Додати чек")
async def start_receipt(message: Message, state: FSMContext):

    await message.answer(
        "🧾 <b>Додавання чека</b>\n\n"
        "Введіть номер чека.\n\n"
        "Формат:\n"
        "№1234567890",
        parse_mode="HTML"
    )


    await state.set_state(
        Register.waiting_receipt
    )



@dp.message(Register.waiting_receipt)
async def process_receipt(message: Message, state: FSMContext):

    receipt = message.text.strip()


    if receipt.startswith("№"):
        receipt = receipt[1:]


    if not re.fullmatch(
        r"\d{10}",
        receipt
    ):

        await message.answer(
            "❌ Номер чека повинен містити 10 цифр."
        )

        return



    await add_receipt(
        message.from_user.id,
        receipt
    )


    await message.answer(
        "✅ Чек прийнято!\n\n"
        "Очікуйте перевірки."
    )


    await state.clear()



# =========================
# ЭКСПОРТ EXCEL
# =========================


@dp.message(F.text == "📊 Експорт Excel")
async def export_excel(message: Message):


    if message.from_user.id not in ADMIN_IDS:

        await message.answer(
            "❌ Немає доступу."
        )

        return



    export_users_to_excel()


    file = FSInputFile(
        "clients.xlsx"
    )


    await message.answer_document(
        file,
        caption="📊 База клієнтів готова!"
    )



# =========================
# PROFILE
# =========================

@dp.message(F.text == "👤 Мій профіль")
async def profile(message: Message):

    user = await get_user_profile(message.from_user.id)

    if user is None:
        await message.answer(
            "❌ Ваш профіль не знайдено."
        )
        return

    full_name, phone, city, birth_date, bonus_balance = user

    await message.answer(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>МІЙ ПРОФІЛЬ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"

        f"🧑 <b>ПІБ:</b> {full_name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"🏙️ <b>Місто:</b> {city}\n"
        f"🎂 <b>Дата народження:</b> {birth_date}\n\n"

        "━━━━━━━━━━━━━━━━━━━━\n"
    
        "💳 <b>Статус картки:</b> 🟢 Активна\n"
        "━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )



# =========================
# ЗАПУСК
# =========================


async def main():

    await create_database()

    await dp.start_polling(
        bot
    )



if __name__ == "__main__":
    asyncio.run(main())