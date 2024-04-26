from aiogram.fsm.state import StatesGroup, State


class ThresholdStates(StatesGroup):
    waiting_for_min_threshold = State()
    waiting_for_max_threshold = State()
    done_collecting_thresholds = State()