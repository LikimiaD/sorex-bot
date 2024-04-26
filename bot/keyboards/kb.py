from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CurrencyAction(CallbackData, prefix="currency"):
    action: str
    currency: str


CURRENCIES = ["BTC", "ETH", "USDT", "BNB", "SOL", "USDC", "XRP", "TON"]


def create_currency_keyboard(selected_currencies=None):
    selected_currencies = selected_currencies or set()
    builder = InlineKeyboardBuilder()
    for currency in CURRENCIES:
        status = "🟩" if currency in selected_currencies else "⬜"
        builder.button(text=f"{currency} {status}", callback_data=CurrencyAction(action="toggle", currency=currency))
    builder.button(text="Готово", callback_data=CurrencyAction(action="done", currency="none"))
    builder.adjust(2, repeat=True)
    return builder.as_markup()
