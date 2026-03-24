import asyncio
import logging

TOKEN = "8380971426:AAFpkVg0N5izPtHIan1F9ueJuLXuFVH4YIw"  # <-- вставь сюда твой новый токен
ADMIN_CHAT_ID = -5204529452

# временное хранилище данных пользователей
users = {}

async def main():
    print("BOT STARTED")  # лог для проверки запуска

    # ------------------ ЛЕНИВЫЙ ИМПОРТ ------------------
    from aiogram import Bot, Dispatcher, F
    from aiogram.types import Message
    from aiogram.filters import CommandStart
    from aiogram.client.default import DefaultBotProperties

    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # ------------------ HANDLERS ------------------
    @dp.message(CommandStart())
    async def start(message: Message):
        users[message.from_user.id] = {"demos": []}
        await message.answer(
            "Привет! Это A&R-бот лейбла Инсайт Мьюзик 👋\n\n"
            "Короткие правила:\n"
            "1. Необходимо указать творческий псевдоним и город проживания.\n"
            "2. Необходимо прислать ссылку на карточку артиста в Яндекс Музыке"
            " (если есть).\n"
            "3. Необходимо указать ссылки на актуальные соцсети (Instagram, TikTok, Telegram, VK).\n"
            "4. Необходимо прислать личный контакт для связи в Telegram.\n"
            "5. Можно прислать не более 5 демо в формате mp3.\n\n"
            "Поехали! Напиши в ответном сообщении псевдоним и город проживания.\n"
        )

    @dp.message(F.text)
    async def handle_text(message: Message):
        user = users.get(message.from_user.id)
        if not user:
            return

        if "name_city" not in user:
            user["name_city"] = message.text
            await message.answer(
                "Супер, теперь пришли ссылку на карточку артиста в Яндекс Музыке, "
                "или напиши «нет», если ее еще нет."
            )
            return

        if "yandex" not in user:
            user["yandex"] = message.text
            await message.answer(
                "Класс, теперь пришли ссылки на соцсети "
                "(Instagram, TikTok, канал в Telegram, сообщество в VK и др.). "
                "Каждая ссылка должна быть с новой строки."
            )
            return

        if "socials" not in user:
            user["socials"] = message.text
            await message.answer(
                "Круто, теперь напиши контакт для связи в Telegram в формате @username."
            )
            return

        if "contact" not in user:
            user["contact"] = message.text
            await message.answer(
                "А теперь самое главное! Загрузи до 5 демо в формате mp3.\n"
                "Когда загрузка файлов закончится, напиши «Готово»."
            )
            return

        if message.text.strip().lower() == "готово":
            await send_to_admin(user_id=message.from_user.id, bot_instance=bot)
            await message.answer(
                "Спасибо! Демо отправлены на рассмотрение. "
                "Если они понравятся команде, то мы обязательно с тобой свяжемся 🙌\n\n"
                "Нажми /start, чтобы запустить бота заново."
            )
            users.pop(message.from_user.id)
            return

    @dp.message(F.audio)
    async def handle_audio(message: Message):
        user = users.get(message.from_user.id)
        if not user:
            return

        if len(user["demos"]) >= 5:
            await message.answer("Можно прислать максимум 5 демо.")
            return

        if message.audio.mime_type != "audio/mpeg":
            await message.answer("Можно прислать только mp3 файлы.")
            return

        user["demos"].append(message.audio.file_id)
        await message.answer(f"Демо принято ({len(user['demos'])}/5).")

    # ------------------ SEND TO ADMIN ------------------
    async def send_to_admin(user_id: int, bot_instance):
        user = users[user_id]

        text = (
            "🎧 Йо, поступило новое демо!\n\n"
            f"Артист / Город:\n{user['name_city']}\n\n"
            f"Яндекс Музыка:\n{user['yandex']}\n\n"
            f"Соцсети:\n{user['socials']}\n\n"
            f"Контакт:\n{user['contact']}"
        )

        await bot_instance.send_message(ADMIN_CHAT_ID, text)

        for file_id in user["demos"]:
            await bot_instance.send_audio(ADMIN_CHAT_ID, file_id)

    # ------------------ START POLLING ------------------
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
