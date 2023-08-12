import datetime
import logging
from datetime import date
from typing import Dict, Optional, List

from aiogram.types import InlineKeyboardButton
from aiogram_dialog import (
    DialogManager,
)
from aiogram_dialog.widgets.kbd import (
    Calendar, CalendarScope, )
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView, CalendarData, CalendarConfig, get_today,
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
        year_now: int = datetime.datetime.now().year
        config = CalendarConfig(
            min_date=date(year_now-100, 1, 1),
            max_date=date(year_now, 12, 31)
        )
        return {
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, config,
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, config,
                month_text=Month(),
                header_text="| " + Format("{date:%Y}") + " |",
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, config,
                header_text="| " + Format("{date:%Y}") + " // " + Month() + " |",
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
            )
        }

    async def _render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> List[List[InlineKeyboardButton]]:
        scope = self.get_scope(manager)
        view = self.views[scope]
        offset = self.get_offset(manager)
        config = await self._get_user_config(data, manager)
        if offset is None:
            new_offset = get_today(config.timezone)
            offset = self.set_offset(new_offset, manager, True)
        return await view.render(config, offset, data, manager)

    def set_offset(self, new_offset: date,
                   manager: DialogManager, create: bool = False) -> date:
        data = self.get_widget_data(manager, {})
        if create:
            adjusted_date = date(new_offset.year - 19, new_offset.month, new_offset.day)
        else:
            adjusted_date = new_offset
        data["current_offset"] = adjusted_date.isoformat()
        return adjusted_date

    def get_offset(self, manager: DialogManager) -> Optional[date]:
        calendar_data: CalendarData = self.get_widget_data(manager, {})
        current_offset = calendar_data.get("current_offset")
        if current_offset is None:
            return None
        return date.fromisoformat(current_offset)
