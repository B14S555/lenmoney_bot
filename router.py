from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
import kb
from states import *
import bd.reqest as bd

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=f"""Привет, {message.from_user.first_name}!
Это бот твоих расходов. Что ты хочешь сделать?""",
        reply_markup=kb.section
    )


@router.callback_query(F.data == "exit")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # ✅ Сразу отвечаем Telegram
    await state.clear()
    await callback.message.answer(
        text="Что ты хочешь сделать?",
        reply_markup=kb.section
    )


@router.callback_query(StateFilter(None), F.data == "add")
async def add_expense(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # ✅ Сразу ответ
    await state.set_state(Add.sum)
    await callback.message.answer("Введите сумму", reply_markup=kb.exit)


@router.message(Add.sum)
async def add_sum(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        await state.update_data(sum=amount)
        await state.set_state(Add.description)
        await message.answer("Введите описание", reply_markup=kb.exit)
    except ValueError:
        await message.answer("Я вас не понял, введите число.")


@router.message(Add.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await bd.add(user_id=message.from_user.id, data=data)

    await message.answer(
        f"""Трата успешно добавлена ✅
Сумма: {data['sum']}
Описание: {data['description']}""",
        reply_markup=kb.section
    )
    await state.clear()


@router.callback_query(StateFilter(None), F.data == "show")
async def show(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # ✅ сразу ответ

    years = await bd.getYears(callback.from_user.id)
    if not years:
        await callback.message.answer("У вас нет ни одной траты.")
        return

    await state.set_state(Get.year)
    await callback.message.answer(
        "Выберите год:",
        reply_markup=kb.getYearsButton(years=years)
    )


@router.callback_query(Get.year, F.data.startswith("year"))
async def year(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # ✅ сразу ответ

    year = callback.data.split(':')[1]
    try:
        await state.update_data(year=int(year))
        await state.set_state(Get.month)
        await callback.message.answer(
            "Выберите месяц:",
            reply_markup=kb.getMonths()
        )
    except ValueError:
        await callback.message.answer("Ошибка при выборе года.")


@router.callback_query(Get.month, F.data.startswith("month:"))
async def month(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # ✅ сразу ответ

    month = callback.data.split(":")[1]
    try:
        month = int(month)
        if 1 <= month <= 12:
            await state.update_data(month=month)
            data = await state.get_data()
            expenses = await bd.getAll(
                user_id=callback.from_user.id,
                data=data
            )
            await callback.message.answer(
                text=expenses,
                reply_markup=kb.exit
            )
    except ValueError:
        await callback.message.answer(
            text="Ошибка при выборе месяца.",
            reply_markup=kb.exit
        )

