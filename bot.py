from aiogram import Bot, Dispatcher
import asyncio
from router import router
from bd.models import async_main



async def main():
    await  async_main()
    bot = Bot("8445908325:AAG191sQXcg-BhZDibV3FYCnXSopNAKdCTM")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")