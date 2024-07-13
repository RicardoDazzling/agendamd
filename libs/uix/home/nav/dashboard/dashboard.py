from functools import partial
from typing import Union, Optional

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFabButton
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from babel.dates import format_datetime, format_time
from datetime import datetime, timedelta, time
from pandas import DataFrame

from libs.uix.components.home import CalendarItem, MinimizedCalendarItem, TaskDialog
from libs.applibs.utils import get_datestamp_from_date
from globals import (
    TASKS,
    USERS,
    TAGS,
    translator as _
)


class Dashboard(MDScreen):
    _task_dialog: Optional[TaskDialog] = ObjectProperty(None)
    cell_height = dp(120)
    _grouped_tasks: list[dict[int, Union[list, dict, tuple]]] = [{}, {}, {}, {}, {}]
    _grouped_items: list[dict[int, Union[MinimizedCalendarItem, CalendarItem]]] = [{}, {}, {}, {}, {}]
    _loading: dict = {}

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self._app = App.get_running_app()
        self._datetime = datetime.now()
        self._task_dialog = TaskDialog()
        __today = self._datetime.date()
        self._tasks: DataFrame = TASKS[__today]
        self._today_datestamp: int = get_datestamp_from_date(__today)
        TASKS.bind(on_add=self.on_task_add, on_update=self.on_task_update, on_remove=self.on_task_remove)

    def on_pre_enter(self, *args):
        super(Dashboard, self).on_pre_enter(*args)
        if USERS.logged() and USERS.user.keep_logged:
            if self._calendar is not None:
                self.enter()
            else:
                self._loading['enter'] = self.enter
        else:
            USERS.bind(on_login=self.enter)

    _calendar: Optional[MDRelativeLayout] = ObjectProperty(None)
    _calendar_header: Optional[MDRelativeLayout] = ObjectProperty(None)
    _btn_task: Optional[MDFabButton] = ObjectProperty(None)
    _lbl_year: Optional[MDLabel] = ObjectProperty(None)
    _lbl_month: Optional[MDLabel] = ObjectProperty(None)
    _scroll: Optional[MDScrollView] = ObjectProperty(None)

    def on_ids(self, instance, value: dict):
        if isinstance(value, dict):
            self._calendar: Optional[MDRelativeLayout] = value.get('calendar', None)
            self._calendar_header: Optional[MDRelativeLayout] = value.get('calendar_header', None)
            self._btn_task: Optional[MDFabButton] = value.get('btn_task', None)
            self._lbl_year: Optional[MDLabel] = value.get('lbl_year', None)
            self._lbl_month: Optional[MDLabel] = value.get('lbl_month', None)
            self._scroll: Optional[MDScrollView] = value.get('scroll', None)
            self._load()

    def _load(self):
        if self._calendar is not None and self._calendar_header is not None and self._btn_task is not None \
                and self._lbl_year is not None and self._lbl_month is not None and self._scroll is not None:
            if 'enter' in self._loading.keys():
                self._loading.pop('enter')
                if self._calendar.width == 100:
                    def enter(instance, value):
                        if value > 100:
                            self.enter()
                            instance.unbind(width=enter)
                    self._calendar.bind(width=enter)
                else:
                    self.enter()

    def on_task_add(self, row: dict):
        __calendar: MDRelativeLayout = self._calendar
        __cell_width = __calendar.width // 6
        __sub = row['day'] - self._today_datestamp
        if not (0 <= __sub < 5):
            return
        __tasks_draft = self._grouped_tasks[__sub]
        __items_draft = self._grouped_items[__sub]
        __start: int = row['start']
        row['tag'] = TAGS.get(row['tag'])

        __previous = None
        __next = None
        for key in __tasks_draft.keys():
            if key >= __start:
                __next = key
                break
            __previous = key

        if __previous is not None:
            __collateral = __tasks_draft.get(__previous, None)
            if __collateral is not None:
                if isinstance(__collateral, dict):
                    if 0 <= __start - __previous <= 15:
                        __tasks_draft[__previous] = [__collateral, row]
                        __calendar.remove_widget(__items_draft.pop(__previous))
                        __items_draft[__previous] = MinimizedCalendarItem(
                            *__tasks_draft[__previous],
                            width=__cell_width,
                            base_height=self.cell_height
                        )
                        __calendar.add_widget(__items_draft[__previous])
                        return
                    elif __collateral['start'] < __start < __collateral['end']:
                        __tasks_draft[__previous] = (__collateral, None)
                        __calendar.remove_widget(__items_draft.pop(__previous))
                        __items_draft[__previous] = MinimizedCalendarItem(
                            __tasks_draft[__previous][0],
                            width=__cell_width,
                            base_height=self.cell_height
                        )
                elif isinstance(__collateral, list):
                    if 0 <= __start - __previous <= 15:
                        __tasks_draft[__previous].append(row)
                        __items_draft[__previous].set_properties_by_dict(row)
                        return
                elif isinstance(__collateral, tuple):
                    if 0 <= __start - __previous <= 15:
                        __tasks_draft[__previous] = [__collateral[0], row]
                        __items_draft[__previous].set_properties_by_dict(row)
                        return
        if __next is not None:
            __collateral = __tasks_draft.get(__next, None)
            if __collateral is not None:
                if __next - __start <= 15:
                    __collateral = __tasks_draft.pop(__next)
                    __collateral = __collateral[0] if isinstance(__collateral, tuple) else __collateral
                    __calendar.remove_widget(__items_draft.pop(__next))
                    if isinstance(__collateral, list):
                        __other = []
                        __idx = 0
                        while __idx < len(__collateral) or not __other:
                            if __collateral[__idx]['start'] - __start > 15:
                                __other = __collateral[__idx:].copy()
                                del __calendar[__idx:]
                            __idx += 1
                        del __idx
                        if __other:
                            self._update_collaterals(
                                start=__other[0]['start'],
                                other=__other,
                                tasks_draft=__tasks_draft,
                                items_draft=__items_draft,
                                calendar=__calendar,
                                cell_width=__cell_width,
                                cell_height=self.cell_height
                            )
                        __tasks_draft[__start] = [row] + __collateral
                    else:
                        __tasks_draft[__start] = [row, __collateral]
                    __items_draft[__start] = MinimizedCalendarItem(
                        *__tasks_draft[__start],
                        width=__cell_width,
                        base_height=self.cell_height
                    )
                    __calendar.add_widget(__items_draft[__start])
                else:
                    __tasks_draft[__start] = (row, None)
                    __items_draft[__start] = MinimizedCalendarItem(
                        row,
                        width=__cell_width,
                        base_height=self.cell_height
                    )
                return
        __tasks_draft[__start] = row
        __items_draft[__start] = CalendarItem(
            row,
            width=__cell_width,
            base_height=self.cell_height
        )
        __calendar.add_widget(__items_draft[__start])

    def on_task_update(self, old: dict, new: dict):
        __old_between = self._today_datestamp <= old['day'] < self._today_datestamp + 4
        __new_between = self._today_datestamp <= new['day'] < self._today_datestamp + 4
        old['tag'] = TAGS.get(old['tag'])
        new['tag'] = TAGS.get(new['tag'])
        if not __old_between and not __new_between:
            return
        elif __old_between and not __new_between:
            self.on_task_remove(old)
            return
        elif not __old_between and __new_between:
            self.on_task_add(new)
            return
        elif old['day'] == new['day'] and old['start'] == new['start'] and old['end'] == new['end']:
            self._grouped_items[old['day'] - self._today_datestamp][old['start']].set_properties_by_dict(new, old)
            return
        self.on_task_remove(old)
        self.on_task_add(new)

    def on_task_remove(self, row: dict):
        __calendar: MDRelativeLayout = self._calendar
        __cell_width = __calendar.width // 6
        __sub = row['day'] - self._today_datestamp
        if not (0 <= __sub < 5):
            return
        __start: int = row['start']
        row['tag'] = TAGS.get(row['tag'])
        __tasks_draft = self._grouped_tasks[__sub]
        __items_draft = self._grouped_items[__sub]
        __value = __tasks_draft.get(row['start'], None)
        for i in range(__start, 0, -1):
            __collateral = __tasks_draft.get(i, None)
            if __collateral is not None:
                if isinstance(__collateral, tuple):
                    __can_maximize = True
                    __collateral_start = __collateral[0]['start'] + 1
                    __collateral_end = __collateral[0]['end']
                    while not __can_maximize or __collateral_start <= __collateral_end:
                        if __tasks_draft.get(__collateral_start, None) is not None:
                            __can_maximize = False
                        __collateral_start += 1
                    if __can_maximize:
                        __calendar.remove_widget(__items_draft.pop(i))
                        __tasks_draft[i] = __tasks_draft[i][0]
                        __items_draft[i] = CalendarItem(
                            __tasks_draft[i],
                            width=__cell_width,
                            base_height=self.cell_height
                        )
                        __calendar.add_widget(__items_draft[i])
                break
        if __value is not None:
            __value = __tasks_draft.pop(row['start'])
            __calendar.remove_widget(__items_draft.pop(row['start']))
            if isinstance(__value, list):
                __value.remove(row)
                if len(__value) == 1:
                    __value = __value[0]
                    __collateral_start = __value['start']
                else:
                    __collateral_start = __value[0]['start']
                self._update_collaterals(
                    start=__collateral_start,
                    other=__value,
                    tasks_draft=__tasks_draft,
                    items_draft=__items_draft,
                    calendar=__calendar,
                    cell_width=__cell_width,
                    cell_height=self.cell_height
                )
            elif isinstance(__value, (dict, tuple)):
                pass
            else:
                raise TypeError("Unknown value type.")
            return
        else:
            for i in range(1, 16):
                __collateral_start = __start - i
                __collateral: Optional[list] = __tasks_draft.get(__collateral_start, None)
                if __collateral is not None:
                    if len(__collateral) == 2:
                        __collateral = __tasks_draft.pop(__collateral_start)
                        __calendar.remove_widget(__items_draft.pop(__collateral_start))
                        __collateral.remove(row)
                        self.on_task_add(__collateral[0])
                        return
                    else:
                        __item = __items_draft.get(__collateral_start)
                        __tasks_draft[__collateral_start].remove(row)
                        if isinstance(__item, MinimizedCalendarItem):
                            __item.remove_properties_by_dict(row)
                        return
            raise IndexError("Row removed doesn't exists in the calendar.")

    def enter(self):
        if not self._calendar_header.children:
            self._update_header()
            self._start_dashboard_calendar()
        self._scroll_to_now()
        self._btn_task.icon = 'plus-outline'

    def add_task(self, *args):
        self._task_dialog.item = None
        self._task_dialog.open()

    def update_task(self, *args, item: Union[CalendarItem | MinimizedCalendarItem]):
        if isinstance(item, MinimizedCalendarItem):
            item = item.item
        self._task_dialog.item = item
        self._task_dialog.open()

    def _update_header(self):
        self._lbl_year.text = str(self._datetime.year)
        self._lbl_month.text = format_datetime(self._datetime, "MMMM", locale=_.language)
        __header: MDRelativeLayout = self._calendar_header
        __cell_width = __header.width // 6
        __datetime = datetime.today() - timedelta(days=1)
        for i in range(6):
            __header.add_widget(
                MDBoxLayout(
                    MDLabel(
                        text=format_datetime(__datetime, "EEEE", locale=_.language),
                        theme_text_color="Hint",
                        halign="center"
                    ),
                    MDLabel(text=str(__datetime.day), halign="center"),
                    orientation="vertical",
                    size_hint=(None, 1),
                    width=__cell_width,
                    pos_hint={"center_y": .5},
                    x=i * __cell_width
                )
            )
            __datetime += timedelta(days=1)

    def _start_dashboard_calendar(self):
        __calendar: MDRelativeLayout = self._calendar
        __cell_width = __calendar.width // 6
        if not __calendar.children:
            self._create_basics(__calendar, __cell_width)
        __tasks = self._tasks
        __today_timestamp = self._today_datestamp
        __last_timestamp = __today_timestamp + 5
        if __tasks is not None:
            __tasks = __tasks[(__tasks['day'] >= __today_timestamp) & (__tasks['day'] < __last_timestamp)]

            __groups = self._grouped_tasks
            for i in range(5):
                __day_tasks = __tasks[__tasks['day'] == (__today_timestamp + i)].sort_values(by=["start"])
                __start = None
                __end = None
                __draft = {}
                for index, task in __day_tasks.iterrows():
                    task = task.to_dict()
                    task['tag'] = TAGS.get(task['tag'])
                    if __start is None:
                        if __end is None:
                            __end = int(task['end'])
                        __start = int(task['start'])
                        __draft[__start] = task
                    elif __start + 15 >= int(task['start']):
                        __value_before = __draft[__start]
                        if not isinstance(__value_before, list):
                            __draft[__start] = [__value_before, task]
                            __end = __start + 15
                        else:
                            __draft[__start].append(task)
                    elif __end > int(task['start']):
                        if not isinstance(__draft[__start], list):
                            __draft[__start] = (__draft[__start], None)
                        __start = int(task['start'])
                        __end = int(task['end'])
                        __draft[__start] = task
                    else:
                        __start = int(task['start'])
                        __end = int(task['end'])
                        __draft[__start] = task
                __groups[i] = __draft
            __index = 0
            for draft in __groups:
                for key, item in draft.items():
                    if isinstance(item, list):
                        __item = MinimizedCalendarItem(*item,
                                                       width=__cell_width,
                                                       base_height=self.cell_height)
                    elif isinstance(item, tuple):
                        __item = MinimizedCalendarItem(item[0],
                                                       width=__cell_width,
                                                       base_height=self.cell_height)
                    elif isinstance(item, dict):
                        __item = CalendarItem(item=item,
                                              width=__cell_width,
                                              base_height=self.cell_height)
                    else:
                        raise TypeError(f"Internal error, item is from a unknown type: {type(item)}.")
                    __item.bind(on_item_release=partial(self.update_task, item=__item))
                    self._grouped_items[__index][key] = __item
                    __calendar.add_widget(__item)
                __index += 1

    def _create_basics(self, calendar: MDRelativeLayout, cell_width: int) -> None:
        for i in range(24):
            calendar.add_widget(MDBoxLayout(
                MDLabel(
                    text=format_time(time(hour=i), format='short', locale=_.language),
                    theme_text_color="Hint",
                    halign="right",
                    adaptive_height=True,
                    pos_hint={"top": 1}
                ),
                size_hint=(None, None),
                height=self.cell_height,
                width=cell_width,
                pos=(0, calendar.height - i * self.cell_height - self.cell_height),
                md_bg_color=self.theme_cls.surfaceContainerLowColor
            ))
        for i in range(1, 6):
            calendar.add_widget(MDDivider(
                color=self.theme_cls.surfaceContainerLowColor,
                orientation="vertical",
                size_hint_y=1,
                x=cell_width * i
            ))

    def _scroll_to_now(self):
        __hour = datetime.now().hour
        __scroll: MDScrollView = self._scroll
        __x, __y = __scroll.convert_distance_to_scroll(0, (24 - __hour - 3) * self.cell_height)
        __scroll.scroll_y = __y

    @staticmethod
    def _update_collaterals(start: int,
                            other: Union[list, dict],
                            tasks_draft: dict[int, Union[list[dict], dict, tuple]],
                            items_draft: dict[int, Union[list[dict], dict, tuple]],
                            calendar: MDRelativeLayout,
                            cell_width: float,
                            cell_height: float) -> Union[list, dict]:
        for i in range(16):
            __collateral_start = start + i
            __collateral = tasks_draft.get(__collateral_start, None)
            if __collateral is not None:
                __collateral = tasks_draft.pop(__collateral_start)
                calendar.remove_widget(items_draft.pop(__collateral_start))
                if not isinstance(other, list):
                    if isinstance(__collateral, dict):
                        other = [other, __collateral]
                    elif isinstance(__collateral, tuple):
                        other = [other, __collateral[0]]
                    elif isinstance(__collateral, list):
                        other = [other] + __collateral
                else:
                    if isinstance(__collateral, dict):
                        other.append(__collateral)
                    elif isinstance(__collateral, tuple):
                        other.append(__collateral[0])
                    elif isinstance(__collateral, list):
                        other.extend(__collateral)

        if isinstance(other, dict):
            for i in range(start + 15, other['end'] + 1):
                if tasks_draft.get(i, None) is not None:
                    other = (other, None)

        tasks_draft[start] = other
        if isinstance(other, dict):
            items_draft[start] = CalendarItem(
                other,
                width=cell_width,
                base_height=cell_height
            )
        elif isinstance(other, tuple):
            items_draft[start] = MinimizedCalendarItem(
                other[0],
                width=cell_width,
                base_height=cell_height
            )
        elif isinstance(other, list):
            items_draft[start] = MinimizedCalendarItem(
                *other,
                width=cell_width,
                base_height=cell_height
            )
        else:
            raise TypeError("Unknown type in the draft!")
        calendar.add_widget(items_draft[start])
        return other
