from datetime import datetime
from calendar import monthrange
from bd.models import async_session, Expense
from sqlalchemy import select, and_, func


async def add(user_id, data):
    """Добавить новую трату"""
    async with async_session() as session:
        session.add(Expense(
            user_id=user_id,
            sum=data["sum"],
            description=data["description"],
            date=datetime.now()
        ))
        await session.commit()


async def getYears(user_id):
    """Получить все года, где были траты"""
    async with async_session() as session:
        result = await session.scalars(
            select(func.strftime("%Y", Expense.date).label("year"))
            .where(Expense.user_id == user_id)
            .distinct()
            .order_by("year")
        )
        years = [int(y) for y in result if y is not None]
        return years


async def getAll(user_id, data):
    """Получить все траты за выбранный месяц и год"""
    year = data['year']
    month = data['month']
    start_date = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = datetime(year, month, last_day, 23, 59, 59)

    async with async_session() as session:
        expenses = await session.scalars(
            select(Expense).where(
                and_(
                    Expense.user_id == user_id,
                    Expense.date >= start_date,
                    Expense.date <= end_date
                )
            )
        )
        result = expenses.all()
        return answerExpenses(result)


def answerExpenses(expenses):
    """Сформировать текстовый ответ по тратам"""
    if not expenses:
        return "В этом месяце не было трат"

    total = 0
    answer = []

    for exp in expenses:
        date = exp.date.strftime("%d.%m.%Y")
        answer.append(f"{date}\n{exp.sum} грн\n{exp.description}")
        total += exp.sum

    answer.append("---------")
    answer.append(f"Всего: {total} грн.")
    return "\n\n".join(answer)
