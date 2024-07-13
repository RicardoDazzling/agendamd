from functools import partial
from typing import Optional, Tuple

from kivy.properties import BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField


class ComboTextField(MDTextField):
    accept_unknown = BooleanProperty(False)
    data = ObjectProperty([])
    items = ObjectProperty([])
    _last_selected_idx = None

    def __init__(self, *args, **kwargs):
        self.dropdown = MDDropdownMenu(caller=self, items=self.items)
        self.dropdown.bind(on_dismiss=self.on_dismiss)

        super(ComboTextField, self).__init__(*args, **kwargs)
        if len(self.data) > 0:
            self.on_text(self, self.text)

    def on_focus(self, instance, value):
        super(ComboTextField, self).on_focus(instance, value)
        if value:
            self.dropdown_open()

    def on_dismiss(self, *args):
        if not self.accept_unknown:
            if self.text not in self.data:
                self.text = ""
                return
        self.on_text(self, self.text, skip=True)
                    
    def keyboard_on_key_up(self, window, keycode: Tuple[int, str]):
        if self._last_selected_idx is not None:
            if keycode[0] == 273 or keycode[1] == 'up':  # Up
                __last = self._last_selected_idx - 1
                if __last >= 0:
                    self.select_item(__last)
                return
            elif keycode[0] == 274 or keycode[1] == 'down':  # Down
                __next = self._last_selected_idx + 1
                if len(self.items) > __next:
                    self.select_item(__next)
                return
        super(ComboTextField, self).keyboard_on_key_up(window, keycode)

    def on_text_validate(self):
        super().on_text_validate()

        self.dropdown.dismiss()

        if self._last_selected_idx is None or len(self.items) == 0:
            return

        if self._last_selected_idx < len(self.items):
            self.text = self.items[self._last_selected_idx]['text']

    @staticmethod
    def on_data(self, value: list):
        if not isinstance(value, list):
            raise TypeError("Data isn't a list instance.")
        if self.text == "" and value:
            self.items = self.get_items_from_list(value)

    @staticmethod
    def on_text(self, value: str, skip: bool = False):
        if self.dropdown.parent is not None and not skip:
            return

        if not self.data or value == "":
            self._last_selected_idx = None
            self.items = self.get_items_from_list(self.data)
            return

        __items = []
        for item in self.data:
            if value.lower() in item.lower():
                __items.append(item)

        if not __items:
            self._last_selected_idx = None
            self.items = []
            return

        self.items = self.get_items_from_list(__items)

        if len(__items) == 1:
            if __items[0] == value:
                self.dropdown.dismiss()

    @staticmethod
    def on_items(self, value: list):
        if self.dropdown.parent:
            self.dropdown.parent.remove_widget(self.dropdown)
        self.dropdown.items = value
        if self.items:
            Clock.schedule_once(lambda x: self.dropdown_open())

    def get_items_from_list(self, values: list):
        __draft = []
        for idx in range(len(values)):
            __item = {'text': values[idx],
                      "trailing_icon_color": self.theme_cls.primaryColor,
                      "on_release": partial(self.set_item, idx)}
            if idx == 0:
                self._last_selected_idx = 0
                __item["trailing_icon"] = "circle"
            __draft.append(__item)
        return __draft

    def set_item(self, index: int):
        if self.dropdown.parent:
            self.dropdown.parent.remove_widget(self.dropdown)
        __new_text = self.items[index].get('text', '')
        if self.text != __new_text and __new_text != '':
            self.text = __new_text

    def select_item(self, index: int):
        if not self.dropdown.parent:
            return

        # Todo: create a trailing icon to show the position.
        # __items = self.items.copy()
        # if __items[index].get("trailing_icon", None) is None:
        #     if self._last_selected_idx is not None:
        #         __items[self._last_selected_idx].pop("trailing_icon")
        #         __items[self._last_selected_idx]['viewclass'] = 'MDDropdownTextItem'
        #     __items[index]["trailing_icon"] = "circle"
        #     __items[index]['viewclass'] = 'MDDropdownTrailingIconItem'
        #     self.items = __items

        self.text = self.items[index]['text']
        self._last_selected_idx = index

    def dropdown_open(self):
        if self.dropdown.parent:
            self.dropdown.parent.remove_widget(self.dropdown)
        if self.x > 0 or self.y > 0:
            self.dropdown.open()

    @property
    def selected(self) -> Optional[str]:
        if self._last_selected_idx is None:
            return None
        if self._last_selected_idx < len(self.items):
            __last: str = self.items[self._last_selected_idx]['text']
        else:
            return None
        return None if __last.lower() != self.text.lower() else __last

    @property
    def leading_icon(self) -> str:
        return self._leading_icon.icon

    @leading_icon.setter
    def leading_icon(self, value):
        self._leading_icon.icon = value
