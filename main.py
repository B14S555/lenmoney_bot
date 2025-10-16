import asyncio
from aiogram import Bot, Dispatcher
from router import router
from bd.models import async_main


TOKEN = "8445908325:AAG191sQXcg-BhZDibV3FYCnXSopNAKdCTM"  # ← сюда вставь токен из BotFather


async def main():
    # создаём таблицы в базе данных
    await async_main()

    # инициализируем бота и диспетчер
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # подключаем роутер с хендлерами
    dp.include_router(router)

    print("Бот запущен 🚀")
    # запускаем опрос Telegram-сервера
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен 🛑")

