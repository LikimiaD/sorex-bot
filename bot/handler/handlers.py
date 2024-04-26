from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F

from bot.handler.helpers import collect_thresholds, handle_threshold_input
from bot.states import ThresholdStates
from database.queries.core import AsyncORM
from bot.keyboards.kb import CurrencyAction, create_currency_keyboard


router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Выберите криптовалюты:", reply_markup=create_currency_keyboard())
    await AsyncORM.ensure_user(telegram_id=message.from_user.id, username=message.from_user.username)
    await state.set_data({"selected_currencies": set()})


@router.callback_query(CurrencyAction.filter(F.action == "toggle"))
async def handle_currency_toggle(query: types.CallbackQuery, callback_data: CurrencyAction, state: FSMContext):
    user_data = await state.get_data()
    selected_currencies = user_data.get("selected_currencies", set())

    if callback_data.currency in selected_currencies:
        selected_currencies.remove(callback_data.currency)
    else:
        selected_currencies.add(callback_data.currency)

    await state.update_data(selected_currencies=selected_currencies)
    await query.message.edit_reply_markup(reply_markup=create_currency_keyboard(selected_currencies))
    await query.answer()


@router.callback_query(CurrencyAction.filter(F.action == "done"))
async def handle_done(query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    selected_currencies = user_data.get("selected_currencies", set())

    if not selected_currencies:
        await query.message.answer("Пожалуйста, выберите хотя бы одну валюту.")
        return

    await state.update_data(selected_currencies=list(selected_currencies), thresholds={})
    await collect_thresholds(query.message, state, 0, query.message.message_id)


@router.message(ThresholdStates.waiting_for_min_threshold)
async def min_threshold_handler(message: types.Message, state: FSMContext):
    return await handle_threshold_input(message, state, "min")


@router.message(ThresholdStates.waiting_for_max_threshold)
async def max_threshold_handler(message: types.Message, state: FSMContext):
    return await handle_threshold_input(message, state, "max")

