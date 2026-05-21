from aiogram.fsm.state import State, StatesGroup


class SearchStates(StatesGroup):
    selecting_direction = State()
    selecting_specialty = State()
    viewing_results = State()
