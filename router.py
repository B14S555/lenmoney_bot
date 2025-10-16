from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import kb
from states import Add, Get
import bd.reqest as bd

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=f"Привет, {message.from_user.first_name}!\n"
             f"Это бот твоих расходов. Что ты хочешь сделать?",
        reply_markup=kb.section
    )


@router.callback_query(F.data == "exit")
async def back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        text="Что ты хочешь сделать?",
        reply_markup=kb.section
    )
    await callback.answer()


# === ДОБАВЛЕНИЕ ТРАТЫ ===
@router.callback_query(StateFilter(None), F.data == "add")
async def add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Add.sum)
    await callback.message.answer("Введите сумму", reply_markup=kb.exit)
    await callback.answer()


@router.message(Add.sum)
async def add_sum(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
        await state.update_data(sum=amount)
        await state.set_state(Add.description)
        await message.answer("Введите описание", reply_markup=kb.exit)
    except ValueError:
        await message.answer("Введите число!")


@router.message(Add.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await bd.add(user_id=message.from_user.id, data=data)
    await message.answer(
        f"Трата успешно добавлена ✅\n\n"
        f"Сумма: {data['sum']} грн\n"
        f"Описание: {data['description']}",
        reply_markup=kb.section
    )
    await state.clear()


# === ПРОСМОТР ТРАТ ===
@router.callback_query(StateFilter(None), F.data == "show")
async def show(callback: CallbackQuery, state: FSMContext):
    years = await bd.getYears(callback.from_user.id)
    if not years:
        await callback.message.answer("У вас нет ни одной траты")
    else:
        await state.set_state(Get.year)
        await callback.message.answer(
            "Выберите год",
            reply_markup=kb.getYearsButton(years=years)
        )
    await callback.answer()


@router.callback_query(Get.year, F.data.startswith("year:"))
async def year(callback: CallbackQuery, state: FSMContext):
    year = callback.data.split(':')[1]
    await state.update_data(year=int(year))
    await state.set_state(Get.month)
    await callback.message.answer("Выберите месяц", reply_markup=kb.getMonths())
    await callback.answer()


@router.callback_query(Get.month, F.data.startswith("month:"))
async def month(callback: CallbackQuery, state: FSMContext):
    month = int(callback.data.split(":")[1])
    await state.update_data(month=month)
    data = await state.get_data()
    expenses = await bd.getAll(user_id=callback.from_user.id, data=data)
    await callback.message.answer(text=expenses, reply_markup=kb.exit)
    await callback.answer()

