from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout


class ConfigCardHeader(MDRelativeLayout):

    icon = StringProperty()
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._box_layout = MDBoxLayout(adaptive_size=True, pos_hint={'center_x': .5})
        self._icon = MDIcon(icon=self.icon, adaptive_size=True)
        self._label = MDLabel(text=self.text, adaptive_size=True, font_style='Title', role='large')
        self.size_hint_y = None
        self.height = self._label.height
        self._box_layout.bind(height=self.setter('height'))

        self.bind(icon=self._icon.setter('icon'), text=self._label.setter('text'))

        self._box_layout.add_widget(self._icon)
        self._box_layout.add_widget(self._label)
        self.add_widget(self._box_layout)
