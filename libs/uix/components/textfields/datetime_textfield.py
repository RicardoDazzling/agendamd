from typing import Optional, Union

from babel.dates import format_date, format_time, format_datetime
from kivy.properties import ObjectProperty, NumericProperty, OptionProperty, StringProperty
from kivymd.uix.pickers import MDModalDatePicker, MDTimePickerDialVertical
from kivymd.uix.textfield import MDTextField
from datetime import date, time, datetime


class DateTimeTextField(MDTextField):

    datetime_mode = OptionProperty("datetime", options=["date", "time", "datetime"])
    date_dialog = ObjectProperty(None)
    time_dialog = ObjectProperty(None)
    datetime: Optional[datetime] = ObjectProperty(None, allownone=True)
    date: Optional[date] = ObjectProperty(None, allownone=True)
    time: Optional[time] = ObjectProperty(None, allownone=True)
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
        if __now.hour > 12:
            self.time_dialog.am_pm = 'pm'

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

    def on_datetime(self, instance, value: Union[datetime, date, time]):
        if self.datetime_mode == 'datetime' and isinstance(value, datetime):
            self.text = format_datetime(value, locale=self.locale)
        elif self.datetime_mode == 'date' and isinstance(value, date):
            self.text = format_date(value, locale=self.locale)
        elif self.datetime_mode == 'time' and isinstance(value, time):
            self.text = format_time(value, locale=self.locale)

    def on_text_validate(self):
        super().on_text_validate()
        if self.date_dialog.is_open:
            self.on_date_ok(self.date_dialog)
        elif self.time_dialog.is_open:
            self.on_time_ok(self.time_dialog)

    def on_cancel(self, instance: Optional[MDModalDatePicker | MDTimePickerDialVertical] = None):
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
