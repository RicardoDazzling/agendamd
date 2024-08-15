from datetime import timedelta, date
from typing import Optional

import pandas as pd
from babel.dates import format_date
from kivy.core.window import Window
from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDockedDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.textfield import MDTextField

from libs.applibs.db.config import CONFIG
from libs.applibs.utils import ignore_args, get_datestamp_from_date
from globals import TAGS, TASKS, translator as _
from libs.uix.components.list import ListItem


class ListScreen(MDScreen):
    _tf_search: Optional[MDTextField] = ObjectProperty(None)
    _swt_date: Optional[MDSwitch] = ObjectProperty(None)
    _btn_date: Optional[MDButton] = ObjectProperty(None)
    _btn_text: Optional[MDButtonText] = ObjectProperty(None)
    _cb_closed: Optional[MDCheckbox] = ObjectProperty(None)
    _ddi_tag: Optional[MDDropDownItemText] = ObjectProperty(None)
    _ddi_tag_menu: Optional[MDDropdownMenu] = None
    _lyo_results: Optional[MDBoxLayout] = ObjectProperty(None)
    _task_dialog = ObjectProperty(None)
    _date_filter: Optional[list] = ListProperty([])
    _selected_text = _("Selected: {}")

    def __init__(self, **kwargs):
        _.bind(self._update_language)
        self._date_picker = MDDockedDatePicker(mode="range")
        self._date_picker.bind(on_cancel=lambda i=None: self._date_picker.dismiss(),
                               on_ok=self._update_date_filter)
        self._date_filter = [self._date_picker.today]
        self._date_filter_changed(self._date_filter)
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self._search(*args)

    @staticmethod
    def on_ids(self, value: dict):
        if value:
            self._tf_search = value.get('tf_search', None)
            self._swt_date = value.get('swt_date', None)
            self._btn_date = value.get('btn_date', None)
            self._cb_closed = value.get('cb_closed', None)
            self._ddi_tag = value.get('ddi_tag', None)
            self._lyo_results = value.get('lyo_results', None)

    @staticmethod
    def on__tf_search(self, value: MDTextField):
        value.bind(text=self._search)

    @staticmethod
    def on__swt_date(self, value: MDSwitch):
        value.bind(active=self._update_date_filter)

    @staticmethod
    def on__btn_date(self, value: MDButton):
        self._swt_date.bind(active=lambda i, v: value.setter('disabled')(i, not v))
        self._date_filter_changed(self._date_filter)
        self.bind(_date_filter=self._search)

    def on_btn_date_release(self):
        __picker_size = self._date_picker.size
        __mouse_pos = Window.mouse_pos
        __window_size = Window.size
        __picker_pos = list(__mouse_pos)
        __picker_pos[1] = __picker_pos[1] - __picker_size[1]
        if __mouse_pos[0] + __picker_size[0] > __window_size[0]:  # x
            __picker_pos[0] = __window_size[0] - __picker_size[0]
        if __mouse_pos[1] - __picker_size[1] < 0:  # y
            __picker_pos[1] = __mouse_pos[1]
        self._date_picker.pos = __picker_pos
        self._date_picker.open()

    def on_ddi_tag_release(self, instance: MDDropDownItem):
        if self._ddi_tag_menu is None:
            def get_menu_items(value: Optional[list] = None) -> list:
                if value is None:
                    value = list(TAGS)
                if "*" not in value:
                    value.insert(0, '*')
                __setter = self._ddi_tag.setter('text')
                return [
                    {
                        "text": f"{tag}",
                        "on_release": lambda i=None, v=tag, setter=__setter: setter(i, v),
                    } for tag in value
                ]

            self._ddi_tag_menu = MDDropdownMenu(caller=instance, items=get_menu_items())
            TAGS.bind(on_data=lambda v: self._ddi_tag_menu.setter('items')(None, get_menu_items(v)))
            self._ddi_tag.bind(text=self._search)
        self._ddi_tag_menu.open()

    @staticmethod
    def on__cb_closed(self, value: MDCheckbox):
        value.bind(active=self._search)

    def on_item_release(self, instance: ListItem):

        def unbind(dialog):
            dialog.unbind(on_remove=remove, on_accept=accept, on_cancel=unbind)

        def remove(dialog):
            self.remove_widget(instance)
            unbind(dialog)

        def accept(dialog, edited: dict):
            instance.task = edited
            unbind(dialog)

        self._task_dialog.item = instance.task
        self._task_dialog.bind(on_remove=remove, on_accept=accept, on_cancel=unbind)
        self._task_dialog.open()

    def set_checked(self, instance: ListItem, value: bool):
        __old = instance.task
        if 'tag' in __old:
            __old['tag'] = TAGS.get(__old['tag'])
        __new = __old.copy()
        __new['closed'] = value
        TASKS.update(__old, __new)
        self._search()

    def _update_language(self):
        self._selected_text = _("Selected: {}")
        self._date_filter_changed(self._date_filter)

    @ignore_args
    def _search(self):
        if self._lyo_results is None:
            return
        self._lyo_results.clear_widgets()
        __text: str = self._tf_search.text
        __closed: bool = self._cb_closed.active
        __tag: str = self._ddi_tag.text
        __tag: int = TAGS.get(__tag) if __tag != '*' else -1
        __date_filter = list(filter(lambda x: isinstance(x, date), self._date_filter))
        if self._swt_date.active:
            if not __date_filter:
                return
            __date: date = __date_filter[0]
            __end_date = __date + timedelta(days=5)
            __end_date: date = __end_date if len(__date_filter) < 2 else \
                __end_date if not isinstance(__date_filter[1], date) else \
                __date_filter[1]
            __current_day = get_datestamp_from_date(__date)
            __end_day = get_datestamp_from_date(__end_date)
            __first_month_days_list = []

            if __date.month != __end_date.month \
                    or __date.year != __end_date.year:
                __draft_date = __date
                __years = __end_date.year - __date.year
                __months = __end_date.month - __date.month
                __months += 12 * __years
                for month in range(__months):
                    __draft_date += timedelta(days=31)
                    __draft_date -= timedelta(days=__draft_date.day - 1)
                    __first_month_days_list.append(get_datestamp_from_date(__draft_date))

            __year = __date.year
            __month = __date.month
            __tasks = TASKS.get(__year, __month)
            while __current_day != __end_day:
                if __current_day in __first_month_days_list:
                    __month += 1
                    if __month > 12:
                        __month = 0
                        __year += 1
                    __tasks = TASKS.get(__year, __month)
                __day_tasks = __tasks[__tasks['day'] == __current_day]
                self._create_items(__day_tasks, __closed, __text, __tag)
                __current_day += 1
        else:
            __scroll_view: MDScrollView = self._lyo_results.parent
            __tasks_months = TASKS.list_dir
            if not __tasks_months:
                return
            __iterator = iter(__tasks_months)

            def _next(instance=None, value=None):
                if None in (instance, value):
                    tasks = TASKS.get(*next(__iterator).split('_'))
                    self._create_items(tasks, __closed, __text, __tag)
                    return
                try:
                    tasks = TASKS.get(*next(__iterator).split('_'))
                    if value != 0:
                        return
                    self._create_items(tasks, __closed, __text, __tag)
                except StopIteration:
                    __scroll_view.unbind(y=_next)

            while self._lyo_results.height <= __scroll_view.height:
                try:
                    _next()
                except StopIteration:
                    return
            __scroll_view.bind(y=_next)
        return

    def _create_items(self, tasks, closed: bool, text: str, tag: int):
        __empty: pd.Series = pd.Series(tasks['closed'] == tasks['closed'])
        __closed_tasks = tasks['closed'] == closed
        __contains_text = __empty.copy() if not text.strip() else \
            (tasks['title'].str.contains(text, regex=False) |
             tasks['description'].str.contains(text, regex=False))
        __contains_tag = __empty.copy() if tag == -1 else tasks['tag'] == tag
        __filtered_tasks = tasks[__closed_tasks & __contains_tag & __contains_text]

        for index, series in __filtered_tasks.iterrows():
            __dict = series.to_dict()
            if 'tag' in __dict:
                __dict['tag'] = TAGS.get(__dict['tag'])
            __list_item = ListItem(__dict)
            __list_item.bind(
                on_list_release=self.on_item_release,
                on_checked_changed=self.set_checked
            )
            self._lyo_results.add_widget(__list_item)

    @ignore_args
    def _update_date_filter(self):
        if self._lyo_results is None:
            return
        if self._date_picker.parent:
            self._date_picker.dismiss()
        if self._date_picker.min_date is None and self._swt_date.active:
            pass
        elif self._swt_date.active:
            __date_filter = [self._date_picker.min_date]
            if self._date_picker.max_date:
                __date_filter.append(self._date_picker.max_date)
            self._date_filter = __date_filter
        else:
            self._date_filter.clear()
        self._date_filter_changed(self._date_filter)

    def _date_filter_changed(self, value: list):
        if not value or self._btn_date is None:
            if self._btn_date is not None:
                self._search()
            return
        if len(value) > 2:
            raise IndexError("Too long date filter list")
        __selected_string = format_date(value[0], format='short', locale=CONFIG.language)
        if len(value) == 2:
            __selected_string += " - " + format_date(value[1], format='short', locale=CONFIG.language)
        if self._btn_text is None:
            self._btn_text = MDButtonText()
            self._btn_date.add_widget(self._btn_text)
        self._btn_text.text = self._selected_text.replace('{}', __selected_string)
