import sys

from typing import Optional, Union, Any

from babel.dates import format_date, format_time, format_datetime
from kivy.properties import ObjectProperty, NumericProperty, OptionProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDModalDatePicker, MDTimePickerDialVertical
from kivymd.uix.textfield import MDTextField
from datetime import date, time, datetime


if sys.version_info >= (3, 11):
    DatetimeBaseType = Optional[datetime]
    DateBaseType = Optional[date]
    TimeBaseType = Optional[time]
    DatetimeUnionType = Union[datetime, date, time]
else:
    DatetimeBaseType = DateBaseType = TimeBaseType = DatetimeUnionType = Any


class DateTimeTextField(MDTextField):
    datetime_mode = OptionProperty("datetime", options=["date", "time", "datetime"])
    date_dialog = ObjectProperty(None)
    time_dialog = ObjectProperty(None)
    datetime: DatetimeBaseType = ObjectProperty(None, allownone=True)
    date: DateBaseType = ObjectProperty(None, allownone=True)
    time: TimeBaseType = ObjectProperty(None, allownone=True)
    locale = StringProperty("en_US")
    start = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(DateTimeTextField, self).__init__(*args, **kwargs)

        self.date_dialog = MDModalDatePicker(
            min_date=date.fromtimestamp(self.start),
            max_date=date.fromtimestamp(self.start + 4_294_967_295)
        )
        self.time_dialog = MDTimePickerDialVertical()
        __now = datetime.now()
        self.time_dialog.set_time(__now.time())

        self.date_dialog.bind(on_ok=self.on_date_ok, on_cancel=self.on_cancel)
        self.time_dialog.bind(on_ok=self.on_time_ok, on_cancel=self.on_cancel)
        self.bind(date=self.on_datetime, time=self.on_datetime)

    def on_focus(self, instance, focus: bool) -> None:
        super().on_focus(instance, focus)
        if focus:
            if self.datetime_mode != "time":
                self.date_dialog.open()
            else:
                self.time_dialog.open()

    def on_date_ok(self, instance: MDModalDatePicker):
        instance.dismiss()
        if self.datetime_mode == 'datetime':
            self.time_dialog.open()
        self.date: date = instance.get_date()[0]
        if self.datetime_mode == 'date':
            self.dispatch('on_text_validate')
            self.focus = False

    def on_time_ok(self, instance: MDTimePickerDialVertical):
        instance.dismiss()
        self.time: time = instance.time
        if self.datetime_mode == 'datetime':
            self.datetime: datetime = datetime.combine(self.date, self.time)
        self.dispatch('on_text_validate')
        self.focus = False

    @staticmethod
    def on_datetime(self, value: DatetimeUnionType):
        if self.datetime_mode == 'datetime' and isinstance(value, datetime):
            self.text = format_datetime(value, locale=self.locale)
        elif self.datetime_mode == 'date' and isinstance(value, date):
            self.text = format_date(value, locale=self.locale)
        elif self.datetime_mode == 'time' and isinstance(value, time):
            self.text = format_time(value, locale=self.locale)
        if 'time' in self.datetime_mode:
            if value is None:
                self.time_dialog.set_time(datetime.now().time())
            else:
                self.time_dialog.set_time(value if isinstance(value, time) else value.time())
        if 'date' in self.datetime_mode:
            if value is None:
                value = datetime.now().date()
            if value.year == self.date_dialog.sel_year and \
                    value.month == self.date_dialog.sel_month and \
                    value.day == self.date_dialog.sel_day:
                return
            self.date_dialog.update_calendar(value.year, value.month)
            __day = str(value.day)
            __child = None
            for child in self.date_dialog.calendar_layout.children:
                __is_MDDatePickerDaySelectableItem_instance = (isinstance(child, MDLabel)
                                                               and isinstance(child, ButtonBehavior))
                if __is_MDDatePickerDaySelectableItem_instance:
                    if child.text == __day:
                        child.is_selected = True
                        __child = child
                        break
            if __child is None:
                raise IndexError("Failed to find the date in the calendar.")
            self.date_dialog.set_selected_widget(__child)

    def on_text_validate(self):
        super().on_text_validate()
        if self.date_dialog.is_open:
            self.on_date_ok(self.date_dialog)
        elif self.time_dialog.is_open:
            self.on_time_ok(self.time_dialog)

    def on_cancel(self, instance: Optional[Union[MDModalDatePicker, MDTimePickerDialVertical]] = None):
        if instance is not None:
            instance.dismiss()
        else:
            self.date_dialog.dismiss()
            self.time_dialog.dismiss()
        if not self.text:
            self.date = self.time = self.datetime = None
        self.focus = False

    @property
    def leading_icon(self) -> str:
        return self._leading_icon.icon

    @leading_icon.setter
    def leading_icon(self, value):
        self._leading_icon.icon = value
