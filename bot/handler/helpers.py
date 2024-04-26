from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import ThresholdStates
from database.queries.core import AsyncORM


async def collect_thresholds(message: types.Message, state: FSMContext, index: int, msg_to_edit_id: int):
    user_data = await state.get_data()
    selected_currencies = user_data["selected_currencies"]

    if index < len(selected_currencies):
        currency = selected_currencies[index]
        await state.update_data(current_index=index)
        await prompt_for_threshold(message, state, currency, "min", msg_to_edit_id)
    else:
        await display_thresholds(message, state, msg_to_edit_id)


async def prompt_for_threshold(message: types.Message, state: FSMContext, currency: str, threshold_type: str, msg_to_edit_id: int):
    state_class = ThresholdStates.waiting_for_min_threshold if threshold_type == "min" else ThresholdStates.waiting_for_max_threshold
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_to_edit_id,
        text=f"Введите {threshold_type} пороговое значение для валюты {currency}:",
        reply_markup=None
    )
    await state.set_state(state_class)
    await state.update_data(current_currency=currency, current_threshold_type=threshold_type, msg_to_edit_id=msg_to_edit_id)


async def display_thresholds(message: types.Message, state: FSMContext, msg_to_edit_id: int):
    user_data = await state.get_data()
    thresholds = user_data["thresholds"]

    await AsyncORM.deactivate_old_alerts(message.from_user.id)

    for currency, value in thresholds.items():
        await AsyncORM.ensure_user_and_create_alert(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            cryptocurrency=currency,
            threshold_value=value['max'],
            direction="above"
        )
        await AsyncORM.ensure_user_and_create_alert(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            cryptocurrency=currency,
            threshold_value=value['min'],
            direction="below"
        )

    response = "Пороговые значения сохранены:\n" + "\n".join(
        [f"{currency}: мин. {values['min']}, макс. {values['max']}" for currency, values in thresholds.items()]) + "\nДля изменения напишите /start"

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=msg_to_edit_id,
        text=response,
        reply_markup=None
    )
    await state.clear()


async def handle_threshold_input(message: types.Message, state: FSMContext, threshold_type: str):
    threshold_value = message.text
    await message.delete()

    if not threshold_value.replace('.', '', 1).isdigit():
        await message.answer("Пожалуйста, введите числовое значение.")
        return

    user_data = await state.get_data()
    current_currency = user_data["current_currency"]
    thresholds = user_data.get("thresholds", {})
    current_index = user_data.get("current_index", 0)

    if current_currency not in thresholds:
        thresholds[current_currency] = {}
    thresholds[current_currency][threshold_type] = float(threshold_value)
    await state.update_data(thresholds=thresholds)

    if threshold_type == "min":
        # Запросить max после установки min
        await prompt_for_threshold(message, state, current_currency, "max", user_data["msg_to_edit_id"])
    else:
        # Увеличить индекс и сохранить его в состоянии после установки max
        current_index += 1
        await state.update_data(current_index=current_index)
        await collect_thresholds(message, state, current_index, user_data["msg_to_edit_id"])
