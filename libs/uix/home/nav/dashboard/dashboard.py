from functools import partial, cached_property
from typing import Union, Optional

from kivy.app import App
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty
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

from libs.uix.components.dashboard import CalendarItem, MinimizedCalendarItem
from libs.uix.components.home.task_dialog import TaskDialog
from libs.applibs.utils import get_datestamp_from_date, ignore_instance, only_the_instance, ignore_args
from globals import (
    TASKS,
    TAGS,
    translator as _
)


class DashboardScreen(MDScreen):
    cell_width = NumericProperty(0)
    cell_height = dp(120)
    _task_dialog = ObjectProperty(None)
    _grouped_tasks: list[dict[int, Union[list, dict, tuple]]] = [{}, {}, {}, {}, {}]
    _grouped_items: list[dict[int, Union[MinimizedCalendarItem, CalendarItem]]] = [{}, {}, {}, {}, {}]
    _loading: dict = {}
    _tasks: Optional[DataFrame] = None

    def __init__(self, **kwargs):
        self._app = App.get_running_app()
        self._datetime = datetime.now()
        self._today_datestamp: int = get_datestamp_from_date(self._datetime.date())
        super(DashboardScreen, self).__init__(**kwargs)
        TASKS.bind(on_add=self.on_task_add, on_update=self.on_task_update, on_remove=self.on_task_remove)

    def on_pre_enter(self, *args):
        super(DashboardScreen, self).on_pre_enter(*args)
        if self._calendar is not None:
            self.enter()
        else:
            self._loading['enter'] = self.enter

    _calendar: Optional[MDRelativeLayout] = ObjectProperty(None)
    _calendar_header: Optional[MDRelativeLayout] = ObjectProperty(None)
    _btn_task: Optional[MDFabButton] = ObjectProperty(None)
    _lbl_year: Optional[MDLabel] = ObjectProperty(None)
    _lbl_month: Optional[MDLabel] = ObjectProperty(None)
    _scroll: Optional[MDScrollView] = ObjectProperty(None)
    _table: Optional[MDBoxLayout] = ObjectProperty(None)

    @ignore_instance
    def on_ids(self, value: dict):
        if isinstance(value, dict):
            __calendar: Optional[MDRelativeLayout] = value.get('calendar', None)
            __calendar_header: Optional[MDRelativeLayout] = value.get('calendar_header', None)
            self._btn_task: Optional[MDFabButton] = value.get('btn_task', None)
            self._lbl_year: Optional[MDLabel] = value.get('lbl_year', None)
            self._lbl_month: Optional[MDLabel] = value.get('lbl_month', None)
            __scroll: Optional[MDScrollView] = value.get('scroll', None)
            __table: Optional[MDBoxLayout] = value.get('table', None)
            if self._calendar is None and __calendar is not None:
                self._calendar = __calendar
                self._calendar.bind(width=self._update_width)
                self._create_basics()
            if __calendar_header is not None and self._calendar_header is None:
                self._calendar_header = __calendar_header
                self._update_header()
            if __scroll is not None and self._scroll is None:
                self._scroll = __scroll
                self._scroll.bind(height=lambda i, v: self._scroll_to_now())
                self._update_scroll_height(__table, __table.height)
                self._scroll_to_now()
            if __table is not None and self._table is None:
                self._table = __table
                __table.bind(height=self._update_scroll_height, padding=self._update_scroll_height)
            self._load()

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
                        __items_draft[__previous] = self.create_list_minimized_calendar_item(__tasks_draft[__previous])
                        __calendar.add_widget(__items_draft[__previous])
                        return
                    elif __collateral['start'] < __start < __collateral['end']:
                        __tasks_draft[__previous] = (__collateral, None)
                        __calendar.remove_widget(__items_draft.pop(__previous))
                        __items_draft[__previous] = self.create_tuple_minimized_calendar_item(__tasks_draft[__previous])
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
                                items_draft=__items_draft
                            )
                        __tasks_draft[__start] = [row] + __collateral
                    else:
                        __tasks_draft[__start] = [row, __collateral]
                    __items_draft[__start] = self.create_list_minimized_calendar_item(__tasks_draft[__start])
                    __calendar.add_widget(__items_draft[__start])
                else:
                    __tasks_draft[__start] = (row, None)
                    __items_draft[__start] = self.create_tuple_minimized_calendar_item(__tasks_draft[__start])
                return
        __tasks_draft[__start] = row
        __items_draft[__start] = self.create_dict_calendar_item(__tasks_draft[__start])
        __calendar.add_widget(__items_draft[__start])

    def on_task_update(self, old: dict, new: dict):
        __old_between = self._today_datestamp <= old['day'] < self._today_datestamp + 5
        __new_between = self._today_datestamp <= new['day'] < self._today_datestamp + 5
        if not __old_between and not __new_between:
            return
        elif __old_between and not __new_between:
            self.on_task_remove(old)
            return
        elif not __old_between and __new_between:
            self.on_task_add(new)
            return
        elif old['day'] == new['day'] and old['start'] == new['start'] and old['end'] == new['end']:
            old['tag'] = TAGS.get(old['tag'])
            new['tag'] = TAGS.get(new['tag'])
            __item = None
            for i in range(old['start'], old['start'] - 16, -1):
                __item = self._grouped_items[old['day'] - self._today_datestamp].get(old['start'], None)
                if __item is not None:
                    break
            if __item is None:
                raise IndexError("Unknown old item.")
            __item.set_properties_by_dict(new, old)
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
                        __items_draft[i] = self.create_dict_calendar_item(__tasks_draft[i])
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
                    items_draft=__items_draft
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
        if self._tasks is None:
            self._tasks: DataFrame = TASKS[self._datetime.date()]
            self._start_dashboard_calendar()
        self._scroll_to_now()
        self._btn_task.icon = 'plus-outline'

    @ignore_args
    def add_task(self):
        self._task_dialog.item = None
        self._task_dialog.open()

    def update_task(self, instance: Union[CalendarItem, MinimizedCalendarItem]):
        item = instance
        if isinstance(instance, MinimizedCalendarItem):
            item = item.item
        self._task_dialog.item = item
        self._task_dialog.open()

    def _update_header(self):
        self._lbl_year.text = str(self._datetime.year)
        self._lbl_month.text = format_datetime(self._datetime, "MMMM", locale=_.language)
        _.bind(lambda lbl: lbl.__setattr__('text', format_datetime(self._datetime, "MMMM", locale=_.language)),
               self._lbl_month)

        __header: MDRelativeLayout = self._calendar_header
        __cell_width = self.cell_width
        __datetime = datetime.today() - timedelta(days=1)
        for i in range(6):
            __label = MDLabel(
                text=format_datetime(__datetime, "EEEE", locale=_.language),
                theme_text_color="Hint",
                halign="center"
            )
            _.bind(lambda lbl: lbl.__setattr__('text', format_datetime(__datetime, "EEEE", locale=_.language)),
                   __label)
            __box_layout = MDBoxLayout(
                __label,
                MDLabel(text=str(__datetime.day), halign="center"),
                orientation="vertical",
                size_hint=(None, 1),
                width=__cell_width,
                pos_hint={"center_y": .5},
                x=i * __cell_width
            )

            def set_x(box_layout, idx, instance, value):
                if instance:
                    pass
                box_layout.x = idx * value

            self.bind(cell_width=__box_layout.setter("width"))
            self.bind(cell_width=partial(set_x, __box_layout, i))
            __header.add_widget(__box_layout)
            __datetime += timedelta(days=1)

    def _start_dashboard_calendar(self):
        __calendar: MDRelativeLayout = self._calendar
        __cell_width = self.cell_width
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
                        __item = self.create_list_minimized_calendar_item(item)
                    elif isinstance(item, tuple):
                        __item = self.create_tuple_minimized_calendar_item(item)
                    elif isinstance(item, dict):
                        __item = self.create_dict_calendar_item(item)
                    else:
                        raise TypeError(f"Internal error, item is from a unknown type: {type(item)}.")
                    self._grouped_items[__index][key] = __item
                    __calendar.add_widget(__item)
                __index += 1

    def create_tuple_minimized_calendar_item(self, item: tuple) -> MinimizedCalendarItem:
        if not isinstance(item, tuple):
            raise TypeError("Item isn't a tuple instance.")
        __item = MinimizedCalendarItem(item[0],
                                       width=self.cell_width,
                                       base_height=self.cell_height)
        self.bind_item(__item)
        return __item

    def create_list_minimized_calendar_item(self, item: list) -> MinimizedCalendarItem:
        if not isinstance(item, list):
            raise TypeError("Item isn't a list instance.")
        __item = MinimizedCalendarItem(*item,
                                       width=self.cell_width,
                                       base_height=self.cell_height)
        self.bind_item(__item)
        return __item

    def create_dict_calendar_item(self, item: dict) -> CalendarItem:
        if not isinstance(item, dict):
            raise TypeError("Item isn't a dict instance.")
        __item = CalendarItem(item=item,
                              width=self.cell_width,
                              base_height=self.cell_height)
        self.bind_item(__item)
        return __item

    def bind_item(self, item: Union[MinimizedCalendarItem, CalendarItem]):
        item.bind(on_item_release=self.update_task)
        self.bind(cell_width=item.setter('width'))

    def _create_basics(self) -> None:

        def set_x(box_layout, idx, instance, value):
            if instance:
                pass
            box_layout.x = idx * value

        for i in range(24):
            __label = MDLabel(
                text=format_time(time(hour=i), format='short', locale=_.language),
                theme_text_color="Hint",
                halign="right",
                adaptive_height=True,
                pos_hint={"top": 1}
            )
            _.bind(lambda lbl: lbl.__setattr__('text', format_time(time(hour=i), format='short', locale=_.language)),
                   __label)
            __box_layout = MDBoxLayout(
                __label,
                size_hint=(None, None),
                height=self.cell_height,
                width=self.cell_width,
                pos=(0, (23 - i) * self.cell_height),
                md_bg_color=self.theme_cls.surfaceContainerLowColor
            )
            self.theme_cls.bind(
                surfaceContainerLowColor=lambda ins, val, lay=__box_layout: lay.setter('md_bg_color')(lay, val))
            self.bind(cell_width=__box_layout.setter("width"))
            self._calendar.add_widget(__box_layout)
        for i in range(1, 6):
            __divider = MDDivider(
                color=self.theme_cls.surfaceContainerLowColor,
                orientation="vertical",
                size_hint_y=1,
                x=self.cell_width * i
            )
            self.theme_cls.bind(
                surfaceContainerLowColor=lambda ins, val, lay=__divider: lay.setter('color')(lay, val))
            self.bind(cell_width=partial(set_x, __divider, i))
            self._calendar.add_widget(__divider)

    # scroll_height = cell_height  # * 1.142857142857143  # 24 / 21

    def _scroll_to_now(self):
        __hour = datetime.now().hour
        __scroll: MDScrollView = self._scroll
        __viewport = getattr(self._scroll, '_viewport', None)
        if __viewport is None or __scroll.height <= 0:
            return
        __scroll_max_cells = self._scroll.height / self.cell_height
        if __scroll_max_cells * self.cell_height < self._scroll.height:
            __scroll_max_cells += 1
        __scroll_cell_number = 24 - __scroll_max_cells
        __scroll_height = __viewport.height - __scroll.height
        __cell_distance = __scroll_height / __scroll_cell_number
        if __hour >= __scroll_cell_number:
            __y = 0
        elif __hour == 0:
            __y = 1
        else:
            __dy = (__scroll_cell_number - __hour) * __cell_distance
            __x, __y = __scroll.convert_distance_to_scroll(0, __dy)
        __scroll.scroll_y = __y
        self.debug = 1

    @only_the_instance
    def _update_scroll_height(self, instance: MDBoxLayout):
        if self._scroll is None or self._calendar_header is None:
            return
        if isinstance(instance.padding, list):
            if len(instance.padding) == 4:
                __padding = instance.padding[1] + instance.padding[3]
            else:
                __padding = instance.padding[1]
        else:
            __padding = 2 * instance.padding
        self._scroll.height = instance.height - self._calendar_header.height - __padding

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

    @ignore_instance
    def _update_width(self, value):
        self.cell_width = value // 6

    def _update_collaterals(self,
                            start: int,
                            other: Union[list, dict],
                            tasks_draft: dict[int, Union[list[dict], dict, tuple]],
                            items_draft: dict[int, Union[CalendarItem, MinimizedCalendarItem]]) -> Union[list, dict]:
        calendar: MDRelativeLayout = self._calendar
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
            items_draft[start] = self.create_dict_calendar_item(other)
        elif isinstance(other, tuple):
            items_draft[start] = self.create_tuple_minimized_calendar_item(other)
        elif isinstance(other, list):
            items_draft[start] = self.create_list_minimized_calendar_item(other)
        else:
            raise TypeError("Unknown type in the draft!")
        calendar.add_widget(items_draft[start])
        return other
