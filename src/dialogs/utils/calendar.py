from datetime import date
from typing import Dict

from aiogram_dialog import (
    DialogManager,
)
from aiogram_dialog.widgets.kbd import (
    Calendar, CalendarScope, )
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView, CalendarData,
)
from aiogram_dialog.widgets.text import Text, Format
from babel.dates import get_day_names, get_month_names


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_day_names(
            width="short", context='stand-alone', locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        return get_month_names(
            'wide', context='stand-alone', locale=locale,
        )[selected_date.month].title()


class CustomCalendar(Calendar):
    def get_scope(self, manager: DialogManager) -> CalendarScope:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_scope = calendar_data.get("current_scope")
        if not current_scope:
            return CalendarScope.YEARS
        try:
            return CalendarScope(current_scope)
        except ValueError:
            return CalendarScope.YEARS

    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
                month_text=Month(),
                header_text="| " + Format("{date:%Y}") + " |",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                header_text="| " + Format("{date:%Y}") + " // " + Month() + " |",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            )
        }
