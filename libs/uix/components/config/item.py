from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemTrailingIcon


class BaseListItemTextField(TextInput):

    numeric = BooleanProperty(False)

    def __init__(self, **kwargs):
        kwargs['multiline'] = False
        super(BaseListItemTextField, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.background_color = (0, 0, 0, 0)

    @staticmethod
    def on_text(self, value: str):
        if self.numeric and not value.isnumeric():
            __new_text = ""
            for char in value:
                if char.isnumeric():
                    __new_text += char
            self.text = __new_text


class ConfigItem(MDListItem):

    text = StringProperty('')
    current = StringProperty('')
    numeric = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.register_event_type('on_edit')

        self._headline_label = MDListItemHeadlineText(text=self.text)
        self._supporting_label = MDListItemSupportingText(text=self.current)
        self._supporting_field = BaseListItemTextField(text=self.current, numeric=self.numeric,
                                                       height=self._supporting_label.height,
                                                       font_size=self._supporting_label.font_size,
                                                       line_height=self._supporting_label.line_height,
                                                       padding=self._supporting_label.padding)
        self._supporting_label.bind(height=self._supporting_field.setter('height'),
                                    font_size=self._supporting_field.setter('font_size'),
                                    line_height=self._supporting_field.setter('line_height'),
                                    padding=self._supporting_field.setter('padding'))

        self.bind(text=self._headline_label.setter('text'),
                  numeric=self._supporting_field.setter('numeric'))
        self._supporting_field.bind(on_text_validate=self._on_text_validate)

        Clock.schedule_once(lambda c: self._add_widgets())

    def _add_widgets(self):
        self.add_widget(self._headline_label)
        self.add_widget(self._supporting_label)
        self.add_widget(MDListItemTrailingIcon(icon='chevron-right'))

    def _on_text_validate(self, instance: BaseListItemTextField):
        self.current = instance.text
        self.dispatch('on_edit', self.current)

    def edit(self):
        self._supporting_field.text = self.current
        self.ids.text_container.remove_widget(self._supporting_label)
        if len(self.ids.text_container.children) < 3:
            self.ids.text_container.add_widget(self._supporting_field)
            self._supporting_field.focus = True
        elif len(self.ids.text_container.children) > 3:
            self._set_warnings(self._supporting_field)

    def on_edit(self, value: str):
        self.ids.text_container.remove_widget(self._supporting_field)
        if len(self.ids.text_container.children) < 3:
            self.ids.text_container.add_widget(self._supporting_label)
        elif len(self.ids.text_container.children) > 3:
            self._set_warnings(self._supporting_field)

    @staticmethod
    def on_current(self, value: str):
        self._supporting_label.text = value
        self._supporting_field.text = value
