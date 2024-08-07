from functools import partial
from typing import Optional, Literal

from kivy.clock import Clock
from kivy.properties import ColorProperty, ObjectProperty
from kivymd.uix.label import MDLabel

from libs.uix.components.dashboard.base_calendar_item import BaseCalendarItem

from .calendar_item_nav import CalendarItemNav


class CalendarItem(BaseCalendarItem):
    text_color = ColorProperty(None)
    _lbl_description = ObjectProperty(None)

    def __init__(self,
                 *args,
                 item: Optional[dict] = None,
                 **kwargs):
        self.on_title = partial(self.update_label, 'lbl_title')
        self.on_tag = partial(self.update_label, 'lbl_tag')
        super(CalendarItem, self).__init__(*args, **kwargs)

        if item is not None:
            self.set_properties_by_dict(item)

        self._lbl_description = MDLabel(id='lbl_description',
                                        font_style="Body",
                                        role="small",
                                        halign="justify",
                                        theme_text_color='Custom' if self.theme_text_color in ['Hint', 'Error']
                                        else self.theme_text_color,
                                        text_color=self.text_color,
                                        text=self.description)

        self.bind(description=self._lbl_description.setter('text'), closed=self.on_closed)
        self.theme_cls.bind(theme_style=lambda: self.set_theme_color(self._theme_text_color))

    @staticmethod
    def update_label(label_name: str, self, value: str):
        __lbl = self.ids.get(label_name, None)
        if __lbl is None:
            return
        __lbl.text = value

    def on_release(self, *args) -> None:
        super(CalendarItem, self).on_release(*args)
        self.dispatch("on_item_release")

    def on_press(self) -> None:
        super(CalendarItem, self).on_press()
        self.dispatch("on_item_press")

    def add_widget(self, widget, *args, **kwargs):
        if isinstance(widget, CalendarItemNav):
            for children in self.ids.item_header.children:
                if isinstance(children, CalendarItemNav):
                    self.ids.item_header.remove_widget(children)
            self.ids.item_header.add_widget(widget)
            return
        super(CalendarItem, self).add_widget(widget, *args, **kwargs)

    def remove_widget(self, widget):
        if isinstance(widget, CalendarItemNav):
            self.ids.item_header.remove_widget(widget)
            return
        super(CalendarItem, self).remove_widget(widget)

    @staticmethod
    def on_height(self, value: int):
        if self._lbl_description is None:
            return
        if value >= self.base_height and self._lbl_description.parent is None:
            Clock.schedule_once(lambda x: self.ids.box_description.add_widget(self._lbl_description))
        elif value < self.base_height and self._lbl_description.parent is not None:
            Clock.schedule_once(lambda x: self.ids.box_description.remove_widget(self._lbl_description))

    @staticmethod
    def on_ids(self, value: list):
        if len(value) > 3:
            self.set_theme_color(self.theme_text_color)

    @staticmethod
    def on_theme_text_color(self, value: Literal['Primary', 'Hint', 'Error', 'Custom']):
        if value == 'Custom' and self.text_color is None:
            return
        if not self.ids:
            return
        if len(self.ids) < 4:
            return
        self.set_theme_color(value)

    @staticmethod
    def on_text_color(self, value):
        if self.theme_text_color != 'Custom' or value is None:
            return
        self.on_theme_text_color(self, 'Custom')

    _theme_text_color = 'Primary'

    def set_theme_color(self, value: Literal['Primary', 'Hint', 'Error', 'Custom']):
        __bg_color = None
        __custom_color = None
        __value = value
        self._theme_text_color = value

        if value in ['Hint', 'Error', 'Custom']:
            if value == 'Custom':
                __custom_color = self.text_color
            elif value == 'Hint':
                __bg_color = self.theme_cls.outlineVariantColor
                self.text_color = __custom_color = self.theme_cls.outlineColor
            else:  # if value == 'Error':
                __bg_color = self.theme_cls.errorContainerColor
                self.text_color = __custom_color = self.theme_cls.errorColor
            __value = 'Custom'

        __check_icon = self.ids.get('check_icon', None)
        if __check_icon is not None:
            if __custom_color is not None:
                __check_icon.icon_color = __custom_color
            __check_icon.theme_icon_color = __value

        for lbl_name in ['lbl_title', 'lbl_duration', 'lbl_tag']:
            __lbl: MDLabel = self.ids.get(lbl_name, None)
            if __lbl is not None:
                if __custom_color is not None:
                    __lbl.text_color = __custom_color
                __lbl.theme_text_color = __value

        if self._lbl_description is not None:
            if __custom_color is not None:
                self._lbl_description.text_color = __custom_color
            self._lbl_description.theme_text_color = __value

        if __bg_color is not None:
            self.md_bg_color = __bg_color

    def on_duration(self, *args):
        if self.start is None or self.end is None:
            return
        super().on_duration(*args)

        self.height = self.base_height * ((self.end - self.start) / 60)
        self.ids.lbl_duration.text = self.format_duration()

    def on_closed(self, *args):
        pass
