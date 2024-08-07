from kivy.properties import StringProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch


class ConfigSwitch(MDBoxLayout):
    text = StringProperty('')
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._label = MDLabel(text=self.text, adaptive_height=True)
        self._switch = MDSwitch(adaptive_height=True, pos_hint={'right': 1, 'center_y': .5}, active=self.active)

        self.size_hint_y = None
        self.height = self._switch.height
        self._switch.bind(active=self.setter('active'), height=self.setter('height'))
        self.bind(active=self._switch.setter('active'), text=self._label.setter('text'))
        self.add_widget(self._label)
        self.add_widget(self._switch)
